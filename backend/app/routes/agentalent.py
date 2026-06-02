"""
Agentalent Sensei Handshake Integration

Allows Agentalent to evaluate ContentAgent by sending test prompts
and receiving scored responses.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

router = APIRouter()

# Import orchestrator lazily to avoid blocking route registration
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        try:
            from app.agents.orchestrator import orchestrator as orch
            orchestrator = orch
        except Exception as e:
            raise RuntimeError(f"Failed to load orchestrator: {str(e)}")
    return orchestrator


class HandshakeTask(BaseModel):
    task_id: str
    prompt: str
    task_type: str  # "blog", "email", "social", "ad", "landing_page", etc.
    requirements: dict = {}


class HandshakeResponse(BaseModel):
    task_id: str
    response: str
    metadata: dict = {}


@router.post("/api/agentalent/evaluate")
async def evaluate_task(task: HandshakeTask):
    """
    Agentalent sends a task prompt.
    ContentAgent generates a response.
    Returns the generated content for Sensei to score.
    """
    try:
        orch = get_orchestrator()

        # Map task_type to content_type and agent
        task_type_mapping = {
            "blog": "blog_post",
            "email": "email",
            "social": "social_post",
            "ad": "ad_copy",
            "landing_page": "landing_page",
            "case_study": "case_study",
        }

        content_type = task_type_mapping.get(task.task_type, "blog_post")

        # Generate content using the orchestrator
        start_time = time.time()

        result = await orch.generate(
            agent_type="blog_writer" if content_type == "blog_post" else content_type,
            task=task.prompt,
            context={
                "org_id": "agentalent-eval",
                "brand_id": None,
                "content_type": content_type,
            },
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Extract the generated content
        generated_content = result.get("result", "")

        return HandshakeResponse(
            task_id=task.task_id,
            response=generated_content,
            metadata={
                "content_type": content_type,
                "latency_ms": latency_ms,
                "tokens_used": result.get("tokens_used", 0),
                "model": "gpt-4o",
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing handshake task: {str(e)}",
        )


@router.post("/api/agentalent/health")
async def agentalent_health():
    """Health check for Agentalent evaluation system."""
    return {
        "status": "healthy",
        "agent": "ContentAgent",
        "api_version": "1.0.0",
        "llm_model": "gpt-4o",
        "capabilities": [
            "blog_post",
            "email",
            "social_post",
            "ad_copy",
            "landing_page",
            "case_study",
        ],
    }
