#!/usr/bin/env python3
"""
Simple demonstration script for M5: Confidence & Weighting Engine
Tests the new confidence functionality without Unicode issues
"""

import sys
import os
sys.path.append('backend')

from backend.src.services.confidence_engine import confidence_engine, ConfidenceFactor
from backend.src.services.comparative_analysis_service import ComparativeAnalysisService
from backend.src.models.comparative_analysis import ComparativeAnalysisRequest, AnalysisOptions
import asyncio

def test_confidence_engine_directly():
    """Test confidence engine with direct examples"""
    print("=" * 60)
    print("M5: Confidence & Weighting Engine - Direct Testing")
    print("=" * 60)

    # Test case 1: Lexical simplification (SL+)
    print("\nTest 1: Lexical Simplification (SL+)")
    print("-" * 40)

    features_sl = {
        "semantic_similarity": 0.85,
        "lexical_overlap": 0.25,
        "avg_word_length_ratio": 0.82,
        "explicitness_score": 0.7,
        "structure_change_score": 0.3,
        "length_ratio": 0.9
    }

    explanation_sl = confidence_engine.calculate_confidence("SL+", features_sl)
    print(f"Strategy: {explanation_sl.strategy_code}")
    print(f"Confidence: {explanation_sl.final_confidence:.3f}")
    print(f"Level: {explanation_sl.confidence_level.value}")
    print(f"Evidence Quality: {explanation_sl.evidence_quality}")

    print("\nFactor Breakdown:")
    for factor in explanation_sl.factors:
        print(f"  {factor.name}: {factor.value * factor.weight:.3f}")

    print("\nTop Contributors:")
    for i, (name, contribution) in enumerate(explanation_sl.get_top_contributors(3), 1):
        print(f"  {i}. {name}: {contribution:.3f}")

    if explanation_sl.recommendations:
        print("\nRecommendations:")
        for rec in explanation_sl.recommendations:
            print(f"  - {rec}")

    # Test case 2: Sentence fragmentation (RP+)
    print("\n\nTest 2: Sentence Fragmentation (RP+)")
    print("-" * 40)

    features_rp = {
        "semantic_similarity": 0.78,
        "sentence_count_ratio": 1.8,  # 80% increase
        "lexical_overlap": 0.4,
        "structure_change_score": 0.6,
        "complexity_reduction": 0.5,
        "length_ratio": 0.95
    }

    custom_factors_rp = [
        ConfidenceFactor(
            name="sentence_increase",
            value=0.8,
            weight=0.4,
            description="Extent of sentence fragmentation",
            evidence="Sentence count increased by 80%"
        )
    ]

    explanation_rp = confidence_engine.calculate_confidence(
        "RP+", features_rp, custom_factors=custom_factors_rp
    )

    print(f"Strategy: {explanation_rp.strategy_code}")
    print(f"Confidence: {explanation_rp.final_confidence:.3f}")
    print(f"Level: {explanation_rp.confidence_level.value}")

    print("\nFactor Breakdown:")
    for factor in explanation_rp.factors:
        print(f"  {factor.name}: {factor.value * factor.weight:.3f}")

    # Test case 3: Perspective reinterpretation (MOD+) - High confidence case
    print("\n\nTest 3: Perspective Reinterpretation (MOD+) - High Confidence")
    print("-" * 40)

    features_mod = {
        "semantic_similarity": 0.88,
        "lexical_overlap": 0.12,  # Very low lexical overlap
        "structure_change_score": 0.7,
        "voice_change_score": 0.3,
        "length_ratio": 0.92
    }

    explanation_mod = confidence_engine.calculate_confidence("MOD+", features_mod)
    print(f"Strategy: {explanation_mod.strategy_code}")
    print(f"Confidence: {explanation_mod.final_confidence:.3f}")
    print(f"Level: {explanation_mod.confidence_level.value}")

    # Test case 4: Global rewriting (RF+) - Very high confidence
    print("\n\nTest 4: Global Rewriting (RF+) - Very High Confidence")
    print("-" * 40)

    features_rf = {
        "semantic_similarity": 0.9,
        "lexical_overlap": 0.15,
        "structure_change_score": 0.85,
        "length_ratio": 0.88
    }

    explanation_rf = confidence_engine.calculate_confidence("RF+", features_rf)
    print(f"Strategy: {explanation_rf.strategy_code}")
    print(f"Confidence: {explanation_rf.final_confidence:.3f}")
    print(f"Level: {explanation_rf.confidence_level.value}")

    # Confidence summary
    print("\n\nConfidence Summary")
    print("-" * 40)

    explanations = [explanation_sl, explanation_rp, explanation_mod, explanation_rf]
    summary = confidence_engine.get_confidence_summary(explanations)

    print(f"Total Strategies: {summary['total_strategies']}")
    print(".3f")
    print(f"Confidence Distribution: {summary['confidence_distribution']}")
    print(f"High Confidence Strategies: {summary['high_confidence_strategies']}")
    print(f"Low Confidence Strategies: {summary['low_confidence_strategies']}")

