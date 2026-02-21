from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.farm import Farm
from app.models.paddock import Paddock
from app.schemas.paddock import PaddockCreate, PaddockImportRequest, PaddockOut, PaddockUpdate
from app.services.geometry import polygon_area_hectares

router = APIRouter()


@router.get('/farms/{farm_id}/paddocks', response_model=dict)
def list_paddocks(farm_id: str, db: Session = Depends(get_db)) -> dict:
    _ensure_farm(db, farm_id)
    paddocks = db.scalars(select(Paddock).where(Paddock.farm_id == farm_id).order_by(Paddock.created_at.asc())).all()
    return {
        'data': [PaddockOut.model_validate(paddock).model_dump() for paddock in paddocks],
        'meta': {'count': len(paddocks)},
    }


@router.post('/farms/{farm_id}/paddocks', response_model=dict, status_code=status.HTTP_201_CREATED)
def create_paddock(farm_id: str, payload: PaddockCreate, db: Session = Depends(get_db)) -> dict:
    _ensure_farm(db, farm_id)
    area = polygon_area_hectares(payload.geom_geojson)
    paddock = Paddock(farm_id=farm_id, name=payload.name, geom_geojson=payload.geom_geojson, area_ha=area)
    db.add(paddock)
    db.commit()
    db.refresh(paddock)
    return {'data': PaddockOut.model_validate(paddock).model_dump()}


@router.patch('/paddocks/{paddock_id}', response_model=dict)
def update_paddock(paddock_id: str, payload: PaddockUpdate, db: Session = Depends(get_db)) -> dict:
    paddock = db.get(Paddock, paddock_id)
    if not paddock:
        raise HTTPException(status_code=404, detail='Paddock not found')

    patch = payload.model_dump(exclude_unset=True)
    if 'geom_geojson' in patch:
        paddock.geom_geojson = patch['geom_geojson']
        paddock.area_ha = polygon_area_hectares(paddock.geom_geojson)
    if 'name' in patch:
        paddock.name = patch['name']

    db.add(paddock)
    db.commit()
    db.refresh(paddock)
    return {'data': PaddockOut.model_validate(paddock).model_dump()}


@router.delete('/paddocks/{paddock_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_paddock(paddock_id: str, db: Session = Depends(get_db)) -> None:
    paddock = db.get(Paddock, paddock_id)
    if not paddock:
        raise HTTPException(status_code=404, detail='Paddock not found')
    db.delete(paddock)
    db.commit()


@router.post('/farms/{farm_id}/paddocks/import', response_model=dict, status_code=status.HTTP_201_CREATED)
def import_paddocks(farm_id: str, payload: PaddockImportRequest, db: Session = Depends(get_db)) -> dict:
    _ensure_farm(db, farm_id)

    fc = payload.feature_collection
    if fc.get('type') != 'FeatureCollection':
        raise HTTPException(status_code=400, detail='feature_collection must be a GeoJSON FeatureCollection')

    created = []
    failures = []
    for idx, feature in enumerate(fc.get('features', [])):
        try:
            geom = feature.get('geometry', {})
            if geom.get('type') != 'Polygon':
                raise ValueError('Feature geometry must be Polygon')
            name = feature.get('properties', {}).get('name') or f'Imported Paddock {idx + 1}'
            paddock = Paddock(
                farm_id=farm_id,
                name=name,
                geom_geojson=geom,
                area_ha=polygon_area_hectares(geom),
            )
            db.add(paddock)
            db.flush()
            created.append(PaddockOut.model_validate(paddock).model_dump())
        except Exception as exc:  # noqa: BLE001
            failures.append({'index': idx, 'error': str(exc)})

    db.commit()
    return {'data': created, 'meta': {'count': len(created), 'failures': failures}}


def _ensure_farm(db: Session, farm_id: str) -> None:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail='Farm not found')
