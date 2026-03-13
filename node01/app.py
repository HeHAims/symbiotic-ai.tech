"""Flask API for CMIS Node_01 governance and inference routing."""

from __future__ import annotations

import os
from typing import Any

import requests
from flask import Flask, jsonify, request, send_from_directory

from chimera_engine_production import build_forensic_event, evaluate_prompt, persist_event

app = Flask(__name__)

OPENAPI_DOC: dict[str, Any] = {
    "openapi": "3.0.3",
    "info": {
        "title": "CMIS Governance API",
        "version": "1.0.0",
        "description": "Deterministic governance interceptor for Symbiotic Node_01",
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "responses": {"200": {"description": "Service healthy"}},
            }
        },
        "/cmis": {
            "post": {
                "summary": "Evaluate governance and route inference",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["input"],
                                "properties": {
                                    "input": {"type": "string"},
                                    "mode": {"type": "string", "default": "governance"},
                                    "language": {"type": "string", "default": "en"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Governance decision returned"},
                    "400": {"description": "Invalid request"},
                },
            }
        },
    },
}


def _forward_to_upstream(payload: dict[str, Any]) -> dict[str, Any]:
    upstream_url = os.getenv("UPSTREAM_CMIS_URL")
    foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT", "").strip().rstrip("/")
    foundry_path = os.getenv("FOUNDRY_PATH", "").strip().lstrip("/")

    if not upstream_url and foundry_project_endpoint:
        upstream_url = f"{foundry_project_endpoint}/{foundry_path}" if foundry_path else foundry_project_endpoint

    if not upstream_url:
        return {
            "message": "Governance ALLOW: upstream endpoint not configured; returning local decision.",
            "upstream": "not_configured",
        }

    is_foundry_project = ".services.ai.azure.com/api/projects/" in upstream_url

    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("UPSTREAM_CMIS_KEY") or os.getenv("FOUNDRY_API_KEY")
    if api_key:
        headers["api-key" if is_foundry_project else "x-api-key"] = api_key

    bearer_token = os.getenv("UPSTREAM_BEARER_TOKEN", "").strip()
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    request_payload = payload
    foundry_chat_model = os.getenv("FOUNDRY_CHAT_MODEL", "").strip()
    if is_foundry_project and foundry_chat_model:
        # Optional payload mapping for Foundry chat routes.
        request_payload = {
            "model": foundry_chat_model,
            "messages": [{"role": "user", "content": payload.get("input", "")}],
        }

    response = requests.post(upstream_url, json=request_payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json() if response.headers.get("content-type", "").startswith("application/json") else {"text": response.text}


@app.get("/")
def root() -> Any:
    return send_from_directory(".", "index.html")


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok", "service": "cmis-node-01", "evidence_status": "v1.4-Evidence-Frozen"})


@app.get("/openapi.json")
def openapi() -> Any:
    return jsonify(OPENAPI_DOC)


@app.post("/cmis")
def cmis() -> Any:
    body = request.get_json(silent=True) or {}
    prompt = (body.get("input") or "").strip()
    mode = (body.get("mode") or "governance").strip()

    if not prompt:
        return jsonify({"error": "Missing required field: input"}), 400

    decision = evaluate_prompt(prompt)

    if decision.status == "REFUSE":
        response_payload = {
            "decision": "REFUSE",
            "reason": decision.reason,
            "trace_id": decision.trace_id,
            "score": decision.score,
        }
        event = build_forensic_event(prompt, mode, decision, response_payload)
        storage = persist_event(event)
        return jsonify({**response_payload, "audit_backend": storage["backend"], "audit_location": storage["location"]}), 200

    try:
        upstream_payload = {
            "input": prompt,
            "mode": mode,
            "language": body.get("language", "en"),
        }
        model_response = _forward_to_upstream(upstream_payload)
        response_payload = {
            "decision": "ALLOW",
            "reason": decision.reason,
            "trace_id": decision.trace_id,
            "score": decision.score,
            "model_response": model_response,
        }
    except requests.RequestException as exc:
        response_payload = {
            "decision": "ALLOW_MODEL_ERROR",
            "reason": f"Governance passed; upstream call failed: {exc}",
            "trace_id": decision.trace_id,
            "score": decision.score,
        }

    event = build_forensic_event(prompt, mode, decision, response_payload)
    storage = persist_event(event)
    return jsonify({**response_payload, "audit_backend": storage["backend"], "audit_location": storage["location"]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=False)
