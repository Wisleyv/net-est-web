"""Testes para modelos de dados"""

from src.models.base import HealthResponse, ProcessingMetrics
from src.models.preprocessor_models import InputType, TextInput


def test_health_response_model():
    """Teste do modelo HealthResponse"""
    response = HealthResponse(version="1.0.0", status="healthy", uptime_seconds=123.45)

    assert response.success is True
    assert response.version == "1.0.0"
    assert response.status == "healthy"
    assert response.uptime_seconds == 123.45


def test_processing_metrics_model():
    """Teste do modelo ProcessingMetrics"""
    metrics = ProcessingMetrics(
        processing_time=0.05, word_count=150, character_count=800, paragraph_count=3
    )

    assert metrics.processing_time == 0.05
    assert metrics.word_count == 150
    assert metrics.character_count == 800
    assert metrics.paragraph_count == 3


def test_text_input_model():
    """Teste do modelo TextInput"""
    text_input = TextInput(source_text="Texto fonte", target_text="Texto alvo")

    assert text_input.source_text == "Texto fonte"
    assert text_input.target_text == "Texto alvo"
    assert text_input.input_type == InputType.TEXT
