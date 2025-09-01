#!/usr/bin/env python3
"""
Simple test for the new SL+ (Simplificação Lexical) semantic implementation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from services.strategy_detector import StrategyDetector, StrategyFeatures

def test_sl_detection():
    """Test the new SL+ detection algorithm with Portuguese text examples"""
    
    print("🧪 Testing SL+ (Simplificação Lexical) Semantic Detection")
    print("=" * 60)
    
    # Initialize detector
    detector = StrategyDetector()
    
    # Test cases from docs/tabela_est.md
    test_cases = [
        {
            "name": "Complex to Simple Word",
            "source": "Suas motivações foram bastante heterogêneas.",
            "target": "Suas motivações foram bastante diversas.",
            "expected": True
        },
        {
            "name": "Technical to Common Language", 
            "source": "O procedimento metodológico implementado demonstrou eficácia.",
            "target": "O método usado mostrou que funciona bem.",
            "expected": True
        },
        {
            "name": "No Lexical Simplification",
            "source": "O gato subiu na árvore.",
            "target": "O gato subiu na árvore alta.",
            "expected": False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['name']}")
        print(f"Source: {case['source']}")
        print(f"Target: {case['target']}")
        print(f"Expected SL+: {case['expected']}")
        
        try:
            # Test the detection
            strategies = detector.identify_strategies(case['source'], case['target'])
            sl_detected = any(s.sigla == 'SL+' for s in strategies)
            
            print(f"✅ SL+ Detected: {sl_detected}")
            
            if sl_detected:
                sl_strategy = next(s for s in strategies if s.sigla == 'SL+')
                print(f"   Confidence: {sl_strategy.confianca:.2f}")
                print(f"   Impact: {sl_strategy.impacto}")
                if sl_strategy.exemplos:
                    print(f"   Examples: {len(sl_strategy.exemplos)}")
            
            # Check if result matches expectation
            result = "✅ PASS" if sl_detected == case['expected'] else "❌ FAIL"
            print(f"   Result: {result}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n🎯 SL+ Implementation Test Complete!")

if __name__ == "__main__":
    test_sl_detection()