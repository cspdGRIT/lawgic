from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class CreditTransaction(Base):
    """Audit ledger for User.credit_balance — every grant and spend is one row, so the
    balance is always reconstructable/explainable, not just a bare counter."""

    __tablename__ = "credit_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = grant, negative = spend
    reason: Mapped[str] = mapped_column(String(30), nullable=False)  # trial_grant | purchase | spend
    feature: Mapped[str | None] = mapped_column(String(30), nullable=True)  # which action spent it, if a spend
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
