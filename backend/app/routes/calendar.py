from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import ContentCalendar, User
from app.schemas import CalendarEntryCreate, CalendarEntryOut
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[CalendarEntryOut])
async def get_calendar(
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get calendar entries. Optionally filter by date range (YYYY-MM-DD)."""
    query = select(ContentCalendar).where(ContentCalendar.org_id == current_user.org_id)
    if start:
        query = query.where(ContentCalendar.scheduled_date >= start)
    if end:
        query = query.where(ContentCalendar.scheduled_date <= end)
    result = await db.execute(query.order_by(ContentCalendar.scheduled_date))
    return result.scalars().all()


@router.post("", response_model=CalendarEntryOut, status_code=201)
async def schedule_content(
    body: CalendarEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = ContentCalendar(org_id=current_user.org_id, **body.model_dump())
    db.add(entry)
    await db.flush()
    return entry


@router.put("/{entry_id}", response_model=CalendarEntryOut)
async def update_calendar_entry(
    entry_id: str,
    body: CalendarEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentCalendar).where(
            ContentCalendar.id == entry_id,
            ContentCalendar.org_id == current_user.org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Calendar entry not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_calendar_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContentCalendar).where(
            ContentCalendar.id == entry_id,
            ContentCalendar.org_id == current_user.org_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Calendar entry not found")
    await db.delete(entry)
