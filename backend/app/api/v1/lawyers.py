import json
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lawyer import Lawyer
from app.schemas.lawyer import LawyerResponse
from app.agents.lawyer_agent import lawyer_matching_node
from app.agents.state import AgentState

router = APIRouter()


class MatchRequest(BaseModel):
    case_description: str
    case_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    budget_per_hour: Optional[int] = None
    preferred_language: Optional[str] = "English"


def parse_lawyer(lawyer: Lawyer) -> dict:
    return {
        "id": lawyer.id,
        "full_name": lawyer.full_name,
        "bar_council_number": lawyer.bar_council_number,
        "specializations": json.loads(lawyer.specializations) if lawyer.specializations else [],
        "practice_areas": json.loads(lawyer.practice_areas) if lawyer.practice_areas else [],
        "city": lawyer.city,
        "state": lawyer.state,
        "years_experience": lawyer.years_experience,
        "hourly_rate": lawyer.hourly_rate,
        "consultation_fee": lawyer.consultation_fee,
        "rating": lawyer.rating,
        "review_count": lawyer.review_count,
        "languages": json.loads(lawyer.languages) if lawyer.languages else [],
        "bio": lawyer.bio,
        "court_levels": json.loads(lawyer.court_levels) if lawyer.court_levels else [],
        "available": lawyer.available,
        "verified": lawyer.verified,
    }


@router.get("/")
async def list_lawyers(
    city: Optional[str] = None,
    practice_area: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_hourly_rate: Optional[int] = None,
    language: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Lawyer).where(Lawyer.available == True)

    if city:
        query = query.where(Lawyer.city.ilike(f"%{city}%"))
    if min_rating:
        query = query.where(Lawyer.rating >= min_rating)
    if max_hourly_rate:
        query = query.where(Lawyer.hourly_rate <= max_hourly_rate)

    query = query.order_by(Lawyer.rating.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    lawyers = result.scalars().all()

    parsed = [parse_lawyer(l) for l in lawyers]

    if practice_area:
        parsed = [l for l in parsed if any(practice_area.lower() in a.lower() for a in l["practice_areas"])]
    if language:
        parsed = [l for l in parsed if any(language.lower() in lang.lower() for lang in l["languages"])]

    return parsed


@router.get("/{lawyer_id}")
async def get_lawyer(
    lawyer_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Lawyer).where(Lawyer.id == lawyer_id))
    lawyer = result.scalar_one_or_none()
    if not lawyer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return parse_lawyer(lawyer)


@router.post("/match")
async def match_lawyers(
    request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    initial_state: AgentState = {
        "messages": [],
        "user_query": request.case_description,
        "intent": "lawyer_matching",
        "case_context": {
            "case_type": request.case_type,
            "jurisdiction": request.jurisdiction,
            "budget_per_hour": request.budget_per_hour,
            "preferred_language": request.preferred_language,
        },
        "research_results": [],
        "generated_document": None,
        "lawyer_matches": [],
        "final_response": "",
        "confidence_score": 0.0,
        "agent_logs": [],
        "language_target": None,
    }

    final_state = await lawyer_matching_node(initial_state, db=db)
    return {
        "matches": final_state.get("lawyer_matches", []),
        "summary": final_state.get("final_response", ""),
    }
