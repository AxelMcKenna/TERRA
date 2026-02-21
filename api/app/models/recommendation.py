from datetime import date

from sqlalchemy import Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Recommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'recommendations'
    __table_args__ = (UniqueConstraint('farm_id', 'created_for_week_start', name='uq_farm_week'),)

    farm_id: Mapped[str] = mapped_column(ForeignKey('farms.id', ondelete='CASCADE'), nullable=False, index=True)
    created_for_week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    summary_md: Mapped[str] = mapped_column(Text, nullable=False)

    paddock_recommendations = relationship(
        'PaddockRecommendation', back_populates='recommendation', cascade='all, delete-orphan'
    )
