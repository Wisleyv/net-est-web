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
