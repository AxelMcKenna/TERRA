from datetime import date

from pydantic import BaseModel


class WeatherDailyOut(BaseModel):
    date: date
    rain_mm: float
    temp_min_c: float
    temp_max_c: float
    wind_kph: float
    source: str

    model_config = {'from_attributes': True}
