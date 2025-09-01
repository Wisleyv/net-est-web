# M5: Confidence & Weighting Engine

## Overview

The Confidence & Weighting Engine provides a unified, explainable confidence calculation system for strategy detection in NET-EST. This module enhances user trust in results by providing transparent confidence scoring with detailed explanations of how confidence scores are calculated.

## Key Features

### 🔍 Unified Confidence Formula
- **Standardized Calculation**: Single, consistent confidence calculation across all strategies
- **Strategy-Specific Profiles**: Tailored confidence parameters for each simplification strategy
- **Multi-Factor Analysis**: Combines semantic similarity, feature analysis, and evidence quality

### 📊 Explainability & Transparency
- **Factor Breakdown**: Detailed breakdown of confidence components
- **Evidence Attribution**: Clear explanation of supporting evidence
- **Recommendations**: Actionable suggestions for improving confidence

### 🎯 Per-Strategy Attribution
- **Strategy-Specific Rules**: Different confidence criteria for different strategies
- **Quality Thresholds**: Minimum confidence requirements per strategy type
- **Dynamic Adjustment**: Real-time confidence updates based on evidence quality

## Architecture

### Core Components

#### ConfidenceEngine
Main orchestrator for confidence calculations:
```python
from src.services.confidence_engine import confidence_engine

# Calculate confidence with explanation
explanation = confidence_engine.calculate_confidence(
    strategy_code="SL+",
    features={
        "semantic_similarity": 0.85,
        "lexical_overlap": 0.3,
        "structure_change_score": 0.6
    },
    evidence_quality="strong"
)
```

#### StrategyConfidenceProfile
Defines confidence calculation rules for each strategy:
```python
@dataclass
class StrategyConfidenceProfile:
    strategy_code: str
    base_confidence: float                    # Base confidence level (0.3-0.6)
    semantic_multiplier_weight: float         # Semantic similarity impact (0.5-0.9)
    feature_weights: Dict[str, float]         # Feature contribution weights
    quality_thresholds: Dict[str, float]      # Quality requirements
    evidence_requirements: List[str]          # Required evidence types
```

#### ConfidenceExplanation
Detailed explanation of confidence calculation:
```python
@dataclass
class ConfidenceExplanation:
    strategy_code: str
    final_confidence: float
    confidence_level: ConfidenceLevel          # VERY_LOW, LOW, MODERATE, HIGH, VERY_HIGH
    factors: List[ConfidenceFactor]           # Individual contributing factors
    recommendations: List[str]                # Improvement suggestions
    evidence_quality: str                     # weak, standard, strong
    calculation_method: str                   # unified_v1
```

## Confidence Formula

### Base Formula
```
Final Confidence = (Base Confidence + Feature Bonuses + Custom Factors) × Semantic Multiplier + Quality Adjustment
```

Where:
- **Base Confidence**: Strategy-specific baseline (0.3-0.6)
- **Feature Bonuses**: Weighted sum of feature contributions
- **Custom Factors**: Additional domain-specific factors
- **Semantic Multiplier**: Semantic similarity adjustment (0.5-1.5)
- **Quality Adjustment**: Evidence quality modifier (-0.1 to +0.1)

### Feature Contributions

#### Lexical Strategies (SL+)
```python
feature_weights = {
    "semantic_similarity": 0.3,      # High semantic preservation
    "lexical_overlap": -0.2,         # Low lexical overlap preferred
    "avg_word_length_ratio": -0.3,   # Shorter words = higher confidence
    "explicitness_score": 0.2        # More explicit = higher confidence
}
```

#### Syntactic Strategies (RP+, DL+)
```python
feature_weights = {
    "sentence_count_ratio": 0.4,     # Sentence fragmentation extent
    "semantic_similarity": 0.2,      # Meaning preservation
    "structure_change_score": 0.2,   # Structural reorganization
    "complexity_reduction": 0.2      # Complexity reduction achieved
}
```

#### Semantic Strategies (MOD+)
```python
feature_weights = {
    "semantic_similarity": 0.4,      # Very high semantic similarity required
    "lexical_overlap": -0.5,         # Very low lexical overlap preferred
    "voice_change_score": 0.1,       # Voice change detection
    "structure_change_score": 0.2    # Perspective shift indicators
}
```

