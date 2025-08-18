/**
 * Simple unit tests for SentenceSalienceHeatmap helpers moved to test_helpers.
 * This file now contains actual test suites so Vitest will not report "No test suite found".
 */
import { describe, it, expect } from 'vitest';
import { validateMicroSpansStructure, testMicroSpansData } from '../test_helpers/SentenceSalienceHeatmap.simple.js';

describe('SentenceSalienceHeatmap simple helpers', () => {
    it('validateMicroSpansStructure returns true for valid data', () => {
        expect(validateMicroSpansStructure(testMicroSpansData)).toBe(true);
    });

    it('returns false for invalid structures', () => {
        expect(validateMicroSpansStructure(null)).toBe(false);
        expect(validateMicroSpansStructure([null])).toBe(false);
        expect(validateMicroSpansStructure([[{ text: 'x', weight: 'not-number' }]])).toBe(false);
    });
});