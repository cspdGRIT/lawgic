from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Lawyer(Base):
    __tablename__ = "lawyers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bar_council_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    specializations: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    practice_areas: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hourly_rate: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # INR
    consultation_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # INR
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=4.0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    languages: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    court_levels: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
