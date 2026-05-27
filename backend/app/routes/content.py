from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import time

from app.database import get_db
from app.models import ContentItem, ContentRevision, AgentTask, BrandProfile, User
from app.schemas import (
    ContentCreate, ContentUpdate, ContentOut,
    ContentGenerateRequest, ContentTransitionRequest,
)
from app.auth import get_current_user
from app.agents.orchestrator import orchestrator, CONTENT_TYPE_TO_AGENT
from app.config import settings

router = APIRouter()

# Valid status transitions (can only move forward, not backward randomly)
VALID_TRANSITIONS = {
    "idea": ["draft"],
    "draft": ["review", "archived"],
    "review": ["approved", "draft"],
    "approved": ["scheduled", "draft"],
    "scheduled": ["published", "approved"],
    "published": ["archived"],
    "archived": [],
}


@router.get("", response_model=List[ContentOut])
async def list_content(
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List content items with optional filters."""
    query = select(ContentItem).where(ContentItem.org_id == current_user.org_id)

    if content_type:
        query = query.where(ContentItem.content_type == content_type)
    if status:
        query = query.where(ContentItem.status == status)
    if platform:
        query = query.where(ContentItem.platform == platform)
    if campaign_id:
        query = query.where(ContentItem.campaign_id == campaign_id)

    query = query.order_by(ContentItem.updated_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ContentOut, status_code=201)
async def create_content(
    body: ContentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually create a content item (without AI generation)."""
    item = ContentItem(
        org_id=current_user.org_id,
        created_by=current_user.id,
        word_count=len((body.body or "").split()),
        **body.model_dump(),
    )
    db.add(item)
    await db.flush()
    return item


@router.post("/generate", response_model=ContentOut, status_code=201)
async def generate_content(
    body: ContentGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Use AI to generate content.

    This is the main endpoint — send a brief and get fully written content back.
    The generated content is saved as a draft automatically.
    """
    # Pick the right agent for this content type
    agent_type = CONTENT_TYPE_TO_AGENT.get(body.content_type)
    if not agent_type:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content_type. Choose from: {list(CONTENT_TYPE_TO_AGENT.keys())}"
        )

    # Build the context the agent tools need
    context = {
        "org_id": current_user.org_id,
        "brand_id": body.brand_id,
        "auth_token": "",  # agent tools use internal calls, not authenticated
        "api_base_url": f"http://localhost:{settings.api_port}",
    }

    # Build the task message
    task = orchestrator.build_task_message(
        brief=body.brief,
        content_type=body.content_type,
        tone=body.tone,
        target_audience=body.target_audience,
        keywords=body.keywords,
        platform=body.platform,
        word_count_target=body.word_count_target,
        brand_id=body.brand_id,
    )

    # Log the task start
    agent_task = AgentTask(
        org_id=current_user.org_id,
        agent_type=agent_type,
        task=body.brief,
        context={"content_type": body.content_type, "tone": body.tone, "keywords": body.keywords},
        status="running",
    )
    db.add(agent_task)
    await db.flush()

    try:
        # Run the AI agent
        result = await orchestrator.generate(
            agent_type=agent_type,
            task=task,
            context=context,
        )

        # Update the task log
        agent_task.status = "completed"
        agent_task.result = result["content"][:1000]  # truncate for storage
        agent_task.tool_uses = result["tool_uses"]
        agent_task.iterations = result["iterations"]
        agent_task.tokens_used = result["tokens_used"]
        agent_task.latency_ms = result["latency_ms"]

        # Parse any metadata the agent extracted (from the structured output format)
        draft_data = result.get("draft_result") or {}
        content_body = result["content"]
        title = draft_data.get("title") or _extract_title(content_body) or body.brief[:100]
        meta_desc = draft_data.get("meta_description") or _extract_meta(content_body)
        excerpt = draft_data.get("excerpt") or content_body[:200]
        word_count = len(content_body.split())

        # Save the generated content as a draft
        content_item = ContentItem(
            org_id=current_user.org_id,
            created_by=current_user.id,
            content_type=body.content_type,
            platform=body.platform,
            title=title,
            body=content_body,
            excerpt=excerpt,
            meta_description=meta_desc,
            keywords=body.keywords,
            seo_data=draft_data.get("seo_data", {}),
            tone=body.tone,
            target_audience=body.target_audience,
            status="draft",
            agent_type=agent_type,
            generation_params={
                "brief": body.brief,
                "model": settings.llm_model,
                "provider": settings.llm_provider,
                "iterations": result["iterations"],
            },
            campaign_id=body.campaign_id,
            brand_id=body.brand_id,
            word_count=word_count,
        )
        db.add(content_item)
        await db.flush()
        return content_item

    except Exception as e:
        agent_task.status = "failed"
        agent_task.error = str(e)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentItem).where(
            ContentItem.id == content_id,
            ContentItem.org_id == current_user.org_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


@router.put("/{content_id}", response_model=ContentOut)
async def update_content(
    content_id: str,
    body: ContentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentItem).where(
            ContentItem.id == content_id,
            ContentItem.org_id == current_user.org_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    # Save revision before updating
    if body.body and body.body != item.body:
        revision = ContentRevision(
            content_id=item.id,
            version=item.version,
            body=item.body,
            changes_summary="Manual edit",
            revised_by=current_user.email,
        )
        db.add(revision)
        item.version += 1

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    if body.body:
        item.word_count = len(body.body.split())

    return item


@router.post("/{content_id}/transition", response_model=ContentOut)
async def transition_status(
    content_id: str,
    body: ContentTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Move content along the pipeline: draft → review → approved → scheduled → published."""
    result = await db.execute(
        select(ContentItem).where(
            ContentItem.id == content_id,
            ContentItem.org_id == current_user.org_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")

    allowed_next = VALID_TRANSITIONS.get(item.status, [])
    if body.new_status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot move from '{item.status}' to '{body.new_status}'. Allowed: {allowed_next}",
        )

    item.status = body.new_status
    if body.new_status == "published":
        from datetime import datetime
        item.published_at = datetime.utcnow()

    return item


@router.get("/{content_id}/revisions")
async def get_revisions(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the edit history for a piece of content."""
    result = await db.execute(
        select(ContentRevision)
        .where(ContentRevision.content_id == content_id)
        .order_by(ContentRevision.version.desc())
    )
    revisions = result.scalars().all()
    return [
        {
            "version": r.version,
            "changes_summary": r.changes_summary,
            "revised_by": r.revised_by,
            "created_at": str(r.created_at),
        }
        for r in revisions
    ]


def _extract_title(content: str) -> Optional[str]:
    """Try to extract the title from the agent's structured output."""
    for line in content.split("\n"):
        if line.startswith("TITLE:"):
            return line.replace("TITLE:", "").strip()
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return None


def _extract_meta(content: str) -> Optional[str]:
    """Try to extract the meta description from the agent's output."""
    for line in content.split("\n"):
        if line.startswith("META_DESCRIPTION:"):
            return line.replace("META_DESCRIPTION:", "").strip()[:300]
    return None
