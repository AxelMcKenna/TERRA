from datetime import date

from pydantic import BaseModel


class ObservationDateList(BaseModel):
    dates: list[date]


class ObservationForDate(BaseModel):
    paddock_id: str
    paddock_name: str
    ndvi_mean: float
    bucket: str
    quality_flag: str
    cloud_pct: float | None
