from datetime import date, datetime

from pydantic import BaseModel


class PaddockRecommendationOut(BaseModel):
    paddock_id: str
    rec_type: str
    message: str
    severity: str


class RecommendationOut(BaseModel):
    id: str
    farm_id: str
    created_for_week_start: date
    summary_md: str
    created_at: datetime
    paddock_recommendations: list[PaddockRecommendationOut]


class RecommendationGenerateRequest(BaseModel):
    week_start: date | None = None
