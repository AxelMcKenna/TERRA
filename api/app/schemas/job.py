from datetime import datetime

from pydantic import BaseModel


class JobRunOut(BaseModel):
    id: str
    job_type: str
    farm_id: str | None
    status: str
    started_at: datetime
    finished_at: datetime | None
    stats_json: dict
    error: str | None

    model_config = {'from_attributes': True}
