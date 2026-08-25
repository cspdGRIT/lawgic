"""Access-approval gate: every resource router except auth (and this module's own
endpoints) requires access_status == "approved", enforced via a shared dependency
passed to include_router(..., dependencies=[...]) in main.py — not sprinkled through
every route function, so nothing can accidentally be left ungated."""

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User


async def require_approved_access(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type == "admin":
        return current_user
    if current_user.access_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "access_pending",
                "access_status": current_user.access_status,
                "message": "Your account needs approval before you can use this. Submit a payment for review.",
            },
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
