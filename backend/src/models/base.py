"""Modelos base para toda a aplicação"""

from datetime import datetime

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Resposta base para todas as APIs"""

    success: bool = True
    message: str = "Operação realizada com sucesso"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Resposta de erro padronizada"""

    success: bool = False
    error_type: str
    details: dict | None = None


class HealthResponse(BaseResponse):
    """Resposta do health check"""

    version: str
    status: str
    uptime_seconds: float


class ProcessingMetrics(BaseModel):
    """Métricas de processamento"""

    processing_time: float = Field(description="Tempo de processamento em segundos")
    word_count: int = Field(description="Número de palavras processadas")
    character_count: int = Field(description="Número de caracteres")
    paragraph_count: int = Field(description="Número de parágrafos")
