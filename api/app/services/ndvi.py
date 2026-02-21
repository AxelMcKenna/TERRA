from datetime import date


def ndvi_bucket(value: float) -> str:
    if value < 0.2:
        return 'Very Low'
    if value < 0.35:
        return 'Low'
    if value < 0.5:
        return 'Medium'
    return 'High'


def trend_slope(points: list[tuple[date, float]]) -> float | None:
    if len(points) < 2:
        return None
    first_date, first_value = points[0]
    last_date, last_value = points[-1]
    days = (last_date - first_date).days
    if days <= 0:
        return None
    return (last_value - first_value) / days


def trend_direction(slope: float | None) -> str | None:
    if slope is None:
        return None
    if slope > 0.001:
        return 'up'
    if slope < -0.001:
        return 'down'
    return 'flat'
