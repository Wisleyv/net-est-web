import uuid
from pathlib import Path
import json

from src.repository.fs_repository import get_repository
from src.repository.sqlite_repository import SQLiteAnnotationRepository
from src.core.config import settings


def test_sqlite_basic_crud(tmp_path, monkeypatch):
    # create isolated DB
    db = tmp_path / 'test.sqlite3'
    repo = SQLiteAnnotationRepository(str(db))
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    repo.load_session(session_id)
    a = repo.create(session_id, 'SL+', [{'start': 1, 'end': 3}], comment='db')
    assert repo.get(a.id) is not None
    repo.modify(a.id, session_id, 'SLX+')
    assert repo.get(a.id).status == 'modified'
    try:
        repo.accept(a.id, session_id)
    except ValueError:
        pass
    repo.reject(a.id, session_id)
    assert repo.get(a.id).status == 'rejected'
    assert len(repo.list_audit(a.id, session_id=session_id)) >= 3


def test_dual_write_consistency(tmp_path, monkeypatch):
    # Force factory to create DualWrite with isolated DB path
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', True)
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path / 'shadow.sqlite3'))

    from importlib import reload
    import src.repository.fs_repository as fsmod
    reload(fsmod)

    repo = fsmod.get_repository()  # DualWriteRepository
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    repo.load_session(session_id)
    a = repo.create(session_id, 'OM+', [{'start': 0, 'end': 2}], comment='dw')
    repo.modify(a.id, session_id, 'OMX+')
    repo.reject(a.id, session_id)

    # Read from FS (source of truth)
    fs_ann = repo.get(a.id)
    assert fs_ann.status == 'rejected'

    # Query from DB directly to ensure it mirrors
    db = SQLiteAnnotationRepository(settings.SQLITE_DB_PATH)
    db.load_session(session_id)
    db_ann = db.get(a.id)
    assert db_ann is not None
    assert db_ann.status == 'rejected'


def test_export_parity_fs_vs_sqlite(tmp_path, monkeypatch):
    # Prepare some data in FS
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    from importlib import reload
    import src.repository.fs_repository as fsmod
    reload(fsmod)
    fs_repo = fsmod.get_repository()
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    fs_repo.load_session(session_id)
    a1 = fs_repo.create(session_id, 'SL+', [{'start': 0, 'end': 1}])
    a2 = fs_repo.create(session_id, 'RF+', [{'start': 2, 'end': 3}])
    fs_repo.modify(a2.id, session_id, 'RF+')
    fs_repo.persist_session(session_id)

    # Migrate to SQLite and compare export filters
    db = SQLiteAnnotationRepository(str(tmp_path / 'exp.sqlite3'))
    db.load_session(session_id)
    for a in fs_repo.query(session_id=session_id):
        db.sync_from_action(a, 'sync', session_id, None, a.status, a.original_code, a.strategy_code)

    fs_export = sorted([x.id for x in fs_repo.export()])
    db_export = sorted([x.id for x in db.export()])
    assert fs_export == db_export


def test_migration_from_json_populates_sqlite(tmp_path):
    # Create a minimal JSON session file
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    from src.repository.fs_repository import DATA_DIR
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        'annotations': [
            {
                'id': 'ann1', 'strategy_code': 'SL+', 'status': 'created', 'origin': 'human',
                'target_offsets': [{'start':0,'end':1}],
                'created_at': '2025-09-08T12:00:00+00:00', 'updated_at': '2025-09-08T12:00:00+00:00'
            }
        ],
        'audit': [
            {'annotation_id': 'ann1', 'action': 'create', 'timestamp': '2025-09-08T12:00:00+00:00', 'session_id': session_id}
        ]
    }
    (DATA_DIR / f"{session_id}.json").write_text(json.dumps(payload), encoding='utf-8')

    db_path = tmp_path / 'mig.sqlite3'
    from src.repository.sqlite_repository import SQLiteAnnotationRepository
    # Prepare an isolated DATA_DIR for migration
    tmp_data = tmp_path / 'data'
    tmp_data.mkdir(parents=True, exist_ok=True)
    (tmp_data / f"{session_id}.json").write_text(json.dumps(payload), encoding='utf-8')
    # Import script as module via filesystem path to avoid PYTHONPATH issues
    import importlib.util, sys
    script_path = Path(__file__).resolve().parents[1] / 'scripts' / 'migrate_fs_to_sqlite.py'
    spec = importlib.util.spec_from_file_location('migrate_fs_to_sqlite', script_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    # Point migration at isolated dir
    setattr(mod, 'DATA_DIR', tmp_data)
    mod.migrate(str(db_path))

    db = SQLiteAnnotationRepository(str(db_path))
    db.load_session(session_id)
    anns = db.query(session_id=session_id)
    assert len(anns) == 1
    assert anns[0].id == 'ann1'
