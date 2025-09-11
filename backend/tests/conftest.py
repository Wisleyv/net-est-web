import pytest
from pathlib import Path
from src.repository.fs_repository import DATA_DIR, reset_repository, get_repository


@pytest.fixture()
def isolated_repo(tmp_path, monkeypatch):
    """Provide a fully isolated in-memory/file-system repo for tests.

    - Redirect DATA_DIR to a temporary directory
    - Clear any persisted session JSON files
    - Reset singleton and return fresh repository instance
    """
    # Ensure temp dir exists
    tmp_annotations = tmp_path / 'annotations'
    tmp_annotations.mkdir(parents=True, exist_ok=True)

    # Monkeypatch DATA_DIR global used in fs_repository
    monkeypatch.setattr('src.repository.fs_repository.DATA_DIR', tmp_annotations, raising=False)

    # Reset singleton
    reset_repository()
    repo = get_repository()

    # Safety clear in-memory
    if hasattr(repo, '_annotations'):
        repo._annotations.clear()  # type: ignore
    if hasattr(repo, '_audit'):
        repo._audit.clear()  # type: ignore

    yield repo

    # Persist nothing (cleanup naturally via tmp_path)
"""Configuração base para testes"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Cliente de teste para a API"""
    return TestClient(app)


@pytest.fixture
def sample_text_pair():
    """Par de textos para testes"""
    return {
        "source_text": "Este é um texto de exemplo para testar o sistema. Contém várias palavras e frases.",
        "target_text": "Texto de exemplo para teste. Tem palavras e frases.",
    }
