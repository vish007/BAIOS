# BAIOS (Bank Agentic Intelligence Operating System)

Enterprise OpenClaw-style **Agentic AI Control Tower** for banks.

## Stack Delivered

- **Backend**: FastAPI + Python microservice architecture
- **Frontend**: Next.js cockpit UI
- **Model Providers**:
  - Llama Vision (default, private-cloud friendly)
  - OpenAI (configurable)
  - Claude (configurable)
- **Observability**: OpenTelemetry bootstrap included
- **Deployment**: Docker Compose (local), Kubernetes manifests (starter)

## Repository Layout

- `backend/` — FastAPI application layer, orchestration, model routing, policy engine
- `frontend/` — BAOS cockpit (Next.js)
- `k8s/` — deployment/service manifests for backend and frontend
- `docs/` — architecture and technical analysis

## Quick Start

### 1) Run locally with Docker Compose

```bash
docker compose up
```

- Backend API: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

### 2) Run backend directly

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 3) Run frontend directly

```bash
cd frontend
npm install
npm run dev
```

## Key API Endpoints

- `GET /api/v1/health`
- `POST /api/v1/agents`
- `POST /api/v1/workflow-runs`

## Provider Configuration

Set in `backend/.env`:

- `DEFAULT_PROVIDER=llama_vision|openai|claude`
- `OPENAI_API_KEY=...`
- `CLAUDE_API_KEY=...`

Provider routing is implemented in `backend/app/services/model_router.py`.

## Documentation

- [BAOS Complete Technical Analysis](docs/baos-technical-analysis.md)
