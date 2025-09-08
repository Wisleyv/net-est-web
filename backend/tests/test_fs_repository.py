import uuid
from pathlib import Path
from src.repository.fs_repository import get_repository

def test_fs_repository_persist_and_reload(tmp_path):
    repo = get_repository()
    session_id = f"testsess-{uuid.uuid4().hex[:8]}"
    repo.load_session(session_id)
    ann = repo.create(session_id, 'SL+', [{'start': 0, 'end': 4}], comment='test')
    repo.persist_session(session_id)

    # simulate fresh in-memory by switching sessions then reloading
    repo.load_session("other-session")
    repo.load_session(session_id)
    loaded = repo.get(ann.id)
    assert loaded is not None
    assert loaded.strategy_code == 'SL+'
    # modify then accept lifecycle
    repo.modify(ann.id, session_id, 'SLX+')
    assert repo.get(ann.id).status == 'modified'
    try:
        repo.accept(ann.id, session_id)
    except ValueError:
        # cannot accept modified (expected)
        pass
    repo.reject(ann.id, session_id)
    assert repo.get(ann.id).status == 'rejected'
    # audit entries recorded
    audit = repo.list_audit(ann.id)
    assert len(audit) >= 3
