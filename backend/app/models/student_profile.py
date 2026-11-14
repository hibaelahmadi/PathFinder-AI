from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    __table_args__ = (
        CheckConstraint(
            "max_annual_budget >= 0",
            name="ck_student_profiles_budget_nonnegative",
        ),
        CheckConstraint(
            "preferred_type IN ('public', 'private', 'other')",
            name="ck_student_profiles_preferred_type",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )
    bac_type: Mapped[str | None] = mapped_column(String(100))
    interests: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)))
    skills: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)))
    grades: Mapped[dict[str, float] | None] = mapped_column(JSONB)
    career_goal: Mapped[str | None] = mapped_column(String(255))
    preferred_type: Mapped[str | None] = mapped_column(String(20))
    preferred_city: Mapped[str | None] = mapped_column(String(100))
    can_relocate: Mapped[bool | None] = mapped_column(Boolean)
    max_annual_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )