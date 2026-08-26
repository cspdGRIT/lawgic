from typing import Literal, Optional
from pydantic import BaseModel


class EligibilityRequest(BaseModel):
    is_woman: bool = False
    is_child: bool = False
    is_sc_st: bool = False
    is_victim_of_trafficking_or_begar: bool = False
    is_disabled: bool = False
    is_victim_of_mass_disaster: bool = False
    is_industrial_workman: bool = False
    is_in_custody: bool = False
    annual_income_rupees: Optional[int] = None
    forum: Literal["supreme_court", "high_court_or_below"] = "high_court_or_below"


class EligibilityResponse(BaseModel):
    eligible: bool
    matched_criteria: list[str]
    guidance: str
    helpline: str
    website: str
