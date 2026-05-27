from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re

from app.database import get_db
from app.models import Organization, User
from app.schemas import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


def slugify(text: str) -> str:
    """Convert 'My Agency Name' -> 'my-agency-name'"""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Create a new organization + admin user. Call this once to set up your account."""
    # Check email not already taken
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create organization
    slug = slugify(body.org_name)
    org = Organization(name=body.org_name, slug=slug)
    db.add(org)
    await db.flush()  # get org.id without committing yet

    # Create admin user
    user = User(
        org_id=org.id,
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"sub": user.id, "org_id": org.id})
    return TokenResponse(access_token=token, user_id=user.id, org_id=org.id)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Log in and receive a JWT token. Include this token in the Authorization header for all other requests."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.id, "org_id": user.org_id})
    return TokenResponse(access_token=token, user_id=user.id, org_id=user.org_id)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's info."""
    return current_user
