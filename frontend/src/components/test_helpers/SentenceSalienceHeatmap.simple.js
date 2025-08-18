/**
 * Simple integration test for SentenceSalienceHeatmap with micro-spans
 * Tests the tooltip integration without DOM rendering
 */

// Simple mock test that validates the micro-spans props structure
export function validateMicroSpansStructure(microSpans) {
    if (!Array.isArray(microSpans)) return false;
    
    return microSpans.every(sentenceSpans => {
        if (!Array.isArray(sentenceSpans)) return false;
        return sentenceSpans.every(span => {
            return span && 
                   typeof span.text === 'string' && 
                   typeof span.weight === 'number';
        });
    });
}

// Test data structure compatibility
export const testMicroSpansData = [
    [
        { text: 'high salience', weight: 0.85, start: 20, end: 32, method: 'ngram-basic' },
        { text: 'First sentence', weight: 0.75, start: 0, end: 14, method: 'ngram-basic' }
    ],
    [
        { text: 'medium salience', weight: 0.6, start: 22, end: 37, method: 'ngram-basic' }
    ]
];