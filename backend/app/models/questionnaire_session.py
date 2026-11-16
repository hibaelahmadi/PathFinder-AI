from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, false, func
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
    profile: Mapped[dict[str, str | bool | None] | None] = mapped_column(
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
