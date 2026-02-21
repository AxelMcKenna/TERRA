import asyncio
from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.farm import Farm
from app.services.pipeline_service import ingest_satellite_scenes
from app.services.recommendation_service import generate_weekly_recommendations
from app.services.weather_service import fetch_weather_forecast
from app.workers.celery_app import celery_app


@celery_app.task
def ingest_satellite_scenes_task(farm_id: str) -> dict:
    with SessionLocal() as db:
        scenes = ingest_satellite_scenes(db, farm_id)
        return {'farm_id': farm_id, 'scenes': len(scenes)}


@celery_app.task
def fetch_weather_forecast_task(farm_id: str) -> dict:
    with SessionLocal() as db:
        weather = asyncio.run(fetch_weather_forecast(db, farm_id))
        return {'farm_id': farm_id, 'days': len(weather)}


@celery_app.task
def generate_weekly_recommendations_task(farm_id: str, week_start: str | None = None) -> dict:
    with SessionLocal() as db:
        date_value = date.fromisoformat(week_start) if week_start else None
        rec = generate_weekly_recommendations(db, farm_id, date_value)
        return {'farm_id': farm_id, 'recommendation_id': rec.id}


@celery_app.task
def run_weekly_recommendations_for_all_farms() -> dict:
    with SessionLocal() as db:
        farm_ids = db.scalars(select(Farm.id)).all()
        for farm_id in farm_ids:
            generate_weekly_recommendations(db, farm_id)
        return {'farm_count': len(farm_ids)}
