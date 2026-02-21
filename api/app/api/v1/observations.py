from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.paddock import Paddock
from app.models.paddock_observation import PaddockObservation
from app.schemas.observation import ObservationForDate
from app.schemas.paddock import PaddockObservationPoint, PaddockObservationSeries
from app.services.ndvi import ndvi_bucket, trend_direction, trend_slope

router = APIRouter()


@router.get('/farms/{farm_id}/observations/dates', response_model=dict)
def list_observation_dates(farm_id: str, db: Session = Depends(get_db)) -> dict:
    stmt = (
        select(distinct(PaddockObservation.obs_date))
        .join(Paddock, Paddock.id == PaddockObservation.paddock_id)
        .where(Paddock.farm_id == farm_id)
        .order_by(PaddockObservation.obs_date.desc())
    )
    dates = [row for row in db.scalars(stmt).all()]
    return {'data': {'dates': dates}}


@router.get('/farms/{farm_id}/observations', response_model=dict)
def observations_by_date(
    farm_id: str,
    observation_date: date = Query(alias='date'),
    db: Session = Depends(get_db),
) -> dict:
    stmt = (
        select(PaddockObservation, Paddock)
        .join(Paddock, Paddock.id == PaddockObservation.paddock_id)
        .where(Paddock.farm_id == farm_id, PaddockObservation.obs_date == observation_date)
        .order_by(Paddock.name.asc())
    )
    rows = db.execute(stmt).all()
    result = [
        ObservationForDate(
            paddock_id=paddock.id,
            paddock_name=paddock.name,
            ndvi_mean=obs.ndvi_mean,
            bucket=ndvi_bucket(obs.ndvi_mean),
            quality_flag=obs.quality_flag.value,
            cloud_pct=obs.cloud_pct,
        ).model_dump()
        for obs, paddock in rows
    ]
    return {'data': result, 'meta': {'count': len(result)}}


@router.get('/paddocks/{paddock_id}/observations', response_model=dict)
def paddock_series(paddock_id: str, db: Session = Depends(get_db)) -> dict:
    paddock = db.get(Paddock, paddock_id)
    if not paddock:
        raise HTTPException(status_code=404, detail='Paddock not found')

    observations = db.scalars(
        select(PaddockObservation)
        .where(PaddockObservation.paddock_id == paddock_id)
        .order_by(PaddockObservation.obs_date.asc())
    ).all()

    points = [
        PaddockObservationPoint(
            obs_date=obs.obs_date,
            ndvi_mean=obs.ndvi_mean,
            ndvi_p10=obs.ndvi_p10,
            ndvi_p50=obs.ndvi_p50,
            ndvi_p90=obs.ndvi_p90,
            cloud_pct=obs.cloud_pct,
            quality_flag=obs.quality_flag.value,
        )
        for obs in observations
    ]
    trend_points = [(obs.obs_date, obs.ndvi_mean) for obs in observations[-3:]]
    slope = trend_slope(trend_points)

    response = PaddockObservationSeries(
        paddock_id=paddock_id,
        points=points,
        slope=slope,
        direction=trend_direction(slope),
    )
    return {'data': response.model_dump()}
