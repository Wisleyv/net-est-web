"""Phase 1 Probe Script

Calls the comparative analysis endpoint and prints:
- strategy_id
- code
- source/target offsets
- model_version
- detection_config
- Ensures OM+/PRO+ absent when flags false.

Usage (after starting backend with VS Code task):
  python tools/demo_phase1_probe.py
"""
import json
import os
import requests

BACKEND_URL = os.environ.get("NET_EST_BACKEND_URL", "http://127.0.0.1:8000/api/v1/comparative-analysis/")

SOURCE = "Este é um texto de origem. Ele contém duas frases."
TARGET = "Este é um texto simplificado. Contém duas frases curtas."  # sample simplification

payload = {
    "source_text": SOURCE,
    "target_text": TARGET,
    "analysis_options": {
        "include_strategy_identification": True,
        "include_semantic_analysis": True,
        "include_lexical_analysis": False,
        "include_syntactic_analysis": False,
        "include_readability_metrics": False
    }
}

print("[Phase1 Probe] POST", BACKEND_URL)
resp = requests.post(BACKEND_URL, json=payload, timeout=30)
print("Status:", resp.status_code)
if resp.status_code != 200:
    print("Error response:", resp.text)
    raise SystemExit(1)

data = resp.json()
print("Model Version:", data.get("model_version"))
print("Detection Config:")
print(json.dumps(data.get("detection_config"), indent=2, ensure_ascii=False))

print("Strategies:")
for s in data.get("simplification_strategies", []):
    print("- id={id} code={code} conf={conf:.2f}".format(id=s.get("strategy_id"), code=s.get("code"), conf=s.get("confidence", 0)))
    print("  source_offsets=", s.get("source_offsets"))
    print("  target_offsets=", s.get("target_offsets"))

codes = {s.get("code") for s in data.get("simplification_strategies", [])}
print("Contains OM+?", "OM+" in codes)
print("Contains PRO+?", "PRO+" in codes)
if "OM+" in codes or "PRO+" in codes:
    print("[WARNING] Guardrail violation: OM+/PRO+ present while defaults should disable them.")
