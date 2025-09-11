from fastapi.testclient import TestClient
from src.main import app
from src.repository.fs_repository import get_repository, reset_repository, DATA_DIR

# clean
for f in DATA_DIR.glob('*.json'):
    try:
        f.unlink()
    except Exception:
        pass
reset_repository()
repo = get_repository()
repo.load_session('test')
a = repo.create('test','SL+',[{'start':0,'end':5}], None)
print('seed', a.status)
client = TestClient(app)
r = client.patch(f'/api/v1/annotations/{a.id}?session_id=test', json={'action':'accept','session_id':'test'})
print('status', r.status_code, r.text)
