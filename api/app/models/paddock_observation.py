from datetime import date

from sqlalchemy import Date, Enum, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import QualityFlag


class PaddockObservation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'paddock_observations'
    __table_args__ = (UniqueConstraint('paddock_id', 'obs_date', name='uq_paddock_obs_date'),)

    paddock_id: Mapped[str] = mapped_column(
        ForeignKey('paddocks.id', ondelete='CASCADE'), nullable=False, index=True
    )
    obs_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    ndvi_mean: Mapped[float] = mapped_column(Float, nullable=False)
    ndvi_p10: Mapped[float | None] = mapped_column(Float)
    ndvi_p50: Mapped[float | None] = mapped_column(Float)
    ndvi_p90: Mapped[float | None] = mapped_column(Float)
    cloud_pct: Mapped[float | None] = mapped_column(Float)
    quality_flag: Mapped[QualityFlag] = mapped_column(
        Enum(QualityFlag, name='quality_flag_enum'), default=QualityFlag.OK, nullable=False
    )

    paddock = relationship('Paddock', back_populates='observations')
