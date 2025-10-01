"""
Data models for simplification strategies, aligned with the documentation.
"""

from enum import Enum
from typing import List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field

class SimplificationStrategyType(str, Enum):
    """Enum for the type of simplification strategy."""
    LEXICAL = "lexical"
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"

class StrategyExample(BaseModel):
    """Model for an example of a strategy."""
    original: str = Field(..., description="Original text segment.")
    simplified: str = Field(..., description="Simplified text segment.")

class SimplificationStrategy(BaseModel):
    """
    Pydantic model for a single simplification strategy, based on the
    "Tabela de Estratégias de Simplificação Textual".
    """
    sigla: str = Field(..., description="The acronym for the strategy (e.g., 'SL+').")
    nome: str = Field(..., description="The descriptive name of the strategy.")
    descricao: str = Field(..., description="The functional description of the strategy.")
    tipo: SimplificationStrategyType = Field(..., description="The type of the strategy.")
    impacto: Literal["baixo", "médio", "alto"] = Field(..., description="The impact of the strategy.")
    confianca: float = Field(..., description="The confidence score of the detection (0.0 to 1.0).")
    exemplos: List[StrategyExample] = Field(..., description="Examples of the strategy in action.")

    # Enhanced confidence features (M5)
    confidence_explanation: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed explanation of confidence calculation with factor breakdown"
    )
    confidence_level: Optional[str] = Field(
        None,
        description="Human-readable confidence level (very_low, low, moderate, high, very_high)"
    )
    evidence_quality: Optional[str] = Field(
        None,
        description="Quality of evidence supporting this strategy detection"
    )
    # Character-level position data for frontend highlighting
    target_offsets: Optional[List[Dict[str, int]]] = Field(
        None,
        description="Character-level boundaries for text highlighting [{'start': int, 'end': int}]"
    )

    # Backwards-compatible English aliases (read/write) used across tests and other modules.
    @property
    def name(self) -> str:
        return self.nome

    @name.setter
    def name(self, value: str) -> None:
        self.nome = value

    @property
    def description(self) -> str:
        return self.descricao

    @description.setter
    def description(self, value: str) -> None:
        self.descricao = value

    @property
    def type(self) -> SimplificationStrategyType:
        return self.tipo

    @type.setter
    def type(self, value: SimplificationStrategyType) -> None:
        self.tipo = value

    @property
    def impact(self) -> str:
        return self.impacto

    @impact.setter
    def impact(self, value: str) -> None:
        self.impacto = value

    @property
    def confidence(self) -> float:
        return self.confianca

    @confidence.setter
    def confidence(self, value: float) -> None:
        self.confianca = value

    # Backwards-compatible Portuguese accented property name used in older tests
    @property
    def confiança(self) -> float:  # type: ignore
        return self.confianca

    @confiança.setter
    def confiança(self, value: float) -> None:  # type: ignore
        self.confianca = value

    @property
    def examples(self) -> List[StrategyExample]:
        return self.exemplos

    @examples.setter
    def examples(self, value: List[StrategyExample]) -> None:
        self.exemplos = value

    @property
    def code(self) -> str | None:
        return getattr(self, 'sigla', None)

    @code.setter
    def code(self, value: str) -> None:
        self.sigla = value

# Canonical data for all strategies, based on "Tabela Simplificação Textual.md"
STRATEGY_DESCRIPTIONS: Dict[str, Dict[str, Any]] = {
    "AS+": {
        "nome": "Alteração de Sentido",
        "descricao": "Embora não seja usada como estratégia intencional, pode ocorrer como resultado de modulações, ao expressar a mesma ideia por outro ponto de vista. Pode ser tolerada se não comprometer o sentido essencial do texto original.",
        "tipo": SimplificationStrategyType.SEMANTIC
    },
    "DL+": {
        "nome": "Reorganização Posicional",
        "descricao": "Mudança na ordem dos elementos na frase para melhorar o fluxo da informação. Inclui extraposição, antecipação e movimentação de inserções ou tópicos para facilitar a leitura.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "EXP+": {
        "nome": "Explicitação e Detalhamento",
        "descricao": "Adição de informações, exemplos ou paráfrases para esclarecer conteúdos implícitos ou complexos. Ajuda o leitor a compreender conceitos que exigiriam conhecimento prévio.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "IN+": {
        "nome": "Manejo de Inserções",
        "descricao": "Eliminação, deslocamento ou reestruturação de inserções que atrapalham a fluidez da sentença. Pode incluir repetição de elementos para manter a coesão em textos falados ou escritos.",
        "tipo": SimplificationStrategyType.SYNTACTIC
    },
    "MOD+": {
        "nome": "Reinterpretação Perspectiva",
        "descricao": "Reformulação semântica para adaptar o conteúdo ao repertório do público. Inclui substituição de metáforas, expressões idiomáticas e construções figurativas por formas mais diretas.",
        "tipo": SimplificationStrategyType.LEXICAL
    },
    "MT+": {
        "nome": "Otimização de Títulos",
        "descricao": "Reformulação ou criação de títulos que tornem o conteúdo mais visível, explícito e tematicamente alinhado ao público-alvo.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "OM+": {
        "nome": "Supressão Seletiva",
        "descricao": "Exclusão de elementos redundantes, ambíguos, idiomáticos ou periféricos que não comprometem o núcleo do conteúdo e atrapalham a compreensão.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "PRO+": {
        "nome": "Desvio Semântico e/ou Interpretativo",
        "descricao": "Tag usada para anotação de problemas tradutórios de interpretação textual.",
        "tipo": SimplificationStrategyType.SEMANTIC
    },
    "RF+": {
        "nome": "Reescrita Global",
        "descricao": "Estratégia abrangente que integra múltiplos procedimentos de simplificação (lexical, sintática, discursiva). Visa à reformulação integral do texto para otimizar sua acessibilidade.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "RD+": {
        "nome": "Estruturação de Conteúdo e Fluxo",
        "descricao": "Reorganização macroestrutural do texto (sequência temática, paragrafação, uso de conectivos) para manter coerência, continuidade e progressão textual.",
        "tipo": SimplificationStrategyType.STRUCTURAL
    },
    "RP+": {
        "nome": "Fragmentação Sintática",
        "descricao": "Divisão de períodos extensos ou complexos em sentenças mais curtas e diretas, facilitando o processamento por parte de leitores com menor fluência.",
        "tipo": SimplificationStrategyType.SYNTACTIC
    },
    "SL+": {
        "nome": "Adequação de Vocabulário",
        "descricao": "Substituição de termos difíceis, técnicos ou raros por sinônimos mais simples, comuns ou hiperônimos. Também envolve evitar polissemia, jargões e repetições desnecessárias.",
        "tipo": SimplificationStrategyType.LEXICAL
    },
    "TA+": {
        "nome": "Clareza Referencial",
        "descricao": "Estratégias para garantir que pronomes e outras referências anafóricas sejam facilmente compreendidos. Inclui evitar catáforas e uso de sinônimos distantes ou ambíguos.",
        "tipo": SimplificationStrategyType.SYNTACTIC
    },
    "MV+": {
        "nome": "Alteração da Voz Verbal",
        "descricao": "Mudança da voz passiva para ativa (ou vice-versa) para garantir maior clareza, fluência e naturalidade. A escolha depende da necessidade de destacar ou omitir agentes.",
        "tipo": SimplificationStrategyType.SYNTACTIC
    }
}
