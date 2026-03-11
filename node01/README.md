# Symbiotic Node_01 Deploy

Production scaffold for CMIS governance interception on Azure App Service.

## What this repo now provides
- Deterministic governance interceptor (`chimera_engine_production.py`)
- Live API service (`app.py`) with endpoints:
  - `POST /cmis`
  - `GET /health`
  - `GET /openapi.json`
- Forensic event persistence:
  - Azure Cosmos DB when configured
  - local JSON fallback in `evidence_reports/`
- UI shell (`index.html`) wired to call `/cmis`
- CI pipeline (`.github/workflows/ci.yml`) for compile, tests, and hash verification

## Environment variables
- `PORT` (default `8000`)
- `CMIS_THRESHOLD` (default `0.80`)
- `UPSTREAM_CMIS_URL` (optional upstream inference endpoint)
- `UPSTREAM_CMIS_KEY` (optional API key)
- `COSMOS_ENDPOINT` (optional)
- `COSMOS_KEY` (optional)
- `COSMOS_DATABASE` (default `cmis`)
- `COSMOS_CONTAINER` (default `audit_events`)

## Run locally
```bash
python -m pip install -r requirements.txt
python app.py
```

## Verify deterministic evidence
```bash
python chimera_engine_production.py --verify-hash
```

## Test suite
```bash
pytest -q
```

## Sample request
```bash
curl -X POST http://localhost:8000/cmis \
  -H "Content-Type: application/json" \
  -d '{"input":"Classify risk for medical protocol X","mode":"governance"}'
```
