import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.annotation import Annotation
from src.repository.fs_repository import get_repository, DATA_DIR

client = TestClient(app)

def setup_function():
    repo = get_repository()
    # Ensure clean persisted state for both sessions used
    for sid in ['test', 'clean']:
        p = DATA_DIR / f'{sid}.json'
        if p.exists():
            p.unlink()
    # Reset in-memory state by switching to a throwaway session
    repo.load_session('clean')
    # Now switch to target session
    repo.load_session('test')
    # Seed with one annotation using repository API
    repo.create('test', 'SL+', [{'start':0,'end':5}], comment=None)

def test_list_annotations_initial():
    r = client.get('/api/v1/annotations/?session_id=test')
    assert r.status_code == 200
    data = r.json()
    assert len(data['annotations']) == 1

def test_accept_annotation():
    repo = get_repository()
    ann_id = repo.query(session_id='test')[0].id
    r = client.patch(f'/api/v1/annotations/{ann_id}?session_id=test', json={'action':'accept','session_id':'test'})
    assert r.status_code == 200
    assert r.json()['annotation']['status'] == 'accepted'

def test_reject_annotation_hides_from_list():
    repo = get_repository()
    ann_id = repo.query(session_id='test')[0].id
    r = client.patch(f'/api/v1/annotations/{ann_id}?session_id=test', json={'action':'reject','session_id':'test'})
    assert r.status_code == 200
    r2 = client.get('/api/v1/annotations/?session_id=test')
    assert len(r2.json()['annotations']) == 0

def test_accept_modified_disallowed():
    # Simulate modified annotation
    repo = get_repository()
    ann_id = repo.query(session_id='test')[0].id
    repo.modify(ann_id, 'test', 'SLX+')
    r = client.patch(f'/api/v1/annotations/{ann_id}?session_id=test', json={'action':'accept','session_id':'test'})
    assert r.status_code == 400
    assert r.json()['detail'] == 'cannot_accept_modified'