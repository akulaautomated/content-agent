from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    org_name: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    org_id: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    org_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Brand Profile ────────────────────────────────────────────
class BrandProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tone: str = "conversational"
    voice_attributes: dict = {}
    vocabulary: dict = {"preferred": [], "banned": []}
    style_rules: dict = {}
    target_audiences: list = []
    is_default: bool = False


class BrandProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tone: Optional[str] = None
    voice_attributes: Optional[dict] = None
    vocabulary: Optional[dict] = None
    style_rules: Optional[dict] = None
    target_audiences: Optional[list] = None
    is_default: Optional[bool] = None


class BrandProfileOut(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    tone: str
    voice_attributes: dict
    vocabulary: dict
    style_rules: dict
    target_audiences: list
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Campaign ─────────────────────────────────────────────────
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    brand_id: Optional[str] = None
    goals: dict = {}
    target_audience: dict = {}
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CampaignOut(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str]
    brand_id: Optional[str]
    goals: dict
    target_audience: dict
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Content Item ─────────────────────────────────────────────
class ContentCreate(BaseModel):
    content_type: str  # blog_post, email, social_post, ad_copy, landing_page, case_study
    platform: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    tone: str = "conversational"
    target_audience: Optional[str] = None
    keywords: List[str] = []
    campaign_id: Optional[str] = None
    brand_id: Optional[str] = None


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    excerpt: Optional[str] = None
    meta_description: Optional[str] = None
    tone: Optional[str] = None
    keywords: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ContentOut(BaseModel):
    id: str
    org_id: str
    content_type: str
    platform: Optional[str]
    title: Optional[str]
    body: Optional[str]
    excerpt: Optional[str]
    meta_description: Optional[str]
    keywords: list
    seo_data: dict
    tone: str
    status: str
    word_count: int
    agent_type: Optional[str]
    campaign_id: Optional[str]
    brand_id: Optional[str]
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentGenerateRequest(BaseModel):
    """What you send to ask the AI to generate content."""
    content_type: str       # e.g. "blog_post"
    platform: Optional[str] = None
    brief: str              # Short description of what you want written
    tone: str = "conversational"
    target_audience: Optional[str] = None
    keywords: List[str] = []
    brand_id: Optional[str] = None
    campaign_id: Optional[str] = None
    word_count_target: Optional[int] = None


class ContentTransitionRequest(BaseModel):
    """Move content from one status to the next."""
    new_status: str  # draft -> review -> approved -> scheduled -> published


# ─── Content Calendar ─────────────────────────────────────────
class CalendarEntryCreate(BaseModel):
    content_id: Optional[str] = None
    platform: Optional[str] = None
    scheduled_date: str   # YYYY-MM-DD
    scheduled_time: Optional[str] = None  # HH:MM
    notes: Optional[str] = None


class CalendarEntryOut(BaseModel):
    id: str
    org_id: str
    content_id: Optional[str]
    platform: Optional[str]
    scheduled_date: Any
    scheduled_time: Any
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── SEO ──────────────────────────────────────────────────────
class SEOKeywordCreate(BaseModel):
    keyword: str
    search_volume: Optional[int] = None
    difficulty: Optional[float] = None
    target_rank: Optional[int] = None
    tracked_url: Optional[str] = None


class SEOKeywordOut(BaseModel):
    id: str
    org_id: str
    keyword: str
    search_volume: Optional[int]
    difficulty: Optional[float]
    current_rank: Optional[int]
    target_rank: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class SEOAnalysisResult(BaseModel):
    readability_score: float
    reading_ease: str   # "Easy", "Moderate", "Difficult"
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    keyword_density: dict   # keyword -> percentage
    suggestions: List[str]


# ─── Analytics ────────────────────────────────────────────────
class AnalyticsIn(BaseModel):
    content_id: str
    platform: str
    date: str   # YYYY-MM-DD
    impressions: int = 0
    clicks: int = 0
    engagement_rate: float = 0
    conversions: int = 0
    shares: int = 0
    comments: int = 0
    likes: int = 0


class DashboardStats(BaseModel):
    total_content: int
    published_this_month: int
    scheduled_upcoming: int
    avg_engagement_rate: float
    top_platform: Optional[str]
    content_by_type: dict
    content_by_status: dict
