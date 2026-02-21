from __future__ import annotations

from datetime import date, datetime, timedelta

import httpx
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.farm import Farm
from app.models.weather_daily import WeatherDaily


async def fetch_weather_forecast(db: Session, farm_id: str) -> list[WeatherDaily]:
    farm = db.get(Farm, farm_id)
    if not farm:
        return []

    settings = get_settings()
    if settings.openweather_api_key:
        forecast = await _fetch_from_openweather(farm.latitude, farm.longitude, settings.openweather_api_key)
    else:
        forecast = _synthetic_forecast()

    db.execute(delete(WeatherDaily).where(WeatherDaily.farm_id == farm_id))
    rows: list[WeatherDaily] = []
    for item in forecast:
        row = WeatherDaily(
            farm_id=farm_id,
            date=item['date'],
            rain_mm=item['rain_mm'],
            temp_min_c=item['temp_min_c'],
            temp_max_c=item['temp_max_c'],
            wind_kph=item['wind_kph'],
            source=item['source'],
            fetched_at=datetime.utcnow(),
        )
        db.add(row)
        rows.append(row)

    db.commit()
    return rows


def get_weather_forecast(db: Session, farm_id: str) -> list[WeatherDaily]:
    stmt = (
        select(WeatherDaily)
        .where(WeatherDaily.farm_id == farm_id)
        .order_by(WeatherDaily.date.asc(), WeatherDaily.fetched_at.desc())
    )
    return db.scalars(stmt).all()


async def _fetch_from_openweather(lat: float, lon: float, api_key: str) -> list[dict]:
    settings = get_settings()
    url = f"{settings.openweather_base_url}/forecast"
    params = {'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'}

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    # Collapse 3-hour data into day buckets.
    day_buckets: dict[date, dict] = {}
    for item in data.get('list', []):
        dt = datetime.fromtimestamp(item['dt'])
        bucket = day_buckets.setdefault(
            dt.date(),
            {
                'date': dt.date(),
                'rain_mm': 0.0,
                'temp_min_c': item['main']['temp_min'],
                'temp_max_c': item['main']['temp_max'],
                'wind_kph': item['wind']['speed'] * 3.6,
                'source': 'openweather',
            },
        )
        bucket['rain_mm'] += item.get('rain', {}).get('3h', 0.0)
        bucket['temp_min_c'] = min(bucket['temp_min_c'], item['main']['temp_min'])
        bucket['temp_max_c'] = max(bucket['temp_max_c'], item['main']['temp_max'])
        bucket['wind_kph'] = max(bucket['wind_kph'], item['wind']['speed'] * 3.6)

    return list(day_buckets.values())[:7]


def _synthetic_forecast() -> list[dict]:
    today = date.today()
    synthetic = []
    for i in range(7):
        current = today + timedelta(days=i)
        rain = [2.0, 4.0, 14.0, 42.0, 8.0, 1.0, 0.0][i]
        synthetic.append(
            {
                'date': current,
                'rain_mm': rain,
                'temp_min_c': 4.0 + i,
                'temp_max_c': 15.0 + i,
                'wind_kph': 12.0 + i,
                'source': 'synthetic',
            }
        )
    return synthetic
