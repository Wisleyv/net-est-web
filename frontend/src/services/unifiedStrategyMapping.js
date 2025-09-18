// Unified Strategy Mapping Utility (Phase 2d Step 1)
// Feature-flag driven additive layer for consistent colors across source/target/superscripts.
// Provides deterministic mapping and accessible contrast.

import { getStrategyColor } from './strategyColorMapping.js';

// Simple luminance-based contrast fallback
function getContrastText(hex) {
  if (!hex) return '#000';
  const c = hex.replace('#','');
  if (c.length !== 6) return '#000';
  const r = parseInt(c.slice(0,2),16);
  const g = parseInt(c.slice(2,4),16);
  const b = parseInt(c.slice(4,6),16);
  const luminance = (0.299*r + 0.587*g + 0.114*b)/255;
  return luminance > 0.58 ? '#000' : '#FFF';
}

// Deterministic ordering helper (stabilize map for tests)
function sortStrategies(sts) {
  return [...sts].sort((a,b) => (a.code || '').localeCompare(b.code || ''));
}

const PATTERN_TYPES = [
  'diagonal-light', 'dots', 'crosshatch', 'horizontal', 'vertical', 'diagonal-bold', 'grid', 'zigzag', 'triangles', 'waves', 'checker', 'hex', 'circles', 'slashes'
];

function patternForIndex(i) { return PATTERN_TYPES[i % PATTERN_TYPES.length]; }

function buildPatternCSS(entry) {
  // Only pattern overlay for spans (not markers) to preserve legibility
  const base = entry.baseColor;
  switch (entry.pattern) {
    case 'diagonal-light':
      return `repeating-linear-gradient(45deg, ${base}33 0 6px, ${base}00 6px 12px)`;
    case 'dots':
      return `radial-gradient(${base}55 15%, transparent 16%) 0 0 / 10px 10px`;
    case 'crosshatch':
      return `repeating-linear-gradient(0deg, ${base}30 0 6px, ${base}00 6px 12px), repeating-linear-gradient(90deg, ${base}30 0 6px, ${base}00 6px 12px)`;
    case 'horizontal':
      return `repeating-linear-gradient(0deg, ${base}40 0 4px, ${base}00 4px 8px)`;
    case 'vertical':
      return `repeating-linear-gradient(90deg, ${base}40 0 4px, ${base}00 4px 8px)`;
    case 'diagonal-bold':
      return `repeating-linear-gradient(45deg, ${base}50 0 8px, ${base}00 8px 16px)`;
    case 'grid':
      return `linear-gradient(${base}30 1px, transparent 1px), linear-gradient(90deg, ${base}30 1px, transparent 1px)`;
    case 'zigzag':
      return `repeating-linear-gradient(135deg, ${base}30 0 5px, ${base}00 5px 10px)`;
    case 'triangles':
      return `repeating-conic-gradient(${base}40 0 25%, ${base}00 0 50%) 50% / 12px 12px`;
    case 'waves':
      return `repeating-radial-gradient(circle at 0 0, ${base}35 0 4px, ${base}00 4px 8px)`;
    case 'checker':
      return `repeating-conic-gradient(${base}40 0 25%, ${base}00 0 50%) 0 / 10px 10px`;
    case 'hex':
      return `repeating-linear-gradient(30deg, ${base}30 0 10px, ${base}00 10px 20px)`;
    case 'circles':
      return `radial-gradient(${base}40 30%, transparent 31%) 0 0 / 14px 14px`;
    case 'slashes':
      return `repeating-linear-gradient(60deg, ${base}40 0 5px, ${base}00 5px 10px)`;
    default:
      return '';
  }
}

export function buildUnifiedStrategyMap(strategies = [], { colorblindMode = false, enablePatterns = false } = {}) {
  const byCode = new Map();
  sortStrategies(strategies).forEach((s, i) => {
    if (!s || !s.code) return;
    if (byCode.has(s.code)) return; // first occurrence wins for stable color
    const baseColor = getStrategyColor(s.code, colorblindMode);
    byCode.set(s.code, {
      code: s.code,
      baseColor,
      markerColor: baseColor, // future: differentiate if needed
      bgSource: baseColor + '1A', // ~10% alpha (1A hex)
      bgTarget: baseColor + '26', // ~15% alpha (26 hex)
      borderColor: baseColor,
      textColor: getContrastText(baseColor),
      pattern: enablePatterns && colorblindMode ? patternForIndex(i) : null
    });
  });
  return Object.fromEntries(byCode.entries());
}

