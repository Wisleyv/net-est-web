import assert from 'assert';
import { normalizeTextForOffsets, computeSHA256Hex } from '../src/services/textNormalizer.js';
import { measureSync, measureAsync } from '../src/services/perfInstrumentation.js';

const run = async () => {
  console.log('Running ad-hoc test runner for textNormalizer and perfInstrumentation');

  // Test 1: marker stripping
  const input1 = 'Algumas [OM+] doenças [SL-] afetam [RF+] muitas mulheres.';
  const expected1 = 'Algumas doenças afetam muitas mulheres.';
  const out1 = normalizeTextForOffsets(input1);
  assert.equal(out1, expected1, 'Marker stripping failed');
  console.log('Test 1 passed: marker stripping');

  // Test 2: whitespace normalization
  const input2 = '  Esta  é\n\tuma    string   com   espa\u00E7os.  ';
  const expected2 = 'Esta é uma string com espaços.';
  const out2 = normalizeTextForOffsets(input2);
  assert.equal(out2, expected2, 'Whitespace normalization failed');
  console.log('Test 2 passed: whitespace normalization');

  // Test 3: hash consistency
  const s = 'Consistent string for hashing.';
  const h1 = await computeSHA256Hex(s);
  const h2 = await computeSHA256Hex(s);
  assert.equal(h1, h2, 'Hash not consistent');
  assert.ok(typeof h1 === 'string' && h1.length > 0, 'Hash invalid');
  console.log('Test 3 passed: hash consistency');

  // Test 4: perf measure sync
  const { result, timeMs } = measureSync(() => {
    let s = 0;
    for (let i = 0; i < 10000; i++) s += i;
    return s;
  });
  assert.ok(typeof timeMs === 'number' && timeMs >= 0, 'measureSync time invalid');
  console.log('Test 4 passed: measureSync');

  // Test 5: measureAsync
  const asyncRes = await measureAsync(async () => {
    await new Promise(r => setTimeout(r, 5));
    return 'ok';
  });
  assert.equal(asyncRes.result, 'ok');
  assert.ok(typeof asyncRes.timeMs === 'number' && asyncRes.timeMs >= 0, 'measureAsync time invalid');
  console.log('Test 5 passed: measureAsync');

  console.log('All ad-hoc tests passed');
};

run().catch(err => { console.error(err); process.exit(1); });