async def test_confidence_engine_via_api():
    """Test confidence engine through the comparative analysis API"""
    print("\n\n" + "=" * 60)
    print("Testing Confidence Engine via API")
    print("=" * 60)

    try:
        service = ComparativeAnalysisService()

        # Test with Portuguese text pair
        source_text = "A Constituicao Federal de 1988 estabelece os principios fundamentais do Estado brasileiro, garantindo direitos e deveres aos cidadaos."
        target_text = "A Constituicao de 1988 define as bases do Estado brasileiro, assegurando direitos aos cidadaos."

        print(f"Source: {source_text}")
        print(f"Target: {target_text}")

        request = ComparativeAnalysisRequest(
            source_text=source_text,
            target_text=target_text,
            analysis_options=AnalysisOptions(
                include_lexical_analysis=True,
                include_syntactic_analysis=True,
                include_semantic_analysis=True,
                include_strategy_identification=True
            )
        )

        print("\nPerforming comparative analysis...")
        result = await service.perform_comparative_analysis(request)

        print("\nAnalysis completed successfully!")
        print(f"Strategies detected: {result.strategies_count}")
        print(".3f")
        print(".3f")

        if result.simplification_strategies:
            print("\nDetected Strategies:")
            for i, strategy in enumerate(result.simplification_strategies, 1):
                strategy_name = getattr(strategy, 'name', 'Unknown Strategy')
                strategy_code = getattr(strategy, 'sigla', getattr(strategy, 'type', 'Unknown'))
                print(f"\n  {i}. {strategy_name} ({strategy_code})")
                print(f"     Confidence: {strategy.confidence:.3f}")

                # Show new confidence explanation features
                if hasattr(strategy, 'confidence_explanation') and strategy.confidence_explanation:
                    exp = strategy.confidence_explanation
                    print(f"     Level: {exp.get('confidence_level', 'unknown')}")
                    print(f"     Evidence Quality: {exp.get('evidence_quality', 'unknown')}")

                    # Show top contributors
                    top_contrib = exp.get('top_contributors', [])
                    if top_contrib:
                        print("     Top Factors:")
                        for factor_name, contribution in top_contrib[:2]:
                            print(f"       - {factor_name}: {contribution:.3f}")

                    # Show recommendations
                    recommendations = exp.get('recommendations', [])
                    if recommendations:
                        print("     Recommendations:")
                        for rec in recommendations[:1]:
                            print(f"       - {rec}")
                else:
                    print("     (Legacy confidence - no detailed explanation)")

        return True

    except Exception as e:
        print(f"API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main demonstration function"""
    print("M5: Confidence & Weighting Engine - Live Demonstration")
    print("Windows 11 Environment - Human-in-the-Loop Testing")
    print("=" * 60)

    # Test confidence engine directly
    test_confidence_engine_directly()

    # Test via API
    try:
        result = asyncio.run(test_confidence_engine_via_api())
        if result:
            print("\nAll tests completed successfully!")
            print("Confidence Engine is working correctly")
            print("Enhanced confidence explanations are functional")
            print("Integration with comparative analysis is successful")
        else:
            print("\nSome tests failed - check the error messages above")
    except Exception as e:
        print(f"\nError running API tests: {e}")

    print("\n" + "=" * 60)
    print("Summary of M5 Features Demonstrated:")
    print("  - Unified confidence formula with explainability")
    print("  - Per-strategy confidence attribution")
    print("  - Enhanced user trust through transparency")
    print("  - Backward compatibility maintained")
    print("  - Real-time confidence calculations")
    print("=" * 60)

if __name__ == "__main__":
    main()