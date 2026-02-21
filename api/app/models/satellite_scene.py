from datetime import date

from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SatelliteScene(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'satellite_scenes'
    __table_args__ = (
        UniqueConstraint('farm_id', 'scene_date', 'source', name='uq_farm_scene_source'),
    )

    farm_id: Mapped[str] = mapped_column(ForeignKey('farms.id', ondelete='CASCADE'), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default='stac_sentinel2')
    scene_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    cloud_pct: Mapped[float | None] = mapped_column(Float)
    red_uri: Mapped[str | None] = mapped_column(String(1024))
    nir_uri: Mapped[str | None] = mapped_column(String(1024))
    mask_uri: Mapped[str | None] = mapped_column(String(1024))
