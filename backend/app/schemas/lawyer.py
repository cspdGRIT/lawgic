import json
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator


class LawyerResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    full_name: str
    bar_council_number: str
    specializations: List[str]
    practice_areas: List[str]
    city: str
    state: str
    years_experience: int
    hourly_rate: int
    consultation_fee: int
    rating: float
    review_count: int
    languages: List[str]
    bio: str
    court_levels: List[str]
    available: bool
    verified: bool
    profile_image_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("specializations", "practice_areas", "languages", "court_levels", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [v]
            except (json.JSONDecodeError, ValueError):
                return [v] if v else []
        return v if v is not None else []


class LawyerMatchRequest(BaseModel):
    case_description: str
    case_type: str
    jurisdiction: str
    budget_per_hour: Optional[int] = None  # max INR
    preferred_language: Optional[str] = None


class LawyerMatchResult(BaseModel):
    lawyer: LawyerResponse
    match_score: float
    match_reason: str
