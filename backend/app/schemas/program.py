from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    campus_id: int
    name: str
    description: str | None
    field: str | None
    duration_months: int | None
    annual_cost: Decimal | None