// Segment text for highlights based on precise character-level offsets
// strategies: filtered strategies having target_offsets/source_offsets with char_start/char_end
export function segmentTextForHighlights(text, strategies, { scope = 'target' } = {}) {
  if (!text) return [];
  
  // Extract character-level offsets for the specified scope
  const segments = [];
  strategies.forEach(strategy => {
    const offsets = scope === 'target' ? strategy.target_offsets : strategy.source_offsets;
    
    // Check for both new format (target_offsets) and legacy format (targetPosition)
    let charStart, charEnd;
    
    if (offsets && typeof offsets === 'object' && 'char_start' in offsets) {
      // New precise format (JavaScript object)
      charStart = offsets.char_start;
      charEnd = offsets.char_end;
    } else if (typeof offsets === 'string' && offsets.includes('char_start')) {
      // Handle PowerShell object string format: "@{paragraph=0; sentence=0; char_start=0; char_end=123}"
      const charStartMatch = offsets.match(/char_start=(\d+)/);
      const charEndMatch = offsets.match(/char_end=(\d+)/);
      if (charStartMatch && charEndMatch) {
        charStart = parseInt(charStartMatch[1], 10);
        charEnd = parseInt(charEndMatch[1], 10);
      }
    } else {
      // Legacy sentence-based fallback - convert to approximate character positions
      const pos = scope === 'target' ? strategy.targetPosition : strategy.sourcePosition;
      if (pos) {
        let sentenceIndex = 0;
        let posType = 'sentence';
        
        if (typeof pos === 'object' && pos.sentence !== undefined) {
          // JavaScript object format
          sentenceIndex = pos.sentence || 0;
          posType = pos.type || 'sentence';
        } else if (typeof pos === 'string' && pos.includes('sentence=')) {
          // Handle PowerShell object string format: "@{sentence=0; type=sentence}"
          const sentenceMatch = pos.match(/sentence=(\d+)/);
          if (sentenceMatch) {
            sentenceIndex = parseInt(sentenceMatch[1], 10);
          }
        }
        
        if (posType === 'sentence') {
          const sentences = defaultSentenceSplit(text);
          if (sentenceIndex < sentences.length) {
            // Calculate approximate character position for the sentence
            let charPos = 0;
            for (let i = 0; i < sentenceIndex; i++) {
              charPos += sentences[i].length + 1; // +1 for space/separator
            }
            charStart = charPos;
            charEnd = charPos + sentences[sentenceIndex].length;
          }
        }
      }
    }
    
    // Only add segment if we have valid character positions
    if (charStart !== undefined && charEnd !== undefined && 
        charStart >= 0 && charEnd > charStart && charEnd <= text.length) {
      segments.push({
        charStart,
        charEnd,
        text: text.substring(charStart, charEnd),
        code: strategy.code,
        strategy_id: strategy.strategy_id || strategy.id,
        confidence: strategy.confidence || 0
      });
    }
  });
  
  // Sort segments by start position for proper rendering
  segments.sort((a, b) => a.charStart - b.charStart);
  return segments;
}

export function defaultSentenceSplit(text) {
  return text
    .split(/[.!?]+/)
    .filter(s => s.trim())
    .map(s => s.trim() + '.');
}

export function generateUnifiedCSS(unifiedMap) {
  const lines = [':root { /* unified strategy mapping generated */ }'];
  Object.values(unifiedMap).forEach(entry => {
  const patternBGTarget = entry.pattern ? buildPatternCSS(entry) : null;
  const patternBGSource = entry.pattern ? buildPatternCSS(entry) : null;
  const targetBgRule = patternBGTarget ? `background: ${entry.bgTarget}, ${patternBGTarget}; background-blend-mode: normal,multiply;` : `background: ${entry.bgTarget};`;
  const sourceBgRule = patternBGSource ? `background: ${entry.bgSource}, ${patternBGSource}; background-blend-mode: normal,multiply;` : `background: ${entry.bgSource};`;
  lines.push(`.unified-highlight[data-code="${entry.code}"] { ${targetBgRule} border: 1px solid ${entry.borderColor}; }`);
  lines.push(`.unified-highlight.source[data-code="${entry.code}"] { ${sourceBgRule} }`);
    lines.push(`.unified-marker[data-code="${entry.code}"] { background: ${entry.markerColor}; color: ${entry.textColor}; border-color: ${entry.borderColor}; }`);
  });
  return lines.join('\n');
}

export function injectUnifiedCSS(unifiedMap) {
  const styleId = 'unified-strategy-styles';
  let el = document.getElementById(styleId);
  if (!el) { el = document.createElement('style'); el.id = styleId; document.head.appendChild(el); }
  el.textContent = generateUnifiedCSS(unifiedMap);
}
