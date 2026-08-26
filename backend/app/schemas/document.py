from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    title: str
    document_type: str
    content: str
    case_id: Optional[int] = None
    language: str = "English"
    template_id: Optional[str] = None
    is_ai_generated: bool = False


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    case_id: Optional[int] = None
    title: str
    document_type: str
    template_id: Optional[str] = None
    content: str
    language: str
    status: str
    is_ai_generated: bool
    unlocked: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateInfo(BaseModel):
    id: str
    name: str
    category: str
    description: str
    fields: List[str]
    applicable_law: str


class GenerateDocumentRequest(BaseModel):
    template_id: str
    form_data: Dict[str, Any]
    case_id: Optional[int] = None
    language: str = "English"
    save: bool = True
