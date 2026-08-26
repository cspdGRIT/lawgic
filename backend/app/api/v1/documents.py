import json
import re
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.access import require_quota_or_credit
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse
from app.agents.document_agent import document_generation_node, get_all_templates, get_template
from app.agents.state import AgentState

router = APIRouter()


class GenerateDocumentRequest(BaseModel):
    template_id: str
    form_data: dict
    case_id: Optional[int] = None
    language: Optional[str] = "English"


PREVIEW_MIN_WORDS = 120
PREVIEW_FRACTION = 0.35  # generation is free — this much of the real draft is visible with no payment


def _preview_words(full_text: str) -> str:
    words = full_text.split()
    if len(words) <= 8:
        # Too short to redact meaningfully either way.
        return full_text
    cutoff = max(PREVIEW_MIN_WORDS, int(len(words) * PREVIEW_FRACTION))
    # Always withhold a real tail — never let the "preview" equal the full document
    # (previously short templates fell under PREVIEW_MIN_WORDS and were returned in
    # full while still showing an "Unlock" button).
    cutoff = min(cutoff, len(words) - max(3, int(len(words) * 0.1)))

    # Walk the raw text (not full_text.split()/" ".join()) so line breaks, numbered
    # clauses, and signature-block indentation survive into the preview instead of
    # being flattened into one paragraph.
    count = 0
    cut_index = len(full_text)
    for m in re.finditer(r"\S+", full_text):
        count += 1
        if count == cutoff:
            cut_index = m.end()
            break
    return full_text[:cut_index] + "\n\n[...] Unlock the full document to see the rest and download it."


def _serialize(doc: Document) -> DocumentResponse:
    """Never return the ORM instance directly through response_model — mutating
    `doc.content` in place would mark it dirty and the session would persist the
    redacted preview over the real draft on commit. Build a detached copy instead."""
    content = doc.content if doc.unlocked else _preview_words(doc.content)
    return DocumentResponse(
        id=doc.id, user_id=doc.user_id, case_id=doc.case_id, title=doc.title,
        document_type=doc.document_type, template_id=doc.template_id, content=content,
        language=doc.language, status=doc.status, is_ai_generated=doc.is_ai_generated,
        unlocked=doc.unlocked, created_at=doc.created_at, updated_at=doc.updated_at,
    )


@router.get("/templates")
async def list_templates():
    return get_all_templates()


@router.get("/templates/{template_id}")
async def get_template_detail(template_id: str):
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    )
    return [_serialize(d) for d in result.scalars().all()]


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # This path is for a user's own authored/pasted content, not the paid AI-generate
    # flow below — nothing to unlock, it's already theirs.
    doc = Document(user_id=current_user.id, unlocked=True, **data.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return _serialize(doc)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize(doc)


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)


@router.post("/{doc_id}/unlock", response_model=DocumentResponse)
async def unlock_document(
    doc_id: int,
    current_user: User = Depends(require_quota_or_credit("documents")),
    db: AsyncSession = Depends(get_db),
):
    """Spends one 'documents' quota unit / credit to reveal the full draft and enable
    download — this is the actual point of payment now, not generation."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == current_user.id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.unlocked = True
    await db.flush()
    await db.refresh(doc)
    return _serialize(doc)


@router.post("/generate")
async def generate_document(
    request: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generation itself is free — see the module docstring in core/access.py for why:
    this is the 'let them feel the value first' half of preview-then-pay. Only a
    truncated preview streams back; POST /{doc_id}/unlock is the paid action."""
    template = get_template(request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{request.template_id}' not found")

    async def event_stream():
        try:
            start_msg = json.dumps({'type': 'start', 'content': f'Generating {template["name"]}...'})
            yield f"data: {start_msg}\n\n"

            initial_state: AgentState = {
                "messages": [],
                "user_query": f"Generate a {template['name']}",
                "intent": "document_generation",
                "case_context": {
                    "template_id": request.template_id,
                    "form_data": request.form_data,
                },
                "research_results": [],
                "generated_document": None,
                "lawyer_matches": [],
                "final_response": "",
                "confidence_score": 0.0,
                "agent_logs": [],
                "language_target": None,
            }

            final_state = await document_generation_node(initial_state, db=db)
            document_text = final_state.get("generated_document")

            if not document_text:
                # Generation failed — final_response holds the error string in that
                # case. Don't persist it as a Document or let a user pay a credit to
                # "unlock" an error message.
                error_msg = final_state.get("final_response") or "Could not generate the document. Please try again."
                yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
                return

            # Save the FULL text — unlock later reveals it, doesn't regenerate it.
            doc = Document(
                user_id=current_user.id,
                case_id=request.case_id,
                title=f"{template['name']} - {request.form_data.get('sender_name') or request.form_data.get('complainant_name') or request.form_data.get('petitioner_name') or 'Draft'}",
                document_type=template["name"],
                template_id=request.template_id,
                content=document_text,
                language=request.language or "English",
                is_ai_generated=True,
                unlocked=False,
            )
            db.add(doc)
            await db.flush()
            await db.refresh(doc)

            # Stream only the free preview portion — the rest is genuinely withheld
            # server-side, not just hidden in the UI.
            preview_text = _preview_words(document_text)
            words = preview_text.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'document_id': doc.id, 'title': doc.title, 'unlocked': False})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
