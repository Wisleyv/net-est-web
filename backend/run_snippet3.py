from fastapi.testclient import TestClient
from src.main import app
import tests.test_annotations_api as t
from src.repository.fs_repository import get_repository

# call test setup
t.setup_function()
repo = get_repository()
anns = repo.query(session_id='test')
print('anns count', len(anns), [(a.id,a.status) for a in anns])
ann_id = anns[0].id
client = TestClient(app)
r = client.patch(f"/api/v1/annotations/{ann_id}?session_id=test", json={'action':'accept','session_id':'test'})
print('status', r.status_code, r.text)
