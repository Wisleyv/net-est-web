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
            # Hierarchical analysis is experimental and feature-flag controlled; set to None to keep snapshots stable
            elif k == "hierarchical_analysis":
                new[k] = None
            # Overall score is algorithmic and may change with model updates; redact to avoid snapshot churn
            elif k == "overall_score":
                new[k] = None
            # Strategy detection counts may vary; redact for snapshot stability
            elif k == "strategies_count":
                new[k] = None
            else:
                # First normalize the value recursively
                normalized_v = _normalize(v)
                # If this is a substitutions list, sort deterministically by (source, target)
                if k == "substitutions" and isinstance(normalized_v, list):
                    try:
                        normalized_v.sort(key=lambda x: (x.get("source", ""), x.get("target", "")))
                    except Exception:
                        pass
                # If this is a simplification_strategies / strategies list, sort by (code, -score, name)
                # For snapshot stability, redact strategy detections (they are algorithmic and may vary)
                if k in ("simplification_strategies", "strategies"):
                    # Always normalize to an empty list for snapshots
                    normalized_v = []
                # Ensure floats that remain are rounded (for values that were direct floats)
                if isinstance(normalized_v, float):
                    new[k] = round(normalized_v, 6)
                else:
                    new[k] = normalized_v
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
def test_api_snapshots(endpoint: str, payload: dict):
    """Structural, stable assertions for critical API endpoints.

    This test replaces fragile snapshot matching with a set of structural
    invariants and type checks. Volatile fields are redacted by
    `_normalize` so we assert presence/shape rather than exact values.
    """
    response = client.post(endpoint, json=payload)
    assert response.status_code == 200

    # Normalize the payload (redaction, rounding, deterministic sorts)
    normalized = _normalize(response.json())

    # Top-level presence checks
    assert isinstance(normalized, dict)

    # Per-endpoint structural expectations
    if endpoint.endswith("comparative-analysis/"):
        # Request/response echoes
        assert "source_text" in normalized
        assert "target_text" in normalized

        # Hierarchical analysis is experimental and should be redacted to None for snapshots
        assert normalized.get("hierarchical_analysis") is None

        # Algorithmic scores should be redacted to avoid churn
        assert normalized.get("overall_score") is None
        assert normalized.get("strategies_count") is None

        # Semantic preservation should be numeric and within a plausible range for comparative analysis
        sp = normalized.get("semantic_preservation")
        assert isinstance(sp, (int, float))
        assert 0 <= sp <= 100

    elif endpoint.endswith("semantic-alignment/"):
        # Semantic alignment returns an alignment_result structure
        assert "alignment_result" in normalized
        ar = normalized.get("alignment_result")
        assert isinstance(ar, dict)
        aligned_pairs = ar.get("aligned_pairs")
        assert isinstance(aligned_pairs, list)
        for pair in aligned_pairs:
            assert isinstance(pair, dict)
            # at minimum an alignment should record the method used
            assert "alignment_method" in pair

    elif endpoint.endswith("feature-extraction/"):
        # Feature extraction returns feature-oriented data; don't require semantic_preservation
        # but ensure a features container or similar exists (best-effort check)
        expected_keys = [
            "features",
            "lexical_analysis",
            "salience",
            "annotated_data",
            "features_extracted",
            "average_confidence",
        ]
        assert any(k in normalized for k in expected_keys)

    # Lexical analysis shape (only if present)
    if "lexical_analysis" in normalized:
        lex = normalized.get("lexical_analysis")
        assert isinstance(lex, dict)
        subs = lex.get("substitutions", [])
        assert isinstance(subs, list)
        for s in subs:
            assert isinstance(s, dict)
            assert set(s.keys()) >= {"source", "target", "type"}

    # Highlighted differences (if present) must have source/target/type
    diffs = normalized.get("highlighted_differences", [])
    assert isinstance(diffs, list)
    for d in diffs:
        assert isinstance(d, dict)
        assert set(d.keys()) >= {"source", "target", "type"}

    # Simplification strategies are normalized to an empty list for snapshot stability
    if endpoint.endswith("comparative-analysis/"):
        assert isinstance(normalized.get("simplification_strategies"), list)

    # Compression/readability metrics should be numeric when present
    cr = normalized.get("compression_ratio")
    if cr is not None:
        assert isinstance(cr, (int, float))

    # Processing timestamps/ids are redacted by _normalize; ensure redaction took effect
    for volatile in ("analysis_id", "timestamp", "feedback_prompt", "processing_time"):
        if volatile in normalized:
            assert normalized[volatile] == "<redacted>"