from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class PaddockBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class PaddockCreate(PaddockBase):
    geom_geojson: dict

    @field_validator('geom_geojson')
    @classmethod
    def validate_geojson(cls, value: dict) -> dict:
        if value.get('type') != 'Polygon':
            raise ValueError('Only GeoJSON Polygon geometries are supported.')
        if not value.get('coordinates'):
            raise ValueError('GeoJSON Polygon requires coordinates.')
        return value


class PaddockUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    geom_geojson: dict | None = None


class PaddockOut(PaddockBase):
    id: str
    farm_id: str
    geom_geojson: dict
    area_ha: float
    created_at: datetime

    model_config = {'from_attributes': True}


class PaddockImportItem(BaseModel):
    name: str
    geom_geojson: dict


class PaddockImportRequest(BaseModel):
    feature_collection: dict


class PaddockObservationPoint(BaseModel):
    obs_date: date
    ndvi_mean: float
    ndvi_p10: float | None
    ndvi_p50: float | None
    ndvi_p90: float | None
    cloud_pct: float | None
    quality_flag: str


class PaddockObservationSeries(BaseModel):
    paddock_id: str
    points: list[PaddockObservationPoint]
    slope: float | None
    direction: str | None
