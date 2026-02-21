from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Farm Intelligence API'
    app_env: str = 'dev'
    app_mode: str = 'dev_facing'
    api_v1_prefix: str = '/api/v1'
    auto_create_tables: bool = True

    database_url: str = Field(
        default='postgresql+psycopg://postgres:postgres@localhost:5432/farm_intelligence'
    )
    redis_url: str = 'redis://localhost:6379/0'

    openweather_api_key: str | None = None
    openweather_base_url: str = 'https://api.openweathermap.org/data/2.5'

    mapbox_access_token: str | None = None

    scenes_lookback_days: int = 30
    seed_demo_data: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
