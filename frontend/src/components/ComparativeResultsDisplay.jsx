/**
 * ComparativeResultsDisplay.jsx - Phase 2.B.5 Implementation
 * Display component for comparative analysis results with color mapping and human-in-the-loop editing
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  FileText,
  TrendingUp,
  BarChart3,
  Target,
  Download,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  Info,
  Edit3,
  Check,
  X,
  Plus,
  Trash2
} from 'lucide-react';
import {
  getStrategyColor,
  getStrategyInfo,
  getStrategyClassName,
  generateStrategyCSSClasses,
  STRATEGY_METADATA
} from '../services/strategyColorMapping.js';
// Phase 2a superscript markers
import StrategySuperscriptRenderer from './strategies/StrategySuperscriptRenderer.jsx';
// Phase 2b detail panel
import StrategyDetailPanel from './strategies/StrategyDetailPanel.jsx';
import StrategyFilterBar from './strategies/StrategyFilterBar.jsx';
import HighContrastPatternLegend from './strategies/HighContrastPatternLegend.jsx';
// Unified mapping (Phase 2d Step1/2)
import { buildUnifiedStrategyMap, segmentTextForHighlights, injectUnifiedCSS } from '../services/unifiedStrategyMapping.js';

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
  }
  return code || strategyName;
};

const ComparativeResultsDisplay = ({
  analysisResult,
  onExport = () => {},
  isExporting = false,
  className = "",
  useColorblindFriendly = false,
  onStrategyUpdate = null
}) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [isLocalExporting, setIsLocalExporting] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    lexical: true,
    syntactic: false,
    strategies: true,
    readability: false,
  });
  const [hoveredStrategy, setHoveredStrategy] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  
  // Human-in-the-loop editing state
  const [manualStrategies, setManualStrategies] = useState([]);
  const [deletedAutoStrategies, setDeletedAutoStrategies] = useState([]);
  const [editingTag, setEditingTag] = useState(null);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedText, setSelectedText] = useState(null);
  // Phase 2b: active strategy detail panel state
  const [activeStrategyId, setActiveStrategyId] = useState(null);
  const lastFocusedMarkerRef = React.useRef(null);
  // Phase 2c filtering + accessibility states
  const [activeCodes, setActiveCodes] = useState([]); // populated after strategies load
  const [confidenceMin, setConfidenceMin] = useState(0); // percent
  const [colorblindMode, setColorblindMode] = useState(useColorblindFriendly);
  const [rovingIndex, setRovingIndex] = useState(0);
  // Feature flag for dark launch of unified highlighting
  const [enableUnifiedHighlighting] = useState(true); // set false to rollback quickly

  // Filter raw strategies early (must be declared before unifiedStrategyMap useMemo)
  const filteredRawStrategies = useMemo(() => {
    const list = analysisResult?.simplification_strategies || [];
    return list.filter(s => activeCodes.includes(s.code) && ((s.confidence ?? s.confidence_score ?? 0) * 100) >= confidenceMin);
  }, [analysisResult?.simplification_strategies, activeCodes, confidenceMin]);

  // Build unified map (strategies include filtered list for color scope determinism)
  const unifiedStrategyMap = useMemo(() => {
    if (!enableUnifiedHighlighting) return {};
    return buildUnifiedStrategyMap(filteredRawStrategies, { colorblindMode, enablePatterns: colorblindMode });
  }, [filteredRawStrategies, colorblindMode, enableUnifiedHighlighting]);

  // Inject CSS when map changes
  useEffect(() => {
    if (enableUnifiedHighlighting) {
      injectUnifiedCSS(unifiedStrategyMap);
    }
  }, [unifiedStrategyMap, enableUnifiedHighlighting]);

  // Guard: clear active strategy only if it no longer exists after analysis updates
  useEffect(() => {
    if (!activeStrategyId) return;
    const exists = (analysisResult?.simplification_strategies || []).some(s => (s.strategy_id || s.id) === activeStrategyId);
    if (!exists) {
      setActiveStrategyId(null);
    }
  }, [analysisResult?.simplification_strategies, activeStrategyId]);

  // Initialize active codes when strategies change
  useEffect(() => {
    const codes = (analysisResult?.simplification_strategies || []).map(s => s.code).filter(Boolean);
    const uniq = Array.from(new Set(codes));
    setActiveCodes(uniq);
  }, [analysisResult?.simplification_strategies]);

  // Helper function to convert Portuguese strategy name to code
  // (Keeping this utility as it's used in strategy processing)
  const getStrategyCodeByName = useCallback((strategyName) => {
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
    
    // Return null to indicate this strategy should be skipped
    return null;
  }, []);

  // Process analysis result to extract strategies - use backend-provided data
  const strategiesDetected = useMemo(() => {
    const strategies = analysisResult?.simplification_strategies?.map((strategy, index) => {
      // Use backend-provided code if available, otherwise derive from name
      const strategyCode = strategy.code || getStrategyCode(strategy.name);
      return {
        id: `strategy_${index}_${strategyCode}`,
        code: strategyCode,
        name: strategy.name,
        confidence: strategy.confidence,
        evidence: strategy.evidence || [],
        // Use backend-provided color if available, otherwise generate
        color: strategy.color || getStrategyColor(strategyCode, colorblindMode),
        info: getStrategyInfo(strategyCode),
        isAutomatic: true,
        // Include backend-provided position data
        targetPosition: strategy.targetPosition,
        sourcePosition: strategy.sourcePosition
      };
    }) || [];

    // Debug logging to help identify issues (can be removed in production)
    if (strategies.length > 0) {
      console.log('🎯 Strategies detected:', strategies.length);
      strategies.forEach((strategy, index) => {
        console.log(`Strategy ${index + 1}: ${strategy.code} - ${strategy.name}`);
        console.log(`  Position data:`, {
          targetPosition: strategy.targetPosition,
          sourcePosition: strategy.sourcePosition
        });
      });
    }

    return strategies;
  }, [analysisResult, colorblindMode]);

  // Generate CSS for strategy highlighting
  useEffect(() => {
    const styleId = 'strategy-highlighting-styles-comparative';
    let styleElement = document.getElementById(styleId);
    
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      document.head.appendChild(styleElement);
    }
    
    styleElement.textContent = generateStrategyCSSClasses(colorblindMode);
  }, [colorblindMode]);

  const handleExport = async (format) => {
    setIsLocalExporting(true);
    try {
      await onExport(format);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsLocalExporting(false);
    }
  };

  if (!analysisResult) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>Nenhuma análise comparativa disponível</p>
      </div>
    );
  }

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-blue-600 bg-blue-50 border-blue-200';
    }
  };

  const getStrategyIcon = (strategy) => {
    switch (strategy.type) {
      case 'lexical': return <Target className="w-4 h-4" />;
      case 'syntactic': return <BarChart3 className="w-4 h-4" />;
      case 'semantic': return <Eye className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  // Human-in-the-loop editing handlers

  // Simple handler to prevent ReferenceError - text selection functionality is commented out
  const handleTextSelection = useCallback(() => {
    // Text selection functionality is currently disabled
    // This prevents the ReferenceError when clicking on target text
  }, []);

  const handleAddManualTag = useCallback((strategyName) => {
    if (!selectedText || !strategyName) return;

    const strategyCode = getStrategyCodeByName(strategyName);
    if (!strategyCode) return;

    const newStrategy = {
      id: `manual_${Date.now()}`,
      code: strategyCode,
      name: strategyName,
      confidence: 1.0, // Manual tags have 100% confidence
      evidence: [`Manually added: "${selectedText.text}"`],
      color: getStrategyColor(strategyCode, useColorblindFriendly),
      info: getStrategyInfo(strategyCode),
      isAutomatic: false,
      selectedText: selectedText.text,
      startIndex: selectedText.startIndex,
      endIndex: selectedText.endIndex
    };

    setManualStrategies(prev => [...prev, newStrategy]);
    setContextMenu(null);
    setSelectedText(null);
    
    // Clear selection
    window.getSelection().removeAllRanges();

    // Notify parent component if callback provided
    if (onStrategyUpdate) {
      onStrategyUpdate('add', newStrategy);
    }
  }, [selectedText, getStrategyCodeByName, useColorblindFriendly, onStrategyUpdate]);

  // Commented out tag editing functions
  // const handleEditTag = useCallback((strategyId, currentStrategy) => {
  //   setEditingTag(strategyId);
  //   setSelectedStrategy(currentStrategy);
  // }, []);

  // const handleSaveTag = useCallback(() => {
  //   if (!editingTag || !selectedStrategy) return;

  //   const strategyCode = getStrategyCodeByName(selectedStrategy);
  //   if (!strategyCode) return;

  //   // Update manual strategies
  //   setManualStrategies(prev => prev.map(strategy =>
  //     strategy.id === editingTag
  //       ? {
  //           ...strategy,
  //           code: strategyCode,
  //           name: selectedStrategy,
  //           color: getStrategyColor(strategyCode, useColorblindFriendly),
  //           info: getStrategyInfo(strategyCode)
  //         }
  //       : strategy
  //   ));

  //   setEditingTag(null);
  //   setSelectedStrategy('');

  //   // Notify parent component
  //   if (onStrategyUpdate) {
  //     onStrategyUpdate('edit', { id: editingTag, strategy: selectedStrategy });
  //   }
  // }, [editingTag, selectedStrategy, getStrategyCodeByName, useColorblindFriendly, onStrategyUpdate]);

  // const handleDeleteTag = useCallback((strategyId) => {
  //   setManualStrategies(prev => prev.filter(strategy => strategy.id !== strategyId));
    
  //   // Notify parent component
  //   if (onStrategyUpdate) {
  //     onStrategyUpdate('delete', { id: strategyId });
  //   }
  // }, [onStrategyUpdate]);

  // const handleCancelEdit = useCallback(() => {
  //   setEditingTag(null);
  //   setSelectedStrategy('');
  // }, []);

  // Commented out context menu effect
  // useEffect(() => {
  //   const handleClickOutside = () => {
  //     setContextMenu(null);
  //     setSelectedText(null);
  //   };

  //   document.addEventListener('click', handleClickOutside);
  //   return () => document.removeEventListener('click', handleClickOutside);
  // }, []);

  // Apply highlighting to text based on detected strategies with interactive editing
  const highlightText = (text, isTarget = false, paraIndex = 0) => {
    if (!text) {
      return <span className="unhighlighted-text">Texto não disponível</span>;
    }

    // For source text, just return the text
    // Unified highlighting path (source & target) when enabled
    if (enableUnifiedHighlighting) {
      const scope = isTarget ? 'target' : 'source';
      const segments = segmentTextForHighlights(text, filteredRawStrategies, { scope });
      if (segments.length === 0) {
        return <div className="highlighted-text-container">{text}</div>;
      }
      // For now sentence-based segmentation; simple reconstruction
      const sentences = text.split(/[.!?]+/).filter(s => s.trim()).map(s => s.trim() + '.');
      return (
        <div className="highlighted-text-container" data-scope={scope}>
          {sentences.map((sentence, idx) => {
            const seg = segments.find(s => s.sentenceIndex === idx);
            if (!seg) return <span key={idx}>{sentence + ' '}</span>;
            const mapEntry = unifiedStrategyMap[seg.code];
            const cls = 'unified-highlight ' + (scope === 'source' ? 'source' : 'target');
            const style = mapEntry ? { color: mapEntry.textColor } : {};
            return (
              <span
                key={idx}
                className={cls}
                data-code={seg.code}
                data-strategy-id={seg.strategy_id}
                style={style}
                title={`${seg.code}`}
              >{sentence + ' '}</span>
            );
          })}
        </div>
      );
    }

    // Legacy path (unchanged) below when not enabled
    if (!isTarget) {
      return (
        <div
          className="highlighted-text-container"
          style={{
            userSelect: 'none',
            cursor: 'default'
          }}
        >
          {text}
        </div>
      );
    }

    // For target text, apply strategy-based highlighting
    return (
      <div
        className="highlighted-text-container selectable-text"
        onMouseUp={handleTextSelection}
        style={{
          userSelect: 'text',
          cursor: 'text'
        }}
      >
        {renderHighlightedText(text, paraIndex)}
      </div>
    );
  };

  // Calculate global sentence indices for proper position mapping
  const targetSentenceMap = useMemo(() => {
    const map = new Map();
    let globalIndex = 0;

    // Split target text into paragraphs and then sentences
    const targetParas = analysisResult?.target_text?.split('\n').filter(para => para.trim()) || [];

    targetParas.forEach((para, paraIndex) => {
      const sentences = para.split(/[.!?]+/).filter(s => s.trim()).map(s => s.trim() + '.');
      sentences.forEach((sentence, localIndex) => {
        map.set(globalIndex, { paraIndex, localIndex, sentence });
        globalIndex++;
      });
    });
    return map;
  }, [analysisResult?.target_text]);

  // Render text with strategy highlighting based on position data
  const renderHighlightedText = (text, paraIndex = 0) => {
    if (!strategiesDetected.length) {
      return text;
    }

    // Split current paragraph into sentences
    const sentences = text.split(/[.!?]+/).filter(s => s.trim()).map(s => s.trim() + '.');

    return sentences.map((sentence, localSentenceIndex) => {
      // Find the global sentence index for this paragraph + local sentence
      let globalSentenceIndex = -1;
      for (const [globalIdx, mapping] of targetSentenceMap.entries()) {
        if (mapping.paraIndex === paraIndex && mapping.localIndex === localSentenceIndex) {
          globalSentenceIndex = globalIdx;
          break;
        }
      }

      // Find strategies that apply to this global sentence index
      const applicableStrategies = strategiesDetected.filter(strategy => {
        // Check if strategy has position data
        if (!strategy.targetPosition) {
          return false;
        }

        // Handle dictionary-based positioning (backend format)
        if (strategy.targetPosition.type === 'sentence') {
          return strategy.targetPosition.sentence === globalSentenceIndex;
        }

        return false;
      });

      if (applicableStrategies.length > 0) {
        // Use the first applicable strategy for highlighting
        const strategy = applicableStrategies[0];
        return (
          <span
            key={localSentenceIndex}
            className="strategy-highlight"
            style={{
              backgroundColor: strategy.color + '40', // Add transparency
              borderRadius: '3px',
              padding: '2px 4px',
              margin: '0 1px',
              border: `1px solid ${strategy.color}`,
              cursor: 'pointer'
            }}
            data-strategy={strategy.code}
            onMouseEnter={handleTextHover}
            onMouseLeave={handleTextOut}
            title={`${strategy.code}: ${strategy.name} (${Math.round(strategy.confidence * 100)}% confidence)`}
          >
            {sentence}
          </span>
        );
      }

      // Return unhighlighted sentence
      return (
        <span key={localSentenceIndex}>
          {sentence + ' '}
        </span>
      );
    });
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

  // Commented out context menu rendering
  // const renderContextMenu = () => {
  //   if (!contextMenu) return null;

  //   return (
  //     <div
  //       className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg py-2 min-w-48"
  //       style={{
  //         left: contextMenu.x,
  //         top: contextMenu.y,
  //       }}
  //       onClick={(e) => e.stopPropagation()}
  //     >
  //       <div className="px-3 py-1 text-xs text-gray-500 border-b border-gray-200 mb-1">
  //         Adicionar estratégia ao texto selecionado:
  //       </div>
  //       {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
  //         <button
  //           key={code}
  //           className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
  //           onClick={() => handleAddManualTag(metadata.name)}
  //         >
  //           <div
  //             className="w-3 h-3 rounded"
  //             style={{ backgroundColor: getStrategyColor(code, useColorblindFriendly) }}
  //           />
  //           <span className="font-medium">{code}</span>
  //           <span className="text-gray-600">- {metadata.name}</span>
  //         </button>
  //       ))}
  //     </div>
  //   );
  // };

  const renderTooltip = () => {
    if (!hoveredStrategy) return null;

    const strategy = strategiesDetected.find(s => s.code === hoveredStrategy);
    if (!strategy) return null;

    return (
      <div
        className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg p-3 max-w-xs"
        style={{
          left: tooltipPosition.x + 10,
          top: tooltipPosition.y - 10,
        }}
      >
        <div className="font-semibold text-gray-900">
          {strategy.code} - {strategy.info.name}
        </div>
        <div className="text-sm text-gray-600 mt-1">
          {strategy.info.description}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Confiança: {Math.round(strategy.confidence * 100)}%
          {strategy.isAutomatic !== undefined && (
            <span className="ml-2">
              ({strategy.isAutomatic ? 'Automático' : 'Manual'})
            </span>
          )}
        </div>
        {strategy.selectedText && (
          <div className="text-xs text-blue-600 mt-1">
            Texto: "{strategy.selectedText}"
          </div>
        )}
      </div>
    );
  };

  return (
    <>
  <div className={`space-y-6 ${className}`} data-testid="results-container">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <BarChart3 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Resultados da Análise Comparativa</h3>
              <p className="text-sm text-gray-600 mt-1">
                Análise realizada em {new Date(analysisResult.timestamp).toLocaleString('pt-BR')}
              </p>
              <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                {(() => {
                  // Calculate word counts from the text
                  const sourceWords = analysisResult.source_text?.split(/\s+/).filter(word => word.length > 0).length || 0;
                  const targetWords = analysisResult.target_text?.split(/\s+/).filter(word => word.length > 0).length || 0;
                  const wordReduction = sourceWords > 0 ? ((sourceWords - targetWords) / sourceWords * 100).toFixed(1) : 0;
                  
                  return (
                    <>
                      <span>Texto fonte: {sourceWords} palavras</span>
                      <span>Texto simplificado: {targetWords} palavras</span>
                      <span>Redução: {wordReduction}%</span>
                    </>
                  );
                })()}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleExport('pdf')}
              disabled={isExporting || isLocalExporting}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
            >
              {(isExporting || isLocalExporting) ? (
                <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Download className="w-3 h-3" />
              )}
              Exportar PDF
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
            { id: 'comparison', label: 'Comparação', icon: FileText },
            { id: 'strategies', label: 'Estratégias', icon: Target },
            { id: 'metrics', label: 'Métricas', icon: TrendingUp },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveSection(id)}
              className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeSection === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content Sections */}
      <div className="space-y-6">
        {/* Overview Section */}
        {activeSection === 'overview' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Resumo Executivo</h4>
            
            {/* Text Characteristics */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h5 className="font-medium text-gray-900">Características Textuais</h5>
              </div>
              
              {(() => {
                // Calculate word counts instead of character counts
                const sourceWords = analysisResult.source_text ? 
                  analysisResult.source_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const targetWords = analysisResult.target_text ? 
                  analysisResult.target_text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
                const reduction = sourceWords > 0 ? ((sourceWords - targetWords) / sourceWords) * 100 : 0;
                const reductionRounded = Math.round(reduction * 10) / 10;
                
                return (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Redução de palavras:</span>
                      <span className={`text-sm font-medium ${
                        reductionRounded > 0 ? 'text-green-600' : 
                        reductionRounded < 0 ? 'text-orange-600' : 'text-gray-600'
                      }`}>
                        {reductionRounded > 0 ? `-${reductionRounded}%` : 
                         reductionRounded < 0 ? `+${Math.abs(reductionRounded)}%` : '0%'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Palavras fonte:</span>
                      <span className="text-sm font-medium">{sourceWords.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Palavras alvo:</span>
                      <span className="text-sm font-medium">{targetWords.toLocaleString()}</span>
                    </div>
                  </div>
                );
              })()}
              
              <p className="text-sm text-gray-600 mt-3">
                {(() => {
                  const strategiesCount = analysisResult.strategies?.length || 0;
                  if (strategiesCount === 0) {
                    return "Nenhuma estratégia de simplificação específica foi identificada automaticamente.";
                  } else if (strategiesCount === 1) {
                    return `Foi identificada 1 estratégia de simplificação principal.`;
                  } else {
                    return `Foram identificadas ${strategiesCount} estratégias de simplificação.`;
                  }
                })()}
              </p>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                {
                  label: 'Preservação Semântica',
                  value: `${analysisResult.semantic_preservation?.toFixed(1)}%`,
                  color: analysisResult.semantic_preservation >= 90 ? 'green' : 
                         analysisResult.semantic_preservation >= 70 ? 'yellow' : 'red'
                },
                {
                  label: 'Melhoria da Legibilidade',
                  value: `+${analysisResult.readability_improvement?.toFixed(1)}pts`,
                  color: analysisResult.readability_improvement >= 10 ? 'green' : 
                         analysisResult.readability_improvement >= 5 ? 'yellow' : 'red'
                },
                {
                  label: 'Estratégias Identificadas',
                  value: analysisResult.strategies_count,
                  color: 'blue'
                }
              ].map((metric, index) => (
                <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="text-sm text-gray-600">{metric.label}</div>
                  <div className={`text-2xl font-semibold mt-1 ${
                    metric.color === 'green' ? 'text-green-600' :
                    metric.color === 'yellow' ? 'text-yellow-600' :
                    metric.color === 'red' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {metric.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Side-by-side Comparison */}
        {activeSection === 'comparison' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Comparação Lado a Lado com Mapeamento de Estratégias</h4>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Source Text */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-gray-500" />
                  <h5 className="font-medium text-gray-900">Texto Fonte (Original)</h5>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {analysisResult.source_text?.split(/\s+/).filter(word => word.length > 0).length || 0} palavras
                  </span>
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="text-sm text-gray-700 font-sans leading-relaxed">
                    {highlightText(analysisResult.source_text || analysisResult.sourceText, false, 0)}
                  </div>
                </div>
              </div>

              {/* Target Text */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-green-600" />
                  <h5 className="font-medium text-gray-900">Texto Simplificado</h5>
                  <span className="text-xs text-gray-500 bg-green-100 px-2 py-1 rounded">
                    {analysisResult.target_text?.split(/\s+/).filter(word => word.length > 0).length || 0} palavras
                  </span>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                  {/* Phase 2a superscript marker layer (additive, non-breaking) */}
      {filteredRawStrategies.length > 0 && (
                    <div
                      className="superscript-layer-wrapper selectable-text"
                      aria-label="Marcadores de estratégias detectadas"
                      onMouseUp={handleTextSelection} // Preserve manual selection handler
                      style={{ cursor: 'text', userSelect: 'text' }}
                    >
                      <StrategySuperscriptRenderer
                        targetText={analysisResult.target_text || analysisResult.targetText}
                        strategies={filteredRawStrategies}
                        colorblindMode={colorblindMode}
                        activeStrategyId={activeStrategyId}
        rovingIndex={rovingIndex}
        onRovingIndexChange={setRovingIndex}
                        onMarkerActivate={(id, el, idx) => {
                          if (id) {
                            lastFocusedMarkerRef.current = el || document.querySelector(`[data-strategy-id="${id}"]`);
                            setActiveStrategyId(id);
                            if (typeof idx === 'number') setRovingIndex(idx);
                          }
                        }}
                        unifiedMap={unifiedStrategyMap}
                      />
                    </div>
                  )}
                  {/* Legacy color-mapped sentence highlighting removed to avoid duplicate rendering */}
                </div>
                {strategiesDetected.length > 0 && (
                  <div className="text-xs text-gray-600 bg-blue-50 p-2 rounded">
                    💡 Os marcadores sobrescritos (¹²³…) indicam onde as estratégias foram detectadas. Selecione texto para adicionar estratégias manuais.
                  </div>
                )}
              </div>
            </div>

            {/* Interactive Strategy Legend with Manual Editing */}
            {strategiesDetected.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Estratégias de Simplificação Detectadas
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {strategiesDetected.map(strategy => (
                    <div
                      key={strategy.id}
                      className="flex items-center gap-3 p-3 rounded-lg border bg-gray-50"
                      style={{ borderLeftColor: strategy.color, borderLeftWidth: '3px' }}
                    >
                      <div
                        className="w-8 h-8 rounded flex items-center justify-center text-xs font-bold"
                        style={{
                          backgroundColor: strategy.color,
                          color: getContrastingTextColor(strategy.color)
                        }}
                      >
                        {strategy.code}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm text-gray-900">{strategy.info.name}</span>
                        </div>
                        <div className="text-xs text-gray-600">
                          {Math.round(strategy.confidence * 100)}% confiança
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Highlighted Differences */}
            {analysisResult.highlightedDifferences && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3">Principais Diferenças Identificadas</h5>
                <div className="space-y-2">
                  {analysisResult.highlightedDifferences.map((diff, index) => (
                    <div key={index} className="flex items-start gap-3 p-2 bg-yellow-50 rounded">
                      <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <div className="text-sm">
                        <span className="font-medium text-yellow-800">{diff.type}:</span>
                        <span className="text-yellow-700 ml-1">{diff.description}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Simplification Strategies */}
        {activeSection === 'strategies' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Estratégias de Simplificação Identificadas</h4>
            
            <div className="space-y-3">
      {analysisResult.simplification_strategies?.map((strategy, index) => {
                // Use backend-provided code if available
                const strategyCode = strategy.code || getStrategyCode(strategy.name);
                const strategyColor = strategy.color || getStrategyColor(strategyCode, useColorblindFriendly);

                return (
        <div key={index} className="bg-white border border-gray-200 rounded-lg p-4" data-testid="strategy-result">
                    <div className="flex items-start gap-3">
                      <div
                        className="p-2 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: strategyColor }}
                      >
                        <span className="text-xs font-bold text-white" data-testid="strategy-name">{strategyCode}</span>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h5 className="font-medium text-gray-900">{strategy.name}</h5>
                            <p className="text-sm text-gray-600 mt-1">{strategy.description}</p>
                          </div>
                          <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(strategy.impact)}`}>
                            {strategy.impact} impacto
                          </div>
                        </div>

                        {strategy.examples && strategy.examples.length > 0 && (
                          <div className="mt-3">
                            <h6 className="text-sm font-medium text-gray-700 mb-2">Exemplos:</h6>
                            <div className="space-y-1">
                              {strategy.examples.map((example, exIndex) => (
                                <div key={exIndex} className="text-sm bg-gray-50 p-2 rounded">
                                  <span className="text-red-600">"{example.original || example.before}"</span>
                                  <span className="text-gray-500 mx-2">→</span>
                                  <span className="text-green-600">"{example.simplified || example.after}"</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Detailed Metrics */}
        {activeSection === 'metrics' && (
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900">Métricas Detalhadas</h4>
            
            {/* Readability Metrics */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-4">Métricas de Legibilidade</h5>
              <div className="space-y-3">
                {analysisResult.readability_metrics && Object.entries(analysisResult.readability_metrics).map(([metric, data]) => (
                  <div key={metric} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{data.label}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-red-600">{data.source}</span>
                      <span className="text-gray-400">→</span>
                      <span className="text-sm text-green-600">{data.target}</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        data.improvement > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {data.improvement > 0 ? '+' : ''}{data.improvement}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Lexical Analysis */}
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <button
                onClick={() => toggleSection('lexical')}
                className="flex items-center justify-between w-full"
              >
                <h5 className="font-medium text-gray-900">Análise Lexical</h5>
                {expandedSections.lexical ? 
                  <ChevronDown className="w-4 h-4 text-gray-500" /> : 
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                }
              </button>
              
              {expandedSections.lexical && analysisResult.lexical_analysis && (
                <div className="mt-4 space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Vocabulário Único</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexical_analysis.source_unique_words}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexical_analysis.target_unique_words}</span>
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Complexidade Média</div>
                      <div className="flex items-center gap-2">
                        <span className="text-red-600">{analysisResult.lexical_analysis.source_complexity?.toFixed(2)}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-green-600">{analysisResult.lexical_analysis.target_complexity?.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Commented out context menu */}
      {/* {renderContextMenu()} */}
      
      {/* Tooltip for strategy hover */}
      {renderTooltip()}
    </div>
    {/* Phase 2b: strategy detail side panel */}
    <StrategyDetailPanel
      targetText={analysisResult.target_text || analysisResult.targetText}
      sourceText={analysisResult.source_text || analysisResult.sourceText}
      rawStrategies={filteredRawStrategies}
      activeStrategyId={activeStrategyId}
      onClose={() => setActiveStrategyId(null)}
      useColorblindFriendly={colorblindMode}
      returnFocusTo={lastFocusedMarkerRef.current}
    />
    {/* Strategy Filter Bar (Phase 2c) */}
    <div style={{ marginTop: '1rem' }}>
      <StrategyFilterBar
        strategies={analysisResult.simplification_strategies || []}
        activeCodes={activeCodes}
        onCodesChange={(codes) => { setActiveCodes(codes); setRovingIndex(0); }}
        confidenceMin={confidenceMin}
        onConfidenceChange={(val) => { setConfidenceMin(val); setRovingIndex(0); }}
        colorblindMode={colorblindMode}
        onColorblindToggle={setColorblindMode}
      />
  <HighContrastPatternLegend unifiedMap={unifiedStrategyMap} show={colorblindMode} />
    </div>
    </>
  );
};

// Utility function to get contrasting text color
function getContrastingTextColor(backgroundColor) {
  // Simple luminance calculation
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

export default ComparativeResultsDisplay;
