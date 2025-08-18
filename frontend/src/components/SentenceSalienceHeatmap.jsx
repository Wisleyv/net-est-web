import React from 'react';
import PropTypes from 'prop-types';
import { Tooltip } from 'react-tooltip';

/**
 * SentenceSalienceHeatmap.jsx
 *
 * Simple, accessible sentence-level salience heatmap component.
 *
 * Props:
 * - sentences: Array<string> | Array<{text: string, salience?: number}>
 * - salienceScores: optional Array<number> (overrides sentence.salience)
 * - colorScheme: 'orange' | 'red' | 'purple' (default 'orange')
 */

function clamp(v, min = 0, max = 1) {
    return Math.max(min, Math.min(max, v));
}

function hexToRgb(hex) {
    const h = hex.replace('#', '');
    const full = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
    const bigint = parseInt(full, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return { r, g, b };
}

/**
 * Map a normalized score [0..1] to an rgb() color string according to a small palette.
 * Exported so unit tests can validate deterministic mapping logic.
 */
export function mapSalienceToColor(score, colorScheme = 'orange') {
    const schemes = {
        orange: { low: '#f2f2f2', high: '#ff7b00' },
        red: { low: '#f8eaea', high: '#d62828' },
        purple: { low: '#f5f0ff', high: '#6a4c93' },
    };
    const s = clamp(score, 0, 1);
    const { low, high } = schemes[colorScheme] || schemes.orange;
    const lowRgb = hexToRgb(low);
    const highRgb = hexToRgb(high);
    const r = Math.round(lowRgb.r + (highRgb.r - lowRgb.r) * s);
    const g = Math.round(lowRgb.g + (highRgb.g - lowRgb.g) * s);
    const b = Math.round(lowRgb.b + (highRgb.b - lowRgb.b) * s);
    return `rgb(${r}, ${g}, ${b})`;
}

export default function SentenceSalienceHeatmap({
    sentences = [],
    salienceScores = null,
    microSpans = null,
    colorScheme = 'orange',
    maxHeight = 'auto',
    ariaLabel = 'Sentence salience heatmap',
    showMicroSpans = true,
}) {
    // Build texts array and source scores
    const texts = sentences.map((s) => (typeof s === 'string' ? s : s.text || ''));
    const scoresSource = salienceScores
        ? salienceScores
        : sentences.map((s) => (typeof s === 'string' ? 0 : Number(s.salience || 0)));

    // Normalize scores relative to the maximum observed (preserve relative scale)
    const maxScore = Math.max(...scoresSource, 1e-6);
    const normalized = scoresSource.map((v) => clamp(v / maxScore, 0, 1));

    // Get micro-spans for each sentence
    const sentenceMicroSpans = microSpans || [];
    
    return (
        <section
            className="sentence-salience-heatmap"
            aria-label={ariaLabel}
            role="group"
            style={{ maxHeight }}
        >
            <ol style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {texts.map((text, i) => {
                    const score = normalized[i] ?? 0;
                    const bg = mapSalienceToColor(score, colorScheme);
                    const barWidth = `${Math.round(score * 100)}%`;
                    const microSpansForSentence = sentenceMicroSpans[i] || [];
                    const hasMicroSpans = showMicroSpans && microSpansForSentence.length > 0;
                    const tooltipId = `sentence-tooltip-${i}`;
                    
                    return (
                        <li
                            key={`s-${i}`}
                            style={{
                                display: 'flex',
                                gap: '12px',
                                alignItems: 'flex-start',
                                padding: '6px 8px',
                                borderRadius: 6,
                            }}
                        >
                            <div
                                aria-hidden
                                style={{
                                    width: 8,
                                    height: '100%',
                                    borderRadius: 4,
                                    background: bg,
                                    flexShrink: 0,
                                }}
                            />
                            <div style={{ flex: 1 }}>
                                <p
                                    data-tooltip-id={hasMicroSpans ? tooltipId : undefined}
                                    style={{
                                        margin: 0,
                                        lineHeight: 1.4,
                                        color: '#0f172a',
                                        background: 'transparent',
                                        cursor: hasMicroSpans ? 'help' : 'default',
                                    }}
                                >
                                    {text}
                                </p>
                                <div
                                    role="progressbar"
                                    aria-valuemin={0}
                                    aria-valuemax={1}
                                    aria-valuenow={Number(score.toFixed(3))}
                                    aria-label={`Salience: ${Math.round(score * 100)}%`}
                                    style={{
                                        height: 6,
                                        marginTop: 6,
                                        borderRadius: 3,
                                        background: '#e6e7e9',
                                        overflow: 'hidden',
                                    }}
                                >
                                    <div
                                        style={{
                                            width: barWidth,
                                            height: '100%',
                                            background: bg,
                                            transition: 'width 200ms ease, background 200ms ease',
                                        }}
                                    />
                                </div>
                                
                                {hasMicroSpans && (
                                    <Tooltip
                                        id={tooltipId}
                                        place="top"
                                        style={{
                                            backgroundColor: '#1f2937',
                                            color: '#f9fafb',
                                            borderRadius: '6px',
                                            padding: '8px 12px',
                                            fontSize: '14px',
                                            maxWidth: '300px',
                                            zIndex: 1000,
                                        }}
                                    >
                                        <div>
                                            <strong>Micro-spans ({microSpansForSentence.length})</strong>
                                            <ul style={{ margin: '4px 0 0 0', padding: '0 0 0 16px' }}>
                                                {microSpansForSentence.map((span, spanIndex) => (
                                                    <li key={spanIndex} style={{ marginBottom: '2px' }}>
                                                        <strong>"{span.text}"</strong>
                                                        <span style={{ color: '#9ca3af', marginLeft: '6px' }}>
                                                            (weight: {(span.weight || span.salience || 0).toFixed(2)})
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </Tooltip>
                                )}
                            </div>
                        </li>
                    );
                })}
            </ol>
        </section>
    );
}

SentenceSalienceHeatmap.propTypes = {
    sentences: PropTypes.array,
    salienceScores: PropTypes.arrayOf(PropTypes.number),
    microSpans: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.shape({
        text: PropTypes.string.isRequired,
        weight: PropTypes.number,
        salience: PropTypes.number,
        start: PropTypes.number,
        end: PropTypes.number,
        method: PropTypes.string,
    }))),
    colorScheme: PropTypes.oneOf(['orange', 'red', 'purple']),
    maxHeight: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    ariaLabel: PropTypes.string,
    showMicroSpans: PropTypes.bool,
};