#!/usr/bin/env python3
"""
Length Disparity Test - 65% Reduction Scenario
Tests how semantic similarity behaves with dramatic length differences
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.strategy_detector import StrategyDetector

def test_length_disparity():
    """Test semantic similarity with 65% text reduction"""
    
    print("=== LENGTH DISPARITY TEST (65% REDUCTION) ===")
    
    # Create a realistic academic text and its 65% reduced version
    source_text = """A informação genética dos organismos eucariotos encontra-se armazenada em estruturas altamente organizadas denominadas cromossomos, que estão localizados no núcleo celular. Estes cromossomos são constituídos por uma complexa associação entre ácido desoxirribonucleico (DNA) e proteínas especializadas conhecidas como histonas, que desempenham um papel fundamental na organização e compactação do material genético. Durante os processos de replicação e transcrição, esta organização cromossômica permite o acesso controlado às sequências de DNA que contêm as informações necessárias para a síntese de proteínas funcionais.

O processo de expressão gênica envolve múltiplas etapas altamente reguladas, iniciando-se com a transcrição do DNA em RNA mensageiro (mRNA) no núcleo celular. Esta molécula de mRNA é posteriormente processada através de modificações pós-transcricionais, incluindo a adição de uma estrutura cap na extremidade 5' e uma cauda poli-A na extremidade 3', além do splicing alternativo que remove os íntrons e une os éxons. Após esse processamento, o mRNA maduro é transportado do núcleo para o citoplasma, onde ocorre a tradução nos ribossomos, resultando na síntese de proteínas específicas que desempenharão funções celulares essenciais.

Durante o ciclo celular, particularmente na fase mitótica, os cromossomos sofrem um processo de condensação extrema que os torna visíveis ao microscópio óptico convencional. Este fenômeno de condensação cromossômica é mediado por complexos proteicos especializados e é essencial para garantir a distribuição equitativa do material genético entre as células filhas resultantes da divisão celular. A manutenção da integridade cromossômica durante este processo é fundamental para preservar a estabilidade genética do organismo e prevenir alterações que poderiam resultar em patologias."""
    
    # 65% reduced version (target should be ~35% of source length)
    target_text = """Os genes ficam nos cromossomos dentro do núcleo da célula. Os cromossomos têm DNA e proteínas especiais que organizam o material genético.

Para fazer proteínas, primeiro o DNA vira RNA no núcleo. Depois o RNA vai para o citoplasma onde vira proteína nos ribossomos.

Na divisão celular, os cromossomos ficam condensados e visíveis no microscópio. Isso garante que cada célula filha receba os genes certos."""
    
    source_words = len(source_text.split())
    target_words = len(target_text.split())
    reduction_percentage = ((source_words - target_words) / source_words) * 100
    target_percentage = (target_words / source_words) * 100
    
    print(f"Source text: {source_words} words")
    print(f"Target text: {target_words} words")
    print(f"Reduction: {reduction_percentage:.1f}%")
    print(f"Target is {target_percentage:.1f}% of source length")
    print()
    
    strategy_detector = StrategyDetector()
    
    # Test semantic similarity
    print("--- SEMANTIC SIMILARITY TEST ---")
    try:
        similarity = strategy_detector._calculate_semantic_similarity(source_text, target_text)
        print(f"Semantic similarity: {similarity:.3f}")
        
        if similarity > 0.7:
            print("✅ High similarity detected despite length disparity")
        elif similarity > 0.5:
            print("⚠️ Moderate similarity - may need adjustment")
        else:
            print("❌ Low similarity - length disparity may be breaking detection")
            
    except Exception as e:
        print(f"❌ Error in similarity calculation: {e}")
    
    # Test paragraph-level similarity
    print("\n--- PARAGRAPH-LEVEL SIMILARITY TEST ---")
    source_paragraphs = [p.strip() for p in source_text.split('\n\n') if p.strip()]
    target_paragraphs = [p.strip() for p in target_text.split('\n\n') if p.strip()]
    
    print(f"Source paragraphs: {len(source_paragraphs)}")
    print(f"Target paragraphs: {len(target_paragraphs)}")
    
    # Test each paragraph pair
    for i, (src_para, tgt_para) in enumerate(zip(source_paragraphs, target_paragraphs)):
        src_words = len(src_para.split())
        tgt_words = len(tgt_para.split())
        para_reduction = ((src_words - tgt_words) / src_words) * 100 if src_words > 0 else 0
        
        try:
            para_similarity = strategy_detector._calculate_semantic_similarity(src_para, tgt_para)
            print(f"Paragraph {i+1}: {para_similarity:.3f} similarity ({para_reduction:.1f}% reduction)")
        except Exception as e:
            print(f"Paragraph {i+1}: Error - {e}")
    
    # Test strategy detection with such disparity
    print("\n--- STRATEGY DETECTION WITH LENGTH DISPARITY ---")
    try:
        strategies = strategy_detector.identify_strategies(source_text, target_text)
        print(f"Strategies detected: {len(strategies)}")
        for strategy in strategies:
            print(f"- {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})")
            
    except Exception as e:
        print(f"❌ Error in strategy detection: {e}")
    
    # Test feature extraction
    print("\n--- FEATURE EXTRACTION WITH LENGTH DISPARITY ---")
    try:
        similarity = strategy_detector._calculate_semantic_similarity(source_text, target_text)
        features = strategy_detector._extract_features(source_text, target_text, similarity)
        
        key_features = [
            'word_reduction', 'sentence_reduction', 'vocabulary_overlap',
            'semantic_similarity', 'readability_improvement'
        ]
        
        for feature in key_features:
            if feature in features:
                print(f"{feature}: {features[feature]:.3f}")
                
    except Exception as e:
        print(f"❌ Error in feature extraction: {e}")
    
    print("\n=== ACADEMIC VALIDITY ASSESSMENT ===")
    print("Can the model reliably detect semantic correspondence with 65% reduction?")
    
    # Test extreme cases
    print("\n--- EXTREME REDUCTION TEST ---")
    extreme_target = "Genes nos cromossomos. DNA vira proteína."
    extreme_words = len(extreme_target.split())
    extreme_reduction = ((source_words - extreme_words) / source_words) * 100
    
    print(f"Extreme target: {extreme_words} words ({extreme_reduction:.1f}% reduction)")
    
    try:
        extreme_similarity = strategy_detector._calculate_semantic_similarity(source_text, extreme_target)
        print(f"Extreme similarity: {extreme_similarity:.3f}")
        
        if extreme_similarity > 0.3:
            print("⚠️ Model may be too permissive - detecting similarity in overly reduced text")
        else:
            print("✅ Model correctly identifies when reduction is too extreme")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== RECOMMENDATIONS ===")
    print("1. Test if semantic models can handle 65% reduction reliably")
    print("2. Consider length-adjusted similarity thresholds")
    print("3. Evaluate paragraph-level vs whole-text performance")
    print("4. Test with real translation pairs at target reduction levels")

if __name__ == "__main__":
    test_length_disparity()
