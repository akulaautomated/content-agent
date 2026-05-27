import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, Float, DateTime, Date, Time, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    users = relationship("User", back_populates="org")
    brands = relationship("BrandProfile", back_populates="org")
    campaigns = relationship("Campaign", back_populates="org")
    content_items = relationship("ContentItem", back_populates="org")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    org = relationship("Organization", back_populates="users")


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str] = mapped_column(String(50), default="conversational")
    voice_attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    vocabulary: Mapped[dict] = mapped_column(JSONB, default=lambda: {"preferred": [], "banned": []})
    style_rules: Mapped[dict] = mapped_column(JSONB, default=dict)
    target_audiences: Mapped[list] = mapped_column(JSONB, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    org = relationship("Organization", back_populates="brands")


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    brand_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("brand_profiles.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[dict] = mapped_column(JSONB, default=dict)
    target_audience: Mapped[dict] = mapped_column(JSONB, default=dict)
    start_date: Mapped[datetime | None] = mapped_column(Date)
    end_date: Mapped[datetime | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    org = relationship("Organization", back_populates="campaigns")
    content_items = relationship("ContentItem", back_populates="campaign")


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    campaign_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("campaigns.id"))
    brand_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("brand_profiles.id"))
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(500))
    body: Mapped[str | None] = mapped_column(Text)
    excerpt: Mapped[str | None] = mapped_column(Text)
    meta_description: Mapped[str | None] = mapped_column(String(300))
    keywords: Mapped[list] = mapped_column(JSONB, default=list)
    seo_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    tone: Mapped[str] = mapped_column(String(50), default="conversational")
    target_audience: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="draft")
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id"))
    agent_type: Mapped[str | None] = mapped_column(String(100))
    generation_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_url: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    org = relationship("Organization", back_populates="content_items")
    campaign = relationship("Campaign", back_populates="content_items")
    revisions = relationship("ContentRevision", back_populates="content_item", cascade="all, delete-orphan")
    analytics = relationship("ContentAnalytics", back_populates="content_item", cascade="all, delete-orphan")


class ContentRevision(Base):
    __tablename__ = "content_revisions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    content_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id", ondelete="CASCADE"))
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str | None] = mapped_column(Text)
    changes_summary: Mapped[str | None] = mapped_column(Text)
    revised_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    content_item = relationship("ContentItem", back_populates="revisions")


class ContentCalendar(Base):
    __tablename__ = "content_calendar"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    content_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id"))
    platform: Mapped[str | None] = mapped_column(String(50))
    scheduled_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[datetime | None] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(50), default="planned")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class SEOKeyword(Base):
    __tablename__ = "seo_keywords"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    keyword: Mapped[str] = mapped_column(String(500), nullable=False)
    search_volume: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[float | None] = mapped_column(Float)
    current_rank: Mapped[int | None] = mapped_column(Integer)
    target_rank: Mapped[int | None] = mapped_column(Integer)
    tracked_url: Mapped[str | None] = mapped_column(Text)
    last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class ContentAnalytics(Base):
    __tablename__ = "content_analytics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    content_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("content_items.id", ondelete="CASCADE"))
    platform: Mapped[str | None] = mapped_column(String(50))
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[float] = mapped_column(Float, default=0)
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    content_item = relationship("ContentItem", back_populates="analytics")


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    org_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("organizations.id"))
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[str | None] = mapped_column(Text)
    tool_uses: Mapped[list] = mapped_column(JSONB, default=list)
    iterations: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
