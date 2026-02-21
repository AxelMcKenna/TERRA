# API Documentation

Base URL (local): `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs`

## API Conventions

- Content type: `application/json`
- Success shape:

```json
{
  "data": {},
  "meta": {}
}
```

- Errors: currently FastAPI default error responses are returned for validation/not-found cases.

## Health

### GET `/health`

Returns API liveness.

## Farms

### GET `/farms`

List farms.

### POST `/farms`

Create farm.

Request body:

```json
{
  "name": "North Block",
  "description": "Dairy platform",
  "latitude": -36.85,
  "longitude": 174.76
}
```

### GET `/farms/{farm_id}`

Get single farm.

### PATCH `/farms/{farm_id}`

Partial update.

### DELETE `/farms/{farm_id}`

Delete farm and related child records.

## Paddocks

### GET `/farms/{farm_id}/paddocks`

List paddocks for farm.

### POST `/farms/{farm_id}/paddocks`

Create paddock from GeoJSON polygon.

Request body:

```json
{
  "name": "Paddock 1",
  "geom_geojson": {
    "type": "Polygon",
    "coordinates": [[[174.75, -36.85], [174.752, -36.85], [174.752, -36.848], [174.75, -36.848], [174.75, -36.85]]]
  }
}
```

### PATCH `/paddocks/{paddock_id}`

Update paddock name and/or geometry.

### DELETE `/paddocks/{paddock_id}`

Delete paddock.

### POST `/farms/{farm_id}/paddocks/import`

Bulk import paddocks from GeoJSON FeatureCollection.

Request body:

```json
{
  "feature_collection": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": {"name": "Imported A"},
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[174.75, -36.85], [174.752, -36.85], [174.752, -36.848], [174.75, -36.848], [174.75, -36.85]]]
        }
      }
    ]
  }
}
```

Response includes per-feature failures in `meta.failures`.

## Observations

### GET `/farms/{farm_id}/observations/dates`

Returns available NDVI observation dates.

### GET `/farms/{farm_id}/observations?date=YYYY-MM-DD`

Returns paddock metrics for selected date:

- `ndvi_mean`
- `bucket`
- `quality_flag`
- `cloud_pct`

### GET `/paddocks/{paddock_id}/observations`

Returns paddock time series and trend metadata:

- `points[]`
- `slope`
- `direction`

## Weather

### GET `/farms/{farm_id}/weather/forecast`

Returns up to 7 daily forecast entries.

- source may be `openweather` or `synthetic`

## Recommendations

### GET `/farms/{farm_id}/recommendations/latest`

Returns most recent recommendation set for farm.

### GET `/farms/{farm_id}/recommendations?week_start=YYYY-MM-DD`

Returns recommendation set for specific week start.

### POST `/farms/{farm_id}/recommendations/generate`

Generates recommendation set on demand.

Optional request body:

```json
{
  "week_start": "2026-02-16"
}
```

## Jobs and Operations

### POST `/farms/{farm_id}/jobs/ingest`

Runs pipeline sequence:

1. scene ingest
2. NDVI aggregation
3. weather fetch
4. recommendation generation

### GET `/jobs/runs?farm_id=<optional>`

Returns recent `job_runs` rows for visibility/debugging.

## Recommendation Rules Summary

Current precedence order:

1. `LOW_DATA`
2. `AVOID_WATERLOG`
3. `MONITOR_STRESS`
4. `GRAZE_NOW`

Threshold values are loaded from `config_thresholds` and seeded by default.

## Important MVP Notes

- No authentication is enabled.
- Endpoints are open for development use.
- NDVI values are synthetic placeholders until real satellite ingest is connected.
