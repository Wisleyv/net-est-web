#!/usr/bin/env python3
"""
Test script to verify backend position tracking for strategies
"""

import sys
import os

# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Import the StrategyDetector
import importlib.util
spec = importlib.util.spec_from_file_location("strategy_detector", os.path.join(os.path.dirname(__file__), 'backend', 'src', 'services', 'strategy_detector.py'))
strategy_detector_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strategy_detector_module)
StrategyDetector = strategy_detector_module.StrategyDetector

def test_backend_positions():
    # Test with the actual text files
    with open('test_files/text_pairs/texto-fonte.txt', 'r', encoding='utf-8') as f:
        source_text = f.read()

    with open('test_files/text_pairs/texto-alvo.txt', 'r', encoding='utf-8') as f:
        target_text = f.read()

    print(f'Source text length: {len(source_text)} characters')
    print(f'Target text length: {len(target_text)} characters')

    # Count paragraphs
    source_paragraphs = [p.strip() for p in source_text.split('\n\n') if p.strip()]
    target_paragraphs = [p.strip() for p in target_text.split('\n\n') if p.strip()]
    print(f'Source paragraphs: {len(source_paragraphs)}')
    print(f'Target paragraphs: {len(target_paragraphs)}')

    detector = StrategyDetector()
    strategies = detector.identify_strategies(source_text, target_text)

    print(f'\nDetected strategies: {len(strategies)}')
    for i, strategy in enumerate(strategies):
        print(f'{i+1}. {strategy.sigla}: {strategy.nome} (confidence: {strategy.confianca:.3f})')
        if hasattr(strategy, 'targetPosition') and strategy.targetPosition:
            print(f'   Target Position: {strategy.targetPosition}')
        if hasattr(strategy, 'sourcePosition') and strategy.sourcePosition:
            print(f'   Source Position: {strategy.sourcePosition}')
        print()

if __name__ == "__main__":
    test_backend_positions()