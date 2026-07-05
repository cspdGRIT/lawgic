from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    session_id: str
    case_id: Optional[int] = None
    language: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    role: str
    content: str
    agent_used: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence_score: float
    session_id: str
