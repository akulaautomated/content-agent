from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import BrandProfile, User
from app.schemas import BrandProfileCreate, BrandProfileUpdate, BrandProfileOut
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[BrandProfileOut])
async def list_brands(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BrandProfile).where(BrandProfile.org_id == current_user.org_id)
    )
    return result.scalars().all()


@router.post("", response_model=BrandProfileOut, status_code=201)
async def create_brand(
    body: BrandProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If this is set as default, unset any existing default first
    if body.is_default:
        existing_defaults = await db.execute(
            select(BrandProfile).where(
                BrandProfile.org_id == current_user.org_id,
                BrandProfile.is_default == True,
            )
        )
        for bp in existing_defaults.scalars().all():
            bp.is_default = False

    brand = BrandProfile(org_id=current_user.org_id, **body.model_dump())
    db.add(brand)
    await db.flush()
    return brand


@router.get("/{brand_id}", response_model=BrandProfileOut)
async def get_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BrandProfile).where(
            BrandProfile.id == brand_id,
            BrandProfile.org_id == current_user.org_id,
        )
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return brand


@router.put("/{brand_id}", response_model=BrandProfileOut)
async def update_brand(
    brand_id: str,
    body: BrandProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BrandProfile).where(
            BrandProfile.id == brand_id,
            BrandProfile.org_id == current_user.org_id,
        )
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    return brand


@router.delete("/{brand_id}", status_code=204)
async def delete_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BrandProfile).where(
            BrandProfile.id == brand_id,
            BrandProfile.org_id == current_user.org_id,
        )
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    await db.delete(brand)
