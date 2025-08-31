"""
Tests for the Confidence & Weighting Engine (M5)
"""

import pytest
from unittest.mock import Mock
from src.services.confidence_engine import (
    ConfidenceEngine,
    ConfidenceExplanation,
    ConfidenceFactor,
    StrategyConfidenceProfile,
    ConfidenceLevel
)


class TestConfidenceEngine:
    """Test suite for the unified confidence engine"""

    def setup_method(self):
        """Setup test fixtures"""
        self.engine = ConfidenceEngine()

    def test_engine_initialization(self):
        """Test that confidence engine initializes with default profiles"""
        assert self.engine.strategy_profiles is not None
        assert "SL+" in self.engine.strategy_profiles
        assert "RP+" in self.engine.strategy_profiles
        assert "RF+" in self.engine.strategy_profiles

    def test_default_profile_creation(self):
        """Test creation of default confidence profiles"""
        profile = StrategyConfidenceProfile.create_default("SL+")

        assert profile.strategy_code == "SL+"
        assert profile.base_confidence == 0.4
        assert "semantic_similarity" in profile.feature_weights
        assert "lexical_overlap" in profile.feature_weights

    def test_confidence_calculation_basic(self):
        """Test basic confidence calculation"""
        features = {
            "semantic_similarity": 0.8,
            "lexical_overlap": 0.3,
            "structure_change_score": 0.6,
            "length_ratio": 0.9
        }

        explanation = self.engine.calculate_confidence("SL+", features)

        assert isinstance(explanation, ConfidenceExplanation)
        assert explanation.strategy_code == "SL+"
        assert 0.0 <= explanation.final_confidence <= 1.0
        assert explanation.confidence_level in ConfidenceLevel
        assert len(explanation.factors) > 0

    def test_confidence_calculation_with_custom_factors(self):
        """Test confidence calculation with custom factors"""
        features = {
            "semantic_similarity": 0.7,
            "lexical_overlap": 0.4,
            "structure_change_score": 0.5
        }

        custom_factors = [
            ConfidenceFactor(
                name="custom_factor",
                value=0.8,
                weight=0.2,
                description="Custom test factor",
                evidence="Test evidence"
            )
        ]

        explanation = self.engine.calculate_confidence(
            "RP+",
            features,
            custom_factors=custom_factors
        )

        assert explanation.final_confidence > 0.0
        assert len(explanation.factors) >= 4  # Base factors + custom factor

    def test_confidence_levels(self):
        """Test confidence level categorization"""
        # Very low confidence
        explanation = self.engine.calculate_confidence("SL+", {"semantic_similarity": 0.1})
        assert explanation.confidence_level == ConfidenceLevel.VERY_LOW

        # High confidence
        explanation = self.engine.calculate_confidence("RF+", {
            "semantic_similarity": 0.9,
            "lexical_overlap": 0.1,
            "structure_change_score": 0.8
        })
        assert explanation.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]

    def test_factor_breakdown(self):
        """Test factor breakdown functionality"""
        features = {
            "semantic_similarity": 0.8,
            "lexical_overlap": 0.2,
            "structure_change_score": 0.7
        }

        explanation = self.engine.calculate_confidence("MOD+", features)

        breakdown = explanation.get_factor_breakdown()
        assert isinstance(breakdown, dict)
        assert len(breakdown) > 0

        # Check that all factors have reasonable contributions
        for factor_name, contribution in breakdown.items():
            assert isinstance(contribution, (int, float))

    def test_top_contributors(self):
        """Test top contributors identification"""
        features = {
            "semantic_similarity": 0.9,
            "lexical_overlap": 0.1,
            "structure_change_score": 0.8,
            "length_ratio": 0.95
        }

        explanation = self.engine.calculate_confidence("RF+", features)

        top_contributors = explanation.get_top_contributors(3)
        assert len(top_contributors) <= 3

        # Top contributors should be sorted by contribution
        if len(top_contributors) > 1:
            assert top_contributors[0][1] >= top_contributors[1][1]

    def test_recommendations_generation(self):
        """Test recommendations generation"""
        # Low semantic similarity case
        features = {
            "semantic_similarity": 0.3,
            "lexical_overlap": 0.8,
            "structure_change_score": 0.2
        }

        explanation = self.engine.calculate_confidence("SL+", features)

        assert len(explanation.recommendations) > 0
        assert any("semantic similarity" in rec.lower() for rec in explanation.recommendations)

    def test_evidence_quality_adjustment(self):
        """Test evidence quality adjustments"""
        features = {
            "semantic_similarity": 0.7,
            "lexical_overlap": 0.4,
            "structure_change_score": 0.5
        }

        # Strong evidence
        explanation_strong = self.engine.calculate_confidence(
            "RP+", features, evidence_quality="strong"
        )

        # Weak evidence
        explanation_weak = self.engine.calculate_confidence(
            "RP+", features, evidence_quality="weak"
        )

        # Strong evidence should generally have higher confidence
        assert explanation_strong.final_confidence >= explanation_weak.final_confidence

    def test_minimum_confidence_threshold(self):
        """Test minimum confidence threshold enforcement"""
        # Create features that would result in very low confidence
        features = {
            "semantic_similarity": 0.2,
            "lexical_overlap": 0.9,
            "structure_change_score": 0.1
        }

        explanation = self.engine.calculate_confidence("SL+", features)

        # Should be rejected if below minimum threshold
        profile = self.engine.get_strategy_profile("SL+")
        min_threshold = profile.quality_thresholds.get("min_confidence", 0.3)

        if explanation.final_confidence < min_threshold:
            assert explanation.final_confidence == 0.0

    def test_rf_strategy_high_confidence(self):
        """Test RF+ strategy with high confidence scenario"""
        features = {
            "semantic_similarity": 0.85,
            "lexical_overlap": 0.15,
            "structure_change_score": 0.9,
            "length_ratio": 0.95
        }

        explanation = self.engine.calculate_confidence("RF+", features)

        assert explanation.final_confidence > 0.7
        assert explanation.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]

    def test_mod_strategy_strict_threshold(self):
        """Test MOD+ strategy strict confidence threshold"""
        # High semantic similarity, low lexical overlap (classic MOD+ case)
        features = {
            "semantic_similarity": 0.88,
            "lexical_overlap": 0.12,
            "structure_change_score": 0.6,
            "voice_change_score": 0.3
        }

        explanation = self.engine.calculate_confidence("MOD+", features)

        # MOD+ should require very high confidence
        profile = self.engine.get_strategy_profile("MOD+")
        min_threshold = profile.quality_thresholds.get("min_confidence", 0.75)

        if explanation.final_confidence >= min_threshold:
            assert explanation.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
        else:
            assert explanation.final_confidence == 0.0

    def test_confidence_summary(self):
        """Test confidence summary generation"""
        explanations = [
            self.engine.calculate_confidence("SL+", {"semantic_similarity": 0.8}),
            self.engine.calculate_confidence("RP+", {"semantic_similarity": 0.6}),
            self.engine.calculate_confidence("RF+", {"semantic_similarity": 0.9, "lexical_overlap": 0.2})
        ]

        summary = self.engine.get_confidence_summary(explanations)

        assert "total_strategies" in summary
        assert "average_confidence" in summary
        assert "confidence_distribution" in summary
        assert "high_confidence_strategies" in summary
        assert "low_confidence_strategies" in summary

        assert summary["total_strategies"] == 3
        assert 0.0 <= summary["average_confidence"] <= 1.0

    def test_profile_update(self):
        """Test strategy profile updates"""
        new_profile = StrategyConfidenceProfile(
            strategy_code="TEST+",
            base_confidence=0.5,
            semantic_multiplier_weight=0.7,
            feature_weights={"test_feature": 0.3},
            quality_thresholds={"min_confidence": 0.4},
            evidence_requirements=["test_evidence"]
        )

        self.engine.update_strategy_profile("TEST+", new_profile)

        retrieved_profile = self.engine.get_strategy_profile("TEST+")
        assert retrieved_profile is not None
        assert retrieved_profile.base_confidence == 0.5

    def test_error_handling(self):
        """Test error handling in confidence calculation"""
        # Invalid strategy code - should gracefully degrade to default profile
        explanation = self.engine.calculate_confidence("INVALID+", {})

        # Should use default profile (base confidence 0.4) but may be adjusted down
        assert explanation.final_confidence >= 0.0
        assert explanation.confidence_level in ConfidenceLevel
        assert len(explanation.recommendations) > 0
        assert explanation.strategy_code == "INVALID+"

    def test_semantic_multiplier_bounds(self):
        """Test semantic multiplier stays within bounds"""
        # Very low semantic similarity
        features_low = {
            "semantic_similarity": 0.1,
            "lexical_overlap": 0.5,
            "structure_change_score": 0.5
        }

        # Very high semantic similarity
        features_high = {
            "semantic_similarity": 0.95,
            "lexical_overlap": 0.5,
            "structure_change_score": 0.5
        }

        explanation_low = self.engine.calculate_confidence("SL+", features_low)
        explanation_high = self.engine.calculate_confidence("SL+", features_high)

        # Both should produce valid confidence scores
        assert 0.0 <= explanation_low.final_confidence <= 1.0
        assert 0.0 <= explanation_high.final_confidence <= 1.0

        # Higher semantic similarity should generally produce higher confidence
        assert explanation_high.final_confidence >= explanation_low.final_confidence


if __name__ == "__main__":
    pytest.main([__file__])