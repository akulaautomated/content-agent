# ✦ ContentAgent — AI-Powered Multi-Channel Content System

> Production-ready AI agent for digital marketing agencies. Generates blog posts, email campaigns, social media content, ad copy, landing pages, and case studies — all from a single dashboard.

---

## 🎯 What It Does

| Channel | Output | Volume |
|---|---|---|
| **Blog Posts** | SEO-optimized, 1500–2500 words, with H2s, FAQ, meta description | 8–12/month |
| **Email Campaigns** | Subject line + full body, welcome/nurture/promo sequences | Weekly |
| **Social Media** | LinkedIn, Twitter/X, Instagram, Facebook posts | Daily |
| **Ad Copy** | Google Ads, Meta Ads — headline + description variants | On demand |
| **Landing Pages** | Hero, features, CTA sections with conversion copy | On demand |
| **Case Studies** | Problem → Solution → Results format | On demand |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Next.js Dashboard                  │
│         (Content calendar, analytics, brands)        │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│  ┌─────────────────────────────────────────────┐    │
│  │           Agent Orchestrator                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │  Blog    │  │  Email   │  │  Social  │  │    │
│  │  │  Writer  │  │ Campaign │  │  Media   │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │    │
│  │  │  Ad Copy │  │ Landing  │  │  Case    │  │    │
│  │  │  Agent   │  │   Page   │  │  Study   │  │    │
│  │  └──────────┘  └──────────┘  └──────────┘  │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   PostgreSQL        Redis         OpenAI
   (content DB)    (cache)        GPT-4o
```

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone & Configure
```bash
git clone https://github.com/akulaautomated/content-agent.git
cd content-agent
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

### 2. Start Everything
```bash
docker compose up --build -d
```

### 3. Open the Dashboard
| URL | What |
|---|---|
| http://localhost:3000 | Dashboard |
| http://localhost:8000/docs | API Docs (Swagger) |

### 4. Create Your Account
Go to http://localhost:3000 → **Create Account** → fill in your details.

---

## ⚙️ Configuration (`.env`)

```env
LLM_PROVIDER=openai          # or "anthropic"
LLM_MODEL=gpt-4o             # or claude-sonnet-4-5 etc.
OPENAI_API_KEY=sk-...        # your key here
```

Switch to Anthropic Claude at any time — just change `LLM_PROVIDER=anthropic` and add your `ANTHROPIC_API_KEY`.

---

## 🤖 The 6 AI Agents

Each agent has a specialized system prompt tuned for its content type:

| Agent | Specialization |
|---|---|
| `blog_writer` | SEO, readability, internal linking, FAQ sections |
| `email_campaign` | Subject lines, open rates, nurture sequences |
| `social_media` | Platform-specific hooks, hashtags, engagement |
| `ad_copy` | AIDA framework, CTR optimization, A/B variants |
| `landing_page` | Conversion copy, hero/features/CTA structure |
| `case_study` | Problem-Solution-Results format, social proof |

All agents adapt to your **Brand Profile** (tone, vocabulary, style rules).

---

## 📊 Features

- ✅ **Multi-channel content generation** via GPT-4o or Claude
- ✅ **Brand voice profiles** — tone, preferred/banned vocabulary, style rules
- ✅ **Content calendar** — schedule posts by date and platform
- ✅ **SEO analysis** — readability score, keyword density, suggestions
- ✅ **Analytics dashboard** — impressions, clicks, engagement rate, CTR
- ✅ **Campaign management** — group content by marketing campaign
- ✅ **Content versioning** — full revision history
- ✅ **JWT authentication** — multi-user, multi-organization
- ✅ **Provider-agnostic** — swap OpenAI ↔ Anthropic in one env var

---

## 🛠️ Tech Stack

**Backend:** Python 3.11 · FastAPI · SQLAlchemy · PostgreSQL · Redis  
**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · Recharts · Zustand  
**AI:** OpenAI GPT-4o · Anthropic Claude (optional)  
**Infrastructure:** Docker · Nginx · Docker Compose

---

## 📁 Project Structure

```
content-agent/
├── backend/
│   └── app/
│       ├── agents/
│       │   ├── orchestrator.py     # Tool-use loop, agent routing
│       │   ├── provider.py         # OpenAI / Anthropic abstraction
│       │   ├── tools.py            # Agent tools (SEO, brand, save)
│       │   └── personas/           # 6 agent system prompts
│       ├── routes/                 # FastAPI endpoints
│       ├── models.py               # SQLAlchemy ORM
│       ├── schemas.py              # Pydantic request/response models
│       └── main.py                 # App entry point
├── frontend/
│   └── src/app/
│       ├── (dashboard)/            # Protected dashboard pages
│       └── login/                  # Auth pages
├── infrastructure/
│   ├── database/migrations/        # SQL schema
│   └── nginx/                      # Reverse proxy config
├── docker-compose.yml
└── .env.example
```

---

## 📄 License

MIT — free to use, modify, and deploy.

---

Built by [Akula Automated](https://github.com/akulaautomated)
