from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis

from app.config import settings
from app.database import engine
from app.models import Base

# Import all route modules
from app.routes import auth, brands, campaigns, content, calendar, seo, analytics

# Import agentalent with error handling
try:
    from app.routes import agentalent
except Exception as e:
    print(f"⚠️  Warning: Failed to import agentalent routes: {str(e)}")
    agentalent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    # Connect to Redis cache
    app.state.redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
    print("✅  Redis connected")
    print(f"✅  LLM Provider: {settings.llm_provider} ({settings.llm_model})")
    yield
    # Cleanup on shutdown
    await app.state.redis.close()


app = FastAPI(
    title="AI Content Agent API",
    description="Multi-channel content creation agent for digital marketing agencies",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the frontend (running on port 3000) to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes under /api prefix
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(brands.router, prefix="/api/brands", tags=["Brands"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(seo.router, prefix="/api/seo", tags=["SEO"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
if agentalent is not None:
    app.include_router(agentalent.router, prefix="", tags=["Agentalent"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "llm_provider": settings.llm_provider, "model": settings.llm_model}
