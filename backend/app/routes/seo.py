from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import textstat

from app.database import get_db
from app.models import SEOKeyword, User
from app.schemas import SEOKeywordCreate, SEOKeywordOut, SEOAnalysisResult
from app.auth import get_current_user

router = APIRouter()


@router.get("/keywords", response_model=List[SEOKeywordOut])
async def list_keywords(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SEOKeyword).where(SEOKeyword.org_id == current_user.org_id)
    )
    return result.scalars().all()


@router.post("/keywords", response_model=SEOKeywordOut, status_code=201)
async def add_keyword(
    body: SEOKeywordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kw = SEOKeyword(org_id=current_user.org_id, **body.model_dump())
    db.add(kw)
    await db.flush()
    return kw


@router.post("/analyze")
async def analyze_content(
    payload: dict,
    current_user: User = Depends(get_current_user),
) -> SEOAnalysisResult:
    """
    Analyze text for SEO quality.
    Send: { "text": "...", "keywords": ["keyword1", "keyword2"] }
    """
    text: str = payload.get("text", "")
    keywords: List[str] = payload.get("keywords", [])

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    # Flesch Reading Ease: 0-100. Higher = easier to read.
    reading_ease_score = textstat.flesch_reading_ease(text)
    if reading_ease_score >= 70:
        reading_ease = "Easy"
    elif reading_ease_score >= 50:
        reading_ease = "Moderate"
    else:
        reading_ease = "Difficult"

    word_count = len(text.split())
    sentences = textstat.sentence_count(text)
    avg_sentence_length = word_count / max(sentences, 1)

    # Calculate how often each keyword appears (as % of total words)
    text_lower = text.lower()
    keyword_density = {}
    for kw in keywords:
        count = text_lower.count(kw.lower())
        keyword_density[kw] = round((count / max(word_count, 1)) * 100, 2)

    # Generate suggestions
    suggestions = []
    if reading_ease_score < 50:
        suggestions.append("Consider shorter sentences to improve readability")
    if avg_sentence_length > 25:
        suggestions.append(f"Average sentence length is {avg_sentence_length:.0f} words — aim for under 20")
    if word_count < 300:
        suggestions.append("Content is very short — consider expanding for better SEO coverage")
    for kw, density in keyword_density.items():
        if density < 0.5:
            suggestions.append(f'Keyword "{kw}" appears rarely — consider using it more naturally')
        elif density > 3:
            suggestions.append(f'Keyword "{kw}" may be overused ({density}%) — risk of keyword stuffing')

    return SEOAnalysisResult(
        readability_score=round(reading_ease_score, 1),
        reading_ease=reading_ease,
        word_count=word_count,
        sentence_count=sentences,
        avg_sentence_length=round(avg_sentence_length, 1),
        keyword_density=keyword_density,
        suggestions=suggestions,
    )
