import json
import os
from pathlib import Path

import pytest

from src.core.config import settings
from src.repository.fs_repository import get_repository, reset_repository


def _setup_session(session: str):
    repo = get_repository()
    repo.load_session(session)
    a = repo.create(session, 'OM+', [{'start': 0, 'end': 3}], comment='c1')
    repo.modify(a.id, session, 'SL+')
    b = repo.create(session, 'RF+', [{'start': 4, 'end': 7}], comment='c2')
    repo.accept(b.id, session)
    repo.persist_session(session)


@pytest.mark.parametrize('fmt', ['jsonl','csv'])
def test_export_cli_fs_backend(tmp_path, monkeypatch, fmt):
    # Configure FS backend
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', True)
    reset_repository()

    session = 'cli_fs'
    _setup_session(session)

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Run tool via module (simulate command line)
    import runpy, sys
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['export', '--session', session, '--format', fmt, '--out', str(out_dir)]
        try:
            runpy.run_module('src.tools.export', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    files = list(out_dir.iterdir())
    assert files, 'no export produced'
    content = files[0].read_text(encoding='utf-8')
    assert content.strip(), 'empty export'
    if fmt == 'jsonl':
        lines = [json.loads(l) for l in content.splitlines() if l.strip()]
        assert any(r['status'] == 'modified' for r in lines)
        assert any(r['status'] == 'accepted' for r in lines)
        for r in lines:
            assert 'session_id' in r and r['session_id'] == session
            assert 'strategy_code' in r
            assert 'created_at' in r
            assert 'decision' in r
    else:
        # header sanity
        header = content.splitlines()[0]
        assert 'id' in header and 'strategy_code' in header and 'status' in header and 'decision' in header


@pytest.mark.parametrize('fmt', ['jsonl','csv'])
def test_export_audit_cli_fs_backend(tmp_path, monkeypatch, fmt):
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', True)
    reset_repository()

    session = 'cli_fs_audit'
    _setup_session(session)

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    import runpy, sys
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['export', '--type', 'audit', '--session', session, '--format', fmt, '--out', str(out_dir)]
        try:
            runpy.run_module('src.tools.export', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    files = list(out_dir.iterdir())
    assert files, 'no audit export produced'
    data = files[0].read_text(encoding='utf-8')
    assert data.strip()
    if fmt == 'jsonl':
        lines = [json.loads(l) for l in data.splitlines() if l.strip()]
        actions = {r['action'] for r in lines}
        assert {'create','modify','accept'}.issubset(actions)
    else:
        header = data.splitlines()[0]
        assert 'annotation_id' in header and 'action' in header and 'timestamp' in header


@pytest.mark.parametrize('fmt', ['jsonl','csv'])
def test_export_audit_cli_sqlite_backend(tmp_path, monkeypatch, fmt):
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path/ 'primary.sqlite3'))
    reset_repository()

    session = 'cli_db_audit'
    _setup_session(session)

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    import runpy, sys
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['export', '--type', 'audit', '--session', session, '--format', fmt, '--out', str(out_dir)]
        try:
            runpy.run_module('src.tools.export', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    files = list(out_dir.iterdir())
    assert files, 'no audit export produced'
    data = files[0].read_text(encoding='utf-8')
    assert data.strip()
    if fmt == 'jsonl':
        lines = [json.loads(l) for l in data.splitlines() if l.strip()]
        actions = {r['action'] for r in lines}
        assert {'create','modify','accept'}.issubset(actions)
    else:
        header = data.splitlines()[0]
        assert 'annotation_id' in header and 'action' in header and 'timestamp' in header


@pytest.mark.parametrize('fmt', ['jsonl','csv'])
def test_export_cli_sqlite_backend(tmp_path, monkeypatch, fmt):
    # Configure SQLite primary without fallback to ensure we hit DB path
    monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
    monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
    monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path/ 'primary.sqlite3'))
    reset_repository()

    session = 'cli_db'
    _setup_session(session)

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    import runpy, sys
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['export', '--session', session, '--format', fmt, '--out', str(out_dir)]
        try:
            runpy.run_module('src.tools.export', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    files = list(out_dir.iterdir())
    assert files, 'no export produced'
    content = files[0].read_text(encoding='utf-8')
    assert content.strip(), 'empty export'
    if fmt == 'jsonl':
        lines = [json.loads(l) for l in content.splitlines() if l.strip()]
        # Same invariants as FS
        assert any(r['status'] == 'modified' for r in lines)
        assert any(r['status'] == 'accepted' for r in lines)
    else:
        header = content.splitlines()[0]
        assert 'id' in header and 'strategy_code' in header and 'status' in header
