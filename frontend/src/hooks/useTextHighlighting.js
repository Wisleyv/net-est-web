/**
 * Text Highlighting Hook
 * Provides utilities for text segmentation and highlighting based on strategy analysis
 */

import { useState, useCallback } from 'react';
import { getStrategyColor } from '../services/strategyColorMapping';

export const useTextHighlighting = () => {
  const [selectedSegments, setSelectedSegments] = useState([]);
  const [highlightMode, setHighlightMode] = useState('all'); // 'all', 'selected', 'none'

  /**
   * Segment text based on strategy positions
   * @param {string} text - The text to segment
   * @param {Array} strategies - Array of strategy objects with positions
   * @returns {Array} Array of text segments with metadata
   */
  const segmentText = useCallback((text, strategies = []) => {
    if (!text || !strategies.length) {
      return [{ text, type: 'text', id: 'text-0' }];
    }

    const segments = [];
    const sortedStrategies = [...strategies].sort((a, b) => a.start_pos - b.start_pos);
    let currentIndex = 0;
    let segmentId = 0;

    sortedStrategies.forEach((strategy, strategyIndex) => {
      // Add text before strategy (if any)
      if (strategy.start_pos > currentIndex) {
        segments.push({
          id: `text-${segmentId++}`,
          text: text.slice(currentIndex, strategy.start_pos),
          type: 'text'
        });
      }

      // Add strategy segment
      segments.push({
        id: `strategy-${strategyIndex}`,
        text: text.slice(strategy.start_pos, strategy.end_pos),
        type: 'strategy',
        strategy: strategy.strategy_type,
        confidence: strategy.confidence,
        position: {
          start: strategy.start_pos,
          end: strategy.end_pos
        },
        metadata: strategy
      });

      currentIndex = strategy.end_pos;
    });

    // Add remaining text
    if (currentIndex < text.length) {
      segments.push({
        id: `text-${segmentId++}`,
        text: text.slice(currentIndex),
        type: 'text'
      });
    }

    return segments;
  }, []);

  /**
   * Generate CSS styles for a strategy segment
   * @param {string} strategy - Strategy code
   * @param {Object} options - Styling options
   * @returns {Object} CSS style object
   */
  const getSegmentStyles = useCallback((strategy, options = {}) => {
    const {
      opacity = 0.25,
      isHovered = false,
      isSelected = false,
      showBorder = true
    } = options;

    const baseColor = getStrategyColor(strategy);
    
    return {
      backgroundColor: `${baseColor}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`,
      borderLeft: showBorder ? `3px solid ${baseColor}` : 'none',
      borderRadius: '2px',
      padding: '1px 2px',
      transition: 'all 0.2s ease-in-out',
      transform: isHovered ? 'scale(1.02)' : 'scale(1)',
      boxShadow: isSelected ? `0 0 0 2px ${baseColor}` : 'none',
      cursor: 'pointer'
    };
  }, []);

  /**
   * Handle segment selection
   * @param {string} segmentId - ID of the segment to select
   * @param {boolean} multiSelect - Whether to allow multiple selections
   */
  const selectSegment = useCallback((segmentId, multiSelect = false) => {
    setSelectedSegments(prev => {
      if (multiSelect) {
        return prev.includes(segmentId)
          ? prev.filter(id => id !== segmentId)
          : [...prev, segmentId];
      } else {
        return prev.includes(segmentId) ? [] : [segmentId];
      }
    });
  }, []);

  /**
   * Clear all selections
   */
  const clearSelection = useCallback(() => {
    setSelectedSegments([]);
  }, []);

  /**
   * Get statistics for highlighted text
   * @param {Array} segments - Array of text segments
   * @returns {Object} Statistics object
   */
  const getHighlightStats = useCallback((segments) => {
    const strategySegments = segments.filter(seg => seg.type === 'strategy');
    const strategyCounts = {};
    let totalConfidence = 0;

    strategySegments.forEach(segment => {
      const strategy = segment.strategy;
      strategyCounts[strategy] = (strategyCounts[strategy] || 0) + 1;
      totalConfidence += segment.confidence || 0;
    });

    return {
      totalStrategies: strategySegments.length,
      uniqueStrategies: Object.keys(strategyCounts).length,
      strategyCounts,
      averageConfidence: strategySegments.length > 0 
        ? totalConfidence / strategySegments.length 
        : 0,
      coveragePercentage: segments.length > 0
        ? (strategySegments.length / segments.length) * 100
        : 0
    };
  }, []);

  /**
   * Filter segments by strategy type
   * @param {Array} segments - Array of segments
   * @param {string|Array} strategyFilter - Strategy or array of strategies to show
   * @returns {Array} Filtered segments
   */
  const filterSegmentsByStrategy = useCallback((segments, strategyFilter) => {
    if (!strategyFilter) return segments;
    
    const strategiesToShow = Array.isArray(strategyFilter) ? strategyFilter : [strategyFilter];
    
    return segments.map(segment => {
      if (segment.type === 'strategy' && !strategiesToShow.includes(segment.strategy)) {
        return { ...segment, type: 'text' }; // Convert to plain text
      }
      return segment;
    });
  }, []);

  return {
    // Functions
    segmentText,
    getSegmentStyles,
    selectSegment,
    clearSelection,
    getHighlightStats,
    filterSegmentsByStrategy,
    
    // State
    selectedSegments,
    highlightMode,
    setHighlightMode,
    
    // State setters
    setSelectedSegments
  };
};

export default useTextHighlighting;

/*
Desenvolvido com ❤️ pelo Núcleo de Estudos de Tradução - PIPGLA/UFRJ | Contém código gerado por IA.
*/
