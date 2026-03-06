# BAOS Developer Architecture Guide: Functional Flow & Skill Extensions

This document is a developer-friendly implementation guide for the current BAOS codebase. It explains:

1. Runtime architecture mapped to code modules.
2. End-to-end functional flow from API request to decision.
3. How to add new business skills such as OCR, Analytics, Voice, PPT, and Excel.
4. Checklists for secure, observable, production-grade extension.

---

## 1) Code-Mapped Architecture Overview

## 1.1 Backend (FastAPI control plane)

### Entrypoint and wiring
- `backend/app/main.py`
  - boots settings
  - configures telemetry
  - registers API routers
  - sets CORS policy
  - initializes DB metadata

### API boundary
- `backend/app/api/routes/health.py` — health probe
- `backend/app/api/routes/agents.py` — agent registration endpoint with RBAC/ABAC + audit
- `backend/app/api/routes/workflows.py` — workflow execution + maker/checker resolution

### Core platform primitives
- `backend/app/core/config.py` — environment settings and runtime budgets
- `backend/app/core/security.py` — JWT decoding + RBAC + ABAC hooks
- `backend/app/core/database.py` — SQLAlchemy engine/session

### Business and orchestration layer
- `backend/app/orchestration/workflow_engine.py` — policy check, model invoke, confidence routing, event publication
- `backend/app/services/policy_engine.py` — policy evaluation
- `backend/app/services/model_router.py` — provider selection
- `backend/app/services/llm_providers.py` — provider adapters (Llama/OpenAI/Claude)
- `backend/app/services/reliability.py` — circuit breaker
- `backend/app/services/event_bus.py` — memory or NATS eventing
- `backend/app/services/audit.py` — immutable-hash audit append

### Persistence
- `backend/app/models.py` — ORM models for agents/workflows/runs/policies/audits/maker-checker
- `backend/alembic/` — migration framework + baseline migration

## 1.2 Frontend (BAOS cockpit)
- `frontend/app/page.tsx` + `frontend/components/dashboard.tsx` provide operator controls to trigger workflow execution and choose model providers.
- `frontend/lib/api.ts` contains typed client-side API integration.

## 1.3 Runtime infra
- `docker-compose.yml` defines local stack with Postgres + NATS + backend + frontend.
- `k8s/` includes deployment templates with resources, probes, PDB, HPA, NetworkPolicy.

---

## 2) Functional Flow (Current Implementation)

## 2.1 Workflow run path
1. User calls `POST /api/v1/workflow-runs` with JWT.
2. Security layer validates JWT and checks `workflow:run` role.
3. Workflow engine evaluates policy constraints.
4. If policy fails:
   - run stored as `blocked_by_policy`
   - violation response returned
   - event published
   - audit log appended
5. If policy passes:
   - model provider resolved (Llama/OpenAI/Claude)
   - provider adapter makes HTTP request with retry/timeout/circuit breaker
   - confidence evaluated
6. If confidence below threshold:
   - status becomes `pending_maker_checker`
   - maker/checker task created
   - escalation event published
7. Workflow run returned to caller and audit record appended.

## 2.2 Maker/checker path
1. Checker calls `POST /api/v1/workflow-runs/maker-checker/{task_id}/resolve`.
2. RBAC verifies `maker_checker:resolve` permission.
3. Task updated with decision + checker ID.
4. Audit log appended.

## 2.3 Agent creation path
1. User calls `POST /api/v1/agents`.
2. RBAC validates `agents:create`; ABAC validates LOB ownership.
3. Agent persisted in DB.
4. Audit record appended.

---

## 3) Skill Model for BAOS (OCR, Analytics, Voice, PPT, Excel)

In BAOS, a "skill" should be modeled as a **tool-capable execution unit** attached to workflows and controlled by policy.

Recommended implementation pattern:
- Skill interface contract (Python protocol/class)
- Skill registry
- Skill invocation service
- Skill telemetry wrapper
- Skill policy gate
- Skill-specific schemas and test suite

### 3.1 Proposed skill package structure

Create:

```text
backend/app/skills/
  __init__.py
  base.py
  registry.py
  ocr_skill.py
  analytics_skill.py
  voice_skill.py
  ppt_skill.py
  excel_skill.py
```

### 3.2 Skill contract (developer-facing)
Each skill should expose:
- `name`
- `version`
- `input_schema`
- `output_schema`
- `execute(context, payload)`
- `healthcheck()`

