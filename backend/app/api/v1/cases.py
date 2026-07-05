import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.limits import require_feature
from app.core.security import get_current_user
from app.models.user import User
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.agents.case_agent import case_analysis_node
from app.agents.state import AgentState

router = APIRouter()


@router.get("/", response_model=list[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Case).where(Case.user_id == current_user.id)
    if status:
        query = query.where(Case.status == status)
    query = query.order_by(Case.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_case(
    data: CaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _limit: None = Depends(require_feature("cases")),
):
    case = Case(user_id=current_user.id, **data.model_dump())
    db.add(case)
    await db.flush()
    await db.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.user_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    data: CaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.user_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(case, field, value)

    await db.flush()
    await db.refresh(case)
    return case


@router.delete("/{case_id}", status_code=204)
async def delete_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.user_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    await db.delete(case)


@router.post("/{case_id}/analyze")
async def analyze_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _limit: None = Depends(require_feature("ai_queries")),
):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.user_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_context = {
        "title": case.title,
        "case_type": case.case_type,
        "description": case.description,
        "jurisdiction": case.jurisdiction,
        "court_level": case.court_level,
        "opposing_party": case.opposing_party,
        "key_facts": case.key_facts,
    }

    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'start', 'content': 'Starting AI analysis...'})}\n\n"

            initial_state: AgentState = {
                "messages": [],
                "user_query": f"Analyze this case: {case.description}",
                "intent": "case_analysis",
                "case_context": case_context,
                "research_results": [],
                "generated_document": None,
                "lawyer_matches": [],
                "final_response": "",
                "confidence_score": 0.0,
                "agent_logs": [],
                "language_target": None,
            }

            final_state = await case_analysis_node(initial_state, db=db)

            # Save analysis to DB
            if final_state.get("case_context", {}).get("ai_analysis"):
                case.ai_analysis = json.dumps(final_state["case_context"]["ai_analysis"])
                case.confidence_score = final_state.get("confidence_score", 0.0)
                case.status = "in_progress"
                await db.flush()

            # Stream the response tokens
            response_text = final_state.get("final_response", "Analysis complete")
            words = response_text.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            analysis = final_state.get("case_context", {}).get("ai_analysis", {})
            yield f"data: {json.dumps({'type': 'done', 'analysis': analysis, 'confidence_score': final_state.get('confidence_score', 0.7)})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
