from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.enums import JobStatus, JobType


class JobRun(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'job_runs'

    job_type: Mapped[JobType] = mapped_column(Enum(JobType, name='job_type_enum'), nullable=False, index=True)
    farm_id: Mapped[str | None] = mapped_column(ForeignKey('farms.id', ondelete='SET NULL'), index=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name='job_status_enum'), default=JobStatus.running, nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stats_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text)
