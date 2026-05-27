from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models import ContentAnalytics, ContentItem, User
from app.schemas import AnalyticsIn, DashboardStats
from app.auth import get_current_user

router = APIRouter()


@router.post("/ingest", status_code=201)
async def ingest_analytics(
    body: AnalyticsIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add performance data for a piece of content (from manual entry or platform integration)."""
    record = ContentAnalytics(**body.model_dump())
    db.add(record)
    await db.flush()
    return {"id": record.id, "message": "Analytics recorded"}


@router.get("/content/{content_id}")
async def get_content_analytics(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentAnalytics)
        .where(ContentAnalytics.content_id == content_id)
        .order_by(ContentAnalytics.date)
    )
    rows = result.scalars().all()
    return [
        {
            "date": str(r.date),
            "platform": r.platform,
            "impressions": r.impressions,
            "clicks": r.clicks,
            "engagement_rate": r.engagement_rate,
            "conversions": r.conversions,
            "shares": r.shares,
            "likes": r.likes,
        }
        for r in rows
    ]


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate stats for the dashboard overview page."""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0)

    # Total content count
    total_result = await db.execute(
        select(func.count()).select_from(ContentItem)
        .where(ContentItem.org_id == current_user.org_id)
    )
    total_content = total_result.scalar() or 0

    # Published this month
    published_result = await db.execute(
        select(func.count()).select_from(ContentItem)
        .where(
            ContentItem.org_id == current_user.org_id,
            ContentItem.status == "published",
            ContentItem.published_at >= month_start,
        )
    )
    published_this_month = published_result.scalar() or 0

    # Scheduled upcoming
    scheduled_result = await db.execute(
        select(func.count()).select_from(ContentItem)
        .where(
            ContentItem.org_id == current_user.org_id,
            ContentItem.status == "scheduled",
        )
    )
    scheduled_upcoming = scheduled_result.scalar() or 0

    # Average engagement rate
    avg_result = await db.execute(
        select(func.avg(ContentAnalytics.engagement_rate))
        .join(ContentItem, ContentAnalytics.content_id == ContentItem.id)
        .where(ContentItem.org_id == current_user.org_id)
    )
    avg_engagement = round(avg_result.scalar() or 0, 2)

    # Content by type
    type_result = await db.execute(
        select(ContentItem.content_type, func.count())
        .where(ContentItem.org_id == current_user.org_id)
        .group_by(ContentItem.content_type)
    )
    content_by_type = {row[0]: row[1] for row in type_result.all()}

    # Content by status
    status_result = await db.execute(
        select(ContentItem.status, func.count())
        .where(ContentItem.org_id == current_user.org_id)
        .group_by(ContentItem.status)
    )
    content_by_status = {row[0]: row[1] for row in status_result.all()}

    return DashboardStats(
        total_content=total_content,
        published_this_month=published_this_month,
        scheduled_upcoming=scheduled_upcoming,
        avg_engagement_rate=avg_engagement,
        top_platform=None,
        content_by_type=content_by_type,
        content_by_status=content_by_status,
    )
