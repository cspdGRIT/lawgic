from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.legal_aid import EligibilityRequest, EligibilityResponse
from app.services.nalsa import check_eligibility

router = APIRouter()


@router.post("/check-eligibility", response_model=EligibilityResponse)
async def eligibility_check(
    body: EligibilityRequest,
    _current_user: User = Depends(get_current_user),
):
    """Free — this routes people to a government program that's already free, so
    there's no reason to charge for the check itself. Deliberately stateless: no DB
    write, so none of these sensitive answers get persisted."""
    return check_eligibility(body)
