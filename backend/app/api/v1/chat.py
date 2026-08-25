import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limits import check_and_increment, require_feature
from app.core.security import get_current_user, get_current_user_from_token
from app.models.user import User
from app.models.message import Message
from app.agents.graph import app_graph
from app.agents.state import AgentState

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    user = None
    try:
        user = await get_current_user_from_token(token, db)
    except Exception:
        await websocket.close(code=4001)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            # Check plan limit before each message
            try:
                await check_and_increment("ai_queries", user.id, db)
            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "content": str(e.detail if hasattr(e, 'detail') else e)}))
                continue
            try:
                payload = json.loads(data)
                user_message = payload.get("message", "")
            except json.JSONDecodeError:
                user_message = data

            if not user_message.strip():
                continue

            # Save user message
            msg = Message(
                user_id=user.id,
                session_id=session_id,
                role="user",
                content=user_message,
            )
            db.add(msg)
            await db.flush()

            # Send typing indicator
            await websocket.send_text(json.dumps({"type": "typing", "content": ""}))

            # Run through LangGraph
            initial_state: AgentState = {
                "messages": [],
                "user_query": user_message,
                "intent": "general",
                "case_context": None,
                "research_results": [],
                "generated_document": None,
                "lawyer_matches": [],
                "final_response": "",
                "confidence_score": 0.0,
                "agent_logs": [],
                "language_target": None,
            }

            try:
                final_state = await app_graph.ainvoke(initial_state)
                response_text = final_state.get("final_response", "I'm here to help with your legal questions.")
                confidence = final_state.get("confidence_score", 0.8)
                agent_logs = final_state.get("agent_logs", [])
                intent = final_state.get("intent", "general")

                # Determine agent name from intent
                agent_names = {
                    "case_analysis": "Case Analysis Agent",
                    "document_generation": "Document Drafting Agent",
                    "legal_research": "Legal Research Agent",
                    "translation": "Translation Agent",
                    "lawyer_matching": "Lawyer Matching Agent",
                    "general": "Lawgic AI",
                }
                agent_name = agent_names.get(intent, "Lawgic AI")

                # Stream response tokens
                words = response_text.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    await websocket.send_text(json.dumps({"type": "token", "content": chunk}))

                # Send done signal
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "agent": agent_name,
                    "confidence_score": confidence,
                    "agent_logs": agent_logs,
                }))

                # Save assistant message
                assistant_msg = Message(
                    user_id=user.id,
                    session_id=session_id,
                    role="assistant",
                    content=response_text,
                    agent_used=agent_name,
                    confidence_score=confidence,
                )
                db.add(assistant_msg)
                await db.flush()

            except Exception as e:
                await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))

    except WebSocketDisconnect:
        pass


@router.post("/message")
async def chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _limit: None = Depends(require_feature("ai_queries")),
):
    """Non-streaming REST endpoint for chat."""
    session_id = request.session_id or str(uuid.uuid4())

    initial_state: AgentState = {
        "messages": [],
        "user_query": request.message,
        "intent": "general",
        "case_context": None,
        "research_results": [],
        "generated_document": None,
        "lawyer_matches": [],
        "final_response": "",
        "confidence_score": 0.0,
        "agent_logs": [],
        "language_target": None,
    }

    final_state = await app_graph.ainvoke(initial_state)
    response_text = final_state.get("final_response", "I'm here to help with your legal questions.")

    # Save messages
    user_msg = Message(user_id=current_user.id, session_id=session_id, role="user", content=request.message)
    db.add(user_msg)

    agent_names = {
        "case_analysis": "Case Analysis Agent",
        "document_generation": "Document Drafting Agent",
        "legal_research": "Legal Research Agent",
        "translation": "Translation Agent",
        "lawyer_matching": "Lawyer Matching Agent",
        "general": "Lawgic AI",
    }
    agent_name = agent_names.get(final_state.get("intent", "general"), "Lawgic AI")

    assistant_msg = Message(
        user_id=current_user.id,
        session_id=session_id,
        role="assistant",
        content=response_text,
        agent_used=agent_name,
        confidence_score=final_state.get("confidence_score", 0.8),
    )
    db.add(assistant_msg)
    await db.flush()

    return {
        "response": response_text,
        "session_id": session_id,
        "agent": agent_name,
        "confidence_score": final_state.get("confidence_score", 0.8),
    }


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Message)
        .where(Message.user_id == current_user.id, Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "agent_used": m.agent_used,
            "confidence_score": m.confidence_score,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
