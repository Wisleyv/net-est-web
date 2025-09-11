import json
from pathlib import Path

import pytest

from src.core.config import settings
from src.repository.fs_repository import get_repository, reset_repository
from src.tools.export import export_annotations


@pytest.mark.parametrize('backend', ['fs','sqlite'])
def test_gold_flags_persist_and_query(isolated_repo, tmp_path, monkeypatch, backend):
    # Configure backend
    if backend == 'sqlite':
        monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
        monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
        monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
        monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path/ 'primary.sqlite3'))
        reset_repository()
        repo = get_repository()
    else:
        repo = isolated_repo

    session = 'gold_test_' + backend
    repo.load_session(session)

    # Seed: one machine-predicted pending ann, one human-created (manually_assigned)
    a = repo.create(session, 'OM+', [{'start':0, 'end':3}], comment='human')
    assert a.manually_assigned is True
    assert a.validated is False
    # Accept it -> becomes gold
    aa = repo.accept(a.id, session)
    assert aa.validated is True
    assert aa.status == 'accepted'

    # Create a machine one via modify flow: create then modify -> not validated
    b = repo.create(session, 'RF+', [{'start':4,'end':7}], comment='machine')
    repo.modify(b.id, session, 'SL+')
    bb = repo.get(b.id)
    assert bb.validated is False and bb.status == 'modified'

    repo.persist_session(session)

    # Gold query via export helper (gold scope)
    out = export_annotations(session, fmt='jsonl', out_dir=tmp_path, scope='gold')
    lines = [json.loads(l) for l in Path(out).read_text(encoding='utf-8').splitlines() if l.strip()]
    assert lines, 'no gold exported'
    # Only validated entries
    assert all(r.get('validated') is True for r in lines)
    # Must include explanation field
    assert all('explanation' in r for r in lines)


@pytest.mark.parametrize('backend', ['fs','sqlite'])
def test_export_scopes_and_fields(isolated_repo, tmp_path, monkeypatch, backend):
    if backend == 'sqlite':
        monkeypatch.setattr(settings, 'PERSISTENCE_BACKEND', 'sqlite')
        monkeypatch.setattr(settings, 'ENABLE_DUAL_WRITE', False)
        monkeypatch.setattr(settings, 'ENABLE_FS_FALLBACK', False)
        monkeypatch.setattr(settings, 'SQLITE_DB_PATH', str(tmp_path/ 'primary.sqlite3'))
        reset_repository()
        repo = get_repository()
    else:
        repo = isolated_repo

    session = 'scope_test_' + backend
    repo.load_session(session)
    x = repo.create(session, 'RP+', [{'start':0,'end':2}], comment='c')
    repo.accept(x.id, session)
    y = repo.create(session, 'SL+', [{'start':3,'end':5}], comment='c2')
    repo.modify(y.id, session, 'OM+')
    repo.persist_session(session)

    # both
    out_both = export_annotations(session, fmt='jsonl', out_dir=tmp_path, scope='both')
    both = [json.loads(l) for l in Path(out_both).read_text(encoding='utf-8').splitlines() if l.strip()]
    assert any(r.get('validated') for r in both)
    assert any(r.get('decision') == 'modified' for r in both)

    # gold
    out_gold = export_annotations(session, fmt='jsonl', out_dir=tmp_path, scope='gold')
    gold = [json.loads(l) for l in Path(out_gold).read_text(encoding='utf-8').splitlines() if l.strip()]
    assert gold and all(r.get('validated') is True for r in gold)

    # raw
    out_raw = export_annotations(session, fmt='jsonl', out_dir=tmp_path, scope='raw')
    raw = [json.loads(l) for l in Path(out_raw).read_text(encoding='utf-8').splitlines() if l.strip()]
    assert raw and all(r.get('decision') in ('pending','modified') for r in raw)