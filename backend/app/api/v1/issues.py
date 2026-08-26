import json
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.issue_navigator import navigate_issue
from app.core.access import require_client, require_quota_or_credit
from app.core.database import get_db
from app.models.case import Case
from app.models.user import User
from app.schemas.issue import IssueRequest

router = APIRouter()


@router.post("/analyze")
async def analyze_issue(
    body: IssueRequest,
    _client: User = Depends(require_client),
    current_user: User = Depends(require_quota_or_credit("ai_queries")),
    db: AsyncSession = Depends(get_db),
):
    """Describe-your-issue -> one AI triage call (+ reused lawyer matching), streamed as SSE
    so the UI can show progress, then a single structured 'done' payload the frontend renders
    as an action-plan card. Also saved as a Case so it shows up in the user's case history —
    without spending a separate 'cases' quota, since it's one action from the user's point of view."""

    async def event_stream():
        try:
            yield f"data: {json.dumps({'type': 'start', 'content': 'Reading your description...'})}\n\n"

            analysis = await navigate_issue(body.message, body.city, db=db)

            deadline = analysis.get("deadline_date")
            case = Case(
                user_id=current_user.id,
                title=analysis.get("case_title", "Untitled matter")[:500],
                description=body.message,
                case_type=analysis.get("issue_type", "Other"),
                jurisdiction=body.city or "India",
                court_level=analysis.get("recommended_forum", "Not specified")[:50],
                status="open",
                ai_analysis=json.dumps(analysis),
                confidence_score=analysis.get("confidence_score", 0.6),
                analysis_unlocked=True,  # already paid for by the require_quota_or_credit gate above
                deadline_date=date.fromisoformat(deadline) if deadline else None,
            )
            db.add(case)
            await db.flush()
            await db.refresh(case)
            analysis["saved_case_id"] = case.id

            yield f"data: {json.dumps({'type': 'token', 'content': analysis.get('plain_summary', '')})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'analysis': analysis})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
