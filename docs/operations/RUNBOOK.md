# Operations Runbook

This runbook supports day-to-day operation of TERRA in dev-facing environments.

## Service Inventory

- `api`: FastAPI service
- `worker`: Celery worker
- `scheduler`: Celery beat
- `postgres`: primary datastore
- `redis`: broker/cache
- `web`: frontend

## Start/Stop

Start all:

```bash
cd infra
docker compose up -d --build
```

Stop all:

```bash
cd infra
docker compose down
```

## Health Checks

API health:

```bash
curl -s http://localhost:8000/api/v1/health
```

List farms:

```bash
curl -s http://localhost:8000/api/v1/farms
```

## Trigger End-to-End Pipeline

```bash
FARM_ID="<farm_id>"
curl -s -X POST "http://localhost:8000/api/v1/farms/${FARM_ID}/jobs/ingest"
```

Verify output:

```bash
curl -s "http://localhost:8000/api/v1/farms/${FARM_ID}/observations/dates"
curl -s "http://localhost:8000/api/v1/farms/${FARM_ID}/recommendations/latest"
curl -s "http://localhost:8000/api/v1/jobs/runs?farm_id=${FARM_ID}"
```

## Common Incidents

### API is up but map has no paddock colors

Checks:

1. Run ingest job for selected farm.
2. Confirm observations exist for at least one date.
3. Ensure frontend selected date matches available date list.

### Weather endpoint returns empty

Checks:

1. Verify farm exists.
2. Trigger ingest (this fetches weather).
3. Validate OpenWeather key or fallback behavior.

### Worker appears idle

Checks:

1. Verify `worker` and `redis` containers are running.
2. Check worker logs for broker connection issues.
3. Confirm same `REDIS_URL` across API/worker/scheduler.

## Logs

Tail API logs:

```bash
cd infra
docker compose logs -f api
```

Tail worker logs:

```bash
cd infra
docker compose logs -f worker scheduler
```

## Data Reset (Local Only)

Destructive local reset:

```bash
cd infra
docker compose down -v
docker compose up -d --build
```

This removes Postgres volume and all local data.

## Release Verification Checklist

1. `GET /api/v1/health` returns success.
2. Demo farm is present or can be created.
3. Ingest job succeeds.
4. Observation dates are returned.
5. Latest recommendation endpoint returns data.
6. UI loads dashboard and map page.
