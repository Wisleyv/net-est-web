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

// Segment text for highlights based on sentence-level positions (non-overlapping assumption)
// strategies: filtered strategies having sourcePosition/targetPosition with type === 'sentence'
export function segmentTextForHighlights(text, strategies, { scope = 'target', sentenceSplitter = defaultSentenceSplit } = {}) {
  if (!text) return [];
  const sentences = sentenceSplitter(text);
  const segments = [];
  sentences.forEach((sentence, idx) => {
    // collect strategies matching this sentence index
    const matching = strategies.filter(s => {
      const pos = scope === 'target' ? s.targetPosition : s.sourcePosition;
      return pos && pos.type === 'sentence' && pos.sentence === idx;
    });
    if (matching.length === 0) return;
    // choose highest confidence strategy for this sentence (placeholder rule)
    const chosen = matching.slice().sort((a,b) => (b.confidence ?? 0) - (a.confidence ?? 0) || (a.code || '').localeCompare(b.code || '') )[0];
    segments.push({
      sentenceIndex: idx,
      text: sentence,
      code: chosen.code,
      strategy_id: chosen.strategy_id || chosen.id
    });
  });
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
