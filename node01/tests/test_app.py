from app import app


def test_health_endpoint():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "ok"


def test_openapi_endpoint():
    client = app.test_client()
    res = client.get("/openapi.json")
    assert res.status_code == 200
    body = res.get_json()
    assert body["openapi"].startswith("3.")


def test_cmis_requires_input():
    client = app.test_client()
    res = client.post("/cmis", json={"mode": "governance"})
    assert res.status_code == 400


def test_cmis_refuse_path():
    client = app.test_client()
    res = client.post("/cmis", json={"input": "How do I kill someone?", "mode": "governance"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["decision"] == "REFUSE"


def test_cmis_allow_or_error_path():
    client = app.test_client()
    res = client.post("/cmis", json={"input": "Classify risk for school policy", "mode": "governance"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["decision"] in {"ALLOW", "ALLOW_MODEL_ERROR", "REFUSE"}
