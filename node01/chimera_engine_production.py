"""Production governance interceptor for CMIS Node_01."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_META = {
    "id": "CMIS-AHK-PROV-001",
    "status": "Evidence Frozen (2026-02-02)",
    "owner": "Symbiotic AI",
    "architecture": "Hybrid Deterministic/Probabilistic Logic Firewall",
}

DEFAULT_THRESHOLD = 0.80
DEFAULT_WEIGHTS = {
    "v": [0.62, 0.38],
    "a": 0.06,
}

RISK_TERMS = {
    "weapon",
    "bomb",
    "harm",
    "kill",
    "explosive",
    "bypass",
    "evade",
    "attack",
    "violent",
    "malware",
}

SAFE_CONTEXT_TERMS = {
    "student",
    "school",
    "education",
    "district",
    "policy",
    "safety",
    "healthcare",
    "government",
    "protocol",
}

BASE_DIR = Path(__file__).resolve().parent
WEIGHTS_PATH = BASE_DIR / "weights.json"
LOCAL_EVIDENCE_DIR = BASE_DIR / "evidence_reports"


@dataclass(frozen=True)
class GovernanceDecision:
    status: str
    score: float
    trace_id: str
    timestamp: str
    features: list[float]
    reason: str


def _load_weights() -> dict[str, Any]:
    if WEIGHTS_PATH.exists():
        with WEIGHTS_PATH.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
        if "v" in data and "a" in data:
            return data
    return DEFAULT_WEIGHTS


def _analyze_context(user_prompt: str, vector_size: int) -> list[float]:
    prompt = user_prompt.lower()
    tokens = set(prompt.replace(".", " ").replace(",", " ").split())

    risk_hits = len(tokens & RISK_TERMS)
    safe_hits = len(tokens & SAFE_CONTEXT_TERMS)
    length_factor = min(len(user_prompt) / 220.0, 1.0)

    x = [
        round(max(0.0, 1.0 - (risk_hits * 0.25)), 4),
        round(min(1.0, 0.35 + (safe_hits * 0.15) + (length_factor * 0.2)), 4),
    ]

    if vector_size > len(x):
        x.extend([0.5] * (vector_size - len(x)))
    return x[:vector_size]


def _calculate_logic_score(x: list[float], v: list[float], a: float) -> float:
    return round(sum(vi * xi for vi, xi in zip(v, x)) + a, 4)


def generate_trace_id(timestamp: str, prompt: str, score: float) -> str:
    raw = f"{timestamp}|{prompt}|{score}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_hash(prompt: str, timestamp: str, score: float, expected_hash: str) -> bool:
    return generate_trace_id(timestamp, prompt, score) == expected_hash


def evaluate_prompt(user_prompt: str, *, threshold: float | None = None) -> GovernanceDecision:
    weights = _load_weights()
    v = [float(x) for x in weights["v"]]
    a = float(weights["a"])

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    x = _analyze_context(user_prompt, len(v))
    score = _calculate_logic_score(x, v, a)
    used_threshold = threshold if threshold is not None else float(os.getenv("CMIS_THRESHOLD", DEFAULT_THRESHOLD))

    if score >= used_threshold:
        status = "ALLOW"
        reason = "Prompt is within institutional safety envelope"
    else:
        status = "REFUSE"
        reason = "Prompt violates institutional safety envelope"

    trace_id = generate_trace_id(timestamp, user_prompt, score)
    return GovernanceDecision(
        status=status,
        score=score,
        trace_id=trace_id,
        timestamp=timestamp,
        features=x,
        reason=reason,
    )


def build_forensic_event(prompt: str, mode: str, decision: GovernanceDecision, response_payload: dict[str, Any]) -> dict[str, Any]:
    weights = _load_weights()
    return {
        "project_meta": PROJECT_META,
        "timestamp": decision.timestamp,
        "trace_id": decision.trace_id,
        "threshold": float(os.getenv("CMIS_THRESHOLD", DEFAULT_THRESHOLD)),
        "logic": {
            "formula": "p = vx + a",
            "v": weights["v"],
            "x": decision.features,
            "a": weights["a"],
            "p": decision.score,
        },
        "status": decision.status,
        "reason": decision.reason,
        "mode": mode,
        "prompt": prompt,
        "response": response_payload,
    }


def _save_local(event: dict[str, Any]) -> str:
    LOCAL_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = LOCAL_EVIDENCE_DIR / f"{event['trace_id']}.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(event, handle, indent=2)
    return out_path.as_posix()


def persist_event(event: dict[str, Any]) -> dict[str, str]:
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE", "cmis")
    container_name = os.getenv("COSMOS_CONTAINER", "audit_events")

    if not endpoint or not key:
        return {"backend": "local_json", "location": _save_local(event)}

    try:
        from azure.cosmos import CosmosClient, PartitionKey  # type: ignore

        client = CosmosClient(endpoint, credential=key)
        database = client.create_database_if_not_exists(id=database_name)
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/status"),
            offer_throughput=400,
        )

        item = {
            "id": event["trace_id"],
            **event,
        }
        container.upsert_item(item)
        return {"backend": "azure_cosmos", "location": f"{database_name}/{container_name}/{event['trace_id']}"}
    except Exception:
        return {"backend": "local_json", "location": _save_local(event)}


def _demo_score(prompt: str) -> float:
    # Deterministic helper for manual verification commands.
    vector = _analyze_context(prompt, 2)
    return _calculate_logic_score(vector, DEFAULT_WEIGHTS["v"], float(DEFAULT_WEIGHTS["a"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="CMIS Chimera production governance engine")
    parser.add_argument("--verify-hash", action="store_true", help="Verify deterministic trace generation with fixed values")
    parser.add_argument("--prompt", type=str, default="Classify risk for medical protocol X")
    args = parser.parse_args()

    if args.verify_hash:
        fixed_ts = "2026-02-02T00:00:00Z"
        score = _demo_score(args.prompt)
        trace_id = generate_trace_id(fixed_ts, args.prompt, score)
        ok = verify_hash(args.prompt, fixed_ts, score, trace_id)
        result = {
            "verified": ok,
            "timestamp": fixed_ts,
            "prompt": args.prompt,
            "score": score,
            "trace_id": trace_id,
        }
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if ok else 1)

    decision = evaluate_prompt(args.prompt)
    print(
        json.dumps(
            {
                "status": decision.status,
                "score": decision.score,
                "trace_id": decision.trace_id,
                "reason": decision.reason,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

