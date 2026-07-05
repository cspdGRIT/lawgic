from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # criminal, civil, corporate, family, property, labour, consumer, taxation
    jurisdiction: Mapped[str] = mapped_column(String(100), nullable=False)
    court_level: Mapped[str] = mapped_column(String(50), nullable=False)
    # district, high_court, supreme_court, tribunal
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    # open, in_progress, closed, won, lost, appealed
    opposing_party: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    key_facts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON stored as string
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assigned_lawyer_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("lawyers.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
