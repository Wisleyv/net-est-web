import json, time, sys, os
import requests

BASE = "http://127.0.0.1:8000"

def wait_ready(timeout=30):
    start=time.time()
    while time.time()-start<timeout:
        try:
            r=requests.get(BASE+"/health", timeout=2)
            if r.status_code==200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

if not wait_ready():
    print("ERROR: backend not ready", file=sys.stderr)
    sys.exit(1)

health=requests.get(BASE+"/health").json()
status=requests.get(BASE+"/status").json()

payload={
  "source_text":"O gato está sentado no tapete vermelho perto da janela iluminada.",
  "target_text":"O gato está no tapete.",
  "analysis_options": {"include_micro_spans": False}
}
resp=requests.post(BASE+"/api/v1/comparative-analysis/", json=payload)
print("HEALTH=", json.dumps(health, ensure_ascii=False))
print("STATUS.models=", json.dumps(status.get("models"), ensure_ascii=False))
print("COMPARATIVE.status=", resp.status_code)
if resp.ok:
    data=resp.json()
    # Show Phase1 fields presence summary
    strategies=data.get("strategies", [])
    sample=strategies[0] if strategies else {}
    subset={k: sample.get(k) for k in ["strategy_id","model_version","detection_config","source_offsets","target_offsets","type","confidence_score"] if k in sample}
    print("SAMPLE_STRATEGY_FIELDS=", json.dumps(subset, ensure_ascii=False))
    print("TOTAL_STRATEGIES=", len(strategies))
    print("HAS_GUARDRAILS=", any(s.get("type")=="PRO_PLUS" for s in strategies)==False)  # PRO+ should be absent unless enabled
else:
    print("COMPARATIVE_ERROR_BODY=", resp.text[:500])
