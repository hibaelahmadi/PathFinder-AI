from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AdmissionCriterionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    program_id: int
    academic_year: str
    campaign: str
    official_text: str
    accepted_bac_types: list[str] | None
    application_opens: date | None
    application_deadline: date | None
    verification_status: Literal["unverified", "verified"]
    verified_at: date | None