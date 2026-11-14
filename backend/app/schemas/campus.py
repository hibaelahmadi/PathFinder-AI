from pydantic import BaseModel, ConfigDict


class CampusRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    institution_id: int
    name: str
    city: str
    address: str | None