/**
 * Interactive Text Highlighter Component
 * Provides visual highlighting and editable strategy tags for tex                <span 
                  className={`sentence ${sentenceStrategies.length > 0 ? 'highlighted-source' : ''}`}
                  style={{
                    backg                            <select 
                              value={selectedStrategy}
                              onChange={(e) => setSelectedStrategy(e.target.value)}
                              className="strategy-select"
                            >
                              <option value="">Selecione estratégia para adicionar...</option>
                              {Object.entries(STRATEGY_METADATA)
                                .filter(([code, metadata]) => {
                                  // Only show strategies that are valid and have proper metadata
                                  return code && metadata && metadata.name && code !== 'UNK+';
                                })
                                .map(([code, metadata]) => (
                                  <option key={code} value={metadata.name}>
                                    {code} - {metadata.name}
                                  </option>
                                ))}
                            </select>sentenceStrategies.length > 0 ? 
                      sentenceStrategies[0].color + '60' : 'transparent',
                    borderLeftColor: sentenceStrategies.length > 0 ? 
                      sentenceStrategies[0].color : 'transparent'
                  }}sis
 * Addresses requirements: 1.2, 1.3 - Source highlighting and target strategy tags
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Edit3, Check, X } from 'lucide-react';
import { STRATEGY_METADATA, getStrategyColor } from '../services/strategyColorMapping.js';
import './InteractiveTextHighlighter.css';

const InteractiveTextHighlighter = ({
  sourceText,
  targetText,
  analysisResult,
  onStrategyUpdate = null
}) => {
  // Convert hex color to rgba with transparency
  const hexToRgba = (hex, alpha = 0.25) => {
    if (!hex || typeof hex !== 'string' || hex.length < 7) {
      return `rgba(128, 128, 128, ${alpha})`; // Gray fallback
    }
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  // Calculate optimal text color (black or white) based on background color luminance
  const getContrastingTextColor = (hexColor) => {
    if (!hexColor || typeof hexColor !== 'string' || hexColor.length < 7) {
      return '#000'; // Default to black
    }
    
    // Convert hex to RGB
    const r = parseInt(hexColor.slice(1, 3), 16);
    const g = parseInt(hexColor.slice(3, 5), 16);
    const b = parseInt(hexColor.slice(5, 7), 16);
    
    // Calculate relative luminance using WCAG formula
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    
    // Return black text for light backgrounds, white text for dark backgrounds
    return luminance > 0.5 ? '#000' : '#fff';
  };

  const [editingTag, setEditingTag] = useState(null);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [addingTag, setAddingTag] = useState(null); // For manual tag insertion
  const [insertPosition, setInsertPosition] = useState(null); // Track insertion position

  // Helper functions for sentence counting (moved up to avoid hoisting issues)
  const getSourceSentenceCount = useCallback(() => {
    return sourceText ? sourceText.split(/[.!?]+/).filter(s => s.trim()).length : 0;
  }, [sourceText]);

  const getTargetSentenceCount = useCallback(() => {
    return targetText ? targetText.split(/[.!?]+/).filter(s => s.trim()).length : 0;
  }, [targetText]);

  // Helper function to convert Portuguese strategy name to code
  const getStrategyCodeByName = (strategyName) => {
    // First, try exact match by name
    const exactMatch = Object.entries(STRATEGY_METADATA).find(
      ([_code, metadata]) => metadata.name === strategyName
    );
    if (exactMatch) {
      return exactMatch[0];
    }
    
    // If no exact match, check if the strategyName is already a code (e.g., "DL+")
    if (STRATEGY_METADATA[strategyName]) {
      return strategyName;
    }
    
    // If still no match, try case-insensitive search
    const caseInsensitiveMatch = Object.entries(STRATEGY_METADATA).find(
      ([_code, metadata]) => metadata.name.toLowerCase() === strategyName.toLowerCase()
    );
    if (caseInsensitiveMatch) {
      return caseInsensitiveMatch[0];
    }
    
    // Instead of returning UNK+, return null to indicate this strategy should be skipped
    return null;
  };

  // Process strategies detected from analysis
  const strategiesDetected = useMemo(() => {
    if (!analysisResult?.simplification_strategies) return [];

    const strategies = analysisResult.simplification_strategies
      .map((strategy, index) => {
        // Backend now sends 'code' field directly, but fallback to name conversion if needed
        const strategyCode = strategy.code || getStrategyCodeByName(strategy.name);

        // Skip strategies that can't be mapped to valid codes
        if (!strategyCode || !STRATEGY_METADATA[strategyCode]) {
          return null;
        }

        const strategyMeta = STRATEGY_METADATA[strategyCode];

        return {
          id: strategy.id || `strategy_${index}`,
          code: strategyCode,
          fullName: strategyMeta.name, // Use the canonical name from metadata
          confidence: strategy.confidence,
          evidence: strategy.evidence || [],
          color: strategy.color || getStrategyColor(strategyCode), // Use backend color if available
          isAutomatic: !strategy.isManual, // Check if manually added
          // Use backend position data if available, otherwise calculate
          targetPosition: strategy.targetPosition || {
            sentence: index % getTargetSentenceCount(),
            type: 'sentence'
          },
          sourcePosition: strategy.sourcePosition || {
            sentence: index % getSourceSentenceCount(),
            type: 'sentence'
          }
        };
      })
      .filter(Boolean); // Remove null entries for invalid strategies

    return strategies;
  }, [analysisResult, getSourceSentenceCount, getTargetSentenceCount]);

  // Split text into sentences for highlighting
  const splitIntoSentences = useCallback((text) => {
    if (!text) return [];
    return text.split(/([.!?]+)/).filter(part => part.trim()).reduce((acc, part, index, array) => {
      if (index % 2 === 0) {
        // Text part
        const punctuation = array[index + 1] || '';
        acc.push(part + punctuation);
      }
      return acc;
    }, []);
  }, []);

  const sourceSentences = useMemo(() => splitIntoSentences(sourceText), [sourceText, splitIntoSentences]);
  const targetSentences = useMemo(() => splitIntoSentences(targetText), [targetText, splitIntoSentences]);

  // Handle strategy tag editing
  const handleEditTag = (strategyId, currentCode) => {
    setEditingTag(strategyId);
    setSelectedStrategy(currentCode);
  };

  const handleSaveTag = () => {
    if (onStrategyUpdate && editingTag && selectedStrategy) {
      onStrategyUpdate(editingTag, selectedStrategy);
    }
    setEditingTag(null);
    setSelectedStrategy('');
  };

  const handleCancelEdit = () => {
    setEditingTag(null);
    setSelectedStrategy('');
  };

  // Handle double-click to add new tag
  const handleAddTagAtPosition = (sentenceIndex, event) => {
    event.preventDefault();
    setInsertPosition({ sentence: sentenceIndex });
    setAddingTag(true);
    setSelectedStrategy('');
  };

  // Handle saving new manually added tag
  const handleSaveNewTag = () => {
    if (onStrategyUpdate && insertPosition && selectedStrategy) {
      // Get the strategy code from the selected Portuguese name
      const strategyCode = getStrategyCodeByName(selectedStrategy);
      
      if (!strategyCode) {
        return;
      }
      
      // Create new strategy object with explicit position validation
      const newStrategy = {
        id: `manual_${Date.now()}`,
        code: strategyCode,
        fullName: selectedStrategy, // Keep full name for reference
        confidence: 1.0, // Manual tags have 100% confidence
        evidence: ['Manually added by human validator'],
        color: getStrategyColor(strategyCode),
        isAutomatic: false, // Mark as manually added
        // Ensure we're using the exact sentence index where the user clicked
        targetPosition: { 
          sentence: insertPosition.sentence, 
          type: 'sentence'
        },
        sourcePosition: { 
          sentence: insertPosition.sentence, 
          type: 'sentence' 
        }
      };
      
      // Add to strategies list
      onStrategyUpdate('add', newStrategy);
    }
    setAddingTag(false);
    setInsertPosition(null);
    setSelectedStrategy('');
  };

  // Handle canceling new tag addition
  const handleCancelNewTag = () => {
    setAddingTag(false);
    setInsertPosition(null);
    setSelectedStrategy('');
  };

  // Render source text with highlighting
  const renderSourceText = () => {
    return (
      <div className="text-panel source-panel">
        <div className="panel-header">
          <h3>Texto Fonte</h3>
          <div className="text-stats">
            {sourceSentences.length} frase{sourceSentences.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="text-content">
          {sourceSentences.map((sentence, index) => {
            // Check if this sentence has strategies
            const sentenceStrategies = strategiesDetected.filter(
              strategy => strategy.sourcePosition.sentence === index
            );

            return (
              <div key={index} className="sentence-block">
                <span 
                  className={`sentence ${sentenceStrategies.length > 0 ? 'highlighted-source' : ''}`}
                  style={{
                    backgroundColor: sentenceStrategies.length > 0 && sentenceStrategies[0]?.color ? 
                      hexToRgba(sentenceStrategies[0].color, 0.25) : 'transparent',
                    borderLeftColor: sentenceStrategies.length > 0 && sentenceStrategies[0]?.color ? 
                      sentenceStrategies[0].color : 'transparent'
                  }}
                >
                  {sentence}
                </span>
                {sentenceStrategies.length > 0 && (
                  <div className="source-indicators">
                    {sentenceStrategies.map(strategy => (
                      <span 
                        key={strategy.id}
                        className="source-indicator"
                        style={{ backgroundColor: strategy.color }}
                        title={`Estratégia detectada: ${strategy.code}`}
                      >
                        •
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Render target text with editable strategy tags
  const renderTargetText = () => {
    return (
      <div className="text-panel target-panel">
        <div className="panel-header">
          <h3>Texto Alvo</h3>
          <div className="text-stats">
            {targetSentences.length} frase{targetSentences.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div className="text-content">
          <div className="add-tag-hint">
            💡 Duplo-clique em uma frase para adicionar tag manual
          </div>
          {targetSentences.map((sentence, index) => {
            // Check if this sentence has strategies
            const sentenceStrategies = strategiesDetected.filter(
              strategy => strategy.targetPosition.sentence === index
            );

            return (
              <div key={index} className="sentence-block">
                {/* Strategy tags displayed before sentence */}
                {(sentenceStrategies.length > 0 || (addingTag && insertPosition?.sentence === index)) && (
                  <div className="strategy-tags-container">
                    {sentenceStrategies.map(strategy => (
                      <div key={strategy.id} className="strategy-tag-container">
                        {editingTag === strategy.id ? (
                          <div className="strategy-editor">
                            <select 
                              value={selectedStrategy}
                              onChange={(e) => setSelectedStrategy(e.target.value)}
                              className="strategy-select"
                            >
                              <option value="">Selecione estratégia...</option>
                              {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
                                <option key={code} value={metadata.name}>
                                  {code} - {metadata.name}
                                </option>
                              ))}
                            </select>
                            <button onClick={handleSaveTag} className="save-btn">
                              <Check size={14} />
                            </button>
                            <button onClick={handleCancelEdit} className="cancel-btn">
                              <X size={14} />
                            </button>
                          </div>
                        ) : (
                          <button 
                            className="strategy-tag unified-tag"
                            style={{ 
                              backgroundColor: strategy.color,
                              color: getContrastingTextColor(strategy.color)
                            }}
                            onClick={() => handleEditTag(strategy.id, strategy.fullName || strategy.code)}
                            title={`${strategy.fullName || strategy.code} - Confiança: ${Math.round(strategy.confidence * 100)}% - ${strategy.isAutomatic ? 'Automático' : 'Manual'}`}
                          >
                            <span className="tag-code">[{strategy.code}]</span>
                            <Edit3 size={12} className="edit-icon" />
                            <span className="confidence">
                              {Math.round(strategy.confidence * 100)}%
                            </span>
                          </button>
                        )}
                      </div>
                    ))}

                    {/* New tag insertion UI */}
                    {addingTag && insertPosition?.sentence === index && (
                      <div className="strategy-tag-container">
                        <div className="strategy-editor new-tag-editor">
                          <select 
                            value={selectedStrategy}
                            onChange={(e) => setSelectedStrategy(e.target.value)}
                            className="strategy-select"
                          >
                            <option value="">Selecione estratégia para adicionar...</option>
                            {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
                              <option key={code} value={metadata.name}>
                                {code} - {metadata.name}
                              </option>
                            ))}
                          </select>
                          <button onClick={handleSaveNewTag} className="save-btn" disabled={!selectedStrategy}>
                            <Check size={14} />
                          </button>
                          <button onClick={handleCancelNewTag} className="cancel-btn">
                            <X size={14} />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <span 
                  className="sentence clickable-sentence"
                  onDoubleClick={(e) => handleAddTagAtPosition(index, e)}
                  title="Duplo-clique para adicionar tag"
                >
                  {sentence}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Render unified strategy legend
  const renderStrategyLegend = () => {
    if (strategiesDetected.length === 0) return null;

    // Group strategies by code to avoid duplicates
    const uniqueStrategies = strategiesDetected.reduce((acc, strategy) => {
      if (!acc[strategy.code]) {
        acc[strategy.code] = {
          code: strategy.code,
          fullName: strategy.fullName,
          color: strategy.color,
          count: 1,
          isAutomatic: strategy.isAutomatic,
          avgConfidence: strategy.confidence
        };
      } else {
        acc[strategy.code].count++;
        acc[strategy.code].avgConfidence = (acc[strategy.code].avgConfidence + strategy.confidence) / 2;
        // Mark as mixed if we have both automatic and manual
        if (acc[strategy.code].isAutomatic !== strategy.isAutomatic) {
          acc[strategy.code].isAutomatic = 'mixed';
        }
      }
      return acc;
    }, {});

    const uniqueStrategiesList = Object.values(uniqueStrategies);

    return (
      <div className="strategy-legend-unified">
        <h4>Estratégias de Simplificação Detectadas</h4>
        <div className="legend-grid">
          {uniqueStrategiesList.map(strategy => (
            <div 
              key={strategy.code}
              className="legend-item"
              style={{ 
                borderLeft: `4px solid ${strategy.color}`,
                backgroundColor: hexToRgba(strategy.color, 0.05)
              }}
            >
              <div className="legend-header">
                <span 
                  className="legend-code"
                  style={{ 
                    backgroundColor: strategy.color,
                    color: getContrastingTextColor(strategy.color)
                  }}
                >
                  [{strategy.code}]
                </span>
                <span className="legend-count">×{strategy.count}</span>
              </div>
              <div className="legend-name">{strategy.fullName}</div>
              <div className="legend-info">
                <span className="legend-confidence">
                  Confiança: {Math.round(strategy.avgConfidence * 100)}%
                </span>
                <span className="legend-origin">
                  {strategy.isAutomatic === 'mixed' ? 'Automático/Manual' : 
                   strategy.isAutomatic ? 'Automático' : 'Manual'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="interactive-highlighter">
      <div className="text-comparison">
        {renderSourceText()}
        {renderTargetText()}
      </div>
      {renderStrategyLegend()}
    </div>
  );
};

export default InteractiveTextHighlighter;

/*
Contains AI-generated code.
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ
Projeto: NET-EST - Sistema de Análise de Estratégias de Simplificação Textual em Tradução Intralingual
Equipe: Coord.: Profa. Dra. Janine Pimentel; Dev. Principal: Wisley Vilela; Especialista Linguística: Luanny Matos de Lima; Agentes IA: Claude Sonnet 4, ChatGPT-4.1, Gemini 2.5 Pro
Instituições: PIPGLA/UFRJ | Politécnico de Leiria
Apoio: CAPES | Licença: MIT
*/
