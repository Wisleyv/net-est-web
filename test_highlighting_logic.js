// Test script for character-level highlighting
import { segmentTextForHighlights } from './frontend/src/services/unifiedStrategyMapping.js';

// Mock data based on the API response
const targetText = "O estudo mostra que os resultados conseguidos com métodos estatísticos simples confirmam a ideia inicial dos pesquisadores.";

const mockStrategies = [
  {
    strategy_id: "ea7d2d89-d196-4e8c-a9b7-94f40cfe0f7b",
    code: "SL+",
    name: "Adequação de Vocabulário", 
    confidence: 1.0,
    target_offsets: {
      paragraph: 0,
      sentence: 0,
      char_start: 0,
      char_end: 123
    }
  }
];

console.log('Testing character-level highlighting...');
console.log('Target text length:', targetText.length);
console.log('Strategy covers chars 0-123');

const segments = segmentTextForHighlights(targetText, mockStrategies, { scope: 'target' });
console.log('Generated segments:', segments);

segments.forEach((segment, idx) => {
  console.log(`Segment ${idx}:`, {
    text: segment.text,
    charStart: segment.charStart,
    charEnd: segment.charEnd,
    code: segment.code,
    confidence: segment.confidence
  });
});