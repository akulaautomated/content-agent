"""
Seed script — creates demo data so you can test the app immediately after startup.
Run with: docker compose exec backend python -m app.scripts.seed
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings
from app.models import Organization, User, BrandProfile, Campaign
from app.auth import hash_password

engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
    async with AsyncSessionLocal() as db:
        # Create demo org
        org = Organization(name="Demo Agency", slug="demo-agency")
        db.add(org)
        await db.flush()

        # Create admin user
        user = User(
            org_id=org.id,
            email="admin@demo.com",
            hashed_password=hash_password("demo1234"),
            full_name="Demo Admin",
        )
        db.add(user)

        # Create a default brand profile
        brand = BrandProfile(
            org_id=org.id,
            name="Demo Brand",
            description="A sample brand voice for testing",
            tone="conversational",
            voice_attributes={"formality": 6, "enthusiasm": 7, "authority": 8},
            vocabulary={
                "preferred": ["results-driven", "data-backed", "scalable"],
                "banned": ["synergy", "paradigm shift", "leverage (as a verb)"],
            },
            style_rules={
                "sentence_length_max": 20,
                "use_contractions": True,
                "active_voice_preference": True,
            },
            is_default=True,
        )
        db.add(brand)

        # Create a sample campaign
        campaign = Campaign(
            org_id=org.id,
            name="Q1 Content Push",
            description="Blog posts and social content for Q1 lead generation",
            status="active",
        )
        db.add(campaign)

        await db.commit()
        print("✅  Demo data seeded!")
        print("   Email:    admin@demo.com")
        print("   Password: demo1234")
        print("   Visit:    http://localhost:3000")


if __name__ == "__main__":
    asyncio.run(seed())
