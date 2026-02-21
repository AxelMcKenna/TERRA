from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.paddock import Paddock
from app.services.geometry import polygon_area_hectares
from app.services.thresholds import seed_thresholds


def seed_demo_data(db: Session) -> None:
    seed_thresholds(db)

    existing_farm = db.scalar(select(Farm).limit(1))
    if existing_farm:
        return

    farm = Farm(name='Demo Farm', description='Seeded farm for dev-facing mode', latitude=-36.85, longitude=174.76)
    db.add(farm)
    db.commit()
    db.refresh(farm)

    polygons = [
        {
            'name': 'Paddock A',
            'geom_geojson': {
                'type': 'Polygon',
                'coordinates': [[
                    [174.7500, -36.8500],
                    [174.7520, -36.8500],
                    [174.7520, -36.8485],
                    [174.7500, -36.8485],
                    [174.7500, -36.8500],
                ]],
            },
        },
        {
            'name': 'Paddock B',
            'geom_geojson': {
                'type': 'Polygon',
                'coordinates': [[
                    [174.7530, -36.8505],
                    [174.7550, -36.8505],
                    [174.7550, -36.8488],
                    [174.7530, -36.8488],
                    [174.7530, -36.8505],
                ]],
            },
        },
        {
            'name': 'Paddock C',
            'geom_geojson': {
                'type': 'Polygon',
                'coordinates': [[
                    [174.7510, -36.8520],
                    [174.7540, -36.8520],
                    [174.7540, -36.8509],
                    [174.7510, -36.8509],
                    [174.7510, -36.8520],
                ]],
            },
        },
    ]

    for polygon in polygons:
        db.add(
            Paddock(
                farm_id=farm.id,
                name=polygon['name'],
                geom_geojson=polygon['geom_geojson'],
                area_ha=polygon_area_hectares(polygon['geom_geojson']),
            )
        )

    db.commit()
