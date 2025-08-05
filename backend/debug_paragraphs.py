#!/usr/bin/env python3
"""
Paragraph Preservation Diagnostic Script
Tests whether paragraph breaks are preserved throughout the text processing pipeline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.text_input_service import TextInputService
from src.services.strategy_detector import StrategyDetector

def test_paragraph_preservation():
    """Test if paragraph breaks are preserved during processing"""
    
    # Create a test text with clear paragraph breaks
    test_text = """Este é o primeiro parágrafo do texto de teste.
Ele contém várias frases para demonstrar a estrutura.

Este é o segundo parágrafo, separado por uma linha em branco.
Ele também contém múltiplas frases.

Este é o terceiro parágrafo.
Vamos ver se as quebras de parágrafo são preservadas durante o processamento."""

    print("=== PARAGRAPH PRESERVATION DIAGNOSTIC ===")
    print(f"Original text (with repr to show \\n):")
    print(repr(test_text))
    print(f"\nOriginal text paragraphs (split by \\n\\n): {len(test_text.split('\\n\\n'))}")
    
    # Test TextInputService cleaning
    text_service = TextInputService()
    
    print("\n--- TextInputService.clean_text() ---")
    cleaned_text = text_service.clean_text(test_text)
    print(f"Cleaned text (with repr):")
    print(repr(cleaned_text))
    print(f"Cleaned text paragraphs (split by \\n\\n): {len(cleaned_text.split('\\n\\n'))}")
    
    print("\n--- TextInputService.segment_paragraphs() ---")
    paragraphs = text_service.segment_paragraphs(cleaned_text)
    print(f"Segmented paragraphs: {len(paragraphs)}")
    for i, para in enumerate(paragraphs):
        print(f"  Paragraph {i+1}: {repr(para[:50])}...")
    
    # Test if paragraphs are joined when passed to strategy detector
    print("\n--- Strategy Detector Input ---")
    strategy_detector = StrategyDetector()
    
    # Test what happens when we pass the cleaned text directly
    print(f"Text passed to strategy detector (with repr):")
    print(repr(cleaned_text))
    
    # Test the semantic similarity calculation
    print("\n--- Strategy Detector Semantic Similarity ---")
    try:
        semantic_similarity = strategy_detector._calculate_semantic_similarity(cleaned_text, cleaned_text)
        print(f"Semantic similarity (same text): {semantic_similarity}")
    except Exception as e:
        print(f"Error in semantic similarity: {e}")
    
    # Test paragraph detection in _extract_features
    print("\n--- Strategy Detector Paragraph Detection ---")
    try:
        # Let's see what _extract_features thinks about paragraphs
        semantic_similarity = strategy_detector._calculate_semantic_similarity(cleaned_text, cleaned_text)
        features = strategy_detector._extract_features(cleaned_text, cleaned_text, semantic_similarity)
        if 'source_paragraphs' in features:
            print(f"Source paragraphs detected by _extract_features: {features['source_paragraphs']}")
        if 'target_paragraphs' in features:
            print(f"Target paragraphs detected by _extract_features: {features['target_paragraphs']}")
    except Exception as e:
        print(f"Error in feature extraction: {e}")
    
    print("\n=== CONCLUSION ===")
    original_paras = len(test_text.split('\n\n'))
    cleaned_paras = len(cleaned_text.split('\n\n'))
    segmented_paras = len(paragraphs)
    
    if original_paras == cleaned_paras == segmented_paras:
        print("✅ Paragraph breaks are preserved throughout the pipeline")
    else:
        print("❌ Paragraph breaks are being lost or modified:")
        print(f"   Original: {original_paras} paragraphs")
        print(f"   Cleaned: {cleaned_paras} paragraphs")
        print(f"   Segmented: {segmented_paras} paragraphs")

if __name__ == "__main__":
    test_paragraph_preservation()
