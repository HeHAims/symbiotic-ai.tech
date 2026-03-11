# Symbiotic AI: Cognitive Governance Infrastructure
Deterministic Layer for Institutional AI

- Live Deployment: `https://www.symbiotic-ai.tech`
- Evidence Status: `v1.4-Evidence-Frozen` (February 2, 2026)
- Audit Score: `96/96` (CGB-1 Benchmark)

## Architecture: Decision-Before-Generation
Symbiotic AI is not a chatbot. It is a deterministic governance envelope that intercepts prompts and applies a mathematical constitutional freeze before model inference.

### Multi-Cloud Nervous System
- Foundry (Azure Node): Deployed in `eastus2`. Hosts PRIORGATE inference and `POST /cmis`.
- Council (Amazon Nova Node): Uses AHKSZ-35 to run multi-perspective reasoning (Aristotle, Hume, Kahneman, Schopenhauer, Z-Warrior) for high-stakes decisions.
- Logic (CMIS): Operates on symbolic equation `p = Sum(v_i * e^(i*theta_i) * x_i) + a` to enforce stable, non-drifting behavior.

## Node_01 Deployment Architecture
- Lightweight Flask/Gunicorn scaffold prepared for Azure App Service.
- `app.py` and `chimera_engine_production.py` act as CMIS interceptor hooks between Azure ingress and PRIORGATE decision logic.
- `web.config` provides App Service default document routing and availability posture.
- `requirements.txt` captures planned integration path:
  - `boto3` (Amazon Nova)
  - `azure-cosmos` (forensic audit persistence)
  - `flask`/`gunicorn` (API delivery)

## API Surface
- OpenAPI / Swagger: `https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/docs`
- CMIS Endpoint: `POST https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/cmis`
- Health Endpoint: `GET https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/health`

## Validation and Evidence (CGB-1)
As of the February 2, 2026 evidence run:
- Determinism: `100%` identical-input SHA-256 logic hashes
- Accuracy: `96/96` on CGB-1 benchmark (policy/risk/incident classification)
- Safety Suite: `28/28` tests passing (zero regression)

## System Readiness
| Component | Status | Source of Truth |
|---|---|---|
| Logic (PRIORGATE) | Verified (96/96) | Kaggle: CMIS-Decision |
| Deployment (Node_01) | Active Scaffold | `app.py` / `chimera_engine_production.py` |
| Infrastructure | Deployed | Azure: `rg-SymbioticAI` |
| Governance | Frozen | CMIS Governance Brief (February 2, 2026) |

## Technical Links
| Resource | Purpose | Source / Link |
|---|---|---|
| Main Web Portal | Public interface | `https://symbiotic-ai.tech` |
| API Documentation | Swagger / OpenAPI | `https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/docs` |
| Benchmark Hub | Reproducible proof | Kaggle: CMIS-Decision Task |
| Governance Brief | Institutional PDF | February 2, 2026 brief |
| Nova Council Node | Multi-perspective reasoning engine | `https://github.com/HeHAims/Amazon_Nova_AI_Hackathon` |

## Repository Structure
- `priorgate_core/`: deterministic safety scoring and governance logic
- `phase_lab/`: phase-geometry and organic-dynamics validation
- `infrastructure/`: Azure App Service and AWS SAM deployment scaffolds
- `evidence_reports/`: forensic JSON audit dumps

## IP Boundary
- Proprietary IP: Context Fabric (Bayesian Emotion Engine), symbolic equation logic, Hero Council weighting algorithm
- Implementation: Python 3.10, FastAPI, Azure Cosmos DB, Amazon Bedrock (Nova Lite/Pro)
- Model agnostic governance layer: can govern Gemma-2b, GPT-4o, Claude 3.5

## Quick Start (Partner Validation)
```bash
# 1) Clone governance node
git clone https://github.com/HeHAims/Symbiotic-Core.git

# 2) Verify frozen logic
python ./priorgate_core/engine.py --verify-hash

# 3) Call governance gateway
curl -X POST https://www.symbiotic-ai.tech/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":"Classify risk for medical protocol X","mode":"governance"}'
