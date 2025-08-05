#!/usr/bin/env python3
"""
Paragraph-level vs Whole-text Analysis Comparison
Tests whether analyzing paragraphs individually yields more strategies
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.strategy_detector import StrategyDetector

def analyze_paragraph_vs_whole_text():
    """Compare paragraph-level vs whole-text strategy detection"""
    
    # Use the long text example from our previous tests
    long_source = """A informação genética do ser humano está armazenada nos cromossomos presentes no núcleo das células. Os cromossomos são estruturas complexas que contêm DNA e proteínas histonas, organizadas de forma específica para facilitar o acesso à informação genética durante os processos celulares.

O DNA (ácido desoxirribonucleico) é uma molécula de dupla hélice que contém a sequência de bases nitrogenadas (adenina, timina, guanina e citosina) responsável por codificar as instruções para a síntese de proteínas. Essa informação genética é transcrita em RNA mensageiro, que posteriormente é traduzido em proteínas pelos ribossomos no citoplasma celular.

Durante a divisão celular, especificamente na mitose, os cromossomos se condensam e se tornam visíveis ao microscópio óptico. Este processo garante que cada célula filha receba uma cópia idêntica da informação genética da célula mãe, mantendo assim a estabilidade genética do organismo ao longo do desenvolvimento e crescimento."""

    long_target = """A informação dos genes humanos fica guardada nos cromossomos dentro das células. Os cromossomos são estruturas que têm DNA e proteínas especiais, organizadas para facilitar o uso da informação genética.

O DNA é uma molécula em forma de dupla hélice. Ele contém uma sequência de bases (adenina, timina, guanina e citosina) que dão as instruções para fazer proteínas. Essa informação é copiada para o RNA mensageiro, que depois vira proteínas nos ribossomos.

Quando a célula se divide (mitose), os cromossomos ficam mais densos e podem ser vistos no microscópio. Isso garante que cada nova célula receba uma cópia igual da informação genética, mantendo a estabilidade dos genes."""

    print("=== PARAGRAPH-LEVEL vs WHOLE-TEXT ANALYSIS ===")
    
    strategy_detector = StrategyDetector()
    
    # Split into paragraphs
    source_paragraphs = [p.strip() for p in long_source.split('\n\n') if p.strip()]
    target_paragraphs = [p.strip() for p in long_target.split('\n\n') if p.strip()]
    
    print(f"Source paragraphs: {len(source_paragraphs)}")
    print(f"Target paragraphs: {len(target_paragraphs)}")
    
    # Whole-text analysis
    print("\n--- WHOLE-TEXT ANALYSIS ---")
    whole_text_strategies = strategy_detector.identify_strategies(long_source, long_target)
    print(f"Strategies detected: {len(whole_text_strategies)}")
    for strategy in whole_text_strategies:
        print(f"- {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})")
    
    # Paragraph-by-paragraph analysis
    print("\n--- PARAGRAPH-BY-PARAGRAPH ANALYSIS ---")
    all_paragraph_strategies = set()
    strategy_details = {}
    
    for i, (src_para, tgt_para) in enumerate(zip(source_paragraphs, target_paragraphs)):
        print(f"\nParagraph {i+1}:")
        print(f"  Source length: {len(src_para)} chars")
        print(f"  Target length: {len(tgt_para)} chars")
        
        para_strategies = strategy_detector.identify_strategies(src_para, tgt_para)
        print(f"  Strategies: {len(para_strategies)}")
        
        for strategy in para_strategies:
            print(f"    - {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})")
            all_paragraph_strategies.add(strategy.sigla)
            
            # Track the highest confidence for each strategy type
            if strategy.sigla not in strategy_details or strategy.confianca > strategy_details[strategy.sigla]['confidence']:
                strategy_details[strategy.sigla] = {
                    'confidence': strategy.confianca,
                    'name': strategy.nome,
                    'paragraph': i+1
                }
    
    # Summary comparison
    print("\n=== COMPARISON SUMMARY ===")
    whole_text_siglas = {s.sigla for s in whole_text_strategies}
    
    print(f"Whole-text strategies ({len(whole_text_siglas)}): {sorted(whole_text_siglas)}")
    print(f"Paragraph-level strategies ({len(all_paragraph_strategies)}): {sorted(all_paragraph_strategies)}")
    
    only_whole = whole_text_siglas - all_paragraph_strategies
    only_paragraph = all_paragraph_strategies - whole_text_siglas
    common = whole_text_siglas & all_paragraph_strategies
    
    print(f"Common strategies ({len(common)}): {sorted(common)}")
    if only_whole:
        print(f"Only detected in whole-text: {sorted(only_whole)}")
    if only_paragraph:
        print(f"Only detected in paragraph-level: {sorted(only_paragraph)}")
    
    print("\n=== DETAILED PARAGRAPH STRATEGY BREAKDOWN ===")
    for sigla in sorted(strategy_details.keys()):
        details = strategy_details[sigla]
        print(f"{sigla}: {details['name']} (max confidence: {details['confidence']:.3f}, paragraph {details['paragraph']})")
    
    # Calculate potential total if we combine approaches
    total_unique_strategies = len(whole_text_siglas | all_paragraph_strategies)
    print(f"\nCombined unique strategies: {total_unique_strategies}")
    
    print("\n=== ACADEMIC ASSESSMENT ===")
    print(f"Is {len(whole_text_strategies)} strategies realistic for a {len(long_source.split())} word text?")
    print(f"Would {total_unique_strategies} strategies be more academically sound?")
    
    # Calculate strategy density
    word_count = len(long_source.split())
    whole_density = len(whole_text_strategies) / word_count * 1000  # strategies per 1000 words
    combined_density = total_unique_strategies / word_count * 1000
    
    print(f"Strategy density - Whole-text: {whole_density:.1f} strategies/1000 words")
    print(f"Strategy density - Combined: {combined_density:.1f} strategies/1000 words")

if __name__ == "__main__":
    analyze_paragraph_vs_whole_text()
