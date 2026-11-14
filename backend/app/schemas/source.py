from datetime import date

from pydantic import BaseModel, ConfigDict


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    url: str
    title: str
    retrieved_at: date
    verified_at: date | None