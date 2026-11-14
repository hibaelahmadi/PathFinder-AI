from typing import Literal

from pydantic import BaseModel, ConfigDict


class InstitutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    type: Literal["public", "private", "other"] | None
    website: str | None