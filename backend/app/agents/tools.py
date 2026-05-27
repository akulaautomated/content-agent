"""
Tool definitions for agent use.
Tools are functions the AI can call during generation to look things up or save results.
"""
import json
import httpx
import textstat
from typing import Any

# Tools available to all agents
TOOL_DEFINITIONS = [
    {
        "name": "get_brand_profile",
        "description": "Retrieve the brand voice profile for content generation. Returns tone, vocabulary preferences, style rules, and target audience.",
        "input_schema": {
            "type": "object",
            "properties": {
                "brand_id": {
                    "type": "string",
                    "description": "The UUID of the brand profile to retrieve",
                }
            },
            "required": ["brand_id"],
        },
    },
    {
        "name": "analyze_seo",
        "description": "Analyze text for SEO quality: readability score, keyword density, word count, and improvement suggestions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The content to analyze"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to check density for",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "save_draft",
        "description": "Save the generated content as a draft in the database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string", "description": "The main content body"},
                "meta_description": {"type": "string"},
                "excerpt": {"type": "string"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "seo_data": {"type": "object"},
                "word_count": {"type": "integer"},
            },
            "required": ["body"],
        },
    },
    {
        "name": "get_keyword_suggestions",
        "description": "Get keyword suggestions and SEO strategy for a given topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The content topic"},
                "industry": {"type": "string", "description": "The industry or niche"},
            },
            "required": ["topic"],
        },
    },
]


async def execute_tool(
    tool_name: str,
    arguments: dict,
    context: dict,
) -> Any:
    """
    Execute a tool call and return the result.
    context contains: org_id, brand_id, api_base_url, db_session (optional)
    """
    if tool_name == "get_brand_profile":
        return await _get_brand_profile(arguments.get("brand_id"), context)

    elif tool_name == "analyze_seo":
        return _analyze_seo(arguments.get("text", ""), arguments.get("keywords", []))

    elif tool_name == "save_draft":
        # Store result in context so the orchestrator can save it after the loop
        context["draft_result"] = arguments
        return {"status": "saved", "message": "Draft captured, will be persisted after generation"}

    elif tool_name == "get_keyword_suggestions":
        return _get_keyword_suggestions(arguments.get("topic", ""), arguments.get("industry", ""))

    return {"error": f"Unknown tool: {tool_name}"}


async def _get_brand_profile(brand_id: str | None, context: dict) -> dict:
    """Fetch brand profile from the API."""
    if not brand_id:
        return {"message": "No brand_id provided — using default tone (conversational)"}

    api_url = context.get("api_base_url", "http://localhost:8000")
    token = context.get("auth_token", "")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{api_url}/api/brands/{brand_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json()
            return {"message": "Brand profile not found — using defaults"}
    except Exception as e:
        return {"message": f"Could not fetch brand profile: {str(e)} — using defaults"}


def _analyze_seo(text: str, keywords: list) -> dict:
    """Run SEO analysis on text."""
    if not text:
        return {"error": "No text provided"}

    reading_ease = textstat.flesch_reading_ease(text)
    word_count = len(text.split())
    sentence_count = textstat.sentence_count(text)

    text_lower = text.lower()
    keyword_density = {}
    for kw in keywords:
        count = text_lower.count(kw.lower())
        keyword_density[kw] = round((count / max(word_count, 1)) * 100, 2)

    suggestions = []
    if reading_ease < 50:
        suggestions.append("Simplify sentences for better readability")
    if word_count < 1000:
        suggestions.append("Consider expanding content (aim for 1500+ words for blog posts)")
    for kw, density in keyword_density.items():
        if density < 0.5:
            suggestions.append(f'Include "{kw}" more naturally in the content')
        elif density > 3:
            suggestions.append(f'Reduce usage of "{kw}" to avoid over-optimization')

    return {
        "readability_score": round(reading_ease, 1),
        "reading_ease": "Easy" if reading_ease >= 70 else ("Moderate" if reading_ease >= 50 else "Difficult"),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "keyword_density": keyword_density,
        "suggestions": suggestions,
    }


def _get_keyword_suggestions(topic: str, industry: str) -> dict:
    """Generate keyword strategy suggestions (heuristic, no external API needed)."""
    return {
        "primary_keyword": f"{topic.lower()}",
        "suggested_long_tail": [
            f"how to {topic.lower()}",
            f"best {topic.lower()} strategies",
            f"{topic.lower()} for {industry.lower() or 'businesses'}" if industry else f"{topic.lower()} guide",
            f"{topic.lower()} tips",
            f"what is {topic.lower()}",
        ],
        "lsi_keywords": [
            f"{topic.lower()} strategy",
            f"{topic.lower()} best practices",
            f"{topic.lower()} examples",
            f"{topic.lower()} tools",
        ],
        "search_intents": {
            "informational": f"what is {topic.lower()}, how does {topic.lower()} work",
            "commercial": f"best {topic.lower()} services, {topic.lower()} pricing",
            "transactional": f"hire {topic.lower()} expert, {topic.lower()} agency",
        },
        "note": "These are starting suggestions. Validate with Google Search Console or SEMrush.",
    }
