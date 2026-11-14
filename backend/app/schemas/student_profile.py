from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


ShortText = Annotated[
    str,
    Field(min_length=1, max_length=100),
]
Grade = Annotated[
    float,
    Field(ge=0, le=20, allow_inf_nan=False),
]


class StudentProfileUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    bac_type: ShortText | None = None
    interests: list[ShortText] | None = Field(default=None, max_length=100)
    skills: list[ShortText] | None = Field(default=None, max_length=100)
    grades: dict[ShortText, Grade] | None = Field(default=None, max_length=100)
    career_goal: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    preferred_type: Literal["public", "private", "other"] | None = None
    preferred_city: ShortText | None = None
    can_relocate: bool | None = None
    max_annual_budget: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
    )


class StudentProfileRead(StudentProfileUpdate):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
    )

    user_id: int
