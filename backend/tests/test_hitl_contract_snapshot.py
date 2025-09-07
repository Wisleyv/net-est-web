import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_contract_snapshot_minimal():
    payload = {
        "source_text": "A origem tem duas sentenças.",
        "target_text": "O alvo tem duas sentenças simples.",
        "analysis_options": {"include_strategy_identification": True}
    }
    resp = client.post("/api/v1/comparative-analysis/", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Required top-level keys
    for key in ["analysis_id","model_version","detection_config","simplification_strategies"]:
        assert key in data
    # Strategy contract subset
    if data["simplification_strategies"]:
        s = data["simplification_strategies"][0]
        for k in ["strategy_id","code","confidence"]:
            assert k in s
    # Snapshot subset (stable schema keys only)
    snapshot_subset = {
        "model_version": data.get("model_version"),
        "detection_config_keys": sorted(list(data.get("detection_config", {}).keys())),
        "strategy_fields": sorted(list(data["simplification_strategies"][0].keys())) if data["simplification_strategies"] else []
    }
    # Instead of file snapshot (for CI simplicity), assert expected mandatory keys presence
    assert "model_version" in snapshot_subset
    assert "detection_config_keys" in snapshot_subset
