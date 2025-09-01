import pytest
from fastapi.testclient import TestClient
from src.main import app
import json
import re


UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def _normalize(obj):
    """Recursively normalize a response object: redact UUIDs/timestamps and round floats."""
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            # Redact commonly-volatile identifiers and timing fields used in nested models
            if k in ("analysis_id", "timestamp", "feedback_id", "processing_time", "feedback_prompt", "embedding_time_seconds", "processing_time_seconds"):
                new[k] = "<redacted>"
            # Hierarchical analysis is experimental and feature-flag controlled; redact to keep snapshots stable
            elif k == "hierarchical_analysis":
                new[k] = "<redacted>"
            elif isinstance(v, float):
                # Round floats to stable precision
                new[k] = round(v, 6)
            else:
                new[k] = _normalize(v)
        return new
    elif isinstance(obj, list):
        return [_normalize(x) for x in obj]
    elif isinstance(obj, float):
        return round(obj, 6)
    elif isinstance(obj, str):
        # redact UUIDs inside strings
        if UUID_RE.search(obj):
            return UUID_RE.sub("<uuid>", obj)
        return obj
    else:
        return obj

client = TestClient(app)

@pytest.mark.parametrize("endpoint, payload", [
    ("/api/v1/semantic-alignment/", {
        "source_text": "O gato preto pulou o muro alto.",
        "target_text": "O felino escuro saltou sobre a parede elevada."
    }),
    ("/api/v1/comparative-analysis/", {
        "source_text": "A reunião foi adiada devido a circunstâncias imprevistas.",
        "target_text": "O encontro foi cancelado por motivos inesperados."
    }),
    ("/api/v1/feature-extraction/", {
        "text": "A rápida raposa marrom salta sobre o cão preguiçoso."
    })
])
def test_api_snapshots(snapshot, endpoint: str, payload: dict):
    """Snapshot test for critical API endpoints"""
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200
    # Serialize to stable JSON string to avoid nondeterministic ordering or float repr
    normalized = _normalize(response.json())
    serialized = json.dumps(normalized, ensure_ascii=False, sort_keys=True, indent=2)
    snapshot.assert_match(serialized, f"{endpoint.replace('/', '_')}_snapshot")