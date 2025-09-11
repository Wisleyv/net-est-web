import json
import runpy
import sys
from pathlib import Path

import pytest

from src.core.config import settings
from src.repository.fs_repository import get_repository, reset_repository


def _seed(session: str):
    repo = get_repository()
    repo.load_session(session)
    a = repo.create(session, 'OM+', [{'start': 0, 'end': 1}], comment='a')
    b = repo.create(session, 'RF+', [{'start': 2, 'end': 3}], comment='b')
    repo.accept(b.id, session)
    repo.persist_session(session)


@pytest.mark.parametrize('backend', ['fs','sqlite'])
@pytest.mark.parametrize('fmt', ['jsonl','csv'])
def test_round_trip_annotations(tmp_path, monkeypatch, backend, fmt):
    # Configure backend
    if backend == 'fs':
        monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'fs')
        monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
        monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', True)
    else:
        monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
        monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path / 'rt.sqlite3'))
        monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
        monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
    reset_repository()

    src_session = f'rt_src_{backend}_{fmt}'
    dst_session = f'rt_dst_{backend}_{fmt}'
    # Clean any leftover FS files for deterministic runs
    try:
        base = Path(__file__).resolve().parents[1] / 'src' / 'data' / 'annotations'
        for s in (src_session, dst_session):
            p = base / f'{s}.json'
            if p.exists():
                p.unlink()
    except Exception:
        pass
    _seed(src_session)

    out_dir = tmp_path / 'out'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export source
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['export', '--session', src_session, '--format', fmt, '--out', str(out_dir)]
        try:
            runpy.run_module('src.tools.export', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    exported_files = list(out_dir.iterdir())
    assert exported_files
    exp = exported_files[0]
    assert exp.exists() and exp.stat().st_size > 0

    # Import into destination
    argv_bak = list(sys.argv)
    try:
        sys.argv = ['import', '--session', dst_session, '--file', str(exp), '--format', fmt]
        try:
            runpy.run_module('src.tools.import_tool', run_name='__main__')
        except SystemExit as e:
            if e.code != 0:
                raise
    finally:
        sys.argv = argv_bak

    # Validate parity in counts
    repo = get_repository()
    repo.load_session(src_session)
    src_count = len(repo.export())
    repo.load_session(dst_session)
    dst_count = len(repo.export())
    assert dst_count == src_count
