from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmOut, FarmUpdate

router = APIRouter()


@router.get('', response_model=dict)
def list_farms(db: Session = Depends(get_db)) -> dict:
    farms = db.scalars(select(Farm).order_by(Farm.created_at.desc())).all()
    return {'data': [FarmOut.model_validate(farm).model_dump() for farm in farms], 'meta': {'count': len(farms)}}


@router.post('', response_model=dict, status_code=status.HTTP_201_CREATED)
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)) -> dict:
    farm = Farm(**payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {'data': FarmOut.model_validate(farm).model_dump()}


@router.get('/{farm_id}', response_model=dict)
def get_farm(farm_id: str, db: Session = Depends(get_db)) -> dict:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail='Farm not found')
    return {'data': FarmOut.model_validate(farm).model_dump()}


@router.patch('/{farm_id}', response_model=dict)
def update_farm(farm_id: str, payload: FarmUpdate, db: Session = Depends(get_db)) -> dict:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail='Farm not found')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, key, value)

    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {'data': FarmOut.model_validate(farm).model_dump()}


@router.delete('/{farm_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: str, db: Session = Depends(get_db)) -> None:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail='Farm not found')
    db.delete(farm)
    db.commit()
