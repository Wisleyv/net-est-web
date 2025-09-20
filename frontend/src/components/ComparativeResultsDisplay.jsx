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
  getAccessibleTextColor,
  getStrategyInfo,
  getStrategyClassName,
  generateStrategyCSSClasses,
  STRATEGY_METADATA
} from '../services/strategyColorMapping.js';
// Phase 2a superscript markers
import StrategySuperscriptRenderer from './strategies/StrategySuperscriptRenderer.jsx';
// Phase 2b detail panel
import StrategyDetailPanel from './strategies/StrategyDetailPanel.jsx';
import useAnnotationStore from '../stores/useAnnotationStore.js';
import StrategyFilterBar from './strategies/StrategyFilterBar.jsx';
// Unified mapping (Phase 2d Step1/2)
import { buildUnifiedStrategyMap, segmentTextForHighlights, injectUnifiedCSS, mergeOverlappingSegments } from '../services/unifiedStrategyMapping.js';

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
  const { createAnnotation, editingAnnotationId, modifyAnnotationSpan, clearEditingAnnotation, setSession, fetchAnnotations, annotations, rejectAnnotation, setEditingAnnotation, modifyAnnotation } = useAnnotationStore();
  // Phase 2b: active strategy detail panel state
  const [activeStrategyId, setActiveStrategyId] = useState(null);
  const lastFocusedMarkerRef = React.useRef(null);
  // Phase 2c filtering + accessibility states
  const [activeCodes, setActiveCodes] = useState([]); // populated after strategies load
  const [confidenceMin, setConfidenceMin] = useState(0); // percent
  const [rovingIndex, setRovingIndex] = useState(0);
  // Feature flag for dark launch of unified highlighting
  const [enableUnifiedHighlighting] = useState(true); // set false to rollback quickly
  // Inline editing state for panel-free approach
  const [inlineEditingStrategy, setInlineEditingStrategy] = useState(null);
  const [inlineEditPosition, setInlineEditPosition] = useState(null);

  // Global click outside to dismiss selection menu
  useEffect(() => {
    const handleClickOutside = () => {
      setContextMenu(null);
      setSelectedText(null);
      setInlineEditingStrategy(null);
      setInlineEditPosition(null);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Unified map will be defined after strategiesDetected

  // Guard: clear active strategy only if it no longer exists after analysis updates
  useEffect(() => {
    if (!activeStrategyId) return;
    const exists = (analysisResult?.simplification_strategies || []).some(s => (s.strategy_id || s.id) === activeStrategyId);
    if (!exists) {
      setActiveStrategyId(null);
    }
  }, [analysisResult?.simplification_strategies, activeStrategyId]);

  // Keep backend session aligned to current analysis_id so PATCH/POST use consistent session keys
  useEffect(() => {
    const session = analysisResult?.analysis_id || analysisResult?.id;
    if (session) {
      try { setSession(session); } catch {}
    }
  }, [analysisResult?.analysis_id, analysisResult?.id, setSession]);

  // Ensure repository has corresponding annotations by refreshing after analysis (backend seeds them)
  useEffect(() => {
    const session = analysisResult?.analysis_id || analysisResult?.id;
    const preds = analysisResult?.simplification_strategies || [];
    if (!session || !Array.isArray(preds) || preds.length === 0) return;
    // Request fresh list from backend (predictions are seeded server-side)
    try { fetchAnnotations(); } catch {}
  }, [analysisResult?.analysis_id, analysisResult?.simplification_strategies, fetchAnnotations]);

  // Initialize active codes when strategies change
  useEffect(() => {
    const codes = (analysisResult?.simplification_strategies || []).map(s => s.code).filter(Boolean);
    // Also include codes from manual annotations so they appear in UI
    const manualCodes = annotations
      .filter(ann => ann.origin === 'human' && ann.status === 'created')
      .map(ann => ann.strategy_code || ann.code)
      .filter(Boolean);
    const allCodes = [...codes, ...manualCodes];
    const uniq = Array.from(new Set(allCodes));
    setActiveCodes(uniq);
  }, [analysisResult?.simplification_strategies, annotations]);

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
    const rawStrategies = analysisResult?.simplification_strategies || [];
    const strategies = rawStrategies.map((strategy, index) => {
      // Use backend-provided code if available, otherwise derive from name
      const strategyCode = strategy.code || getStrategyCode(strategy.name);
      const strategyId = strategy.strategy_id || strategy.id || `strategy_${index}_${strategyCode}`;
      
      // Check if this strategy has been modified in the annotation store
      const annotation = annotations.find(a => 
        a.strategy_id === strategyId || 
        a.id === strategyId || 
        (a.strategy_id === strategy.strategy_id && strategy.strategy_id) ||
        (a.id === strategy.id && strategy.id)
      );
      
      // Use annotation data if available (for real-time updates), otherwise use original strategy data
      const effectiveCode = annotation?.strategy_code || annotation?.code || strategyCode;
      const effectiveStatus = annotation?.status || 'pending';
      const isModified = annotation?.status === 'modified';
      const originalCode = annotation?.original_code;
      
      return {
        id: strategyId,
        strategy_id: strategyId,
        code: effectiveCode,
        strategy_code: effectiveCode,
        name: strategy.name,
        confidence: strategy.confidence,
        evidence: strategy.evidence || [],
        color: strategy.color || getStrategyColor(effectiveCode, false),
        info: getStrategyInfo(effectiveCode),
        isAutomatic: true,
        // Include backend-provided position data
        targetPosition: strategy.targetPosition,
        sourcePosition: strategy.sourcePosition,
        // Include annotation state for UI feedback
        status: effectiveStatus,
        original_code: originalCode,
        validated: annotation?.validated || false,
        manually_assigned: annotation?.manually_assigned || false
      };
    });

    // Add manual annotations that don't correspond to any original strategy
    const manualAnnotations = annotations.filter(annotation => 
      annotation.origin === 'human' && 
      annotation.status === 'created' &&
      !rawStrategies.some(strategy => {
        const strategyId = strategy.strategy_id || strategy.id || `strategy_${rawStrategies.indexOf(strategy)}_${strategy.code || getStrategyCode(strategy.name)}`;
        return annotation.strategy_id === strategyId || annotation.id === strategyId;
      })
    );

    manualAnnotations.forEach(annotation => {
      const strategyCode = annotation.strategy_code || annotation.code;
      strategies.push({
        id: annotation.id,
        strategy_id: annotation.strategy_id || annotation.id,
        code: strategyCode,
        strategy_code: strategyCode,
        name: getStrategyInfo(strategyCode)?.name || 'Manual Annotation',
        confidence: 1.0, // Manual annotations have 100% confidence
        evidence: [],
        color: getStrategyColor(strategyCode, false),
        info: getStrategyInfo(strategyCode),
        isAutomatic: false,
        // Use annotation's target_offsets for position data
        targetPosition: annotation.target_offsets?.[0] || null,
        sourcePosition: null,
        // Include annotation state
        status: annotation.status,
        validated: annotation.validated || false,
        manually_assigned: true
      });
    });

    return strategies;
  }, [analysisResult, annotations, getStrategyCode]);

  // Filter raw strategies based on confidence and active codes
  const filteredRawStrategies = useMemo(() => {
    return strategiesDetected.filter(s => activeCodes.includes(s.code) && ((s.confidence ?? s.confidence_score ?? 0) * 100) >= confidenceMin);
  }, [strategiesDetected, activeCodes, confidenceMin]);

  // Build unified map (strategies include filtered list for color scope determinism)
  const unifiedStrategyMap = useMemo(() => {
    if (!enableUnifiedHighlighting) return {};
    return buildUnifiedStrategyMap(filteredRawStrategies, { colorblindMode: false, enablePatterns: false });
  }, [filteredRawStrategies, enableUnifiedHighlighting]);

  // Inject CSS when map changes
  useEffect(() => {
    if (enableUnifiedHighlighting) {
      injectUnifiedCSS(unifiedStrategyMap);
    }
  }, [unifiedStrategyMap, enableUnifiedHighlighting]);

  // Store debug info for development
  useEffect(() => {
    if (import.meta.env.DEV) {
      window.debugHitl = {
        activeCodes,
        confidenceMin,
        strategiesDetected,
        filteredRawStrategies,
        unifiedStrategyMap,
        enableUnifiedHighlighting,
        hasAnalysisResult: !!analysisResult,
        analysisResultStrategies: analysisResult?.simplification_strategies?.length || 0,
        targetText: analysisResult?.target_text ? analysisResult.target_text.substring(0, 50) + '...' : 'none'
      };
    }
  }, [activeCodes, confidenceMin, strategiesDetected, filteredRawStrategies, unifiedStrategyMap, enableUnifiedHighlighting, analysisResult]);

  // Generate CSS for strategy highlighting
  useEffect(() => {
    const styleId = 'strategy-highlighting-styles-comparative';
    let styleElement = document.getElementById(styleId);
    
    if (!styleElement) {
      styleElement = document.createElement('style');
      styleElement.id = styleId;
      document.head.appendChild(styleElement);
    }
    
    styleElement.textContent = generateStrategyCSSClasses(false);
  }, []);

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

  // Do not early-return; hooks below must always run. Fallback is rendered in JSX.

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
  // Global context menu prevention for the results container
  useEffect(() => {
    const handleGlobalContextMenu = (e) => {
      // Only prevent context menu within our component
      const resultsContainer = document.querySelector('[data-testid="results-container"]');
      if (resultsContainer && resultsContainer.contains(e.target)) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
    };

    document.addEventListener('contextmenu', handleGlobalContextMenu, { capture: true });
    return () => {
      document.removeEventListener('contextmenu', handleGlobalContextMenu, { capture: true });
    };
  }, []);

  // Text selection handler - defined first to avoid hoisting issues
  const handleTextSelection = useCallback((e) => {
    try {
      const sel = window.getSelection();
      if (!sel || sel.rangeCount === 0) {
        return;
      }
      const range = sel.getRangeAt(0);
      // Use DOM-based position calculation for exact selection mapping
      const selectedString = sel.toString();
      if (!selectedString || selectedString.trim().length === 0) {
        return;
      }
      
      // Calculate character offsets from the actual DOM selection range
      const containerElement = range.commonAncestorContainer.nodeType === Node.TEXT_NODE 
        ? range.commonAncestorContainer.parentElement 
        : range.commonAncestorContainer;
      
      // Find the text content and calculate precise offsets
      const full = (analysisResult?.target_text || analysisResult?.targetText || '');
      let startOffset, endOffset;
      
      try {
        // Create a range that spans from start of container to start of selection
        const preRange = document.createRange();
        preRange.setStart(containerElement, 0);
        preRange.setEnd(range.startContainer, range.startOffset);
        startOffset = preRange.toString().length;
        endOffset = startOffset + selectedString.length;
        preRange.detach();
      } catch (rangeError) {
        // Fallback to indexOf only if DOM calculation fails
        startOffset = full.indexOf(selectedString);
        if (startOffset === -1) {
          return; // couldn't map reliably
        }
        endOffset = startOffset + selectedString.length;
      }
      // If we're editing an existing annotation's span, apply immediately
      if (editingAnnotationId) {
        modifyAnnotationSpan(editingAnnotationId, [{ start: startOffset, end: endOffset }])
          .finally(() => clearEditingAnnotation());
        try { window.getSelection().removeAllRanges(); } catch (e) { /* ignore selection clear errors */ }
        return;
      }
      // Else open add-annotation context menu
      setSelectedText({ text: selectedString, startIndex: startOffset, endIndex: endOffset });
      setContextMenu({ x: (e?.clientX || 0), y: (e?.clientY || 0) });
    } catch (err) { /* noop */ }
  }, [analysisResult?.target_text, analysisResult?.targetText, editingAnnotationId, modifyAnnotationSpan, clearEditingAnnotation]);

  // Enhanced context menu handler with robust Chrome support
  const handleContextMenu = useCallback((e) => {
    // Aggressive prevention for Chrome compatibility
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    
    // Additional Chrome-specific prevention
    if (e.nativeEvent) {
      e.nativeEvent.preventDefault();
      e.nativeEvent.stopPropagation();
      e.nativeEvent.stopImmediatePropagation();
    }
    
    const sel = window.getSelection();
    if (sel && sel.rangeCount > 0 && sel.toString().trim()) {
      handleTextSelection(e);
    }
    
    return false; // Additional prevention
  }, [handleTextSelection]);

  const handleAddManualTag = useCallback(async (strategyName) => {
    if (!selectedText || !strategyName) return;

    const strategyCode = getStrategyCodeByName(strategyName);
    if (!strategyCode) return;
    try {
      await createAnnotation({ strategy_code: strategyCode, target_offsets: [{ start: selectedText.startIndex, end: selectedText.endIndex }], comment: null });
    } catch (error) {
      console.error('Failed to create annotation:', error);
    } finally {
      setContextMenu(null);
      setSelectedText(null);
      try { window.getSelection().removeAllRanges(); } catch (e) { /* ignore selection clear errors */ }
      if (onStrategyUpdate) onStrategyUpdate('add', { strategy_code: strategyCode });
    }
  }, [selectedText, getStrategyCodeByName, createAnnotation, onStrategyUpdate]);

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

  // moved clickOutside effect above to satisfy hook rules

  // Apply highlighting to text based on detected strategies with interactive editing
  const highlightText = (text, isTarget = false, paraIndex = 0) => {
    if (!text) {
      return <span className="unhighlighted-text">Texto não disponível</span>;
    }

    // For source text, just return the text
    // Unified highlighting path (source & target) when enabled
    if (enableUnifiedHighlighting) {
      const scope = isTarget ? 'target' : 'source';
      let segments = segmentTextForHighlights(text, filteredRawStrategies, { scope });

      if (segments.length === 0) {
        return <div className="highlighted-text-container">{text}</div>;
      }

      // Phase 1: Handle overlapping segments by merging them
      segments = mergeOverlappingSegments(segments);

      // Character-based rendering with precise highlighting
      const elements = [];
      let currentPos = 0;

      segments.forEach((segment, idx) => {
        // Add any unhighlighted text before this segment
        if (currentPos < segment.charStart) {
          elements.push(
            <span key={`text-${idx}-before`}>
              {text.substring(currentPos, segment.charStart)}
            </span>
          );
        }

        // Add the highlighted segment
        const mapEntry = unifiedStrategyMap[segment.code];
        const cls = 'unified-highlight ' + (scope === 'source' ? 'source' : 'target');

        // Phase 1: Handle overlapping segments with single background + pattern
        let style = {};
        let title = '';
        let clickHandler = undefined;

        if (mapEntry) {
          // Use primary strategy color as background
          const baseColor = mapEntry.textColor;
          style = {
            color: baseColor,
            backgroundColor: baseColor + '20', // Add subtle background
            borderRadius: '3px',
            padding: '1px 2px',
            cursor: isTarget ? 'pointer' : 'default'
          };

          // Add pattern for overlapping segments
          if (segment.isMerged && segment.strategies && segment.strategies.length > 1) {
            // Create a diagonal stripe pattern for overlapping segments
            style.backgroundImage = `
              repeating-linear-gradient(
                45deg,
                ${baseColor}20 0px,
                ${baseColor}20 2px,
                ${baseColor}40 2px,
                ${baseColor}40 4px
              )
            `;
            title = `Múltiplas estratégias: ${segment.strategies.join(', ')}`;
          } else {
            title = `${segment.code} (${Math.round(segment.confidence * 100)}%)`;
          }

          // Set up click handler for target text
          if (isTarget) {
            clickHandler = (e) => {
              e.stopPropagation();
              // Use the primary strategy for inline editing
              const strategy = filteredRawStrategies.find(s => s.strategy_id === segment.strategy_id);
              if (strategy) {
                const rect = e.currentTarget.getBoundingClientRect();
                setInlineEditingStrategy(strategy);
                setInlineEditPosition({
                  x: rect.left + window.scrollX,
                  y: rect.bottom + window.scrollY,
                  charStart: segment.charStart,
                  charEnd: segment.charEnd
                });
                // Prevent side panel from opening
                setActiveStrategyId(null);
              }
            };
          }
        }

        elements.push(
          <span
            key={`highlight-${idx}`}
            className={cls}
            data-code={segment.code}
            data-strategy-id={segment.strategy_id}
            style={style}
            title={title}
            onClick={clickHandler}
            onMouseEnter={(e) => {
              setHoveredStrategy(segment.code);
              setTooltipPosition({ x: e.clientX, y: e.clientY });
            }}
            onMouseLeave={() => {
              setHoveredStrategy(null);
            }}
          >
            {segment.text}
          </span>
        );

        currentPos = segment.charEnd;
      });

      // Add any remaining unhighlighted text
      if (currentPos < text.length) {
        elements.push(
          <span key="text-after">
            {text.substring(currentPos)}
          </span>
        );
      }

      return (
        <div
          className="highlighted-text-container"
          data-scope={scope}
          onMouseUp={isTarget ? handleTextSelection : undefined}
          onContextMenu={isTarget ? (e) => {
            e.preventDefault();
            e.stopPropagation();
            // If there's a selection, trigger the same logic as onMouseUp
            const sel = window.getSelection();
            if (sel && sel.rangeCount > 0 && sel.toString().trim()) {
              handleTextSelection(e);
            }
          } : undefined}
          style={{
            userSelect: isTarget ? 'text' : 'none',
            cursor: isTarget ? 'text' : 'default'
          }}
        >
          {elements}
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
        onMouseUp={(e) => {
          handleTextSelection(e);
        }}
        onContextMenu={(e) => {
          e.preventDefault();
          e.stopPropagation();
          // If there's a selection, trigger the same logic as onMouseUp
          const sel = window.getSelection();
          if (sel && sel.rangeCount > 0 && sel.toString().trim()) {
            handleTextSelection(e);
          }
        }}
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

  const renderContextMenu = () => {
    if (!contextMenu) return null;

    return (
      <div
        className="fixed z-50 bg-white border border-gray-300 rounded-lg shadow-lg py-2 min-w-48"
        style={{ left: contextMenu.x, top: contextMenu.y }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-3 py-1 text-xs text-gray-500 border-b border-gray-200 mb-1">
          Adicionar estratégia ao texto selecionado:
        </div>
        {Object.entries(STRATEGY_METADATA).map(([code, metadata]) => (
          <button
            key={code}
            className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
            onClick={() => handleAddManualTag(metadata.name)}
          >
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: getStrategyColor(code, false) }}
            />
            <span className="font-medium">{code}</span>
            <span className="text-gray-600">- {metadata.name}</span>
          </button>
        ))}
      </div>
    );
  };

  const renderInlineEditor = () => {
    if (!inlineEditingStrategy || !inlineEditPosition) return null;

    const availableStrategies = Object.entries(STRATEGY_METADATA).filter(
      ([code, metadata]) => code !== 'UNK+' && metadata.name
    );

    return (
      <div
        className="fixed z-50 bg-white border-2 border-blue-300 rounded-lg shadow-xl p-4 min-w-80 max-w-96"
        style={{ 
          left: Math.min(inlineEditPosition.x, window.innerWidth - 400), 
          top: Math.max(inlineEditPosition.y - 10, 10),
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: getStrategyColor(inlineEditingStrategy.code, false) }}
            />
            <span className="font-bold text-sm text-blue-700">EDITANDO: {inlineEditingStrategy.code}</span>
          </div>
          <button
            onClick={() => {
              setInlineEditingStrategy(null);
              setInlineEditPosition(null);
            }}
            className="text-gray-400 hover:text-gray-600 text-lg font-bold w-6 h-6 flex items-center justify-center"
          >
            ✕
          </button>
        </div>
        
        <div className="text-sm text-gray-700 mb-2 font-medium">
          {inlineEditingStrategy.name}
        </div>
        
        <div className="text-xs text-gray-500 mb-4 p-2 bg-blue-50 rounded">
          📍 Posição: caracteres {inlineEditPosition.charStart}-{inlineEditPosition.charEnd}
        </div>

        {/* Strategy Type Selector */}
        <div className="mb-4">
          <label className="block text-sm font-bold text-gray-700 mb-2">
            Alterar Tipo de Estratégia:
          </label>
          <select
            value={inlineEditingStrategy.code}
            onChange={(e) => {
              const newCode = e.target.value;
              const newMetadata = STRATEGY_METADATA[newCode];
              setInlineEditingStrategy({
                ...inlineEditingStrategy,
                code: newCode,
                name: newMetadata?.name || newCode
              });
            }}
            className="w-full px-3 py-2 text-sm border-2 border-gray-300 rounded focus:outline-none focus:border-blue-500"
          >
            {availableStrategies.map(([code, metadata]) => (
              <option key={code} value={code}>
                {code} - {metadata.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          <button
            className="flex-1 px-4 py-2 text-sm bg-green-500 text-white rounded hover:bg-green-600 font-medium"
            onClick={async () => {
              try {
                // Save changes to strategy type
                await modifyAnnotation(inlineEditingStrategy.strategy_id, inlineEditingStrategy.code);
                setInlineEditingStrategy(null);
                setInlineEditPosition(null);
                if (onStrategyUpdate) onStrategyUpdate('update', inlineEditingStrategy);
              } catch (error) {
                console.error('Failed to update strategy:', error);
              }
            }}
          >
            ✓ Salvar Alterações
          </button>
        </div>
        <div className="flex gap-2 mt-2">
          <button
            className="flex-1 px-3 py-1 text-xs bg-amber-100 text-amber-700 rounded hover:bg-amber-200 border border-amber-300"
            onClick={() => {
              // Expand selection for easier span adjustment
              const textContainer = document.querySelector('.selectable-text');
              if (textContainer) {
                const range = document.createRange();
                const selection = window.getSelection();
                
                // Try to select the text around the current position
                const textNodes = [];
                const walker = document.createTreeWalker(
                  textContainer,
                  NodeFilter.SHOW_TEXT,
                  null,
                  false
                );
                
                let node;
                while (node = walker.nextNode()) {
                  textNodes.push(node);
                }
                
                // Find the text that corresponds to our character positions
                let charCount = 0;
                let startNode = null, endNode = null;
                let startOffset = 0, endOffset = 0;
                
                for (const textNode of textNodes) {
                  const nodeLength = textNode.textContent.length;
                  
                  if (charCount <= inlineEditPosition.charStart && charCount + nodeLength > inlineEditPosition.charStart) {
                    startNode = textNode;
                    startOffset = inlineEditPosition.charStart - charCount;
                  }
                  
                  if (charCount <= inlineEditPosition.charEnd && charCount + nodeLength >= inlineEditPosition.charEnd) {
                    endNode = textNode;
                    endOffset = inlineEditPosition.charEnd - charCount;
                    break;
                  }
                  
                  charCount += nodeLength;
                }
                
                if (startNode && endNode) {
                  try {
                    range.setStart(startNode, startOffset);
                    range.setEnd(endNode, endOffset);
                    selection.removeAllRanges();
                    selection.addRange(range);
                    
                    // Close this editor and enable text selection mode
                    setInlineEditingStrategy(null);
                    setInlineEditPosition(null);
                    
                    // Show user instruction
                    alert('Texto selecionado. Ajuste a seleção conforme necessário e use o menu de contexto para aplicar a nova posição.');
                  } catch (e) {
                    console.warn('Failed to select text:', e);
                    alert('Não foi possível selecionar o texto automaticamente. Selecione manualmente o texto desejado.');
                  }
                }
              }
            }}
          >
            📐 Ajustar Posição
          </button>
          <button
            className="flex-1 px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 border border-red-300"
            onClick={async () => {
              if (confirm('Deseja remover esta anotação de estratégia?')) {
                try {
                  await rejectAnnotation(inlineEditingStrategy.strategy_id);
                  setInlineEditingStrategy(null);
                  setInlineEditPosition(null);
                  if (onStrategyUpdate) onStrategyUpdate('remove', inlineEditingStrategy);
                } catch (error) {
                  console.error('Failed to remove strategy:', error);
                }
              }
            }}
          >
            🗑️ Remover
          </button>
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
      {!analysisResult ? (
        <div className={`text-center py-8 text-gray-500 ${className}`}>
          <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p>Nenhuma análise comparativa disponível</p>
        </div>
      ) : (
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
                <div className="border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto bg-gray-50">
                  <div className="text-sm font-sans leading-relaxed text-gray-700">
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
                <div className="border border-green-200 rounded-lg p-4 max-h-96 overflow-y-auto bg-green-50">
                  {/* Phase 2a superscript marker layer (additive, non-breaking) */}
      {filteredRawStrategies.length > 0 ? (
                    <div
                      className="superscript-layer-wrapper selectable-text"
                      aria-label="Marcadores de estratégias detectadas"
                      onMouseUp={handleTextSelection} // Preserve manual selection handler
                      onContextMenu={handleContextMenu}
                      style={{ cursor: 'text', userSelect: 'text' }}
                    >
                      <StrategySuperscriptRenderer
                        targetText={analysisResult.target_text || analysisResult.targetText}
                        strategies={filteredRawStrategies}
                        activeStrategyId={activeStrategyId}
        rovingIndex={rovingIndex}
        onRovingIndexChange={setRovingIndex}
                        onMarkerActivate={(id, el, idx) => {
                          if (id) {
                            // Find the strategy for inline editing instead of side panel
                            const strategy = filteredRawStrategies.find(s => s.strategy_id === id);
                            if (strategy && el) {
                              const rect = el.getBoundingClientRect();
                              setInlineEditingStrategy(strategy);
                              setInlineEditPosition({ 
                                x: rect.left + window.scrollX, 
                                y: rect.bottom + window.scrollY,
                                charStart: strategy.targetPosition?.start || 0,
                                charEnd: strategy.targetPosition?.end || 0
                              });
                              // Prevent side panel from opening
                              setActiveStrategyId(null);
                            }
                          }
                        }}
                        unifiedMap={unifiedStrategyMap}
                      />
                    </div>
                  ) : (
                    /* Fallback for when no strategies are detected - plain text with selection handlers */
                    <div
                      className="selectable-text"
                      onMouseUp={handleTextSelection}
                      onContextMenu={handleContextMenu}
                      style={{ cursor: 'text', userSelect: 'text', whiteSpace: 'pre-wrap' }}
                    >
                      {analysisResult.target_text || analysisResult.targetText}
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

            {/* Read-Only Strategy Overview Panel */}
            {strategiesDetected.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Estratégias de Simplificação Detectadas
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded ml-auto">
                    Somente leitura - edite diretamente no texto
                  </span>
                </h5>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {strategiesDetected.map(strategy => (
                    <div
                      key={strategy.id}
                      className="flex items-center gap-3 p-3 rounded-lg border bg-gray-50"
                      style={{ borderLeftColor: strategy.color, borderLeftWidth: '3px' }}
                    >
                      <div
                        className="w-8 h-8 rounded flex items-center justify-center text-xs font-bold relative overflow-hidden"
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
                          {strategy.manually_assigned && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Manual</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          {Math.round(strategy.confidence * 100)}% confiança
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Posição: {strategy.spans?.[0]?.start || 0}-{strategy.spans?.[0]?.end || 0}
                        </div>
                      </div>
                      {/* No editing controls - users must edit inline in the target text */}
                      <div className="text-xs text-gray-400 italic">
                        Clique no texto destacado para editar
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
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-600" />
                Estratégias de Simplificação Identificadas
              </h4>
              <p className="text-sm text-gray-600 mt-2">
                Esta análise identificou {strategiesDetected?.length || 0} estratégias de simplificação intralingual. 
                Cada estratégia representa uma técnica específica para tornar o texto mais acessível.
              </p>
            </div>
            
            <div className="space-y-4">
              {strategiesDetected?.map((strategy, index) => {
                // Use backend-provided code if available
                const strategyCode = strategy.code || getStrategyCode(strategy.name);
                const strategyColor = strategy.color || getStrategyColor(strategyCode, false);
                const strategyInfo = getStrategyInfo(strategyCode);
                
                return (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg overflow-hidden" data-testid="strategy-result">
                    {/* Strategy Header */}
                    <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm"
                          style={{
                            backgroundColor: strategyColor,
                            color: getContrastingTextColor(strategyColor)
                          }}
                        >
                          {strategyCode}
                        </div>
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-900">{strategyInfo.name}</h5>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              strategyInfo.type === 'lexical' ? 'bg-blue-100 text-blue-800' :
                              strategyInfo.type === 'syntactic' ? 'bg-green-100 text-green-800' :
                              strategyInfo.type === 'semantic' ? 'bg-purple-100 text-purple-800' :
                              strategyInfo.type === 'structural' ? 'bg-orange-100 text-orange-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {strategyInfo.type === 'lexical' ? 'Léxica' :
                               strategyInfo.type === 'syntactic' ? 'Sintática' :
                               strategyInfo.type === 'semantic' ? 'Semântica' :
                               strategyInfo.type === 'structural' ? 'Estrutural' :
                               'Conteúdo'}
                            </span>
                            {strategy.manually_assigned && (
                              <span className="px-2 py-1 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                                Manual
                              </span>
                            )}
                            {strategyInfo.autoDetect === false && (
                              <span className="px-2 py-1 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                Detecção Manual
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-bold text-gray-900">
                            {Math.round((strategy.confidence || 0) * 100)}%
                          </div>
                          <div className="text-xs text-gray-500">confiança</div>
                        </div>
                      </div>
                    </div>

                    {/* Strategy Content */}
                    <div className="p-4">
                      <div className="space-y-4">
                        {/* Description */}
                        <div>
                          <h6 className="text-sm font-medium text-gray-700 mb-2">📝 Descrição</h6>
                          <p className="text-sm text-gray-600">{strategyInfo.description}</p>
                        </div>

                        {/* Methodology Information */}
                        <div className="bg-gray-50 rounded-lg p-3">
                          <h6 className="text-sm font-medium text-gray-700 mb-2">🔬 Metodologia</h6>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                            <div>
                              <span className="font-medium text-gray-600">Categoria:</span>
                              <span className="ml-1 text-gray-800">
                                {strategyInfo.type === 'lexical' ? 'Alteração de vocabulário' :
                                 strategyInfo.type === 'syntactic' ? 'Modificação sintática' :
                                 strategyInfo.type === 'semantic' ? 'Mudança semântica' :
                                 strategyInfo.type === 'structural' ? 'Reorganização estrutural' :
                                 'Modificação de conteúdo'}
                              </span>
                            </div>
                            <div>
                              <span className="font-medium text-gray-600">Detecção:</span>
                              <span className="ml-1 text-gray-800">
                                {strategyInfo.autoDetect ? 'Automática' : 'Manual obrigatória'}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Position Information */}
                        {strategy.spans && strategy.spans.length > 0 && (
                          <div>
                            <h6 className="text-sm font-medium text-gray-700 mb-2">📍 Posições Detectadas</h6>
                            <div className="space-y-1">
                              {strategy.spans.map((span, spanIndex) => (
                                <div key={spanIndex} className="text-xs bg-blue-50 border border-blue-200 rounded px-2 py-1">
                                  <span className="font-medium">Caracteres {span.start}-{span.end}</span>
                                  {span.text && (
                                    <span className="ml-2 text-gray-600">"{span.text.substring(0, 50)}{span.text.length > 50 ? '...' : ''}"</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Examples if available */}
                        {strategy.examples && strategy.examples.length > 0 && (
                          <div>
                            <h6 className="text-sm font-medium text-gray-700 mb-2">💡 Exemplos</h6>
                            <div className="space-y-2">
                              {strategy.examples.map((example, exIndex) => (
                                <div key={exIndex} className="bg-gradient-to-r from-red-50 to-green-50 border rounded p-3">
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                    <div>
                                      <div className="text-xs font-medium text-red-700 mb-1">Texto Original</div>
                                      <div className="text-sm text-red-800 bg-red-100 rounded px-2 py-1">
                                        "{example.original || example.before}"
                                      </div>
                                    </div>
                                    <div>
                                      <div className="text-xs font-medium text-green-700 mb-1">Texto Simplificado</div>
                                      <div className="text-sm text-green-800 bg-green-100 rounded px-2 py-1">
                                        "{example.simplified || example.after}"
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Special handling notes */}
                        {strategyInfo.specialHandling && (
                          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                            <h6 className="text-sm font-medium text-amber-800 mb-1">⚠️ Considerações Especiais</h6>
                            <p className="text-xs text-amber-700">
                              {strategyInfo.specialHandling === 'manual-only' && 
                                'Esta estratégia nunca é detectada automaticamente e deve ser aplicada manualmente pelo anotador.'
                              }
                              {strategyInfo.specialHandling === 'manual-activation' && 
                                'Esta estratégia está desabilitada por padrão e requer ativação manual nas configurações.'
                              }
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Methodology Summary */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Info className="w-4 h-4 text-slate-600" />
                Sobre a Metodologia NET-EST
              </h5>
              <div className="text-sm text-gray-600 space-y-2">
                <p>
                  O NET-EST (Núcleo de Estudos em Tradução - Estratégias de Simplificação) analisa 
                  traduções intralinguais com foco em técnicas de simplificação textual.
                </p>
                <p>
                  As 14 estratégias identificadas são baseadas em pesquisa acadêmica e permitem 
                  uma análise sistemática de como textos complexos são transformados para maior acessibilidade.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-2 mt-3 text-xs">
                  <div className="bg-blue-100 text-blue-800 rounded px-2 py-1">
                    <strong>Léxicas:</strong> Vocabulário
                  </div>
                  <div className="bg-green-100 text-green-800 rounded px-2 py-1">
                    <strong>Sintáticas:</strong> Estrutura
                  </div>
                  <div className="bg-purple-100 text-purple-800 rounded px-2 py-1">
                    <strong>Semânticas:</strong> Sentido
                  </div>
                  <div className="bg-orange-100 text-orange-800 rounded px-2 py-1">
                    <strong>Estruturais:</strong> Organização
                  </div>
                </div>
              </div>
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
      
  {/* Text selection -> annotation create menu */}
  {renderContextMenu()}
      
      {/* Tooltip for strategy hover */}
      {renderTooltip()}
      
      {/* Inline strategy editor (panel-free approach) */}
      {renderInlineEditor()}
    </div>
    {/* Phase 2b: strategy detail side panel - hidden when using inline editing */}
    {!inlineEditingStrategy && (
      <StrategyDetailPanel
        targetText={analysisResult.target_text || analysisResult.targetText}
        sourceText={analysisResult.source_text || analysisResult.sourceText}
        rawStrategies={filteredRawStrategies}
        activeStrategyId={activeStrategyId}
        onClose={() => setActiveStrategyId(null)}
        returnFocusTo={lastFocusedMarkerRef.current}
      />
    )}
    {/* Strategy Filter Bar (Phase 2c) */}
    <div style={{ marginTop: '1rem' }}>
      <StrategyFilterBar
        strategies={strategiesDetected || []}
        activeCodes={activeCodes}
        onCodesChange={(codes) => { setActiveCodes(codes); setRovingIndex(0); }}
        confidenceMin={confidenceMin}
        onConfidenceChange={(val) => { setConfidenceMin(val); setRovingIndex(0); }}
      />
    </div>
        </>
      )}
      
      {/* Inline Editor for Direct Tag Editing */}
      {renderInlineEditor()}
      
      {/* Tooltip for Strategy Info */}
      {renderTooltip()}
    </>
  );
};

// Utility function to get contrasting text color
function getContrastingTextColor(backgroundColor) {
  return getAccessibleTextColor(backgroundColor);
}

export default ComparativeResultsDisplay;
