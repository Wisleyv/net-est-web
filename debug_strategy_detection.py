#!/usr/bin/env python3
"""
Systematic Debugging Script for Strategy Detection Issue
Following software engineering best practices for persistent bug resolution

PHASE 1: Comprehensive Logging & Instrumentation
PHASE 2: Isolated Component Testing
PHASE 3: Step-by-Step Pipeline Verification
PHASE 4: Execution Flow Tracing
"""

import sys
import os
import logging
import time
from typing import List, Dict, Any

# Setup comprehensive logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_strategy_detection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Add backend src to path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, backend_src)

# Change to backend directory to fix relative imports
os.chdir(os.path.join(os.path.dirname(__file__), 'backend'))

def phase_1_comprehensive_logging():
    """PHASE 1: Add comprehensive logging to trace sentence processing"""
    logger.info("=" * 80)
    logger.info("PHASE 1: COMPREHENSIVE LOGGING & INSTRUMENTATION")
    logger.info("=" * 80)

    # Test data with clear sentence boundaries
    source_text = """Esta é a primeira sentença do texto fonte.
Esta é a segunda sentença com mais detalhes.
Esta é a terceira sentença que continua o raciocínio.
Esta é a quarta sentença com informações adicionais.
Esta é a quinta sentença que aprofunda o tema.
Esta é a sexta sentença com exemplos concretos.
Esta é a sétima sentença que conclui a primeira parte.
Esta é a oitava sentença iniciando nova seção.
Esta é a nona sentença com dados importantes.
Esta é a décima sentença finalizando o texto."""

    target_text = """Esta é a primeira sentença simplificada.
Esta é a segunda sentença mais simples.
Esta é a terceira sentença reduzida.
Esta é a quarta sentença abreviada.
Esta é a quinta sentença condensada.
Esta é a sexta sentença resumida.
Esta é a sétima sentença final."""

    logger.info(f"Source text sentences: {len(source_text.split('. '))}")
    logger.info(f"Target text sentences: {len(target_text.split('. '))}")

    # Log each sentence with index
    for i, sentence in enumerate(source_text.split('. ')):
        logger.info(f"SOURCE[{i}]: {sentence.strip()}")

    for i, sentence in enumerate(target_text.split('. ')):
        logger.info(f"TARGET[{i}]: {sentence.strip()}")

    return source_text, target_text

