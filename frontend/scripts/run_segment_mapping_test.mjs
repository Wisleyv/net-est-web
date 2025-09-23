import assert from 'assert';
import path from 'path';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const modulePath = path.resolve(__dirname, '../src/services/unifiedStrategyMapping.js');
const { segmentTextForHighlights } = await import('file://' + modulePath);

function run() {
  const text = 'One. Two. Three. Four.';
  const strategies = [
    { id: 's1', code: 'OM+', target_offsets: [{ start: 0, end: 4 }], confidence: 0.9 },
    { id: 's2', code: 'RF+', target_offsets: [{ start: 10, end: 16 }], confidence: 0.8 }
  ];

  const segs = segmentTextForHighlights(text, strategies, { scope: 'target' });
  assert.strictEqual(segs.length, 2, 'Two segments expected');
  assert.strictEqual(segs[0].charStart, 0);
  assert.strictEqual(segs[0].charEnd, 4);
  assert.strictEqual(segs[1].charStart, 10);
  assert.strictEqual(segs[1].charEnd, 16);

  console.log('segmentTextForHighlights array-offsets test passed');
}

try { run(); } catch (e) { console.error('Segment mapping test failed:', e); process.exit(1); }
