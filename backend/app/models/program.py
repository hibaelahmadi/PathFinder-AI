from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Program(Base):
    __tablename__ = "programs"

    __table_args__ = (
        CheckConstraint(
            "duration_months > 0",
            name="ck_programs_duration_positive",
        ),
        CheckConstraint(
            "annual_cost >= 0",
            name="ck_programs_annual_cost_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    campus_id: Mapped[int] = mapped_column(
        ForeignKey("campuses.id"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    field: Mapped[str | None] = mapped_column(String(150))
    duration_months: Mapped[int | None] = mapped_column()
    annual_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))