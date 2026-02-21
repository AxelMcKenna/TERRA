from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import JobStatus, JobType, QualityFlag
from app.models.job_run import JobRun
from app.models.paddock import Paddock
from app.models.paddock_observation import PaddockObservation
from app.models.satellite_scene import SatelliteScene
from app.services.thresholds import get_threshold_value


def ingest_satellite_scenes(db: Session, farm_id: str) -> list[SatelliteScene]:
    run = _start_job(db, JobType.ingest_satellite, farm_id)
    created: list[SatelliteScene] = []
    try:
        today = date.today()
        for offset in [3, 10, 17]:
            scene_date = today - timedelta(days=offset)
            existing = db.scalar(
                select(SatelliteScene).where(
                    SatelliteScene.farm_id == farm_id,
                    SatelliteScene.scene_date == scene_date,
                    SatelliteScene.source == 'stac_sentinel2',
                )
            )
            if existing:
                created.append(existing)
                continue

            cloud_pct = float((offset * 7) % 65)
            scene = SatelliteScene(
                farm_id=farm_id,
                source='stac_sentinel2',
                scene_date=scene_date,
                cloud_pct=cloud_pct,
                red_uri=f's3://synthetic/red/{farm_id}/{scene_date}.tif',
                nir_uri=f's3://synthetic/nir/{farm_id}/{scene_date}.tif',
                mask_uri=f's3://synthetic/mask/{farm_id}/{scene_date}.tif',
            )
            db.add(scene)
            created.append(scene)

        db.commit()
        for scene in created:
            db.refresh(scene)
            aggregate_paddock_ndvi(db, scene.id)

        _finish_job(db, run, JobStatus.success, {'scenes': len(created)})
        return created
    except Exception as exc:
        _finish_job(db, run, JobStatus.failed, {'scenes': 0}, str(exc))
        raise


def aggregate_paddock_ndvi(db: Session, scene_id: str) -> None:
    run = _start_job(db, JobType.aggregate_ndvi)
    try:
        scene = db.get(SatelliteScene, scene_id)
        if not scene:
            _finish_job(db, run, JobStatus.failed, {}, 'Scene not found')
            return

        paddocks = db.scalars(select(Paddock).where(Paddock.farm_id == scene.farm_id)).all()
        cloud_high = get_threshold_value(db, 'cloud_pct_high_threshold', 40.0)

        for paddock in paddocks:
            ndvi = _synthetic_ndvi(scene.scene_date, paddock.id)
            quality = QualityFlag.OK
            if (scene.cloud_pct or 0.0) >= cloud_high:
                quality = QualityFlag.CLOUDY

            existing = db.scalar(
                select(PaddockObservation).where(
                    PaddockObservation.paddock_id == paddock.id,
                    PaddockObservation.obs_date == scene.scene_date,
                )
            )
            if existing:
                existing.ndvi_mean = ndvi
                existing.ndvi_p10 = max(0.0, ndvi - 0.12)
                existing.ndvi_p50 = ndvi
                existing.ndvi_p90 = min(1.0, ndvi + 0.12)
                existing.cloud_pct = scene.cloud_pct
                existing.quality_flag = quality
            else:
                db.add(
                    PaddockObservation(
                        paddock_id=paddock.id,
                        obs_date=scene.scene_date,
                        ndvi_mean=ndvi,
                        ndvi_p10=max(0.0, ndvi - 0.12),
                        ndvi_p50=ndvi,
                        ndvi_p90=min(1.0, ndvi + 0.12),
                        cloud_pct=scene.cloud_pct,
                        quality_flag=quality,
                    )
                )

        db.commit()
        _finish_job(db, run, JobStatus.success, {'paddocks': len(paddocks)})
    except Exception as exc:
        _finish_job(db, run, JobStatus.failed, {}, str(exc))
        raise


def _synthetic_ndvi(scene_date: date, paddock_id: str) -> float:
    seed = f'{scene_date.isoformat()}:{paddock_id}'.encode('utf-8')
    hashed = hashlib.sha256(seed).hexdigest()
    value = int(hashed[:8], 16)
    return round(0.12 + (value % 6800) / 10000.0, 4)


def _start_job(db: Session, job_type: JobType, farm_id: str | None = None) -> JobRun:
    run = JobRun(job_type=job_type, farm_id=farm_id, status=JobStatus.running, stats_json={})
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def _finish_job(
    db: Session,
    run: JobRun,
    status: JobStatus,
    stats_json: dict,
    error: str | None = None,
) -> None:
    run.status = status
    run.finished_at = datetime.utcnow()
    run.stats_json = stats_json
    run.error = error
    db.add(run)
    db.commit()