def phase_2_isolated_testing():
    """PHASE 2: Test each component in isolation"""
    logger.info("=" * 80)
    logger.info("PHASE 2: ISOLATED COMPONENT TESTING")
    logger.info("=" * 80)

    source_text, target_text = phase_1_comprehensive_logging()

    # Test 1: Sentence splitting
    logger.info("TEST 1: Sentence Splitting")
    try:
        from services.strategy_detector import StrategyDetector
        detector = StrategyDetector()

        # Test the sentence splitter directly
        source_sentences = detector._split_into_sentences(source_text)
        target_sentences = detector._split_into_sentences(target_text)

        logger.info(f"StrategyDetector source sentences: {len(source_sentences)}")
        logger.info(f"StrategyDetector target sentences: {len(target_sentences)}")

        for i, sent in enumerate(source_sentences):
            logger.info(f"SD_SOURCE[{i}]: {sent}")

        for i, sent in enumerate(target_sentences):
            logger.info(f"SD_TARGET[{i}]: {sent}")

    except Exception as e:
        logger.error(f"Error in sentence splitting test: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # Test 2: Feature extraction
    logger.info("TEST 2: Feature Extraction")
    try:
        from strategies.feature_extractor import FeatureExtractor
        extractor = FeatureExtractor()

        features = extractor.extract_features(source_text, target_text)
        logger.info("Feature extraction successful")
        logger.info(f"Semantic similarity: {features.semantic_similarity}")
        logger.info(f"Lexical overlap: {features.lexical_overlap}")
        logger.info(f"Sentence count ratio: {features.sentence_count_ratio}")

    except Exception as e:
        logger.error(f"Error in feature extraction test: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # Test 3: Individual strategy detection methods
    logger.info("TEST 3: Individual Strategy Methods")
    try:
        # Test sentence fragmentation detection
        has_fragmentation = detector._has_sentence_fragmentation(source_text, target_text)
        logger.info(f"Sentence fragmentation detected: {has_fragmentation}")

        if has_fragmentation:
            fragments = detector._find_sentence_splits(source_text, target_text)
            logger.info(f"Found {len(fragments)} sentence fragments")
            for i, frag in enumerate(fragments):
                logger.info(f"FRAGMENT[{i}]: {frag}")

        # Test lexical simplification
        has_lexical = detector._has_lexical_simplification(source_text, target_text)
        logger.info(f"Lexical simplification detected: {has_lexical}")

    except Exception as e:
        logger.error(f"Error in strategy method test: {e}")
        import traceback
        logger.error(traceback.format_exc())

def phase_3_pipeline_verification():
    """PHASE 3: Step-by-step pipeline verification"""
    logger.info("=" * 80)
    logger.info("PHASE 3: PIPELINE VERIFICATION")
    logger.info("=" * 80)

    source_text, target_text = phase_1_comprehensive_logging()

    try:
        from services.strategy_detector import StrategyDetector
        detector = StrategyDetector()

        logger.info("STEP 1: Initialize detector")
        logger.info(f"Detector cascade orchestrator: {detector.cascade_orchestrator is not None}")

        logger.info("STEP 2: Call identify_strategies")
        start_time = time.time()
        strategies = detector.identify_strategies(source_text, target_text)
        end_time = time.time()

        logger.info(f"STEP 3: Processing completed in {end_time - start_time:.3f}s")
        logger.info(f"STEP 4: Strategies found: {len(strategies)}")

        for i, strategy in enumerate(strategies):
            logger.info(f"STRATEGY[{i}]: {strategy.sigla} - {strategy.nome}")
            logger.info(f"  Confidence: {strategy.confiança}")
            logger.info(f"  Examples: {len(strategy.exemplos) if strategy.exemplos else 0}")

            # Log position information
            if hasattr(strategy, 'targetPosition'):
                logger.info(f"  Target Position: {strategy.targetPosition}")
            if hasattr(strategy, 'sourcePosition'):
                logger.info(f"  Source Position: {strategy.sourcePosition}")

    except Exception as e:
        logger.error(f"Error in pipeline verification: {e}")
        import traceback
        logger.error(traceback.format_exc())

def phase_4_execution_tracing():
    """PHASE 4: Detailed execution flow tracing"""
    logger.info("=" * 80)
    logger.info("PHASE 4: EXECUTION FLOW TRACING")
    logger.info("=" * 80)

    # Create a monkey-patched version to trace execution
    source_text, target_text = phase_1_comprehensive_logging()

    try:
        from services.strategy_detector import StrategyDetector

        # Monkey patch methods to add tracing
        original_split_sentences = StrategyDetector._split_into_sentences
        original_find_sentence_splits = StrategyDetector._find_sentence_splits
        original_find_perspective_shifts = StrategyDetector._find_perspective_shifts

        def traced_split_sentences(self, text):
            logger.info(f"TRACING: _split_into_sentences called with text length: {len(text)}")
            result = original_split_sentences(self, text)
            logger.info(f"TRACING: _split_into_sentences returned {len(result)} sentences")
            return result

        def traced_find_sentence_splits(self, source_text, target_text):
            logger.info("TRACING: _find_sentence_splits called")
            logger.info(f"TRACING: Source text length: {len(source_text)}")
            logger.info(f"TRACING: Target text length: {len(target_text)}")

            # Check configuration
            from core.config import settings
            logger.info(f"TRACING: STRATEGY_DETECTION_MODE = {settings.STRATEGY_DETECTION_MODE}")

            result = original_find_sentence_splits(self, source_text, target_text)
            logger.info(f"TRACING: _find_sentence_splits returned {len(result)} fragments")
            return result

        def traced_find_perspective_shifts(self, source_text, target_text):
            logger.info("TRACING: _find_perspective_shifts called")
            result = original_find_perspective_shifts(self, source_text, target_text)
            logger.info(f"TRACING: _find_perspective_shifts returned {len(result)} shifts")
            return result

        # Apply patches
        StrategyDetector._split_into_sentences = traced_split_sentences
        StrategyDetector._find_sentence_splits = traced_find_sentence_splits
        StrategyDetector._find_perspective_shifts = traced_find_perspective_shifts

        # Run test
        detector = StrategyDetector()
        strategies = detector.identify_strategies(source_text, target_text)

        logger.info(f"FINAL RESULT: {len(strategies)} strategies detected")

    except Exception as e:
        logger.error(f"Error in execution tracing: {e}")
        import traceback
        logger.error(traceback.format_exc())

def main():
    """Main debugging execution"""
    logger.info("STARTING SYSTEMATIC DEBUGGING OF STRATEGY DETECTION ISSUE")
    logger.info("Following software engineering best practices for persistent bug resolution")

    try:
        phase_1_comprehensive_logging()
        phase_2_isolated_testing()
        phase_3_pipeline_verification()
        phase_4_execution_tracing()

        logger.info("=" * 80)
        logger.info("DEBUGGING COMPLETE")
        logger.info("Check debug_strategy_detection.log for detailed analysis")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Critical error in debugging script: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()