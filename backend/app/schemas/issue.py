from typing import List, Optional
from pydantic import BaseModel


class IssueRequest(BaseModel):
    message: str
    city: Optional[str] = None  # helps narrow the court/forum and lawyer search


class LawyerMatch(BaseModel):
    id: int
    full_name: str
    city: str
    state: str
    specializations: List[str] = []
    rating: float
    hourly_rate: int
    consultation_fee: int
    languages: List[str] = []
    match_reason: Optional[str] = None


class IssueAnalysis(BaseModel):
    detected_language: str
    issue_type: str
    case_title: str
    plain_summary: str
    urgency: str
    limitation_warning: Optional[str] = None
    recommended_forum: str
    forum_reasoning: str
    petition_or_document: str
    document_template_id: Optional[str] = None
    relevant_statutes: List[str] = []
    documents_needed: List[str] = []
    estimated_court_fee: str
    estimated_lawyer_fee: str
    next_steps: List[str] = []
    disclaimer: str
    confidence_score: float
    matched_lawyers: List[LawyerMatch] = []
    saved_case_id: Optional[int] = None
