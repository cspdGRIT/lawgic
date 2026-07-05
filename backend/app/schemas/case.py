import json
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator


class CaseCreate(BaseModel):
    title: str
    description: str
    case_type: str
    jurisdiction: str
    court_level: str
    opposing_party: Optional[str] = None
    key_facts: Optional[str] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    case_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    court_level: Optional[str] = None
    status: Optional[str] = None
    opposing_party: Optional[str] = None
    key_facts: Optional[str] = None
    assigned_lawyer_id: Optional[int] = None


class CaseResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    case_type: str
    jurisdiction: str
    court_level: str
    status: str
    opposing_party: Optional[str] = None
    key_facts: Optional[str] = None
    ai_analysis: Optional[Any] = None
    confidence_score: Optional[float] = None
    assigned_lawyer_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("ai_analysis", mode="before")
    @classmethod
    def parse_json(cls, v):
        if isinstance(v, str) and v:
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                return None
        return v
