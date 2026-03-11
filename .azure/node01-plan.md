# Azure Preparation Plan

## Project
- Name: Symbiotic Node_01 Deployment
- Mode: MODIFY (upgrade scaffold to production-ready governance API)
- Date: 2026-03-11

## Requirements
- Provide deterministic governance gate before model inference
- Expose Azure-ready HTTP API (`POST /cmis`, `GET /health`, `GET /openapi.json`)
- Persist forensic events to Azure Cosmos DB with local fallback
- Preserve static UI and connect it to live API
- Add CI checks and regression tests

## Architecture Decisions
- Runtime: Python Flask + Gunicorn
- Governance engine: `chimera_engine_production.py`
- API app: `app.py`
- Forensic persistence:
  - Primary: Azure Cosmos DB (`azure-cosmos`)
  - Fallback: local JSON files in `evidence_reports/`
- Deployment target: Azure App Service (Windows/Linux)

## Execution Steps
1. Implement deterministic routing and trace generation logic
2. Implement API endpoints and OpenAPI contract
3. Implement Cosmos persistence and local fallback
4. Add frontend request wiring for `/cmis`
5. Add tests and CI workflow
6. Document runbook and verification commands

## Validation Criteria
- `pytest -q` passes
- Harmful prompt returns `REFUSE`
- Safe prompt returns `ALLOW`
- Trace IDs deterministic for fixed input
- Forensic event persisted (Cosmos or local)
