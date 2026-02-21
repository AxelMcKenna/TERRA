# Deployment Guide

This guide describes deploying TERRA using a single VM and Docker Compose.

## Scope

- Current target: controlled environment deployment for dev-facing MVP.
- Not suitable for public internet exposure in current no-auth state.

## Prerequisites

- Linux VM with Docker Engine + Docker Compose plugin
- DNS and TLS termination plan (Nginx/Caddy/Cloud load balancer)
- Access to container registry or source checkout on host

## Required Configuration

Set environment variables before bringing up stack:

- `OPENWEATHER_API_KEY` (optional but recommended)
- `VITE_MAPBOX_TOKEN` (optional for map rendering)

Current compose file: `infra/docker-compose.yml`

## Deployment Steps

### 1) Clone and checkout release commit

```bash
git clone <repo-url>
cd farm-intelligence
git checkout <commit-or-tag>
```

### 2) Export environment variables

```bash
export OPENWEATHER_API_KEY="<key>"
export VITE_MAPBOX_TOKEN="<token>"
```

### 3) Build and run

```bash
cd infra
docker compose up -d --build
```

### 4) Verify

```bash
curl -s http://127.0.0.1:8000/api/v1/health
```

Open UI:

- `http://<host>:5173`

## Updating to a New Version

```bash
git fetch --all
git checkout <new-commit-or-tag>
cd infra
docker compose up -d --build
```

## Rollback

```bash
git checkout <previous-known-good-commit>
cd infra
docker compose up -d --build
```

## Persistence and Backups

Postgres data is persisted via Docker volume `pg_data`.

Backup example:

```bash
docker exec -t infra-postgres-1 pg_dump -U postgres farm_intelligence > backup.sql
```

Restore example:

```bash
cat backup.sql | docker exec -i infra-postgres-1 psql -U postgres -d farm_intelligence
```

## Production Hardening Required Before Public Launch

- Add authentication and authorization.
- Restrict exposed endpoints and admin operations.
- Add TLS, WAF/rate limiting, and secret management.
- Add observability stack (metrics, tracing, alerting).
- Implement real satellite ingest and validation checks.
