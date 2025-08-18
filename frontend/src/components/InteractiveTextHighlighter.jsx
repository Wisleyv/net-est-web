/**
 * Interactive Text Highlighter Component
 * Provides visual highlighting and editable strategy tags for text analysis
 * Addresses requirements: 1.2, 1.3 - Source highlighting and target strategy tags
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Edit3, Check, X } from 'lucide-react';
import { STRATEGY_METADATA, getStrategyColor } from '../services/strategyColorMapping.js';
import ManualTagsService from '../services/manualTagsService.js';
import './InteractiveTextHighlighter.css';

const InteractiveTextHighlighter = ({
  sourceText,
  targetText,
  analysisResult,
  analysisId, // Add analysisId prop for backend persistence
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
  
  // Manual tags state
  const [manualTags, setManualTags] = useState([]);
  const [loadingTags, setLoadingTags] = useState(false);
  const [savingTag, setSavingTag] = useState(false);
  const [tagError, setTagError] = useState(null);

  // Helper functions for sentence counting (moved up to avoid hoisting issues)
  const getSourceSentenceCount = useCallback(() => {
    return sourceText ? sourceText.split(/[.!?]+/).filter(s => s.trim()).length : 0;
  }, [sourceText]);

  const getTargetSentenceCount = useCallback(() => {
    return targetText ? targetText.split(/[.!?]+/).filter(s => s.trim()).length : 0;
  }, [targetText]);

  // Load manual tags when component mounts or analysisId changes
  useEffect(() => {
    const loadManualTags = async () => {
      if (!analysisId) return;
      
      setLoadingTags(true);
      setTagError(null);
      
      try {
        const tags = await ManualTagsService.getTagsForAnalysis(analysisId);
        setManualTags(tags);
        console.log('Loaded manual tags:', tags);
      } catch (error) {
        console.error('Failed to load manual tags:', error);
        setTagError('Erro ao carregar tags manuais');
      } finally {
        setLoadingTags(false);
      }
    };

    loadManualTags();
  }, [analysisId]);

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

  // Process strategies detected from analysis and merge with manual tags
  const strategiesDetected = useMemo(() => {
    const automaticStrategies = [];
    
    // Process automatic strategies from analysis
    if (analysisResult?.simplification_strategies) {
    
      const autoStrategies = analysisResult.simplification_strategies
        .map((strategy, index) => {
          const strategyCode = getStrategyCodeByName(strategy.name);
          
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
            color: getStrategyColor(strategyCode),
            isAutomatic: true, // Mark as automatic
            // Use preserved position if available, otherwise calculate
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
      
      automaticStrategies.push(...autoStrategies);
    }

    // Process manual tags
    const manualStrategies = manualTags.map(tag => {
      const strategyMeta = STRATEGY_METADATA[tag.tag_type] || { name: tag.tag_type };
      
      const manualStrategy = {
        id: tag.id,
        code: tag.tag_type,
        fullName: strategyMeta.name,
        confidence: tag.confidence || 1.0,
        evidence: tag.evidence || ['Manually added by human validator'],
        color: getStrategyColor(tag.tag_type),
        isAutomatic: false, // Mark as manual
        targetPosition: {
          sentence: tag.sentence_index,
          type: 'sentence'
        },
        sourcePosition: {
          sentence: tag.sentence_index,
          type: 'sentence'
        },
        // Additional manual tag data
        isManual: true,
        userNotes: tag.user_notes,
        createdAt: tag.created_at,
        updatedAt: tag.updated_at
      };
      
      console.log('🔧 Processing manual tag:', tag, '→', manualStrategy);
      return manualStrategy;
    });

    // Merge automatic and manual strategies
    const allStrategies = [...automaticStrategies, ...manualStrategies];
    console.log('🔧 All strategies detected:', allStrategies);
    return allStrategies;
  }, [analysisResult, manualTags, getSourceSentenceCount, getTargetSentenceCount]);

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
    console.log('🔧 handleEditTag called:', { strategyId, currentCode });
    setEditingTag(strategyId);
    setSelectedStrategy(currentCode);
  };

  const handleSaveTag = async () => {
    console.log('🔧 handleSaveTag called:', { editingTag, selectedStrategy });
    
    if (!editingTag || !selectedStrategy) {
      console.log('❌ handleSaveTag: missing editingTag or selectedStrategy');
      return;
    }
    
    setSavingTag(true);
    setTagError(null);
    
    try {
      // Find the strategy being edited
      const strategy = strategiesDetected.find(s => s.id === editingTag);
      console.log('🔧 Found strategy to edit:', strategy);
      
      if (!strategy) {
        throw new Error('Estratégia não encontrada');
      }
      
      const strategyCode = getStrategyCodeByName(selectedStrategy);
      console.log('🔧 Strategy code:', strategyCode);
      
      if (!strategyCode) {
        throw new Error('Código de estratégia inválido');
      }
      
      if (!strategy.isAutomatic) {
        console.log('🔧 Updating existing manual tag via API');
        // This is an existing manual tag - update it via API
        const result = await ManualTagsService.updateTag(editingTag, {
          tagType: strategyCode
        });
        console.log('🔧 Update result:', result);
        
        if (result.success) {
          // Update local state
          setManualTags(prevTags =>
            prevTags.map(tag =>
              tag.id === editingTag
                ? { ...tag, tag_type: strategyCode, updated_at: new Date().toISOString() }
                : tag
            )
          );
          console.log('✅ Manual tag updated successfully');
        }
      } else {
        console.log('🔧 Converting automatic strategy to manual tag');
        // This is an automatic strategy - convert it to a manual tag
        if (!analysisId) {
          throw new Error('Analysis ID is required to save manual tags');
        }
        
        // Get sentence text for the tag
        const sentenceText = targetSentences[strategy.targetPosition.sentence] || '';
        
        // Check if a manual tag already exists for this sentence and strategy
        const existingTag = manualTags.find(tag =>
          tag.sentence_index === strategy.targetPosition.sentence &&
          tag.tag_type === strategyCode
        );
        
        if (existingTag) {
          setTagError(`Tag ${strategyCode} já existe para esta frase`);
          return;
        }
        
        // Create new manual tag via API
        const result = await ManualTagsService.createTag({
          tagType: strategyCode,
          sentenceIndex: strategy.targetPosition.sentence,
          sentenceText: sentenceText,
          analysisId: analysisId,
          userNotes: `Converted from automatic strategy: ${strategy.fullName}`
        });
        console.log('🔧 Create result:', result);
        
        if (result.success) {
          // Add to local state
          setManualTags(prevTags => [...prevTags, result.tag]);
          console.log('✅ Automatic strategy converted to manual tag successfully');
          
          // Also call the callback to update the UI
          if (onStrategyUpdate) {
            onStrategyUpdate(editingTag, selectedStrategy);
          }
        } else {
          setTagError(result.message || 'Erro ao converter estratégia para tag manual');
        }
      }
    } catch (error) {
      console.error('❌ Failed to save tag:', error);
      setTagError(error.message || 'Erro ao salvar alterações na tag');
    } finally {
      setSavingTag(false);
      setEditingTag(null);
      setSelectedStrategy('');
    }
  };

  const handleCancelEdit = () => {
    setEditingTag(null);
    setSelectedStrategy('');
    setTagError(null);
  };

  // Handle double-click to add new tag
  const handleAddTagAtPosition = (sentenceIndex, event) => {
    event.preventDefault();
    setInsertPosition({ sentence: sentenceIndex });
    setAddingTag(true);
    setSelectedStrategy('');
  };

  // Handle saving new manually added tag
  const handleSaveNewTag = async () => {
    if (!analysisId || !insertPosition || !selectedStrategy) return;
    
    setSavingTag(true);
    setTagError(null);
    
    try {
      // Get the strategy code from the selected Portuguese name
      const strategyCode = getStrategyCodeByName(selectedStrategy);
      
      if (!strategyCode) {
        throw new Error('Código de estratégia inválido');
      }
      
      // Get sentence text for the tag
      const sentenceText = targetSentences[insertPosition.sentence] || '';
      
      // Check if tag already exists for this sentence and strategy
      const existingTag = manualTags.find(tag =>
        tag.sentence_index === insertPosition.sentence &&
        tag.tag_type === strategyCode
      );
      
      if (existingTag) {
        setTagError(`Tag ${strategyCode} já existe para esta frase`);
        return;
      }
      
      // Create tag via API
      const result = await ManualTagsService.createTag({
        tagType: strategyCode,
        sentenceIndex: insertPosition.sentence,
        sentenceText: sentenceText,
        analysisId: analysisId
      });
      
      if (result.success) {
        // Add to local state
        setManualTags(prevTags => [...prevTags, result.tag]);
        
        // Also update via callback if provided (for backward compatibility)
        if (onStrategyUpdate) {
          const newStrategy = {
            id: result.tag.id,
            code: strategyCode,
            fullName: STRATEGY_METADATA[strategyCode]?.name || strategyCode,
            confidence: 1.0,
            evidence: ['Manually added by human validator'],
            color: getStrategyColor(strategyCode),
            isAutomatic: false,
            targetPosition: {
              sentence: insertPosition.sentence,
              type: 'sentence'
            },
            sourcePosition: {
              sentence: insertPosition.sentence,
              type: 'sentence'
            }
          };
          onStrategyUpdate('add', newStrategy);
        }
        
        console.log('Manual tag created successfully:', result.tag);
      } else {
        setTagError(result.message || 'Erro ao criar tag manual');
      }
    } catch (error) {
      console.error('Failed to create manual tag:', error);
      setTagError(error.message || 'Erro ao criar tag manual');
    } finally {
      setSavingTag(false);
      setAddingTag(false);
      setInsertPosition(null);
      setSelectedStrategy('');
    }
  };

  // Handle canceling new tag addition
  const handleCancelNewTag = () => {
    setAddingTag(false);
    setInsertPosition(null);
    setSelectedStrategy('');
    setTagError(null);
  };

  // Handle tag deletion
  const handleDeleteTag = async (strategyId) => {
    console.log('🔧 handleDeleteTag called:', { strategyId });
    
    if (!strategyId) {
      console.log('❌ handleDeleteTag: missing strategyId');
      return;
    }
    
    setSavingTag(true);
    setTagError(null);
    
    try {
      // Find the strategy being deleted
      const strategy = strategiesDetected.find(s => s.id === strategyId);
      console.log('🔧 Found strategy to delete:', strategy);
      
      if (!strategy) {
        throw new Error('Estratégia não encontrada');
      }
      
      // Only allow deletion of manual tags
      if (!strategy.isAutomatic || strategy.isManual) {
        console.log('🔧 Deleting manual tag via API');
        // This is a manual tag - delete it via API
        const result = await ManualTagsService.deleteTag(strategyId);
        console.log('🔧 Delete result:', result);
        
        if (result.success) {
          // Remove from local state
          setManualTags(prevTags => prevTags.filter(tag => tag.id !== strategyId));
          console.log('✅ Manual tag deleted successfully');
        } else {
          setTagError(result.message || 'Erro ao excluir tag');
        }
      } else {
        console.log('❌ Cannot delete automatic strategy');
        setTagError('Não é possível excluir estratégias automáticas');
        return;
      }
      
      // Also use callback for UI updates if provided
      if (onStrategyUpdate) {
        console.log('🔧 Calling onStrategyUpdate for delete');
        onStrategyUpdate('delete', strategyId);
      }
    } catch (error) {
      console.error('❌ Failed to delete tag:', error);
      setTagError(error.message || 'Erro ao excluir tag');
    } finally {
      setSavingTag(false);
    }
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
            {loadingTags && <span> (Carregando tags...)</span>}
            {tagError && <div className="error-message">❌ {tagError}</div>}
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
                              disabled={savingTag}
                            >
                              <option value="">Selecione estratégia...</option>
                              {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
                                <option key={code} value={metadata.name}>
                                  {code} - {metadata.name}
                                </option>
                              ))}
                            </select>
                            <button
                              onClick={handleSaveTag}
                              className="save-btn"
                              disabled={savingTag || !selectedStrategy}
                            >
                              {savingTag ? '...' : <Check size={14} />}
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              className="cancel-btn"
                              disabled={savingTag}
                            >
                              <X size={14} />
                            </button>
                          </div>
                        ) : (
                          <div className="strategy-tag-wrapper">
                            <button
                              className="strategy-tag unified-tag"
                              style={{
                                backgroundColor: strategy.color,
                                color: getContrastingTextColor(strategy.color)
                              }}
                              onClick={() => handleEditTag(strategy.id, strategy.fullName || strategy.code)}
                              title={`${strategy.fullName || strategy.code} - Confiança: ${Math.round(strategy.confidence * 100)}% - ${strategy.isAutomatic ? 'Automático' : 'Manual'}`}
                              disabled={savingTag}
                            >
                              <span className="tag-code">[{strategy.code}]</span>
                              <Edit3 size={12} className="edit-icon" />
                              <span className="confidence">
                                {Math.round(strategy.confidence * 100)}%
                              </span>
                            </button>
                            {!strategy.isAutomatic && (
                              <button
                                className="delete-tag-btn"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteTag(strategy.id);
                                }}
                                title="Excluir tag manual"
                                disabled={savingTag}
                              >
                                <X size={12} />
                              </button>
                            )}
                          </div>
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
                            disabled={savingTag}
                          >
                            <option value="">Selecione estratégia para adicionar...</option>
                            {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
                              <option key={code} value={metadata.name}>
                                {code} - {metadata.name}
                              </option>
                            ))}
                          </select>
                          <button
                            onClick={handleSaveNewTag}
                            className="save-btn"
                            disabled={savingTag || !selectedStrategy}
                          >
                            {savingTag ? '...' : <Check size={14} />}
                          </button>
                          <button
                            onClick={handleCancelNewTag}
                            className="cancel-btn"
                            disabled={savingTag}
                          >
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
