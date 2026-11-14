from datetime import date


from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base import Base



class AdmissionCriterion(Base):
    __tablename__ = "admission_criteria"

    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "academic_year",
            "campaign",
            name="uq_admission_program_year_campaign",
        ),
        CheckConstraint(
            "application_deadline >= application_opens",
            name="ck_admission_application_dates",
        ),
        CheckConstraint(
            "verification_status IN ('unverified', 'verified')",
            name="ck_admission_verification_status",
        ),
        CheckConstraint(
            "(verification_status = 'verified' AND verified_at IS NOT NULL) "
            "OR (verification_status = 'unverified' AND verified_at IS NULL)",
            name="ck_admission_verification_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"),
        index=True,
    )
    academic_year: Mapped[str] = mapped_column(String(9))
    campaign: Mapped[str] = mapped_column(String(100))
    official_text: Mapped[str] = mapped_column(Text)
    accepted_bac_types: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(100))
    )

    application_opens: Mapped[date | None] = mapped_column(Date)
    application_deadline: Mapped[date | None] = mapped_column(Date)
    verification_status: Mapped[str] = mapped_column(
        String(20),
        server_default="unverified",
    )
    verified_at: Mapped[date | None] = mapped_column(Date)