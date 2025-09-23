import assert from 'assert';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const modulePath = path.resolve(__dirname, '../src/services/fallbackDisambiguation.js');
const { disambiguateWithContext } = await import('file://' + modulePath);

function run() {
  const full = 'Sentence one. Reused phrase here. Another line. Reused phrase here. Final sentence with Reused phrase here.';
  const needle = 'Reused phrase here.';

  // Not found
  assert.strictEqual(disambiguateWithContext(full, 'not present'), null);

  // No approx -> last occurrence
  const res = disambiguateWithContext(full, needle);
  assert.ok(res, 'Expected a match for last occurrence');
  assert.strictEqual(full.slice(res.start, res.end), needle);

  const firstIdx = full.indexOf(needle);
  const lastIdx = full.lastIndexOf(needle);
  const res1 = disambiguateWithContext(full, needle, firstIdx + 2);
  assert.strictEqual(res1.start, firstIdx, 'Should pick first occurrence when approx near first');
  const res2 = disambiguateWithContext(full, needle, lastIdx + 2);
  assert.strictEqual(res2.start, lastIdx, 'Should pick last occurrence when approx near last');

  // Boundary validation test
  const tricky = 'abcReused phrase here.xyz Reused phrase here. Reused phrase here!';
  const needle2 = 'Reused phrase here';
  const res3 = disambiguateWithContext(tricky, needle2, 30);
  assert.ok(res3, 'Expected a contextual match for tricky string');
  assert.strictEqual(tricky.slice(res3.start, res3.end), needle2);

  console.log('All disambiguation tests passed');
}

try {
  run();
} catch (err) {
  console.error('Disambiguation tests failed:', err);
  process.exit(1);
}
