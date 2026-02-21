# TERRA Documentation

This directory contains implementation and operations documentation for the TERRA dev-facing MVP.

## Documentation Index

- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Guide](./SECURITY.md)
- [API Documentation](./api/README.md)
- [Operations Runbook](./operations/RUNBOOK.md)

## Current Product State

- App mode: dev-facing MVP.
- Authentication: intentionally not implemented yet.
- NDVI ingest: deterministic synthetic values are used for end-to-end validation.
- Intended use: local development and controlled non-public environments.

## Stack

- Backend: FastAPI + SQLAlchemy + Celery
- Frontend: React + Vite + Mapbox GL
- Data stores: PostgreSQL (PostGIS image), Redis
- Runtime: Docker Compose

## Canonical Entry Points

- Root overview: `README.md`
- API app entrypoint: `api/app/main.py`
- API router root: `api/app/api/v1/router.py`
- Worker tasks: `api/app/workers/tasks.py`
- Local infra: `infra/docker-compose.yml`

## Conventions

- API base prefix: `/api/v1`
- API success envelope: `{ "data": ..., "meta": ... }`
- ID type: UUID strings
- Timezone handling: UTC timestamps persisted by backend

## Known Gaps (Planned)

- Auth and tenant isolation
- Real satellite/STAC pipeline in place of synthetic NDVI generation
- Production-grade CI/CD and deployment manifests
- Alerting/monitoring dashboards
