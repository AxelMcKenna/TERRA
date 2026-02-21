from datetime import date

from app.services.ndvi import ndvi_bucket, trend_direction, trend_slope


def test_ndvi_bucket_boundaries() -> None:
    assert ndvi_bucket(0.15) == 'Very Low'
    assert ndvi_bucket(0.25) == 'Low'
    assert ndvi_bucket(0.40) == 'Medium'
    assert ndvi_bucket(0.60) == 'High'


def test_trend_helpers() -> None:
    points = [
        (date(2026, 1, 1), 0.52),
        (date(2026, 1, 11), 0.47),
    ]
    slope = trend_slope(points)
    assert slope is not None
    assert slope < 0.0
    assert trend_direction(slope) == 'down'
