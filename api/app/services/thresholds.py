from datetime import datetime

from sqlalchemy.orm import Session

from app.models.config_threshold import ConfigThreshold

DEFAULT_THRESHOLDS = {
    'ndvi_good_threshold': {'value': 0.50},
    'rain_light_threshold': {'value': 10.0},
    'rain_heavy_threshold': {'value': 40.0},
    'ndvi_drop_threshold': {'value': -0.003},
    'max_obs_age_days': {'value': 14},
    'cloud_pct_high_threshold': {'value': 40.0},
}


def seed_thresholds(db: Session) -> None:
    for key, value in DEFAULT_THRESHOLDS.items():
        existing = db.get(ConfigThreshold, key)
        if not existing:
            db.add(ConfigThreshold(key=key, value=value, updated_at=datetime.utcnow()))
    db.commit()


def get_threshold_value(db: Session, key: str, fallback: float) -> float:
    threshold = db.get(ConfigThreshold, key)
    if not threshold:
        return fallback
    value = threshold.value.get('value')
    if isinstance(value, (int, float)):
        return float(value)
    return fallback
