from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RecommendationType, Severity


class PaddockRecommendation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'paddock_recommendations'

    recommendation_id: Mapped[str] = mapped_column(
        ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False, index=True
    )
    paddock_id: Mapped[str] = mapped_column(ForeignKey('paddocks.id', ondelete='CASCADE'), nullable=False)
    rec_type: Mapped[RecommendationType] = mapped_column(
        Enum(RecommendationType, name='rec_type_enum'), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[Severity] = mapped_column(Enum(Severity, name='severity_enum'), nullable=False)

    recommendation = relationship('Recommendation', back_populates='paddock_recommendations')
