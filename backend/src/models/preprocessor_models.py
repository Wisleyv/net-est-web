"""Modelos específicos do pré-processador"""

from enum import Enum

from pydantic import BaseModel, Field

from .base import BaseResponse, ProcessingMetrics


class InputType(str, Enum):
    """Tipos de entrada suportados"""

    TEXT = "text"
    FILE = "file"


class FileFormat(str, Enum):
    """Formatos de arquivo suportados"""

    TXT = "txt"
    MD = "md"
    DOCX = "docx"
    ODT = "odt"
    PDF = "pdf"


class TextInput(BaseModel):
    """Entrada de texto direto"""

    source_text: str = Field(description="Texto fonte")
    target_text: str = Field(description="Texto alvo")
    input_type: InputType = InputType.TEXT


class PreprocessorOutput(BaseResponse):
    """Saída do pré-processador"""

    source_text: str = Field(description="Texto fonte limpo")
    target_text: str = Field(description="Texto alvo limpo")
    source_metrics: ProcessingMetrics
    target_metrics: ProcessingMetrics
    warnings: list[str] = Field(default_factory=list, description="Avisos para o usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Textos processados com sucesso",
                "source_text": "Texto fonte processado...",
                "target_text": "Texto alvo processado...",
                "source_metrics": {
                    "processing_time": 0.05,
                    "word_count": 150,
                    "character_count": 800,
                    "paragraph_count": 3,
                },
                "target_metrics": {
                    "processing_time": 0.03,
                    "word_count": 120,
                    "character_count": 650,
                    "paragraph_count": 3,
                },
                "warnings": [
                    "Texto fonte excede 2000 palavras. Processamento pode ser mais lento."
                ],
            }
        }
