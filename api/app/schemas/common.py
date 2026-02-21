from datetime import date, datetime

from pydantic import BaseModel


class MetaResponse(BaseModel):
    count: int | None = None


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict | None = None


class Timestamped(BaseModel):
    created_at: datetime


class DateRange(BaseModel):
    start: date
    end: date
