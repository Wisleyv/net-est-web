 // Simple unit test for micro-spans tooltip logic

// Extract tooltip logic helpers for testing
export function formatMicroSpansTooltip(microSpans) {
    if (!Array.isArray(microSpans) || microSpans.length === 0) {
        return null;
    }
    
    return {
        count: microSpans.length,
        spans: microSpans.map(span => ({
            text: span.text,
            weight: (span.weight || span.salience || 0).toFixed(2)
        }))
    };
}

export function shouldShowTooltip(microSpans, showMicroSpans) {
    return showMicroSpans && 
           Array.isArray(microSpans) && 
           microSpans.length > 0;
}

describe('MicroSpans Tooltip Logic', () => {
    it('formats micro-spans data for tooltip display', () => {
        const microSpans = [
            { text: 'high salience', weight: 0.85, start: 20, end: 32 },
            { text: 'test phrase', weight: 0.6, start: 0, end: 11 }
        ];
        
        const result = formatMicroSpansTooltip(microSpans);
        
        expect(result).toEqual({
            count: 2,
            spans: [
                { text: 'high salience', weight: '0.85' },
                { text: 'test phrase', weight: '0.60' }
            ]
        });
    });

    it('returns null for empty or invalid micro-spans', () => {
        expect(formatMicroSpansTooltip([])).toBe(null);
        expect(formatMicroSpansTooltip(null)).toBe(null);
        expect(formatMicroSpansTooltip(undefined)).toBe(null);
    });

    it('determines when to show tooltip correctly', () => {
        const validSpans = [{ text: 'test', weight: 0.5 }];
        
        expect(shouldShowTooltip(validSpans, true)).toBe(true);
        expect(shouldShowTooltip(validSpans, false)).toBe(false);
        expect(shouldShowTooltip([], true)).toBe(false);
        expect(shouldShowTooltip(null, true)).toBe(false);
    });

    it('handles salience fallback for weight property', () => {
        const microSpans = [
            { text: 'with weight', weight: 0.8 },
            { text: 'with salience', salience: 0.7 },
            { text: 'no weight', start: 0, end: 9 }
        ];
        
        const result = formatMicroSpansTooltip(microSpans);
        
        expect(result.spans).toEqual([
            { text: 'with weight', weight: '0.80' },
            { text: 'with salience', weight: '0.70' },
            { text: 'no weight', weight: '0.00' }
        ]);
    });
});