### 3.3 Skill invocation flow
1. Workflow step requests skill execution.
2. Policy engine checks permission and data classification.
3. Registry resolves skill implementation.
4. Skill executes in bounded timeout.
5. Result stored in run-step output.
6. Metrics + trace span emitted.
7. Audit event appended.

---

## 4) How to Add New Skills (Step-by-Step)

## Step 1: Define the business use-case
For each skill, define:
- objective
- expected input
- expected output
- data sensitivity
- allowed user roles
- failure and fallback strategy

## Step 2: Add skill module
Create `backend/app/skills/<skill>_skill.py` implementing the standard contract.

Examples:
- `ocr_skill.py`: image/pdf ingestion + text extraction + field confidence
- `analytics_skill.py`: KPI computation + anomaly flags + insights summary
- `voice_skill.py`: transcription/TTS pipeline + compliance filtering
- `ppt_skill.py`: deck generation from structured summary templates
- `excel_skill.py`: spreadsheet generation and formula-safe transformations

## Step 3: Register skill
Update `registry.py` to map skill name → implementation class.

## Step 4: Add API or workflow step hook
- Add workflow step types in orchestration config.
- Route step execution through skill invocation service.

## Step 5: Enforce policy and auth controls
- Add policy rules for sensitive inputs (PII/audio/docs).
- Enforce RBAC/ABAC in invocation endpoint.

## Step 6: Add observability
For each skill add:
- latency histogram (`baos_skill_latency_ms{skill=...}`)
- error counter (`baos_skill_errors_total{skill=...,code=...}`)
- trace spans with `skill.name`, `skill.version`, `workflow.run_id`

## Step 7: Add tests
- unit tests for business logic
- API tests for authn/authz
- integration tests for workflow invocation
- negative tests for policy denials
- load tests for throughput/latency

## Step 8: Add runbook + docs
Document in `/docs`:
- dependencies
- rollout plan
- fallback plan
- SLO target and alerts

---

## 5) Skill-Specific Guidance

## 5.1 OCR Skill
- Input: scanned docs/PDF/images.
- Output: extracted text + key-value fields + confidence per field.
- Controls:
  - malware scan before processing
  - document type allowlist
  - PII masking before downstream model calls

## 5.2 Analytics Skill
- Input: structured workflow outputs.
- Output: KPI aggregates, trend stats, anomalies.
- Controls:
  - deterministic calculations
  - versioned KPI definitions
  - explainability notes for every computed metric

## 5.3 Voice Skill
- Input: audio stream/file.
- Output: transcript, sentiment/compliance tags, optional TTS output.
- Controls:
  - audio retention policy
  - profanity/regulated-phrase detector
  - consent and region-based data storage enforcement

## 5.4 PPT Skill
- Input: narrative summary + chart/table payload.
- Output: generated deck (PPTX) with controlled templates.
- Controls:
  - template signing
  - no external image fetching by default
  - classification watermarking

## 5.5 Excel Skill
- Input: tabular datasets + transformation instructions.
- Output: generated workbook (XLSX) with formulas/tables/charts.
- Controls:
  - formula injection safeguards
  - column-level classification enforcement
  - deterministic export metadata

---

## 6) Suggested Backlog to Productize Skill Framework

1. Implement `app/skills/base.py` and `app/skills/registry.py`.
2. Add workflow step model for `skill_call`.
3. Add skill execution telemetry middleware.
4. Add policy bundles for each skill class.
5. Add sandbox execution profile for document/media conversion.
6. Add integration tests per skill type.
7. Add cockpit UI page for skill catalog + enable/disable + versioning.

---

## 7) Developer Checklist Before Merging a New Skill

- [ ] Input/output schema defined and versioned.
- [ ] RBAC/ABAC gates implemented.
- [ ] Policy denials tested.
- [ ] Telemetry metrics + traces emitted.
- [ ] Audit events generated for execution and errors.
- [ ] Retry/timeout budgets and fallback strategy documented.
- [ ] Load test threshold documented.
- [ ] Security review completed.
- [ ] Docs and runbook updated.

---

## 8) Architecture Analysis Notes for Current Codebase

Current implementation already includes solid extension points:
- policy gate before inference in workflow engine.
- provider routing abstraction.
- event bus abstraction.
- immutable audit helper.
- maker/checker queue pattern.

To support richer skills, the main missing piece is a dedicated skill registry and step executor abstraction.
