import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.access import require_approved_access
from app.core.database import get_db
from app.core.limits import require_feature
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
    return result.scalars().all()


@router.post("/", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = Document(user_id=current_user.id, **data.model_dump())
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


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
    return doc


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


@router.post("/generate")
async def generate_document(
    request: GenerateDocumentRequest,
    current_user: User = Depends(require_approved_access),
    db: AsyncSession = Depends(get_db),
    _limit: None = Depends(require_feature("documents")),
):
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
            document_text = final_state.get("generated_document") or final_state.get("final_response", "")

            # Save to DB
            doc = Document(
                user_id=current_user.id,
                case_id=request.case_id,
                title=f"{template['name']} - {request.form_data.get('sender_name') or request.form_data.get('complainant_name') or request.form_data.get('petitioner_name') or 'Draft'}",
                document_type=template["name"],
                template_id=request.template_id,
                content=document_text,
                language=request.language or "English",
                is_ai_generated=True,
            )
            db.add(doc)
            await db.flush()
            await db.refresh(doc)

            # Stream document text
            words = document_text.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'document_id': doc.id, 'title': doc.title})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
