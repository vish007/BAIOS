# BAIOS (Bank Agentic Intelligence Operating System)

Enterprise OpenClaw-style **Agentic AI Control Tower** for banks.

## Production Hardening Implemented

- Real provider adapters over HTTP for:
  - Llama Vision service endpoint
  - OpenAI API
  - Anthropic Claude API
- Reliability controls: retry budget + timeout + provider circuit breaker.
- PostgreSQL persistence via SQLAlchemy + Alembic migration bootstrap.
- OIDC/JWT-style authn + RBAC/ABAC authorization checks on protected routes.
- Immutable audit logs (hash chained entries) and event bus abstraction (Memory/NATS).
- Maker/checker queue for low-confidence workflow runs.
- Hardened Kubernetes manifests (resources, probes, HPA, PDB, NetworkPolicy, secret refs).
- Expanded telemetry (OTel tracing + Prometheus counters/histograms hooks).
- Test pyramid baseline: unit + API/security + integration + load placeholder.

## Repository Layout

- `backend/` — FastAPI application layer, orchestration, model routing, policy engine, auth, persistence
- `frontend/` — BAOS cockpit (Next.js)
- `k8s/` — hardened deployment/service manifests and policies
- `docs/` — architecture and technical analysis

## Quick Start

```bash
docker compose up
```

- Backend API: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## Database Migration

```bash
cd backend
alembic upgrade head
```

## Security Note

This repository uses HS256 local dev tokens for demonstrability. For production, wire OIDC JWKS validation, KMS/Vault-managed secrets, and mTLS service mesh identity.

## Documentation

- [BAOS Complete Technical Analysis](docs/baos-technical-analysis.md)
