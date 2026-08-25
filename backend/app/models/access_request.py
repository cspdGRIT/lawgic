from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AccessRequest(Base):
    """A user's self-reported UPI payment, awaiting admin review. There's no payment
    gateway webhook here — the user pays out-of-band and reports it; an admin checks
    their own UPI app for the credit and approves/rejects manually."""

    __tablename__ = "access_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending | approved | rejected
    amount_rupees: Mapped[int] = mapped_column(Integer, nullable=False, default=72)
    utr_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)  # UPI transaction ref, self-reported
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
