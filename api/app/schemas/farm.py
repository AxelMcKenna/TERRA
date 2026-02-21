from datetime import datetime

from pydantic import BaseModel, Field


class FarmBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class FarmCreate(FarmBase):
    pass


class FarmUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class FarmOut(FarmBase):
    id: str
    created_at: datetime

    model_config = {'from_attributes': True}
