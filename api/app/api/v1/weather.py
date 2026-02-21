from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.weather import WeatherDailyOut
from app.services.weather_service import fetch_weather_forecast, get_weather_forecast

router = APIRouter()


@router.get('/farms/{farm_id}/weather/forecast', response_model=dict)
async def weather_forecast(farm_id: str, db: Session = Depends(get_db)) -> dict:
    data = get_weather_forecast(db, farm_id)
    if not data:
        data = await fetch_weather_forecast(db, farm_id)

    payload = [WeatherDailyOut.model_validate(item).model_dump() for item in data]
    return {'data': payload, 'meta': {'count': len(payload)}}
