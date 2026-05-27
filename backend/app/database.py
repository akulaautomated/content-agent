from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# The "engine" is the connection to the database
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Session factory — each request gets its own database session
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


async def get_db():
    """FastAPI dependency: provides a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
