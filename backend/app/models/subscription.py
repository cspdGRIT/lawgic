from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


PLAN_FREE = "free"
PLAN_PRO = "pro"
PLAN_FIRM = "firm"

PLAN_LIMITS = {
    PLAN_FREE:  {"ai_queries": 10,  "cases": 3,  "documents": 5,  "research": 5},
    PLAN_PRO:   {"ai_queries": 500, "cases": 50, "documents": 100, "research": 100},
    PLAN_FIRM:  {"ai_queries": -1,  "cases": -1, "documents": -1,  "research": -1},  # -1 = unlimited
}

PLAN_PRICE_INR = {
    PLAN_FREE: 0,
    PLAN_PRO:  49900,   # paise
    PLAN_FIRM: 199900,  # paise
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False, default=PLAN_FREE)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    # active | cancelled | past_due
    razorpay_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    razorpay_order_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    razorpay_signature: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    # created | paid | failed | refunded
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
