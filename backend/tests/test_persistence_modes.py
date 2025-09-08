import uuid
from pathlib import Path

from src.core.config import settings


def _reload_repo_module(monkeypatch):
    from importlib import reload
    import src.repository.fs_repository as fsmod
    reload(fsmod)
    return fsmod


def test_sqlite_primary_reads(monkeypatch, tmp_path):
    # Configure SQLite as primary, no dual-write
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path / 'primary.sqlite3'))
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    fsmod = _reload_repo_module(monkeypatch)
    repo = fsmod.get_repository()
    session_id = f"s-{uuid.uuid4().hex[:6]}"
    repo.load_session(session_id)
    a = repo.create(session_id, 'SL+', [{'start': 0, 'end': 1}])
    assert repo.get(a.id) is not None
    assert any(x.id == a.id for x in repo.list_visible())


def test_fs_fallback_when_db_missing(monkeypatch, tmp_path):
    # SQLite primary with fallback enabled; break DB path
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path / 'nonexistent' / 'missing.sqlite3'))
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', True)
    fsmod = _reload_repo_module(monkeypatch)
    repo = fsmod.get_repository()
    session_id = f"s-{uuid.uuid4().hex[:6]}"
    repo.load_session(session_id)
    # If DB operations fail, fallback should still operate
    a = repo.create(session_id, 'RF+', [{'start': 1, 'end': 2}])
    assert repo.get(a.id) is not None


def test_sqlite_primary_dual_write_to_fs(monkeypatch, tmp_path):
    # DB primary, mirror to FS; then reload FS-only and verify data mirrored
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path / 'dw.sqlite3'))
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', True)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    fsmod = _reload_repo_module(monkeypatch)
    repo = fsmod.get_repository()  # DualWriteSQLitePrimary or Fallback(DualWrite,...)
    session_id = f"s-{uuid.uuid4().hex[:6]}"
    repo.load_session(session_id)
    a = repo.create(session_id, 'OM+', [{'start': 0, 'end': 1}])
    repo.modify(a.id, session_id, 'OMX+')

    # Now switch to FS-only and verify mirrored data exists
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    fsmod2 = _reload_repo_module(monkeypatch)
    fsrepo = fsmod2.get_repository()
    fsrepo.load_session(session_id)
    ann = fsrepo.get(a.id)
    assert ann is not None
    assert ann.status == 'modified'


def test_migration_then_switch_to_sqlite_consistent(monkeypatch, tmp_path):
    # Seed FS, migrate, then switch to SQLite and compare export parity
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    fsmod = _reload_repo_module(monkeypatch)
    fsrepo = fsmod.get_repository()
    session_id = f"s-{uuid.uuid4().hex[:6]}"
    fsrepo.load_session(session_id)
    a1 = fsrepo.create(session_id, 'SL+', [{'start': 0, 'end': 1}])
    a2 = fsrepo.create(session_id, 'RF+', [{'start': 1, 'end': 2}])
    fsrepo.modify(a2.id, session_id, 'RF+')
    fsrepo.persist_session(session_id)

    # Migrate
    import importlib.util
    script_path = Path(__file__).resolve().parents[1] / 'scripts' / 'migrate_fs_to_sqlite.py'
    spec = importlib.util.spec_from_file_location('migrate_fs_to_sqlite', script_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore
    db_path = tmp_path / 'mig.sqlite3'
    mod.migrate(str(db_path))

    # Switch to SQLite primary
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(db_path))
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    fsmod_sql = _reload_repo_module(monkeypatch)
    dbrepo = fsmod_sql.get_repository()
    dbrepo.load_session(session_id)

    fs_ids = sorted([x.id for x in fsrepo.export()])
    db_ids = sorted([x.id for x in dbrepo.export()])
    assert fs_ids == db_ids
