import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

SESSION = 'test_export'

def test_create_modify_accept_and_export_jsonl_csv():
    # create
    payload = {
        "strategy_code": "OM+",
        "target_offsets": [{"start":0,"end":5}],
        "origin": "human",
        "status": "created",
        "comment": "teste"
    }
    r = client.post(f"/api/v1/annotations?session_id={SESSION}", json=payload)
    assert r.status_code == 200
    ann_id = r.json()['annotation']['id']

    # modify
    r = client.patch(f"/api/v1/annotations/{ann_id}?session_id={SESSION}", json={"action":"modify","session_id":SESSION,"new_code":"SL+"})
    assert r.status_code == 200
    assert r.json()['annotation']['strategy_code'] == 'SL+'

    # accept should fail on modified
    r = client.patch(f"/api/v1/annotations/{ann_id}?session_id={SESSION}", json={"action":"accept","session_id":SESSION})
    assert r.status_code == 400

    # create a second annotation and accept it directly
    r2 = client.post(f"/api/v1/annotations?session_id={SESSION}", json=payload)
    second_id = r2.json()['annotation']['id']
    r3 = client.patch(f"/api/v1/annotations/{second_id}?session_id={SESSION}", json={"action":"accept","session_id":SESSION})
    assert r3.status_code == 200

    # export jsonl
    r = client.post(f"/api/v1/annotations/export?session_id={SESSION}&format=jsonl")
    assert r.status_code == 200
    lines = [l for l in r.text.split('\n') if l.strip()]
    assert len(lines) >= 2  # two annotations (modified + accepted)
    recs = [json.loads(l) for l in lines]
    statuses = {rec['status'] for rec in recs}
    assert 'modified' in statuses and 'accepted' in statuses or 'created' in statuses

    # export csv
    r = client.post(f"/api/v1/annotations/export?session_id={SESSION}&format=csv")
    assert r.status_code == 200
    assert 'id,strategy_code,status' in r.text.splitlines()[0]

    # audit list
    audit = client.get(f"/api/v1/annotations/audit?session_id={SESSION}")
    assert audit.status_code == 200
    events = audit.json()
    assert any(e['action']=='create' for e in events)
    assert any(e['action']=='modify' for e in events)
    assert any(e['action']=='accept' for e in events)
