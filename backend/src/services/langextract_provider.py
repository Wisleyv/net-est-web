"""
LangExtract Provider - Enhanced Salience Extraction for NET-EST
Integrates LangExtract library for improved key-phrase detection
"""

from typing import List, Dict, Optional, Any, Tuple
import logging
from .salience_provider import SalienceProvider, SalienceResult
from ..core.feature_flags import feature_flags

logger = logging.getLogger(__name__)

class LangExtractProvider:
    """
    Enhanced salience provider with LangExtract integration.
    Provides observation mode and A/B testing capabilities.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_provider = SalienceProvider()
        self.langextract_available = self._check_langextract_availability()
        self._load_feature_flags()

        if self.langextract_available:
            self.logger.info("✅ LangExtract library detected - enhanced salience available")
        else:
            self.logger.info("ℹ️ LangExtract not available - using base salience provider")

    def _load_feature_flags(self):
        """Load LangExtract configuration from feature flags"""
        try:
            # Prefer module-level feature_flags (tests patch this symbol)
            experimental_flags = None
            try:
                if hasattr(feature_flags, 'get'):
                    # If get returns a dict for a general call, use it
                    try:
                        maybe = feature_flags.get('langextract_integration')
                        if maybe:
                            experimental_flags = maybe
                        else:
                            # Fall back to a general get() that returns full config
                            maybe_all = feature_flags.get()
                            if isinstance(maybe_all, dict) and maybe_all:
                                experimental_flags = maybe_all
                    except TypeError:
                        # Some mocks implement get with a single-arg signature; iterate known keys
                        for key in ('langextract_integration', 'langextract', 'experimental'):
                            try:
                                val = feature_flags.get(key)
                            except Exception:
                                val = None
                            if val:
                                experimental_flags = val
                                break
            except Exception:
                experimental_flags = None

            if experimental_flags is None:
                experimental_flags = getattr(feature_flags, 'flags', {}) or {}

            # If the returned value is nested under 'langextract_integration', unwrap it
            if isinstance(experimental_flags, dict) and 'langextract_integration' in experimental_flags:
                langextract_config = experimental_flags.get('langextract_integration', {})
            elif isinstance(experimental_flags, dict):
                langextract_config = experimental_flags
            else:
                langextract_config = {}

            # Tests may mock feature_flags.get to return a dict directly with 'enabled'
            # or return a nested structure. Support both by looking for 'enabled'.
            if isinstance(langextract_config, dict):
                self.enabled = bool(langextract_config.get("enabled", False))
            else:
                # If experimental_flags was a higher-level object, coerce
                try:
                    self.enabled = bool(getattr(experimental_flags, 'get', lambda k, d=None: d)('enabled', False))
                except Exception:
                    self.enabled = False
            self.observation_mode = bool(langextract_config.get("observation_mode", True))
            self.ab_testing_enabled = bool(langextract_config.get("ab_testing_enabled", False))
            self.allowed_strategies = langextract_config.get("strategies", ["SL+", "MOD+", "RF+"])

            monitoring_config = langextract_config.get("monitoring", {}) if isinstance(langextract_config, dict) else {}
            self.log_improvements = bool(monitoring_config.get("log_improvements", True))
            self.track_performance = bool(monitoring_config.get("track_performance", True))
            self.alert_threshold = float(monitoring_config.get("alert_threshold", 0.05))

        except Exception as e:
            # Safe defaults if feature flags fail to load
            self.logger.warning(f"Failed to load LangExtract feature flags: {e}")
            self.enabled = False
            self.observation_mode = True
            self.ab_testing_enabled = False
            self.allowed_strategies = ["SL+", "MOD+", "RF+"]
            self.log_improvements = True
            self.track_performance = True
            self.alert_threshold = 0.05

    def _check_langextract_availability(self) -> bool:
        """Check if LangExtract library is available"""
        try:
            # Placeholder for LangExtract import
            # import langextract as le  # When library becomes available
            # self.langextract_model = le.KeyPhraseExtractor()
            return False  # Currently not available
        except ImportError:
            return False

    def extract_with_langextract(
        self,
        text: str,
        max_units: int = 15,
        strategy_context: Optional[str] = None
    ) -> Tuple[SalienceResult, Optional[SalienceResult]]:
        """
        Extract salience using both base and LangExtract methods.
        Returns (base_result, langextract_result) for comparison.
        """
        # Always get base result
        base_result = self.base_provider.extract(text, max_units)

        # Get LangExtract result if available
        langextract_result = None
        if self.langextract_available and not self.observation_mode:
            try:
                langextract_result = self._extract_langextract(text, max_units, strategy_context)
            except Exception as e:
                self.logger.warning(f"LangExtract extraction failed: {e}")
                langextract_result = None

        return base_result, langextract_result

    def _extract_langextract(
        self,
        text: str,
        max_units: int,
        strategy_context: Optional[str] = None
    ) -> SalienceResult:
        """
        Extract key phrases using LangExtract.
        This is a placeholder implementation for when LangExtract becomes available.
        """
        # Placeholder implementation
        # When LangExtract is available, this will be replaced with actual implementation

        units = []

        # Simulate LangExtract behavior with enhanced Portuguese key phrase detection
        # This would be replaced with actual LangExtract API calls

        portuguese_key_indicators = [
            'importante', 'fundamental', 'essencial', 'principal', 'básico',
            'complexo', 'difícil', 'fácil', 'simples', 'claro',
            'técnico', 'especializado', 'comum', 'geral',
            'específico', 'particular', 'geral', 'universal'
        ]

        words = text.lower().split()
        for i, word in enumerate(words):
            if word in portuguese_key_indicators:
                # Find phrase context
                start = max(0, i-2)
                end = min(len(words), i+3)
                phrase = ' '.join(words[start:end])

                # Calculate enhanced weight based on context
                base_weight = 0.7
                if strategy_context == 'SL+':
                    # For lexical simplification, weight technical terms higher
                    if word in ['complexo', 'técnico', 'especializado']:
                        base_weight = 0.9
                    elif word in ['simples', 'fácil', 'claro']:
                        base_weight = 0.8

                units.append({
                    'unit': phrase,
                    'weight': base_weight,
                    'span': (text.lower().find(phrase), text.lower().find(phrase) + len(phrase)),
                    'method': 'langextract_enhanced'
                })

                if len(units) >= max_units:
                    break

        return SalienceResult(units, 'langextract_enhanced')

    def get_comparison_metrics(
        self,
        base_result: SalienceResult,
        langextract_result: Optional[SalienceResult]
    ) -> Dict[str, Any]:
        """Compare base and LangExtract results for A/B testing"""
        if not langextract_result:
            return {
                'comparison_available': False,
                'base_units': len(base_result.units),
                'langextract_units': 0,
                'overlap_score': 0.0,
                'quality_improvement': 0.0
            }

        # Calculate overlap between methods
        # Support both dict-like unit objects and Mock objects used in tests
        def unit_text(u):
            try:
                return u['unit']
            except Exception:
                return getattr(u, 'unit', None)

        def unit_weight(u):
            try:
                return u['weight']
            except Exception:
                return getattr(u, 'weight', 0.0)

        base_units = {unit_text(unit) for unit in base_result.units}
        langextract_units = {unit_text(unit) for unit in langextract_result.units}

        overlap = len(base_units.intersection(langextract_units))
        union = len(base_units.union(langextract_units))

        overlap_score = overlap / max(union, 1)

        # Calculate quality improvement (simplified metric)
        base_avg_weight = sum(unit_weight(u) for u in base_result.units) / max(len(base_result.units), 1)
        langextract_avg_weight = sum(unit_weight(u) for u in langextract_result.units) / max(len(langextract_result.units), 1)

        quality_improvement = langextract_avg_weight - base_avg_weight

        # Prepare comparison dict
        comparison = {
            'comparison_available': True,
            'base_units': len(base_result.units),
            'langextract_units': len(langextract_result.units),
            'overlap_score': overlap_score,
            'quality_improvement': quality_improvement,
            'base_avg_weight': base_avg_weight,
            'langextract_avg_weight': langextract_avg_weight
        }

        # Log comparison metrics if monitoring is enabled
        if getattr(self, 'log_improvements', False) and quality_improvement != 0.0:
            self._log_comparison_metrics(base_result, langextract_result, comparison)

        return comparison

    def _log_comparison_metrics(self, base_result: SalienceResult, langextract_result: SalienceResult, metrics: Dict[str, Any]):
        """Log comparison metrics for monitoring and analysis"""
        if not self.log_improvements:
            return

        quality_improvement = metrics.get('quality_improvement', 0.0)

        # Log significant improvements or degradations
        if abs(quality_improvement) >= self.alert_threshold:
            log_level = "INFO" if quality_improvement > 0 else "WARNING"
            self.logger.log(
                logging.INFO if quality_improvement > 0 else logging.WARNING,
                f"LangExtract {'improvement' if quality_improvement > 0 else 'degradation'}: "
                f"{quality_improvement:.3f} | Base: {metrics.get('base_avg_weight', 0):.3f} | "
                f"Enhanced: {metrics.get('langextract_avg_weight', 0):.3f} | "
                f"Overlap: {metrics.get('overlap_score', 0):.3f}"
            )

        # Always log in debug mode for detailed analysis
        self.logger.debug(
            f"LangExtract comparison - Quality: {quality_improvement:.3f}, "
            f"Overlap: {metrics.get('overlap_score', 0):.3f}, "
            f"Base units: {len(base_result.units)}, "
            f"Enhanced units: {len(langextract_result.units)}"
        )

    def should_use_langextract(self, strategy_code: str) -> bool:
        """Determine if LangExtract should be used for a specific strategy"""
        # Check if LangExtract integration is enabled
        if not self.enabled:
            return False

        # Check if LangExtract library is available
        if not self.langextract_available:
            return False

        # In observation mode, always return False (passive monitoring only)
        if self.observation_mode:
            return False

        # Check if strategy is in allowed list
        if strategy_code not in self.allowed_strategies:
            return False

        # A/B testing logic (placeholder for future implementation)
        if self.ab_testing_enabled:
            # For now, use simple strategy-based decision
            return True

        return True

    def get_enhanced_features(
        self,
        text: str,
        strategy_code: str,
        max_units: int = 15
    ) -> Dict[str, Any]:
        """
        Get enhanced features for confidence calculation.
        Includes both base and LangExtract-enhanced salience metrics.
        """
        base_result, langextract_result = self.extract_with_langextract(
            text, max_units, strategy_code
        )

        features = {
            'base_salience_units': len(base_result.units),
            'base_avg_salience_weight': sum(u['weight'] for u in base_result.units) / max(len(base_result.units), 1),
            'langextract_available': langextract_result is not None,
        }

        if langextract_result:
            # Compute average first to avoid referencing a key not yet in features
            langextract_avg = (
                sum(u['weight'] for u in langextract_result.units)
                / max(len(langextract_result.units), 1)
            )
            features.update({
                'langextract_units': len(langextract_result.units),
                'langextract_avg_weight': langextract_avg,
                'salience_improvement': langextract_avg - features['base_avg_salience_weight']
            })

            # Add comparison metrics
            comparison = self.get_comparison_metrics(base_result, langextract_result)
            features.update({
                'methods_overlap': comparison['overlap_score'],
                'quality_improvement': comparison['quality_improvement']
            })

        return features

# Global instance
langextract_provider = LangExtractProvider()