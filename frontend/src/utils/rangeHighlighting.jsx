import React from 'react';

// Enhanced utility for creating both range highlighting and marker positioning
// This fixes the core issue where only markers were shown at start positions
// instead of highlighting the full text ranges

/**
 * Builds both text range spans for highlighting and insertion points for markers
 * @param {Array} strategies - Normalized strategy objects with target_offsets
 * @param {number} textLength - Length of target text
 * @returns {Object} - { ranges: [...], insertionPoints: [...] }
 */
export function buildRangeHighlighting(strategies, textLength) {
  const ranges = [];
  const insertionPoints = [];
  
  strategies.forEach(s => {
    if (!Array.isArray(s.target_offsets) || s.target_offsets.length === 0) {
      if (typeof window !== 'undefined' && import.meta.env && import.meta.env.DEV) {
        console.debug('RANGE_HIGHLIGHT: strategy has no offsets', { id: s.strategy_id, code: s.code });
      }
      return;
    }
    
    s.target_offsets.forEach(range => {
      const start = Math.max(0, Math.min(textLength, range.start || 0));
      const end = Math.max(0, Math.min(textLength, range.end || range.start || 0));
      
      if (start < end) {
        // Add range for text highlighting
        ranges.push({
          start,
          end,
          strategy_id: s.strategy_id,
          code: s.code,
          status: s.status,
          confidence: s.confidence
        });
        
        // Add insertion point for marker at start of range
        insertionPoints.push({ pos: start, id: s.strategy_id });
      }
    });
  });
  
  // Sort ranges by start position
  ranges.sort((a, b) => a.start - b.start);
  insertionPoints.sort((a, b) => a.pos - b.pos);
  
  if (typeof window !== 'undefined' && import.meta.env && import.meta.env.DEV) {
    console.debug('RANGE_HIGHLIGHT: built', { 
      ranges: ranges.length, 
      insertionPoints: insertionPoints.length 
    });
    console.debug('RANGE_HIGHLIGHT: ranges sample=', ranges.slice(0, 3));
  }
  
  return { ranges, insertionPoints };
}

/**
 * Converts text with ranges into DOM nodes with highlighting and markers
 * @param {string} text - Target text to process
 * @param {Array} ranges - Range objects for highlighting
 * @param {Array} insertionPoints - Points for marker insertion
 * @param {Object} options - Rendering options (colorMapping, etc.)
 * @returns {Array} - Array of React nodes
 */
export function buildHighlightedNodes(text, ranges, insertionPoints, options = {}) {
  const { colorMapping = {}, markerRenderer } = options;
  const nodes = [];
  let currentPos = 0;
  
  // Create segments based on range boundaries
  const boundaries = new Set();
  ranges.forEach(range => {
    boundaries.add(range.start);
    boundaries.add(range.end);
  });
  
  const sortedBoundaries = Array.from(boundaries).sort((a, b) => a - b);
  
  // Process each segment
  for (let i = 0; i < sortedBoundaries.length; i++) {
    const segmentStart = i === 0 ? 0 : sortedBoundaries[i - 1];
    const segmentEnd = sortedBoundaries[i];
    
    if (segmentStart < segmentEnd && segmentStart < text.length) {
      // Find ranges that cover this segment
      const activeRanges = ranges.filter(range => 
        range.start <= segmentStart && range.end >= segmentEnd
      );
      
      const segmentText = text.slice(segmentStart, segmentEnd);
      
      if (activeRanges.length > 0) {
        // Create highlighted span
        const primaryRange = activeRanges[0]; // Use first range for styling
        const bgColor = colorMapping[primaryRange.code] || '#f3f4f6';
        
        nodes.push(
          <span
            key={`highlight-${segmentStart}-${segmentEnd}`}
            style={{ backgroundColor: bgColor, padding: '2px 0' }}
            data-strategy-codes={activeRanges.map(r => r.code).join(',')}
          >
            {segmentText}
          </span>
        );
      } else {
        // Plain text
        nodes.push(segmentText);
      }
    }
    
    // Add markers at this boundary
    const markersAtPos = insertionPoints.filter(p => p.pos === sortedBoundaries[i]);
    markersAtPos.forEach(marker => {
      if (markerRenderer) {
        nodes.push(markerRenderer(marker));
      }
    });
  }
  
  // Add any remaining text
  const lastBoundary = sortedBoundaries[sortedBoundaries.length - 1] || 0;
  if (lastBoundary < text.length) {
    nodes.push(text.slice(lastBoundary));
  }
  
  return nodes;
}