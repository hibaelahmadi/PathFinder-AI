from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AdmissionCriterionSource(Base):
    __tablename__ = "admission_criterion_sources"

    admission_criterion_id: Mapped[int] = mapped_column(
        ForeignKey("admission_criteria.id"),
        primary_key=True,
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"),
        primary_key=True,
        index=True,
    )