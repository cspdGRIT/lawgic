from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False, default="client")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # pending | approved | rejected — legacy: "approved" is a permanent bypass of the
    # subscription-or-credit gate (see core/access.py), kept for accounts that went
    # through the old blanket-approval flow. New accounts no longer need this — they're
    # gated per-action by subscription quota or credit_balance instead.
    access_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    # Pay-per-outcome balance — one credit = one paid action (issue analysis, document
    # unlock, lawyer match, research search) once subscription quota runs out. Granted
    # by trial signup, by an admin-approved UPI purchase, or (once wired) an automated
    # Razorpay top-up.
    credit_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
