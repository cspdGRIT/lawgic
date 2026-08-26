"""Dual access model for the four paid actions (issue analysis, document unlock,
lawyer match, research search): subscription quota first, then pay-per-outcome
credits, in that order — so a paying subscriber never sees a credit paywall while
they still have quota, and someone without a subscription can still pay per use.
Applied per-endpoint (not router-wide) since only these four are paid; everything
else (browsing, chat, case creation, education) stays free."""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.credits import spend_credit
from app.core.database import get_db
from app.core.limits import Feature, try_consume_quota
from app.core.security import get_current_user
from app.models.user import User


async def try_pay(user: User, feature: Feature, db: AsyncSession) -> bool:
    """Non-raising core of the dual access model — admin/legacy bypass, then
    subscription quota, then credits. Used both by the hard-gate dependency below and
    by preview-then-pay endpoints (cases.py, documents.py) that need a bool, not an
    exception, since they still owe the caller a free teaser either way."""
    if user.user_type == "admin":
        return True
    if user.access_status == "approved":  # legacy blanket-approval bypass
        return True
    if await try_consume_quota(feature, user.id, db):
        return True
    return await spend_credit(user, feature, db)


def require_quota_or_credit(feature: Feature):
    """FastAPI dependency factory. Use as: Depends(require_quota_or_credit("documents"))"""

    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        if await try_pay(current_user, feature, db):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "payment_required",
                "feature": feature,
                "credit_balance": current_user.credit_balance,
                "message": "You're out of plan quota and credits for this. Subscribe for unlimited-ish access, "
                           "or buy a credit pack to keep going.",
                "options": ["subscribe", "buy_credits"],
            },
        )

    return _check


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


async def require_client(current_user: User = Depends(get_current_user)) -> User:
    """Rejects lawyer accounts before any payment dependency runs, so a lawyer hitting
    a client-only endpoint (issue triage, lawyer matching) never gets charged for the
    request that's about to be refused."""
    if current_user.user_type == "lawyer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This feature is for clients seeking representation.")
    return current_user
