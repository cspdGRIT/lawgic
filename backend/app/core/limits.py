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
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.subscription import PLAN_LIMITS, Subscription
from app.models.usage import MonthlyUsage
from app.models.user import User

Feature = Literal["ai_queries", "cases", "documents", "research", "lawyer_matches"]


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def sync_expired_subscription(sub: Subscription, db: AsyncSession) -> Subscription:
    """No recurring billing/webhook is wired yet (see payments.py — Razorpay orders
    are one-shot, current_period_end is just set to now+30d on verify) — so a
    subscription whose paid period has lapsed without a renewal has to be downgraded
    here rather than kept 'active'/paid-plan forever. Covers both an explicitly
    cancelled plan past its paid-through date and one that was simply never renewed."""
    if sub.current_period_end and sub.current_period_end < datetime.now(timezone.utc) and sub.status != "expired":
        sub.status = "expired"
        sub.plan = "free"
        await db.flush()
    return sub


async def _get_plan(user_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalar_one_or_none()
    if not sub:
        return "free"
    sub = await sync_expired_subscription(sub, db)
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


async def try_consume_quota(feature: Feature, user_id: int, db: AsyncSession) -> bool:
    """Non-raising version — consumes one unit of subscription quota and returns True,
    or returns False (without consuming anything) if the plan has none left. Used by
    require_quota_or_credit to fall through to credits instead of hard-failing."""
    plan = await _get_plan(user_id, db)
    limits = PLAN_LIMITS[plan]
    limit = limits.get(feature, 0)

    if limit == -1:  # unlimited
        return True

    month = _current_month()
    usage = await _get_or_create_usage(user_id, month, db)
    col = getattr(MonthlyUsage, feature)

    # Conditional UPDATE, not read-check-then-write — two concurrent requests (double
    # click, two tabs) both reading `current < limit` before either writes would
    # otherwise both pass the check and overshoot the plan's monthly quota.
    result = await db.execute(
        update(MonthlyUsage)
        .where(MonthlyUsage.id == usage.id, col < limit)
        .values({feature: col + 1})
        .returning(col)
    )
    row = result.first()
    if row is None:
        return False
    setattr(usage, feature, row[0])
    await db.flush()
    return True


async def check_and_increment(feature: Feature, user_id: int, db: AsyncSession) -> None:
    """Raising version — for endpoints with no credit fallback (kept for anything that
    should hard-stop at the plan limit rather than offer a pay-per-use alternative)."""
    plan = await _get_plan(user_id, db)
    limits = PLAN_LIMITS[plan]
    limit = limits.get(feature, 0)

    if await try_consume_quota(feature, user_id, db):
        return

    month = _current_month()
    usage = await _get_or_create_usage(user_id, month, db)
    current = getattr(usage, feature)
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


def require_feature(feature: Feature):
    """FastAPI dependency factory. Use as: Depends(require_feature('ai_queries'))"""
    async def _check(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> None:
        await check_and_increment(feature, current_user.id, db)

    return _check
