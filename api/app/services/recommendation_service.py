from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from app.models.enums import RecommendationType, Severity
from app.models.farm import Farm
from app.models.paddock import Paddock
from app.models.paddock_observation import PaddockObservation
from app.models.paddock_recommendation import PaddockRecommendation
from app.models.recommendation import Recommendation
from app.models.weather_daily import WeatherDaily
from app.services.ndvi import trend_slope
from app.services.thresholds import get_threshold_value


def generate_weekly_recommendations(db: Session, farm_id: str, week_start: date | None = None) -> Recommendation:
    farm = db.get(Farm, farm_id)
    if not farm:
        raise ValueError('Farm not found.')

    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    existing = db.scalar(
        select(Recommendation).where(
            Recommendation.farm_id == farm_id,
            Recommendation.created_for_week_start == week_start,
        )
    )

    if existing:
        db.execute(
            delete(PaddockRecommendation).where(PaddockRecommendation.recommendation_id == existing.id)
        )
        db.delete(existing)
        db.commit()

    rec = Recommendation(
        farm_id=farm_id,
        created_for_week_start=week_start,
        summary_md='Generating recommendations...',
        created_at=datetime.utcnow(),
    )
    db.add(rec)
    db.flush()

    paddocks = db.scalars(select(Paddock).where(Paddock.farm_id == farm_id)).all()
    forecast = db.scalars(
        select(WeatherDaily)
        .where(WeatherDaily.farm_id == farm_id)
        .order_by(WeatherDaily.date.asc())
        .limit(3)
    ).all()
    rain_3day = sum(item.rain_mm for item in forecast)

    results: list[PaddockRecommendation] = []
    counts = Counter()

    for paddock in paddocks:
        obs = db.scalars(
            select(PaddockObservation)
            .where(PaddockObservation.paddock_id == paddock.id)
            .order_by(desc(PaddockObservation.obs_date))
            .limit(3)
        ).all()
        if not obs:
            row = _build_rec(rec.id, paddock.id, RecommendationType.LOW_DATA)
            results.append(row)
            counts[RecommendationType.LOW_DATA.value] += 1
            continue

        latest = obs[0]
        points = list(reversed([(o.obs_date, o.ndvi_mean) for o in obs]))
        slope = trend_slope(points)

        ndvi_good = get_threshold_value(db, 'ndvi_good_threshold', 0.50)
        rain_light = get_threshold_value(db, 'rain_light_threshold', 10.0)
        rain_heavy = get_threshold_value(db, 'rain_heavy_threshold', 40.0)
        ndvi_drop = get_threshold_value(db, 'ndvi_drop_threshold', -0.003)
        max_obs_age_days = get_threshold_value(db, 'max_obs_age_days', 14)
        cloud_high = get_threshold_value(db, 'cloud_pct_high_threshold', 40.0)

        age_days = (date.today() - latest.obs_date).days
        if age_days > max_obs_age_days or (latest.cloud_pct or 0.0) >= cloud_high:
            rec_type = RecommendationType.LOW_DATA
        elif rain_3day >= rain_heavy:
            rec_type = RecommendationType.AVOID_WATERLOG
        elif slope is not None and slope <= ndvi_drop:
            rec_type = RecommendationType.MONITOR_STRESS
        elif latest.ndvi_mean >= ndvi_good and rain_3day <= rain_light:
            rec_type = RecommendationType.GRAZE_NOW
        else:
            rec_type = RecommendationType.MONITOR_STRESS

        row = _build_rec(rec.id, paddock.id, rec_type)
        results.append(row)
        counts[rec_type.value] += 1

    for result in results:
        db.add(result)

    rec.summary_md = _summary_from_counts(counts)
    db.commit()
    db.refresh(rec)
    return rec


def get_latest_recommendation(db: Session, farm_id: str) -> Recommendation | None:
    return db.scalar(
        select(Recommendation)
        .where(Recommendation.farm_id == farm_id)
        .order_by(desc(Recommendation.created_for_week_start))
    )


def get_recommendation_for_week(db: Session, farm_id: str, week_start: date) -> Recommendation | None:
    return db.scalar(
        select(Recommendation).where(
            Recommendation.farm_id == farm_id,
            Recommendation.created_for_week_start == week_start,
        )
    )


def _build_rec(
    recommendation_id: str, paddock_id: str, rec_type: RecommendationType
) -> PaddockRecommendation:
    templates = {
        RecommendationType.GRAZE_NOW: (
            'High pasture health and light rain forecast. Good grazing window next 2 days.',
            Severity.info,
        ),
        RecommendationType.AVOID_WATERLOG: (
            'Heavy rain forecast in next 72h. Avoid grazing to reduce pugging.',
            Severity.warning,
        ),
        RecommendationType.MONITOR_STRESS: (
            'NDVI trend down across last observations. Check for pests or irrigation needs.',
            Severity.warning,
        ),
        RecommendationType.LOW_DATA: (
            'Recent imagery too cloudy or stale; limited confidence.',
            Severity.warning,
        ),
    }
    message, severity = templates[rec_type]
    return PaddockRecommendation(
        recommendation_id=recommendation_id,
        paddock_id=paddock_id,
        rec_type=rec_type,
        message=message,
        severity=severity,
    )


def _summary_from_counts(counts: Counter) -> str:
    lines = []
    if counts['GRAZE_NOW']:
        lines.append(f"- **{counts['GRAZE_NOW']} paddocks ready to graze**")
    if counts['AVOID_WATERLOG']:
        lines.append(f"- **Avoid waterlogging risk** in {counts['AVOID_WATERLOG']} paddocks")
    if counts['MONITOR_STRESS']:
        lines.append(f"- **Monitor stress** in {counts['MONITOR_STRESS']} paddocks")
    if counts['LOW_DATA']:
        lines.append(f"- **Low confidence data** for {counts['LOW_DATA']} paddocks")
    return '\n'.join(lines) if lines else '- No actionable recommendations this week.'
