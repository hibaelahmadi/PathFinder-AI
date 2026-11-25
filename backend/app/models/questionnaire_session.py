from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, false, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestionnaireSession(Base):
    __tablename__ = "questionnaire_sessions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed')",
            name="ck_questionnaire_sessions_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="in_progress",
    )
    expected_question_code: Mapped[str | None] = mapped_column(String(100))
    next_question: Mapped[dict[str, str] | None] = mapped_column(
        JSONB(none_as_null=True)
    )
    questionnaire_options: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    profile: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB(none_as_null=True)
    )
    profile_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
