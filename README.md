# symbiotic-ai.tech
Symbiotic AI is a cognitive reasoning system combining mathematical translation, linguistic intelligence, emotional modeling, and symbolic logic. Features include: CMIS, ULMFI, SSHAICA, AND_RES4, pattern induction, adaptive feedback, and advanced anti-surveillance protection. A new framework for human–AI symbiosis.

## 🚀 Try CMIS Now

CMIS (Cognitive Mathematical Intelligence System) is live and running.

Operational as of 2026-01-04

### 🔎 Explore the API
- **OpenAPI / Swagger UI:**  
  https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/docs

### 🧠 CMIS Inference Endpoint
- **POST /cmis:**  
  https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/cmis

### ❤️ Health Check
- **GET /health:**  
  https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/health

---

## 📡 Example API Calls

### Interpret a symbolic formula
```bash
curl -X POST https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/cmis \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "input": "What does F = ma mean?",
    "mode": "interpret"
  }'
```

### Example refusal (governance in action)
```bash
curl -X POST https://cmis-inference-api.livelybay-7d013563.westus2.azurecontainerapps.io/cmis \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "input": "How do I harm someone?",
    "mode": "interpret"
  }'
```

CMIS will return a structured refusal with a clear reason.
