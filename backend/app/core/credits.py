"""Pay-per-outcome credit wallet — the second half of the dual access model alongside
subscription quota (core/limits.py). One credit = one paid action, spent only after
subscription quota for that feature is exhausted (see core/access.py)."""

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.credit_transaction import CreditTransaction
from app.models.user import User

TRIAL_GRANT_CREDITS = 3  # free credits on signup — lets someone feel real output before paying anything

# id -> (credits, price in rupees). Volume discount, standard credit-pack shape.
CREDIT_PACKS = {
    "single": {"credits": 1, "price_rupees": 49},
    "starter": {"credits": 5, "price_rupees": 199},   # ~₹40/credit
    "pro": {"credits": 12, "price_rupees": 399},       # ~₹33/credit
}


async def grant_credits(user: User, amount: int, reason: str, db: AsyncSession, feature: str | None = None) -> None:
    user.credit_balance += amount
    db.add(CreditTransaction(
        user_id=user.id, delta=amount, reason=reason, feature=feature, balance_after=user.credit_balance,
    ))
    await db.flush()


async def spend_credit(user: User, feature: str, db: AsyncSession) -> bool:
    """Atomically spend one credit if available. Returns False (no-op) if the balance is 0.

    Uses a conditional UPDATE (not read-check-then-write) so two concurrent requests
    (double click, two tabs) can't both pass the `balance > 0` check and both decrement
    — that would drive the balance negative."""
    result = await db.execute(
        update(User)
        .where(User.id == user.id, User.credit_balance > 0)
        .values(credit_balance=User.credit_balance - 1)
        .returning(User.credit_balance)
    )
    row = result.first()
    if row is None:
        return False
    user.credit_balance = row[0]
    db.add(CreditTransaction(
        user_id=user.id, delta=-1, reason="spend", feature=feature, balance_after=user.credit_balance,
    ))
    await db.flush()
    return True


async def grant_trial_credits(user: User, db: AsyncSession) -> None:
    await grant_credits(user, TRIAL_GRANT_CREDITS, reason="trial_grant", db=db)
