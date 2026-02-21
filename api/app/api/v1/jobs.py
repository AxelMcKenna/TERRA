from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job_run import JobRun
from app.services.pipeline_service import ingest_satellite_scenes
from app.services.recommendation_service import generate_weekly_recommendations
from app.services.weather_service import fetch_weather_forecast

router = APIRouter()


@router.post('/farms/{farm_id}/jobs/ingest', response_model=dict)
async def run_ingest_pipeline(farm_id: str, db: Session = Depends(get_db)) -> dict:
    scenes = ingest_satellite_scenes(db, farm_id)
    weather = await fetch_weather_forecast(db, farm_id)
    recommendation = generate_weekly_recommendations(db, farm_id)
    return {
        'data': {
            'farm_id': farm_id,
            'scenes_processed': len(scenes),
            'weather_days': len(weather),
            'recommendation_id': recommendation.id,
        }
    }


@router.get('/jobs/runs', response_model=dict)
def job_runs(
    farm_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    stmt = select(JobRun)
    if farm_id:
        stmt = stmt.where(JobRun.farm_id == farm_id)
    rows = db.scalars(stmt.order_by(desc(JobRun.started_at)).limit(200)).all()
    payload = [
        {
            'id': row.id,
            'job_type': row.job_type.value,
            'farm_id': row.farm_id,
            'status': row.status.value,
            'started_at': row.started_at,
            'finished_at': row.finished_at,
            'stats_json': row.stats_json,
            'error': row.error,
        }
        for row in rows
    ]
    return {'data': payload, 'meta': {'count': len(payload)}}
