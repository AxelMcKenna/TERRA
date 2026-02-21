# Setup Guide

This guide covers local setup for TERRA in dev-facing MVP mode.

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 20+
- GNU-compatible shell (bash/zsh)

## Repository Structure

- `api/` backend service
- `web/` frontend service
- `infra/` local stack orchestration

## Environment Files

Copy templates as needed:

- `api/.env.example`
- `web/.env.example`

Optional keys:

- `OPENWEATHER_API_KEY`: enables live weather data.
- `VITE_MAPBOX_TOKEN`: enables interactive map rendering.

If omitted:

- weather uses synthetic fallback data
- map view shows fallback panel

## Quickstart (All Services)

```bash
cd infra
docker compose up --build
```

Expected endpoints:

- Web: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`
- API base: `http://localhost:8000/api/v1`

## Local-Only Service Startup

### 1) Start infrastructure dependencies

```bash
cd infra
docker compose up -d postgres redis
```

### 2) Run backend API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Run worker

```bash
cd api
source .venv/bin/activate
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

### 4) Run scheduler

```bash
cd api
source .venv/bin/activate
celery -A app.workers.celery_app.celery_app beat --loglevel=info
```

### 5) Run frontend

```bash
cd web
npm install
npm run dev
```

## Data Seeding Behavior

On API startup, if no farms exist and `SEED_DEMO_DATA=true`:

- one demo farm is created
- three demo paddocks are created
- default recommendation thresholds are inserted

Relevant service: `api/app/services/seed.py`

## Sanity Checks

### Health

```bash
curl -s http://localhost:8000/api/v1/health
```

### Farms

```bash
curl -s http://localhost:8000/api/v1/farms
```

### Run pipeline for seeded farm

```bash
FARM_ID="<farm_id_from_previous_response>"
curl -s -X POST "http://localhost:8000/api/v1/farms/${FARM_ID}/jobs/ingest"
```

### Confirm observation dates

```bash
curl -s "http://localhost:8000/api/v1/farms/${FARM_ID}/observations/dates"
```

## Running Tests

```bash
cd api
PYTHONPATH=. pytest -q
```

## Troubleshooting

- Map is blank: ensure `VITE_MAPBOX_TOKEN` is set in frontend environment.
- No weather data: if `OPENWEATHER_API_KEY` is not set, synthetic values should still appear.
- Database errors after schema changes: remove local postgres volume and restart stack.
- Worker not picking tasks: confirm Redis is reachable and worker is running with same `REDIS_URL`.
