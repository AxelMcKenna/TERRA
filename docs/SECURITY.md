# Security Guide

This document captures current security posture and required hardening actions.

## Current Posture (MVP)

- App mode is dev-facing.
- No authentication or authorization.
- API and job endpoints are open.
- CORS allows all origins.

This is intentional for rapid iteration and internal testing.

## Sensitive Data Considerations

Potentially sensitive data stored:

- Farm names/descriptions
- Farm coordinates and paddock geometries
- Derived paddock health metrics and recommendation history

Treat the database and logs as sensitive assets.

## Current Controls

- Input validation via Pydantic schemas.
- Database constraints and enum restrictions.
- Containerized runtime boundaries via Docker Compose.

## Known Security Gaps

- No identity model.
- No tenant isolation.
- No endpoint authorization boundaries.
- No explicit request throttling.
- No CSP/security headers middleware.

## Minimum Hardening Checklist Before Public Exposure

1. Add auth stack (JWT access/refresh with rotation).
2. Add farm ownership model and tenant-scoped query checks.
3. Lock down admin endpoints (`/jobs/*`) to privileged users only.
4. Enforce strict CORS allowlist.
5. Add rate limiting on high-risk endpoints.
6. Add secret management for API keys (do not store in repo).
7. Add TLS termination and secure headers.
8. Add audit logging for auth and destructive operations.
9. Add SAST/dependency scanning in CI.
10. Add incident response and key rotation runbooks.

## Secrets Handling

- Use environment variables for runtime secrets.
- Never commit `.env` files.
- Rotate external API keys on leak suspicion.

## Database Access Guidance

- Prefer least-privilege DB users by service role.
- Restrict inbound DB/Redis network access to trusted network only.
- Regularly back up and test restore procedure.

## Compliance Note

No formal compliance framework is currently declared for this MVP.