#### Structural Strategies (RF+, RD+)
```python
feature_weights = {
    "semantic_similarity": 0.3,      # Semantic preservation
    "structure_change_score": 0.4,   # Structural transformation extent
    "lexical_overlap": -0.2,         # Low lexical overlap for rewriting
    "length_ratio": 0.1              # Length relationship
}
```

## Strategy-Specific Profiles

### SL+ (Lexical Simplification)
- **Base Confidence**: 0.4
- **Semantic Multiplier**: 0.7
- **Key Features**: Word length reduction, semantic preservation
- **Threshold**: Min 0.5 confidence for acceptance

### RP+ (Sentence Fragmentation)
- **Base Confidence**: 0.5
- **Semantic Multiplier**: 0.6
- **Key Features**: Sentence count increase, fragmentation quality
- **Threshold**: Min 0.6 confidence for acceptance

### MOD+ (Perspective Reinterpretation)
- **Base Confidence**: 0.5
- **Semantic Multiplier**: 0.9
- **Key Features**: High semantic similarity, low lexical overlap
- **Threshold**: Min 0.75 confidence (strict requirement)

### RF+ (Global Rewriting)
- **Base Confidence**: 0.6
- **Semantic Multiplier**: 0.8
- **Key Features**: Structural change, semantic preservation
- **Threshold**: Min 0.7 confidence for acceptance

## Usage Examples

### Basic Confidence Calculation
```python
from src.services.confidence_engine import confidence_engine

# Calculate confidence for lexical simplification
explanation = confidence_engine.calculate_confidence(
    strategy_code="SL+",
    features={
        "semantic_similarity": 0.85,
        "lexical_overlap": 0.25,
        "avg_word_length_ratio": 0.85,
        "explicitness_score": 0.7
    }
)

print(f"Confidence: {explanation.final_confidence:.3f}")
print(f"Level: {explanation.confidence_level.value}")
print(f"Top factors: {explanation.get_top_contributors(3)}")
```

### Advanced Usage with Custom Factors
```python
from src.services.confidence_engine import ConfidenceFactor

# Add custom domain-specific factors
custom_factors = [
    ConfidenceFactor(
        name="domain_expertise",
        value=0.8,
        weight=0.15,
        description="Domain-specific vocabulary expertise",
        evidence="Technical term recognition accuracy: 80%"
    )
]

explanation = confidence_engine.calculate_confidence(
    strategy_code="SL+",
    features=features,
    custom_factors=custom_factors,
    evidence_quality="strong"
)
```

### Confidence Summary Analysis
```python
# Analyze multiple strategies
explanations = [
    confidence_engine.calculate_confidence("SL+", sl_features),
    confidence_engine.calculate_confidence("RP+", rp_features),
    confidence_engine.calculate_confidence("RF+", rf_features)
]

summary = confidence_engine.get_confidence_summary(explanations)
print(f"Average confidence: {summary['average_confidence']:.3f}")
print(f"High confidence strategies: {summary['high_confidence_strategies']}")
```

## Integration Points

### Strategy Detection Cascade
The confidence engine integrates seamlessly with the existing cascade detection system:

1. **Feature Extraction**: Extracts relevant features from text pairs
2. **Strategy Detection**: Identifies applicable strategies
3. **Confidence Calculation**: Calculates confidence with detailed explanations
4. **Result Enhancement**: Adds confidence metadata to strategy objects

### API Response Enhancement
Strategy results now include confidence explanations:
```json
{
  "strategies": [
    {
      "sigla": "SL+",
      "nome": "Adequação de Vocabulário",
      "confianca": 0.78,
      "confidence_explanation": {
        "final_confidence": 0.78,
        "confidence_level": "high",
        "factor_breakdown": {
          "base_confidence": 0.4,
          "feature_semantic_similarity": 0.24,
          "feature_lexical_overlap": -0.05,
          "semantic_multiplier": 0.19
        },
        "top_contributors": [
          ["base_confidence", 0.4],
          ["feature_semantic_similarity", 0.24],
          ["semantic_multiplier", 0.19]
        ],
        "recommendations": [],
        "evidence_quality": "strong",
        "calculation_method": "unified_v1"
      }
    }
  ]
}
```

