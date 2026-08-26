from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint
from app.core.database import Base


class MonthlyUsage(Base):
    """Per-user monthly usage counters. One row per (user, YYYY-MM)."""
    __tablename__ = "monthly_usage"
    __table_args__ = (UniqueConstraint("user_id", "month", name="uq_usage_user_month"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # "YYYY-MM"
    ai_queries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    documents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    research: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lawyer_matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
