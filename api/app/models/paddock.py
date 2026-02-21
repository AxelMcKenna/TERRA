from sqlalchemy import Float, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Paddock(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'paddocks'

    farm_id: Mapped[str] = mapped_column(ForeignKey('farms.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    geom_geojson: Mapped[dict] = mapped_column(JSON, nullable=False)
    area_ha: Mapped[float] = mapped_column(Float, nullable=False)

    farm = relationship('Farm', back_populates='paddocks')
    observations = relationship('PaddockObservation', back_populates='paddock', cascade='all, delete-orphan')
