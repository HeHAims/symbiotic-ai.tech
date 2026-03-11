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
    if not upstream_url:
        return {
            "message": "Governance ALLOW: upstream endpoint not configured; returning local decision.",
            "upstream": "not_configured",
        }

    headers = {"Content-Type": "application/json"}
    api_key = os.getenv("UPSTREAM_CMIS_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    response = requests.post(upstream_url, json=payload, headers=headers, timeout=30)
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
