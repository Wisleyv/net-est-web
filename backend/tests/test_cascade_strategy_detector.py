"""
Test suite for the new cascade strategy detector architecture
"""

import pytest
from unittest.mock import Mock, patch
from src.services.strategy_detector import StrategyDetector
from src.strategies import CascadeOrchestrator, MacroStageEvaluator, MesoStageEvaluator, MicroStageEvaluator


class TestCascadeStrategyDetector:
    """Test the cascade strategy detector implementation"""

    def test_cascade_orchestrator_initialization(self):
        """Test that cascade orchestrator initializes correctly"""
        mock_nlp = Mock()
        mock_semantic = Mock()

        orchestrator = CascadeOrchestrator(
            nlp_model=mock_nlp,
            semantic_model=mock_semantic,
            enable_performance_logging=True
        )

        assert orchestrator.nlp == mock_nlp
        assert orchestrator.semantic_model == mock_semantic
        assert orchestrator.enable_performance_logging is True

    def test_strategy_detector_uses_cascade(self):
        """Test that StrategyDetector uses the cascade orchestrator"""
        detector = StrategyDetector()

        # Verify cascade orchestrator was created and is accessible
        assert hasattr(detector, 'cascade_orchestrator')
        assert detector.cascade_orchestrator is not None

    def test_empty_text_handling(self):
        """Test handling of empty text inputs"""
        detector = StrategyDetector()

        result = detector.identify_strategies("", "")
        assert result == []

        result = detector.identify_strategies("text", "")
        assert result == []

        result = detector.identify_strategies("", "text")
        assert result == []

    def test_cascade_error_handling(self):
        """Test error handling in cascade detection"""
        with patch('src.services.strategy_detector._initialize_models') as mock_init, \
             patch('src.strategies.cascade_orchestrator.CascadeOrchestrator') as mock_orchestrator:

            mock_init.return_value = (None, None)
            mock_orchestrator_instance = Mock()
            mock_orchestrator_instance.detect_strategies.side_effect = Exception("Test error")
            mock_orchestrator.return_value = mock_orchestrator_instance

            detector = StrategyDetector()

            # Should return empty list on error, not crash
            result = detector.identify_strategies("source text", "target text")
            assert result == []

    def test_macro_stage_evaluator(self):
        """Test macro stage evaluator initialization"""
        macro_evaluator = MacroStageEvaluator(nlp_model=None, semantic_model=None)
        assert macro_evaluator.nlp is None
        assert macro_evaluator.semantic_model is None

    def test_meso_stage_evaluator(self):
        """Test meso stage evaluator initialization"""
        meso_evaluator = MesoStageEvaluator(nlp_model=None, semantic_model=None)
        assert meso_evaluator.nlp is None
        assert meso_evaluator.semantic_model is None

    def test_micro_stage_evaluator(self):
        """Test micro stage evaluator initialization"""
        micro_evaluator = MicroStageEvaluator(nlp_model=None, semantic_model=None)
        assert micro_evaluator.nlp is None
        assert micro_evaluator.semantic_model is None

    @pytest.mark.parametrize("source,target,expected_strategies", [
        ("", "", 0),  # Both empty - no strategies
        ("text", "", 0),  # Source only - no strategies (handled at StrategyDetector level)
        ("", "text", 1),  # Target only - should detect EXP+ (Explicitação e Detalhamento)
        ("source", "target", "variable"),  # Non-empty - variable results
    ])
    def test_cascade_orchestrator_empty_inputs(self, source, target, expected_strategies):
        """Test cascade orchestrator with various empty input combinations"""
        orchestrator = CascadeOrchestrator()

        result = orchestrator.detect_strategies(source, target)

        if expected_strategies == 0:
            assert result == []
        elif expected_strategies == 1:
            # Should detect EXP+ when target has content but source is empty
            assert len(result) >= 1
            assert any(strategy.sigla == "EXP+" for strategy in result)
        else:
            # For non-empty inputs, we expect some processing to occur
            assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__])