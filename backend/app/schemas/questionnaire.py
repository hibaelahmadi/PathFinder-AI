from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class QuestionnaireSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: Literal["in_progress", "completed"]
    expected_question_code: str | None
    profile: dict[str, str | None] | None
    profile_confirmed: bool
    created_at: datetime


class QuestionnaireAnswerSave(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=1, max_length=2000)
    answer_text: str = Field(min_length=1, max_length=10000)
    answer_value: JsonValue = None


class QuestionnaireAnswerRead(QuestionnaireAnswerSave):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: int
    session_id: int
    question_code: str
    updated_at: datetime
