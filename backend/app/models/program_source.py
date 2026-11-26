from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProgramSource(Base):
    __tablename__ = "program_sources"

    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"),
        primary_key=True,
    )
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id"),
        primary_key=True,
        index=True,
    )