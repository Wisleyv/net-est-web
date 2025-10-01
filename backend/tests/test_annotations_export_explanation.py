import json
import os
from fastapi.testclient import TestClient
from src.main import app
from src.repository.fs_repository import reset_repository
from src.core.config import settings

client = TestClient(app)

SESSION_EXPL = 'test_export_explanation'

# Helper to force backend mode for each test variant

def _set_backend(mode: str):
    # Directly patch settings object (already instantiated at import time)
    settings.PERSISTENCE_BACKEND = mode  # type: ignore
    settings.ENABLE_DUAL_WRITE = False   # type: ignore
    settings.ENABLE_FS_FALLBACK = False  # type: ignore
    reset_repository()


def _create_annotations():
    # create one that will be accepted (machine origin via create->accept)
    payload = {
        "strategy_code": "SL+",  # has explanation template
        "target_offsets": [{"start":0,"end":3}],
        "origin": "human",
        "status": "created",
        "comment": "primeiro"
    }
    r = client.post(f"/api/v1/annotations?session_id={SESSION_EXPL}", json=payload)
    assert r.status_code == 200
    first_id = r.json()['annotation']['id']

    # accept it
    r = client.patch(f"/api/v1/annotations/{first_id}?session_id={SESSION_EXPL}", json={"action":"accept","session_id":SESSION_EXPL})
    assert r.status_code == 200

    # create and then modify another (modified should keep / set explanation)
    r2 = client.post(f"/api/v1/annotations?session_id={SESSION_EXPL}", json=payload)
    second_id = r2.json()['annotation']['id']
    r3 = client.patch(f"/api/v1/annotations/{second_id}?session_id={SESSION_EXPL}", json={"action":"modify","session_id":SESSION_EXPL,"new_code":"SL+"})
    assert r3.status_code == 200


def _export_and_assert():
    # jsonl
    r = client.post(f"/api/v1/annotations/export?session_id={SESSION_EXPL}&format=jsonl")
    assert r.status_code == 200
    lines = [l for l in r.text.split('\n') if l.strip()]
    assert len(lines) >= 2
    recs = [json.loads(l) for l in lines]
    # All exported records with strategy_code SL+ should have explanation populated (template based)
    sl_recs = [r for r in recs if r['strategy_code'] == 'SL+']
    assert sl_recs, 'Expected SL+ records present'
    assert all(r.get('explanation') for r in sl_recs), 'Explanation missing for some SL+ records (jsonl)'

    # csv
    r2 = client.post(f"/api/v1/annotations/export?session_id={SESSION_EXPL}&format=csv")
    assert r2.status_code == 200
    import csv, io
    reader = csv.reader(io.StringIO(r2.text))
    rows = list(reader)
    assert rows, 'CSV export empty'
    header = rows[0]
    assert 'explanation' in header, f'CSV header missing explanation: {header}'
    idx = header.index('explanation')
    data_rows = rows[1:]
    sl_rows = [r for r in data_rows if len(r) >= 2 and r[1] == 'SL+']  # column 1 is strategy_code in header ordering
    assert sl_rows, 'No SL+ rows in CSV export'
    for rrow in sl_rows:
        assert rrow[idx].strip() != '', 'Explanation column empty for SL+ row in CSV'


def test_export_explanation_fs_backend():
    _set_backend('fs')
    _create_annotations()
    _export_and_assert()


def test_export_explanation_sqlite_backend():
    _set_backend('sqlite')
    _create_annotations()
    _export_and_assert()
