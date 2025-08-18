import React, { useState, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import { getStrategyColor, getStrategyInfo, getStrategyClassName, generateStrategyCSSClasses, STRATEGY_METADATA } from '../services/strategyColorMapping.js';
import './SideBySideTextDisplay.css';

// Create reverse mapping from Portuguese names to strategy codes
const NAME_TO_CODE_MAPPING = {};
Object.entries(STRATEGY_METADATA).forEach(([code, metadata]) => {
  NAME_TO_CODE_MAPPING[metadata.name] = code;
});

/**
 * Converts Portuguese strategy name to strategy code
 * @param {string} strategyName - Portuguese strategy name
 * @returns {string} - Strategy code (e.g., 'RF+', 'MOD+')
 */
const getStrategyCode = (strategyName) => {
  const code = NAME_TO_CODE_MAPPING[strategyName];
  if (!code) {
    console.warn('Unknown strategy name:', strategyName);
    console.log('Available mappings:', NAME_TO_CODE_MAPPING);
  }
  return code || strategyName;
};

/**
 * Enhanced side-by-side text display with strategy highlighting
 * Shows source and target texts with color-coded strategy detection
 */
const SideBySideTextDisplay = ({ 
  sourceText, 
  targetText, 
  analysisResult, 
  useColorblindFriendly = false,
  onStrategyClick = null,
  selectedStrategies = new Set(),
  showStrategyLegend = true 
}) => {
  const [hoveredStrategy, setHoveredStrategy] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Process analysis result to extract strategies and evidence
  const strategiesDetected = useMemo(() => {
    console.log('SideBySideTextDisplay - analysisResult:', analysisResult);
    
    if (!analysisResult?.simplification_strategies) {
      console.log('No simplification_strategies found');
      return [];
    }
    
    console.log('Found strategies:', analysisResult.simplification_strategies);
    
    const mappedStrategies = analysisResult.simplification_strategies.map((strategy, index) => {
      console.log('Processing strategy:', strategy);
      const strategyCode = getStrategyCode(strategy.name);
      const mapped = {
        id: `strategy_${index}_${strategyCode}`, // Unique identifier
        code: strategyCode,
        confidence: strategy.confidence,
        evidence: strategy.evidence || [],
        color: getStrategyColor(strategyCode, useColorblindFriendly),
        info: getStrategyInfo(strategyCode)
      };
      console.log('Mapped strategy:', mapped);
      return mapped;
    });
    
    console.log('Final mapped strategies:', mappedStrategies);
    return mappedStrategies;
  }, [analysisResult, useColorblindFriendly]);

  // Generate CSS for strategy highlighting
  useEffect(() => {
    const styleId = 'strategy-highlighting-styles';
    let styleElement = document.getElementById(styleId);
    
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      document.head.appendChild(styleElement);
    }
    
    styleElement.textContent = generateStrategyCSSClasses(useColorblindFriendly);
  }, [useColorblindFriendly]);

  // Split text into paragraphs for better alignment
  const sourceParas = useMemo(() => {
    return sourceText ? sourceText.split('\n').filter(para => para.trim()) : [];
  }, [sourceText]);

  const targetParas = useMemo(() => {
    return targetText ? targetText.split('\n').filter(para => para.trim()) : [];
  }, [targetText]);

  // Apply highlighting to text based on detected strategies
  const highlightText = (text, isTarget = false, paragraphIndex = 0) => {
    if (!text) return <span className="unhighlighted-text">{text}</span>;

    // Find strategies that explicitly target this paragraph (preferred)
    const strategiesForParagraph = strategiesDetected.filter((strategy) => {
      const key = isTarget ? 'targetParagraph' : 'sourceParagraph';
      return strategy[key] === paragraphIndex;
    });

    // Fallback: if none found, fall back to evidence-based tags (existing behavior)
    const fallbackStrategies = strategiesForParagraph.length === 0
      ? strategiesDetected.filter(s => (selectedStrategies.size === 0 || selectedStrategies.has(s.code)))
      : strategiesForParagraph;

    // Build prefix HTML with tags for strategies found for this paragraph
    const prefixTags = fallbackStrategies.map((strategy) => {
      const className = getStrategyClassName(strategy.code);
      const color = strategy.color || '#ddd';
      const evidenceText = (strategy.evidence || []).slice(0,3).join('; ');
      const title = `${strategy.code} — ${strategy.name} (${Math.round(strategy.confidence*100)}%)${evidenceText ? ' — ' + evidenceText : ''}`;
      return `<button type="button" title="${title}" class="${className} strategy-inline-tag" data-strategy="${strategy.code}" style="background:${color};color:${getContrastingTextColor(color)};border:none;padding:2px 6px;margin-right:6px;border-radius:4px;font-size:0.8em;cursor:pointer;">${strategy.code}</button>`;
    }).join(' ');

    const safeText = text.replace(/</g, '<').replace(/>/g, '>');

    return (
      <div
        className="highlighted-text"
        dangerouslySetInnerHTML={{ __html: (prefixTags ? prefixTags + ' ' : '') + safeText }}
        onMouseOver={handleTextHover}
        onMouseOut={handleTextOut}
        onFocus={handleTextHover}
        onBlur={handleTextOut}
        tabIndex={0}
        role="textbox"
        aria-readonly="true"
      />
    );
  };

  const handleTextHover = (event) => {
    const strategyCode = event.target.getAttribute('data-strategy');
    if (strategyCode) {
      setHoveredStrategy(strategyCode);
      setTooltipPosition({ x: event.clientX, y: event.clientY });
    }
  };

  const handleTextOut = () => {
    setHoveredStrategy(null);
  };

  const handleStrategyClick = (strategyCode) => {
    if (onStrategyClick) {
      onStrategyClick(strategyCode);
    }
  };

  const renderStrategyLegend = () => {
    if (!showStrategyLegend || strategiesDetected.length === 0) return null;

    const handleKeyDown = (event, strategyCode) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handleStrategyClick(strategyCode);
      }
    };

    return (
      <div className="strategy-legend">
        <h4>Estratégias Detectadas</h4>
        <div className="strategy-list">
          {strategiesDetected.map(strategy => (
            <button 
              key={strategy.id}
              className={`strategy-item ${selectedStrategies.has(strategy.code) ? 'selected' : ''}`}
              onClick={() => handleStrategyClick(strategy.code)}
              onKeyDown={(e) => handleKeyDown(e, strategy.code)}
              style={{ 
                backgroundColor: strategy.color,
                color: getContrastingTextColor(strategy.color)
              }}
              type="button"
              aria-pressed={selectedStrategies.has(strategy.code)}
              aria-label={`${strategy.info.name} - ${Math.round(strategy.confidence * 100)}% confiança`}
            >
              <span className="strategy-code">{strategy.code}</span>
              <span className="strategy-name">{strategy.info.name}</span>
              <span className="strategy-confidence">
                {Math.round(strategy.confidence * 100)}%
              </span>
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderTooltip = () => {
    if (!hoveredStrategy) return null;

    const strategy = strategiesDetected.find(s => s.code === hoveredStrategy);
    if (!strategy) return null;

    return (
      <div 
        className="strategy-tooltip"
        style={{
          left: tooltipPosition.x + 10,
          top: tooltipPosition.y - 10,
          position: 'fixed',
          zIndex: 1000
        }}
      >
        <div className="tooltip-header">
          <strong>{strategy.code}</strong> - {strategy.info.name}
        </div>
        <div className="tooltip-description">
          {strategy.info.description}
        </div>
        <div className="tooltip-confidence">
          Confiança: {Math.round(strategy.confidence * 100)}%
        </div>
        {strategy.evidence.length > 0 && (
          <div className="tooltip-evidence">
            <strong>Evidências:</strong>
            <ul>
              {strategy.evidence.slice(0, 3).map((evidence, idx) => (
                <li key={idx}>{evidence}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="side-by-side-container">
      {/* Analysis Summary */}
      {analysisResult && (
        <div className="analysis-summary">
          <div className="summary-metrics">
            <div className="metric">
              <span className="metric-label">Similaridade Semântica:</span>
              <span className="metric-value">
                {(() => {
                  const semanticValue = analysisResult.semantic_analysis?.semantic_similarity || analysisResult.semantic_similarity || 0;
                  console.log('Semantic similarity calculation:', {
                    semantic_analysis: analysisResult.semantic_analysis,
                    semantic_similarity: analysisResult.semantic_similarity,
                    final_value: semanticValue
                  });
                  return Math.round(semanticValue * 100);
                })()}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Redução de Palavras:</span>
              <span className="metric-value">
                {(() => {
                  const sourceWords = analysisResult.source_text ? 
                    analysisResult.source_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                  const targetWords = analysisResult.target_text ? 
                    analysisResult.target_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                  
                  if (sourceWords === 0) return '0%';
                  
                  const reduction = ((sourceWords - targetWords) / sourceWords) * 100;
                  const reductionRounded = Math.round(reduction * 10) / 10; // Round to 1 decimal
                  
                  if (reductionRounded > 0) {
                    return `-${reductionRounded}%`; // Negative indicates reduction
                  } else if (reductionRounded < 0) {
                    return `+${Math.abs(reductionRounded)}%`; // Positive indicates expansion
                  } else {
                    return '0%'; // No change
                  }
                })()}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Estratégias:</span>
              <span className="metric-value">
                {strategiesDetected.length}
              </span>
            </div>
          </div>
          
          {/* Explanatory Text - Option 2 Implementation */}
          <div className="analysis-explanation">
            <p className="explanation-text">
              {(() => {
                const strategiesCount = strategiesDetected.length;
                const sourceWords = analysisResult.source_text ? 
                  analysisResult.source_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const targetWords = analysisResult.target_text ? 
                  analysisResult.target_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const reduction = sourceWords > 0 ? ((sourceWords - targetWords) / sourceWords) * 100 : 0;
                const reductionRounded = Math.round(reduction * 10) / 10;
                
                let explanation = "";
                
                // Explain word reduction
                if (reductionRounded > 5) {
                  explanation += `O texto alvo apresenta uma redução significativa de ${reductionRounded}% no número de palavras, `;
                } else if (reductionRounded > 0) {
                  explanation += `O texto alvo apresenta uma redução leve de ${reductionRounded}% no número de palavras, `;
                } else if (reductionRounded < -5) {
                  explanation += `O texto alvo é ${Math.abs(reductionRounded)}% maior que o original, `;
                } else {
                  explanation += "O texto alvo mantém aproximadamente o mesmo tamanho do original, ";
                }
                
                // Explain strategies
                if (strategiesCount === 0) {
                  explanation += "com estratégias de simplificação sutis que não foram automaticamente categorizadas pelo sistema.";
                } else if (strategiesCount === 1) {
                  explanation += "aplicando 1 estratégia principal de simplificação identificada automaticamente.";
                } else {
                  explanation += `aplicando ${strategiesCount} estratégias distintas de simplificação identificadas automaticamente.`;
                }
                
                return explanation;
              })()}
            </p>
          </div>
        </div>
      )}

      {/* Main Text Comparison */}
      <div className="text-comparison">
        <div className="text-panel source-panel">
          <div className="panel-header">
            <h3>Texto Fonte</h3>
            <div className="text-stats">
              {(() => {
                const sourceWords = analysisResult.source_text ? 
                  analysisResult.source_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                return `${sourceWords} palavra${sourceWords !== 1 ? 's' : ''}`;
              })()}
            </div>
          </div>
          <div className="text-content">
            {sourceParas.map((para, index) => (
              <div key={index} className="text-paragraph">
                {highlightText(para, false)}
              </div>
            ))}
          </div>
        </div>

        <div className="text-panel target-panel">
          <div className="panel-header">
            <h3>Texto Alvo</h3>
            <div className="text-stats">
              {(() => {
                const targetWords = analysisResult.target_text ? 
                  analysisResult.target_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                return `${targetWords} palavra${targetWords !== 1 ? 's' : ''}`;
              })()}
            </div>
          </div>
          <div className="text-content">
            {targetParas.map((para, index) => (
              <div key={index} className="text-paragraph">
                {highlightText(para, true)}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Strategy Legend */}
      {renderStrategyLegend()}

      {/* Tooltip */}
      {renderTooltip()}
    </div>
  );
};

// Utility function (duplicated for component independence)
function getContrastingTextColor(backgroundColor) {
  // Simple luminance calculation
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

SideBySideTextDisplay.propTypes = {
  sourceText: PropTypes.string.isRequired,
  targetText: PropTypes.string.isRequired,
  analysisResult: PropTypes.object,
  useColorblindFriendly: PropTypes.bool,
  onStrategyClick: PropTypes.func,
  selectedStrategies: PropTypes.instanceOf(Set),
  showStrategyLegend: PropTypes.bool
};

export default SideBySideTextDisplay;

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código assistido por IA
*/
