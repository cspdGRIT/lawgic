"""
Plan limit enforcement.

Usage in route handlers:
    from app.core.limits import require_feature
    ...
    _: None = Depends(require_feature("ai_queries")),
"""
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.subscription import PLAN_LIMITS, Subscription
from app.models.usage import MonthlyUsage
from app.models.user import User

Feature = Literal["ai_queries", "cases", "documents", "research"]


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def _get_plan(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()
    if not sub:
        return "free"
    if sub.status == "cancelled" and sub.current_period_end and sub.current_period_end < datetime.now(timezone.utc):
        return "free"
    return sub.plan


async def _get_or_create_usage(user_id: int, month: str, db: AsyncSession) -> MonthlyUsage:
    result = await db.execute(
        select(MonthlyUsage).where(
            MonthlyUsage.user_id == user_id,
            MonthlyUsage.month == month,
        )
    )
    usage = result.scalar_one_or_none()
    if not usage:
        usage = MonthlyUsage(user_id=user_id, month=month)
        db.add(usage)
        await db.flush()
        await db.refresh(usage)
    return usage


async def check_and_increment(feature: Feature, user_id: int, db: AsyncSession) -> None:
    plan = await _get_plan(user_id, db)
    limits = PLAN_LIMITS[plan]
    limit = limits.get(feature, 0)

    if limit == -1:  # unlimited
        return

    month = _current_month()
    usage = await _get_or_create_usage(user_id, month, db)
    current = getattr(usage, feature)

    if current >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "plan_limit_exceeded",
                "feature": feature,
                "limit": limit,
                "used": current,
                "plan": plan,
                "upgrade_url": "/pricing",
                "message": f"You've reached your {plan.upper()} plan limit of {limit} {feature.replace('_', ' ')} this month. Upgrade to continue.",
            },
        )

    setattr(usage, feature, current + 1)
    await db.flush()


def require_feature(feature: Feature):
    """FastAPI dependency factory. Use as: Depends(require_feature('ai_queries'))"""
    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        await check_and_increment(feature, current_user.id, db)

    return _check
