from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator


class QuestionnaireSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: Literal["in_progress", "completed"]
    expected_question_code: str | None
    profile: dict[str, JsonValue] | None
    profile_confirmed: bool
    created_at: datetime


class QuestionnaireAnswerSave(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=1, max_length=2000)
    answer_text: str = Field(max_length=10000)
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


class QuestionnaireResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_code: str = Field(min_length=1, max_length=100)
    answer_text: str = Field(max_length=10000)
    question_text: str | None = Field(default=None, max_length=2000)
    answer_value: JsonValue = None


class QuestionnaireAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["start", "answer", "correct", "confirm", "reopen"]
    reponse: QuestionnaireResponse | None = None

    @model_validator(mode="after")
    def validate_response(self):
        requires_response = self.action in ("answer", "correct")
        if requires_response != (self.reponse is not None):
            raise ValueError("Only answer and correct require a response.")
        return self


class QuestionnaireQuestion(BaseModel):
    question_code: str = Field(min_length=1, max_length=100)
    question_text: str = Field(min_length=1, max_length=2000)


class QuestionnaireAnswerData(QuestionnaireAnswerSave):
    question_code: str = Field(min_length=1, max_length=100)


class QuestionnaireState(BaseModel):
    status: Literal["in_progress", "completed"]
    expected_question_code: str | None
    answers: dict[str, QuestionnaireAnswerData]


class QuestionnaireResult(BaseModel):
    etat: QuestionnaireState
    next_question: QuestionnaireQuestion | None
    answers_to_save: list[QuestionnaireAnswerData]
    answer_codes_to_delete: list[str]
    profile: dict[str, JsonValue]
    profile_confirmed: bool
    errors: list[str]
