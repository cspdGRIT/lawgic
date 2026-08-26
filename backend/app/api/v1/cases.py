import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.access import try_pay
from app.core.database import get_db
from app.core.limits import require_feature
from app.core.security import get_current_user
from app.models.user import User
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.agents.case_agent import case_analysis_node
from app.agents.state import AgentState

router = APIRouter()

# Free forever, regardless of payment — enough to prove the analysis is real and worth
# unlocking. Everything else in the analysis dict (statutes, strategy, next steps,
# risk factors, similar cases, duration/cost estimates) is the paid part.
TEASER_FIELDS = {"win_probability", "summary"}


def _serialize_case(case: Case) -> CaseResponse:
    """Same reasoning as documents.py's _serialize: never let response_model validate
    the tracked ORM instance directly if we're about to strip fields from it."""
    analysis = None
    if case.ai_analysis:
        try:
            full = json.loads(case.ai_analysis)
        except (json.JSONDecodeError, ValueError):
            full = None
        if full is not None:
            analysis = full if case.analysis_unlocked else {k: v for k, v in full.items() if k in TEASER_FIELDS}
    return CaseResponse(
        id=case.id, user_id=case.user_id, title=case.title, description=case.description,
        case_type=case.case_type, jurisdiction=case.jurisdiction, court_level=case.court_level,
        status=case.status, opposing_party=case.opposing_party, key_facts=case.key_facts,
        ai_analysis=analysis, analysis_unlocked=case.analysis_unlocked,
        confidence_score=case.confidence_score, assigned_lawyer_id=case.assigned_lawyer_id,
        created_at=case.created_at, updated_at=case.updated_at,
    )


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
    return [_serialize_case(c) for c in result.scalars().all()]


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
    return _serialize_case(case)


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
    return _serialize_case(case)


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
    return _serialize_case(case)


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
):
    """Preview-then-pay: the AI always runs and the full result is stored either way —
    the win-probability + summary teaser is free forever; the rest streams back (and
    persists as visible on refetch) only if quota/credits cover it. Not a hard Depends
    gate because we still owe the caller a teaser even when payment fails."""
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
            full_analysis = final_state.get("case_context", {}).get("ai_analysis", {})

            unlocked = await try_pay(current_user, "ai_queries", db)

            # Store the full analysis regardless — a later unlock (subscribe/buy
            # credits) reveals what's already there rather than re-running the AI.
            if full_analysis:
                case.ai_analysis = json.dumps(full_analysis)
                case.confidence_score = final_state.get("confidence_score", 0.0)
                case.status = "in_progress"
                case.analysis_unlocked = case.analysis_unlocked or unlocked
                await db.flush()

            visible = full_analysis if unlocked else {k: v for k, v in full_analysis.items() if k in TEASER_FIELDS}

            # Stream only what they're actually allowed to see.
            response_text = final_state.get("final_response", "Analysis complete") if unlocked else visible.get(
                "summary", "Analysis ready — unlock to see the full breakdown."
            )
            words = response_text.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'analysis': visible, 'unlocked': unlocked, 'confidence_score': final_state.get('confidence_score', 0.7)})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/{case_id}/unlock", response_model=CaseResponse)
async def unlock_case_analysis(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retries payment for an already-computed analysis (e.g. the user just bought
    credits after seeing the teaser) without re-running the AI."""
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.user_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if not case.ai_analysis:
        raise HTTPException(status_code=400, detail="Run analysis first.")
    if not case.analysis_unlocked:
        if not await try_pay(current_user, "ai_queries", db):
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "payment_required", "feature": "ai_queries",
                    "credit_balance": current_user.credit_balance,
                    "message": "You're out of plan quota and credits for this.",
                    "options": ["subscribe", "buy_credits"],
                },
            )
        case.analysis_unlocked = True
        await db.flush()
        await db.refresh(case)
    return _serialize_case(case)
