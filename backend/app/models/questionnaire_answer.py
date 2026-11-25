from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestionnaireAnswer(Base):
    __tablename__ = "questionnaire_answers"

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_code",
            name="uq_questionnaire_answers_session_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("questionnaire_sessions.id"),
        index=True,
    )
    question_code: Mapped[str] = mapped_column(String(100))
    question_text: Mapped[str] = mapped_column(Text)
    answer_text: Mapped[str] = mapped_column(Text)
    answer_value: Mapped[Any | None] = mapped_column(
        JSONB(none_as_null=True),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
