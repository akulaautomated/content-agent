-- ─── Extensions ──────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTE: We use VARCHAR instead of PostgreSQL native ENUMs to keep
-- SQLAlchemy integration simple. Values are validated at the API layer.

-- ─── Organizations (multi-tenant: each agency client is an org) ─
CREATE TABLE organizations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Users ───────────────────────────────────────────────────
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Brand Profiles ───────────────────────────────────────────
CREATE TABLE brand_profiles (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id            UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name              VARCHAR(255) NOT NULL,
    description       TEXT,
    tone              VARCHAR(50) DEFAULT 'conversational',
    voice_attributes  JSONB DEFAULT '{}',
    vocabulary        JSONB DEFAULT '{"preferred": [], "banned": []}',
    style_rules       JSONB DEFAULT '{}',
    target_audiences  JSONB DEFAULT '[]',
    is_default        BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Campaigns ────────────────────────────────────────────────
CREATE TABLE campaigns (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    brand_id        UUID REFERENCES brand_profiles(id),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    goals           JSONB DEFAULT '{}',
    target_audience JSONB DEFAULT '{}',
    start_date      DATE,
    end_date        DATE,
    status          VARCHAR(50) DEFAULT 'active',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Content Items ────────────────────────────────────────────
-- content_type values: blog_post, email, social_post, ad_copy, landing_page, case_study
-- platform values:     linkedin, twitter_x, instagram, facebook, google_ads, meta_ads, email, website, blog
-- tone values:         technical, conversational, formal, casual, persuasive, educational
-- status values:       idea, draft, review, approved, scheduled, published, archived
CREATE TABLE content_items (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id         UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    brand_id            UUID REFERENCES brand_profiles(id),
    content_type        VARCHAR(50) NOT NULL,
    platform            VARCHAR(50),
    title               VARCHAR(500),
    body                TEXT,
    excerpt             TEXT,
    meta_description    VARCHAR(300),
    keywords            JSONB DEFAULT '[]',
    seo_data            JSONB DEFAULT '{}',
    tone                VARCHAR(50) DEFAULT 'conversational',
    target_audience     VARCHAR(255),
    status              VARCHAR(50) DEFAULT 'draft',
    version             INTEGER DEFAULT 1,
    parent_id           UUID REFERENCES content_items(id),
    agent_type          VARCHAR(100),
    generation_params   JSONB DEFAULT '{}',
    scheduled_at        TIMESTAMPTZ,
    published_at        TIMESTAMPTZ,
    published_url       TEXT,
    word_count          INTEGER DEFAULT 0,
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Content Revisions ────────────────────────────────────────
CREATE TABLE content_revisions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id      UUID REFERENCES content_items(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    body            TEXT,
    changes_summary TEXT,
    revised_by      VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Content Calendar ─────────────────────────────────────────
CREATE TABLE content_calendar (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    content_id      UUID REFERENCES content_items(id) ON DELETE SET NULL,
    platform        VARCHAR(50),
    scheduled_date  DATE NOT NULL,
    scheduled_time  TIME,
    status          VARCHAR(50) DEFAULT 'planned',
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── SEO Keywords ─────────────────────────────────────────────
CREATE TABLE seo_keywords (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    keyword         VARCHAR(500) NOT NULL,
    search_volume   INTEGER,
    difficulty      FLOAT,
    current_rank    INTEGER,
    target_rank     INTEGER,
    tracked_url     TEXT,
    last_checked    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Content Analytics ────────────────────────────────────────
CREATE TABLE content_analytics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id      UUID REFERENCES content_items(id) ON DELETE CASCADE,
    platform        VARCHAR(50),
    date            DATE NOT NULL,
    impressions     INTEGER DEFAULT 0,
    clicks          INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0,
    conversions     INTEGER DEFAULT 0,
    shares          INTEGER DEFAULT 0,
    comments        INTEGER DEFAULT 0,
    likes           INTEGER DEFAULT 0,
    ctr             FLOAT DEFAULT 0,
    raw_data        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Agent Tasks ──────────────────────────────────────────────
CREATE TABLE agent_tasks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID REFERENCES organizations(id),
    agent_type      VARCHAR(100) NOT NULL,
    task            TEXT NOT NULL,
    context         JSONB DEFAULT '{}',
    result          TEXT,
    tool_uses       JSONB DEFAULT '[]',
    iterations      INTEGER DEFAULT 0,
    tokens_used     INTEGER DEFAULT 0,
    latency_ms      INTEGER DEFAULT 0,
    status          VARCHAR(50) DEFAULT 'pending',
    error           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Indexes ──────────────────────────────────────────────────
CREATE INDEX idx_content_org_type_status ON content_items(org_id, content_type, status);
CREATE INDEX idx_content_scheduled       ON content_items(org_id, scheduled_at);
CREATE INDEX idx_content_campaign        ON content_items(campaign_id);
CREATE INDEX idx_analytics_content_date  ON content_analytics(content_id, date);
CREATE INDEX idx_keywords_org            ON seo_keywords(org_id);
CREATE INDEX idx_calendar_org_date       ON content_calendar(org_id, scheduled_date);
CREATE INDEX idx_agent_tasks_org         ON agent_tasks(org_id, created_at);
