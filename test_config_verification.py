#!/usr/bin/env python3
"""
Test script to verify configuration and strategy detection behavior
"""

import sys
import os

# Add the backend src directory to the path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

from core.config import settings
from services.strategy_detector import StrategyDetector

def test_configuration():
    """Test that configuration is loaded correctly"""
    print("=== Configuration Test ===")
    print(f"STRATEGY_DETECTION_MODE: {settings.STRATEGY_DETECTION_MODE}")
    print(f"MAX_SENTENCES_FOR_PERFORMANCE: {settings.MAX_SENTENCES_FOR_PERFORMANCE}")
    print()

def test_strategy_detector():
    """Test strategy detector with sample text"""
    print("=== Strategy Detector Test ===")

    # Create a long text with multiple sentences
    source_text = (
        "Este é o primeiro parágrafo com várias frases importantes. "
        "Ele contém informações relevantes sobre o tema principal. "
        "Os pesquisadores realizaram um estudo detalhado e abrangente. "
        "Foram analisadas mais de cem amostras diferentes no laboratório. "
        "Os resultados mostraram tendências interessantes e significativas. "
        "Em particular, houve um aumento significativo nos indicadores. "
        "Este aumento foi observado em diversos contextos experimentais. "
        "Os especialistas discutiram as implicações dos achados. "
        "Foram propostas várias hipóteses explicativas para os fenômenos. "
        "Algumas hipóteses foram confirmadas experimentalmente. "
        "Outras necessitam de validação adicional em estudos futuros. "
        "O debate científico continua ativo na comunidade acadêmica. "
        "Novos métodos estão sendo desenvolvidos constantemente. "
        "A colaboração internacional é fundamental para o progresso. "
        "Os avanços prometem benefícios significativos para a sociedade."
    )

    target_text = (
        "Este é o primeiro parágrafo com frases importantes. "
        "Ele contém informações sobre o tema. "
        "Os pesquisadores fizeram um estudo. "
        "Foram analisadas amostras no laboratório. "
        "Os resultados mostraram tendências. "
        "Houve um aumento nos indicadores. "
        "Este aumento foi observado. "
        "Os especialistas discutiram. "
        "Foram propostas hipóteses. "
        "Algumas foram confirmadas. "
        "Outras necessitam validação. "
        "O debate continua. "
        "Novos métodos estão sendo criados. "
        "A colaboração é importante. "
        "Os avanços prometem benefícios."
    )

    # Count sentences
    source_sentences = source_text.split('. ')
    target_sentences = target_text.split('. ')

    print(f"Source sentences: {len(source_sentences)}")
    print(f"Target sentences: {len(target_sentences)}")
    print()

    # Test strategy detection
    detector = StrategyDetector()
    strategies = detector.identify_strategies(source_text, target_text)

    print(f"Detected strategies: {len(strategies)}")
    for i, strategy in enumerate(strategies):
        print(f"  {i+1}. {strategy.sigla} - {strategy.nome} (conf: {strategy.confiança:.3f})")

    print()
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_configuration()
    test_strategy_detector()