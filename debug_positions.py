#!/usr/bin/env python3
"""
Debug position calculation specifically
"""

import sys
sys.path.insert(0, 'backend/src')

from strategies.stage_meso import MesoStageEvaluator
from strategies.stage_micro import MicroStageEvaluator
from strategies.feature_extractor import FeatureExtractor

def test_position_calculation():
    """Test position calculation logic"""

    # Test text
    source_text = "Este é um texto complexo com muitas ideias. Ele contém conceitos importantes. Os pesquisadores desenvolveram uma metodologia detalhada."
    target_text = "Este é um texto simples. Ele contém conceitos básicos. Os pesquisadores criaram um método. Esta é uma ideia adicional. Mais uma informação relevante."

    print("SOURCE TEXT:")
    print(source_text)
    print(f"Length: {len(source_text)}")
    print()

    print("TARGET TEXT:")
    print(target_text)
    print(f"Length: {len(target_text)}")
    print()

    # Test sentence splitting
    meso_evaluator = MesoStageEvaluator()
    src_sentences = meso_evaluator._split_into_sentences(source_text)
    tgt_sentences = meso_evaluator._split_into_sentences(target_text)

    print("SOURCE SENTENCES:")
    for i, sent in enumerate(src_sentences):
        print(f"  {i}: '{sent}' (len={len(sent)})")
    print()

    print("TARGET SENTENCES:")
    for i, sent in enumerate(tgt_sentences):
        print(f"  {i}: '{sent}' (len={len(sent)})")
    print()

    # Test position finding
    print("POSITION TESTING:")
    for i, src_sent in enumerate(src_sentences):
        print(f"Looking for sentence {i}: '{src_sent[:50]}...'")

        # Find in source text
        start_pos = source_text.find(src_sent)
        if start_pos != -1:
            end_pos = start_pos + len(src_sent)
            print(f"  Found at position: ({start_pos}, {end_pos})")
        else:
            print("  Not found in source text!")
        print()

if __name__ == "__main__":
    test_position_calculation()