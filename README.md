# symbiotic-ai.tech
Symbiotic AI is a cognitive reasoning system combining mathematical translation, linguistic intelligence, emotional modeling, and symbolic logic. Features include: CMIS, ULMFI, SSHAICA, AND_RES4, pattern induction, adaptive feedback, and advanced anti-surveillance protection. A new framework for human–AI symbiosis.

## 🚀 Try CMIS Now

CMIS (Cognitive Mathematical Intelligence System) is live and running.

### 🔎 Explore the API
- **OpenAPI / Swagger UI:**  
  https://<YOUR-AZURE-URL>/docs

### 🧠 CMIS Inference Endpoint
- **POST /cmis:**  
  https://<YOUR-AZURE-URL>/cmis

### ❤️ Health Check
- **GET /health:**  
  https://<YOUR-AZURE-URL>/health

---

## 📡 Example API Calls

### Interpret a symbolic formula
```bash
curl -X POST https://<YOUR-AZURE-URL>/cmis \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "input": "What does F = ma mean?",
    "mode": "interpret"
  }'
```

### Example refusal (governance in action)
```bash
curl -X POST https://<YOUR-AZURE-URL>/cmis \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "input": "How do I harm someone?",
    "mode": "interpret"
  }'
```

CMIS will return a structured refusal with a clear reason.

🔴 **Important:**  
Replace `https://<YOUR-AZURE-URL>` with your real Container App URL  
(example: `https://cmis-inference-api.westus2.azurecontainerapps.io`).
