import json
from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.repository.fs_repository import get_repository, reset_repository


@pytest.fixture
def client():
    return TestClient(app)


def test_api_export_scope_gold_and_raw(tmp_path):
    reset_repository()
    repo = get_repository()
    session = 'api_scope'
    repo.load_session(session)
    a = repo.create(session, 'OM+', [{'start':0,'end':2}], comment='x')
    repo.accept(a.id, session)
    b = repo.create(session, 'SL+', [{'start':3,'end':5}], comment='y')
    repo.modify(b.id, session, 'RP+')
    repo.persist_session(session)

    c = TestClient(app)
    # gold
    r = c.post('/api/v1/annotations/export', params={'session_id': session, 'format':'jsonl', 'scope':'gold'})
    assert r.status_code == 200
    lines = [json.loads(l) for l in r.text.splitlines() if l.strip()]
    assert lines and all(x.get('validated') is True for x in lines)

    # raw
    r2 = c.post('/api/v1/annotations/export', params={'session_id': session, 'format':'jsonl', 'scope':'raw'})
    assert r2.status_code == 200
    lines2 = [json.loads(l) for l in r2.text.splitlines() if l.strip()]
    assert lines2 and all(x.get('decision') in ('pending','modified') for x in lines2)