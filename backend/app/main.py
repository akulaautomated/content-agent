from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis.asyncio as aioredis

from app.config import settings
from app.database import engine
from app.models import Base

# Import all route modules
from app.routes import auth, brands, campaigns, content, calendar, seo, analytics

# Note: Agentalent endpoints are defined inline in this file
# (to avoid module import issues)


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


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "model": settings.llm_model,
        "agentalent_available": True,
    }


# ─── Agentalent Sensei Handshake Endpoints ───────────────────────────────────

class EvaluateRequest(BaseModel):
    task_id: str
    task_type: str
    prompt: str
    requirements: dict = {}


@app.post("/api/agentalent/health")
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


@app.post("/api/agentalent/evaluate")
async def agentalent_evaluate(request: EvaluateRequest):
    """
    Agentalent sends a task prompt.
    ContentAgent generates a response.
    Returns the generated content for Sensei to score.
    """
    try:
        from app.agents.orchestrator import orchestrator
        import time

        task_id = request.task_id
        task_type = request.task_type
        prompt = request.prompt

        # Map task_type to agent
        task_type_mapping = {
            "blog": "blog_writer",
            "email": "email",
            "social": "social_post",
            "ad": "ad_copy",
            "landing_page": "landing_page",
            "case_study": "case_study",
        }

        agent_type = task_type_mapping.get(task_type, "blog_writer")

        # Generate content
        start_time = time.time()
        result = await orchestrator.generate(
            agent_type=agent_type,
            task=prompt,
            context={"org_id": "agentalent-eval", "brand_id": None},
        )
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "task_id": task_id,
            "response": result.get("result", ""),
            "metadata": {
                "latency_ms": latency_ms,
                "tokens_used": result.get("tokens_used", 0),
                "model": "gpt-4o",
            },
        }
    except Exception as e:
        return {"error": str(e)}, 500
