import sys, json
sys.path.insert(0,'c:/net/backend')
from fastapi.testclient import TestClient
from src.main import app
from src.core.config import settings
settings.PERSISTENCE_BACKEND='fs'
settings.ENABLE_DUAL_WRITE=False
settings.ENABLE_FS_FALLBACK=False
client = TestClient(app)
with open('c:/net/tmp_comparative_response.json','r',encoding='utf-8') as f:
    saved = json.load(f)
src = saved['source_text']
tgt = saved['target_text']
payload = {'source_text': src, 'target_text': tgt, 'analysis_options': {'include_strategy_identification': True}}
r = client.post('/api/v1/comparative-analysis/', json=payload)
print('status', r.status_code)
print('analysis_id', r.json().get('analysis_id'))
print('strategies', len(r.json().get('simplification_strategies', [])))
