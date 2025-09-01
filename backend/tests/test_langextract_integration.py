"""
LangExtract Integration Tests
Tests for the LangExtract provider and enhanced confidence calculations
"""

import pytest
from unittest.mock import Mock, patch
from src.services.langextract_provider import LangExtractProvider
from src.services.confidence_engine import confidence_engine
from src.strategies.cascade_orchestrator import CascadeOrchestrator


class TestLangExtractIntegration:
    """Test LangExtract integration with confidence engine"""

    def test_langextract_provider_initialization(self):
        """Test LangExtract provider initializes correctly"""
        provider = LangExtractProvider()

        # Should initialize with safe defaults
        assert provider.observation_mode == True
        assert provider.enabled == False  # Safe default
        assert provider.ab_testing_enabled == False

    @patch('src.services.langextract_provider.feature_flags')
    def test_langextract_feature_flags_loading(self, mock_feature_flags):
        """Test loading configuration from feature flags"""
        mock_feature_flags.get.return_value = {
            'enabled': True,
            'observation_mode': False,
            'ab_testing_enabled': True,
            'strategies': ['SL+', 'MOD+'],
            'monitoring': {
                'log_improvements': True,
                'alert_threshold': 0.1
            }
        }

        provider = LangExtractProvider()

        assert provider.enabled == True
        assert provider.observation_mode == False
        assert provider.ab_testing_enabled == True
        assert 'SL+' in provider.allowed_strategies
        assert 'MOD+' in provider.allowed_strategies
        assert provider.alert_threshold == 0.1

    def test_langextract_should_use_logic(self):
        """Test the decision logic for when to use LangExtract"""
        provider = LangExtractProvider()

        # With safe defaults, should not use LangExtract
        assert provider.should_use_langextract('SL+') == False
        assert provider.should_use_langextract('MOD+') == False

        # Mock enabled state
        provider.enabled = True
        provider.langextract_available = True
        provider.observation_mode = False

        # Should use for allowed strategies
        assert provider.should_use_langextract('SL+') == True
        assert provider.should_use_langextract('MOD+') == True
        assert provider.should_use_langextract('RF+') == True

        # Should not use for non-allowed strategies
        assert provider.should_use_langextract('TA+') == False

    def test_langextract_enhanced_features(self):
        """Test enhanced feature extraction"""
        provider = LangExtractProvider()

        text = "Texto complexo com termos técnicos difíceis de entender"
        features = provider.get_enhanced_features(text, 'SL+')

        # Should return feature dictionary
        assert isinstance(features, dict)
        assert 'base_salience_units' in features
        assert 'langextract_available' in features

        # Since LangExtract is not available, enhanced features should be minimal
        assert features['langextract_available'] == False

    @patch('src.services.confidence_engine.feature_flags')
    def test_confidence_engine_langextract_integration(self, mock_feature_flags):
        """Test confidence engine with LangExtract features"""
        mock_feature_flags.get.return_value = {}

        # Test basic confidence calculation
        explanation = confidence_engine.calculate_confidence(
            strategy_code='SL+',
            features={
                'semantic_similarity': 0.8,
                'lexical_overlap': 0.3,
                'structure_change_score': 0.2,
                'length_ratio': 0.9
            }
        )

        assert explanation.final_confidence > 0
        assert explanation.confidence_level.value in ['very_low', 'low', 'moderate', 'high', 'very_high']
        assert 'base_confidence' in explanation.get_factor_breakdown()

    def test_confidence_engine_with_langextract_features(self):
        """Test confidence engine with LangExtract-enhanced features"""
        langextract_features = {
            'langextract_available': True,
            'salience_improvement': 0.15,
            'quality_improvement': 0.1,
            'methods_overlap': 0.4
        }

        explanation = confidence_engine.calculate_confidence(
            strategy_code='SL+',
            features={
                'semantic_similarity': 0.8,
                'lexical_overlap': 0.3,
                'structure_change_score': 0.2,
                'length_ratio': 0.9
            },
            use_langextract=True,
            langextract_features=langextract_features
        )

        assert explanation.final_confidence > 0

        # Check if LangExtract factors are included
        factor_names = [f.name for f in explanation.factors]
        assert any('langextract' in name for name in factor_names)

    def test_cascade_orchestrator_langextract_integration(self):
        """Test cascade orchestrator with LangExtract integration"""
        orchestrator = CascadeOrchestrator()

        # Test with simple text pair
        source_text = "Texto complexo com palavras difíceis"
        target_text = "Texto simples com palavras fáceis"

        strategies = orchestrator.detect_strategies(source_text, target_text)

        # Should return strategies (may be empty if no strong matches)
        assert isinstance(strategies, list)

        # If strategies are found, they should have confidence information
        for strategy in strategies:
            assert hasattr(strategy, 'confianca')
            assert hasattr(strategy, 'confidence_explanation')
            assert strategy.confidence_explanation is not None

    def test_langextract_fallback_behavior(self):
        """Test that system gracefully falls back when LangExtract fails"""
        provider = LangExtractProvider()

        # Mock a failure scenario
        provider.langextract_available = False

        # Should still work with base provider
        base_result, langextract_result = provider.extract_with_langextract(
            "Test text", max_units=5
        )

        assert base_result is not None
        assert langextract_result is None  # Should be None when not available

    def test_confidence_engine_error_handling(self):
        """Test confidence engine handles errors gracefully"""
        # Test with invalid features
        explanation = confidence_engine.calculate_confidence(
            strategy_code='INVALID',
            features={}
        )

        # Should return valid explanation even with invalid input
        assert explanation.final_confidence == 0.0
        assert explanation.confidence_level.value == 'very_low'

    def test_langextract_monitoring_and_logging(self):
        """Test monitoring and logging functionality"""
        provider = LangExtractProvider()

        # Enable monitoring
        provider.log_improvements = True
        provider.alert_threshold = 0.05

        # Create mock results for comparison
        base_result = Mock()
        base_result.units = [Mock(weight=0.5), Mock(weight=0.6)]

        langextract_result = Mock()
        langextract_result.units = [Mock(weight=0.7), Mock(weight=0.8)]

        # Test comparison metrics
        metrics = provider.get_comparison_metrics(base_result, langextract_result)

        assert metrics['comparison_available'] == True
        assert metrics['quality_improvement'] > 0  # Should show improvement

    @pytest.mark.parametrize("strategy_code,expected_use", [
        ("SL+", True),
        ("MOD+", True),
        ("RF+", True),
        ("TA+", False),
        ("IN+", False),
    ])
    def test_strategy_specific_langextract_usage(self, strategy_code, expected_use):
        """Test strategy-specific LangExtract usage decisions"""
        provider = LangExtractProvider()

        # Configure for testing
        provider.enabled = True
        provider.langextract_available = True
        provider.observation_mode = False
        provider.allowed_strategies = ['SL+', 'MOD+', 'RF+']

        result = provider.should_use_langextract(strategy_code)
        assert result == expected_use


if __name__ == "__main__":
    # Run basic integration test
    print("🧪 Running LangExtract Integration Tests...")

    provider = LangExtractProvider()
    print(f"✅ Provider initialized: {provider.enabled}")

    # Test confidence engine
    explanation = confidence_engine.calculate_confidence(
        strategy_code='SL+',
        features={
            'semantic_similarity': 0.8,
            'lexical_overlap': 0.3,
            'structure_change_score': 0.2,
            'length_ratio': 0.9
        }
    )

    print(f"✅ Confidence calculation: {explanation.final_confidence:.3f}")
    print(f"✅ Confidence level: {explanation.confidence_level.value}")

    # Test cascade orchestrator
    orchestrator = CascadeOrchestrator()
    strategies = orchestrator.detect_strategies(
        "Texto complexo técnico",
        "Texto simples fácil"
    )

    print(f"✅ Cascade detection: {len(strategies)} strategies found")

    print("🎉 LangExtract integration test completed successfully!")