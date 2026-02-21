from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.paddock_recommendation import PaddockRecommendation
from app.models.recommendation import Recommendation
from app.schemas.recommendation import RecommendationGenerateRequest
from app.services.recommendation_service import (
    generate_weekly_recommendations,
    get_latest_recommendation,
    get_recommendation_for_week,
)

router = APIRouter()


@router.get('/farms/{farm_id}/recommendations/latest', response_model=dict)
def latest_recommendation(farm_id: str, db: Session = Depends(get_db)) -> dict:
    rec = get_latest_recommendation(db, farm_id)
    if not rec:
        raise HTTPException(status_code=404, detail='No recommendations available')
    return {'data': _serialize_recommendation(db, rec)}


@router.get('/farms/{farm_id}/recommendations', response_model=dict)
def recommendation_by_week(
    farm_id: str,
    week_start: date = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    rec = get_recommendation_for_week(db, farm_id, week_start)
    if not rec:
        raise HTTPException(status_code=404, detail='Recommendation not found')
    return {'data': _serialize_recommendation(db, rec)}


@router.post('/farms/{farm_id}/recommendations/generate', response_model=dict)
def generate_recommendation(
    farm_id: str,
    payload: RecommendationGenerateRequest,
    db: Session = Depends(get_db),
) -> dict:
    rec = generate_weekly_recommendations(db, farm_id, payload.week_start)
    return {'data': _serialize_recommendation(db, rec)}


def _serialize_recommendation(db: Session, recommendation: Recommendation) -> dict:
    paddock_rows = db.scalars(
        select(PaddockRecommendation)
        .where(PaddockRecommendation.recommendation_id == recommendation.id)
        .order_by(PaddockRecommendation.created_at.asc())
    ).all()
    return {
        'id': recommendation.id,
        'farm_id': recommendation.farm_id,
        'created_for_week_start': recommendation.created_for_week_start,
        'summary_md': recommendation.summary_md,
        'created_at': recommendation.created_at,
        'paddock_recommendations': [
            {
                'paddock_id': row.paddock_id,
                'rec_type': row.rec_type.value,
                'message': row.message,
                'severity': row.severity.value,
            }
            for row in paddock_rows
        ],
    }
