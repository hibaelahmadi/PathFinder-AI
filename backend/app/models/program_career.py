from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgramCareer(Base):
    __tablename__ = "program_careers"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"),
        primary_key=True,
    )
    career_id: Mapped[int] = mapped_column(
        ForeignKey("careers.id"),
        primary_key=True,
        index=True,
    )