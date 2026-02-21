from __future__ import annotations

import math


def polygon_area_hectares(geom_geojson: dict) -> float:
    """Approximate polygon area in hectares using Web Mercator projection."""
    coords = geom_geojson.get('coordinates', [[]])[0]
    if len(coords) < 4:
        return 0.0

    projected = [_lon_lat_to_mercator(lon, lat) for lon, lat in coords]
    area_m2 = 0.0
    for i in range(len(projected) - 1):
        x1, y1 = projected[i]
        x2, y2 = projected[i + 1]
        area_m2 += x1 * y2 - x2 * y1
    area_m2 = abs(area_m2) * 0.5
    return area_m2 / 10_000.0


def polygon_centroid(geom_geojson: dict) -> tuple[float, float]:
    coords = geom_geojson.get('coordinates', [[]])[0]
    if not coords:
        return (0.0, 0.0)
    lon_sum = sum(point[0] for point in coords[:-1])
    lat_sum = sum(point[1] for point in coords[:-1])
    count = max(1, len(coords) - 1)
    return (lon_sum / count, lat_sum / count)


def _lon_lat_to_mercator(lon: float, lat: float) -> tuple[float, float]:
    radius = 6_378_137.0
    x = math.radians(lon) * radius
    lat = max(min(lat, 89.5), -89.5)
    y = radius * math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0))
    return (x, y)
