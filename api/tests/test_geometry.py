from app.services.geometry import polygon_area_hectares


def test_polygon_area_hectares_is_positive() -> None:
    geom = {
        'type': 'Polygon',
        'coordinates': [
            [
                [174.75, -36.85],
                [174.752, -36.85],
                [174.752, -36.848],
                [174.75, -36.848],
                [174.75, -36.85],
            ]
        ],
    }

    area = polygon_area_hectares(geom)
    assert area > 0.0