## Quality Assurance

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end confidence calculation
- **Regression Tests**: Backward compatibility verification
- **Performance Tests**: Confidence calculation efficiency

### Validation Metrics
- **Accuracy**: Confidence scores correlate with human judgment
- **Consistency**: Similar cases produce similar confidence scores
- **Explainability**: Factor contributions are meaningful and accurate
- **Robustness**: Graceful handling of edge cases and missing data

## Performance Considerations

### Optimization Features
- **Caching**: Profile caching for repeated calculations
- **Lazy Loading**: On-demand model loading
- **Batch Processing**: Efficient bulk confidence calculations
- **Early Exit**: Skip unnecessary calculations for low-confidence cases

### Memory Management
- **Profile Reuse**: Shared profile instances across calculations
- **Feature Recycling**: Reuse extracted features when possible
- **Result Caching**: Cache confidence results for identical inputs

## Future Enhancements

### Planned Features
- **Machine Learning Integration**: ML-based confidence calibration
- **User Feedback Loop**: Incorporate user confidence ratings
- **Dynamic Profile Updates**: Self-tuning confidence profiles
- **Multi-language Support**: Language-specific confidence rules

### Research Directions
- **Confidence Calibration**: Statistical calibration of confidence scores
- **Uncertainty Quantification**: Probabilistic confidence intervals
- **Explainability Improvements**: More detailed factor attributions
- **Cross-domain Adaptation**: Domain-specific confidence profiles

## Troubleshooting

### Common Issues

#### Low Confidence Scores
**Symptoms**: All strategies return low confidence scores
**Causes**:
- Poor semantic similarity between texts
- Insufficient evidence quality
- Missing or incorrect features

**Solutions**:
- Verify text pair semantic relationship
- Check evidence quality parameters
- Validate feature extraction accuracy

#### Inconsistent Results
**Symptoms**: Same inputs produce different confidence scores
**Causes**:
- Non-deterministic feature extraction
- Random factors in calculation
- Caching issues

**Solutions**:
- Ensure deterministic feature extraction
- Remove random components from calculations
- Clear confidence caches

#### Performance Issues
**Symptoms**: Slow confidence calculations
**Causes**:
- Large feature sets
- Complex profile calculations
- Inefficient caching

**Solutions**:
- Optimize feature extraction
- Simplify confidence profiles
- Implement efficient caching strategies

## API Reference

### ConfidenceEngine Methods

#### calculate_confidence(strategy_code, features, evidence_quality, custom_factors)
Calculate confidence for a strategy with detailed explanation.

**Parameters:**
- `strategy_code` (str): Strategy identifier (e.g., "SL+", "RP+")
- `features` (Dict[str, float]): Dictionary of feature values
- `evidence_quality` (str): Quality of evidence ("weak", "standard", "strong")
- `custom_factors` (List[ConfidenceFactor]): Additional custom factors

**Returns:** `ConfidenceExplanation` object

#### get_strategy_profile(strategy_code)
Get confidence profile for a specific strategy.

**Parameters:**
- `strategy_code` (str): Strategy identifier

**Returns:** `StrategyConfidenceProfile` or `None`

#### update_strategy_profile(strategy_code, profile)
Update confidence profile for a strategy.

**Parameters:**
- `strategy_code` (str): Strategy identifier
- `profile` (StrategyConfidenceProfile): New profile configuration

#### get_confidence_summary(explanations)
Generate summary statistics for multiple confidence explanations.

**Parameters:**
- `explanations` (List[ConfidenceExplanation]): List of explanations

**Returns:** Dictionary with summary statistics

## Conclusion

The Confidence & Weighting Engine provides a robust, explainable foundation for strategy confidence calculation in NET-EST. By offering transparent confidence scoring with detailed factor breakdowns, it enhances user trust and enables better decision-making in text simplification analysis.

The unified approach ensures consistency across all strategies while maintaining the flexibility to customize confidence calculations for specific use cases and domains.