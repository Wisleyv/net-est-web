#!/usr/bin/env python3
"""
Debug script to investigate length-dependent strategy detection issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.strategy_detector import StrategyDetector

def test_length_sensitivity():
    """Test how strategy detection varies with text length using real user data"""
    
    detector = StrategyDetector()
    
    # Read the actual files provided by the user
    try:
        with open('../texto-fonte-curto.txt', 'r', encoding='utf-8') as f:
            short_source = f.read().strip()
        with open('../texto-alvo-curto.txt', 'r', encoding='utf-8') as f:
            short_target = f.read().strip()
        with open('../texto-fonte.txt', 'r', encoding='utf-8') as f:
            long_source = f.read().strip()
        with open('../texto-alvo.txt', 'r', encoding='utf-8') as f:
            long_target = f.read().strip()
    except FileNotFoundError as e:
        print(f"Error reading files: {e}")
        return
    
    print(f"Short text lengths: Source={len(short_source)}, Target={len(short_target)}")
    print(f"Long text lengths: Source={len(long_source)}, Target={len(long_target)}")
    print()
    
    # Test short text
    print("=== SHORT TEXT ANALYSIS ===")
    short_strategies = detector.identify_strategies(short_source, short_target, True, True)
    print(f"Strategies detected: {len(short_strategies)}")
    for strategy in short_strategies:
        print(f"- {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})")
    
    # Test semantic similarity for short text
    short_similarity = detector._calculate_semantic_similarity(short_source, short_target)
    print(f"Semantic similarity: {short_similarity:.3f}")
    
    # Extract features for short text
    short_features = detector._extract_features(short_source, short_target, short_similarity)
    print("Key features:")
    for key, value in short_features.items():
        if key in ['word_complexity_reduction', 'vocabulary_overlap', 'sentence_simplification', 'semantic_similarity']:
            print(f"  {key}: {value:.3f}")
    
    print("\n" + "="*50 + "\n")
    
    # Test long text
    print("=== LONG TEXT ANALYSIS ===")
    long_strategies = detector.identify_strategies(long_source, long_target, True, True)
    print(f"Strategies detected: {len(long_strategies)}")
    for strategy in long_strategies:
        print(f"- {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})")
    
    # Test semantic similarity for long text
    long_similarity = detector._calculate_semantic_similarity(long_source, long_target)
    print(f"Semantic similarity: {long_similarity:.3f}")
    
    # Extract features for long text
    long_features = detector._extract_features(long_source, long_target, long_similarity)
    print("Key features:")
    for key, value in long_features.items():
        if key in ['word_complexity_reduction', 'vocabulary_overlap', 'sentence_simplification', 'semantic_similarity']:
            print(f"  {key}: {value:.3f}")
    
    print("\n" + "="*50 + "\n")
    
    # Analysis
    print("=== DETAILED DIAGNOSTIC ANALYSIS ===")
    print(f"Similarity difference: {short_similarity - long_similarity:.3f}")
    print(f"Strategy count difference: {len(short_strategies) - len(long_strategies)}")
    
    # Compare strategies detected
    short_strat_names = {s.sigla for s in short_strategies}
    long_strat_names = {s.sigla for s in long_strategies}
    
    print(f"\nShort text strategies: {short_strat_names}")
    print(f"Long text strategies: {long_strat_names}")
    print(f"Identical strategies: {short_strat_names == long_strat_names}")
    
    # Compare confidence scores for identical strategies
    if short_strat_names == long_strat_names:
        print("\n🚨 CRITICAL ISSUE: Identical strategies detected for different texts!")
        print("Confidence score comparison:")
        for short_strat in short_strategies:
            for long_strat in long_strategies:
                if short_strat.sigla == long_strat.sigla:
                    diff = short_strat.confianca - long_strat.confianca
                    print(f"  {short_strat.sigla}: Short={short_strat.confianca:.3f}, Long={long_strat.confianca:.3f}, Diff={diff:.3f}")
    
    feature_diffs = {}
    for key in ['word_complexity_reduction', 'vocabulary_overlap', 'sentence_simplification']:
        diff = short_features[key] - long_features[key]
        feature_diffs[key] = diff
        print(f"{key} difference: {diff:.3f}")
    
    # Enhanced issue detection
    print("\n=== ISSUE ANALYSIS ===")
    if abs(short_similarity - long_similarity) > 0.1:
        print("⚠️  ISSUE: Semantic similarity varies significantly with text length")
    
    if len(short_strategies) != len(long_strategies):
        print(f"⚠️  ISSUE: Strategy count inconsistent ({len(short_strategies)} vs {len(long_strategies)})")
    elif short_strat_names == long_strat_names:
        print("🚨 CRITICAL: Same strategies detected for vastly different texts")
        print("   This indicates the system is not properly differentiating text complexity")
    
    if any(abs(diff) > 0.1 for diff in feature_diffs.values()):
        print("⚠️  ISSUE: Feature extraction varies significantly with text length")
    
    # Threshold analysis
    print("\n=== THRESHOLD ANALYSIS ===")
    print("Checking if our thresholds are too permissive...")
    
    # Check which features are triggering each strategy for short text
    print("\nShort text feature analysis:")
    for strategy in short_strategies:
        print(f"\n{strategy.sigla} ({strategy.confianca:.3f}):")
        if strategy.sigla == "RP+":
            print(f"  - sentence_count_ratio: {short_features.get('sentence_count_ratio', 'N/A')}")
            print(f"  - sentence_fragmentation: {short_features.get('sentence_fragmentation', 'N/A')}")
            print(f"  - sentence_simplification: {short_features.get('sentence_simplification', 'N/A')}")
        elif strategy.sigla == "RF+":
            print(f"  - vocabulary_overlap: {short_features.get('vocabulary_overlap', 'N/A')}")
            print(f"  - vocabulary_innovation: {short_features.get('vocabulary_innovation', 'N/A')}")
            print(f"  - readability_improvement: {short_features.get('readability_improvement', 'N/A')}")
        elif strategy.sigla == "MOD+":
            print(f"  - semantic_similarity: {short_features.get('semantic_similarity', 'N/A')}")
            print(f"  - vocabulary_overlap: {short_features.get('vocabulary_overlap', 'N/A')}")
            print(f"  - sentence_simplification: {short_features.get('sentence_simplification', 'N/A')}")
    
    print("\nLong text feature analysis:")
    for strategy in long_strategies:
        print(f"\n{strategy.sigla} ({strategy.confianca:.3f}):")
        if strategy.sigla == "RP+":
            print(f"  - sentence_count_ratio: {long_features.get('sentence_count_ratio', 'N/A')}")
            print(f"  - sentence_fragmentation: {long_features.get('sentence_fragmentation', 'N/A')}")
            print(f"  - sentence_simplification: {long_features.get('sentence_simplification', 'N/A')}")
        elif strategy.sigla == "RF+":
            print(f"  - vocabulary_overlap: {long_features.get('vocabulary_overlap', 'N/A')}")
            print(f"  - vocabulary_innovation: {long_features.get('vocabulary_innovation', 'N/A')}")
            print(f"  - readability_improvement: {long_features.get('readability_improvement', 'N/A')}")
        elif strategy.sigla == "MOD+":
            print(f"  - semantic_similarity: {long_features.get('semantic_similarity', 'N/A')}")
            print(f"  - vocabulary_overlap: {long_features.get('vocabulary_overlap', 'N/A')}")
            print(f"  - sentence_simplification: {long_features.get('sentence_simplification', 'N/A')}")

if __name__ == "__main__":
    test_length_sensitivity()
