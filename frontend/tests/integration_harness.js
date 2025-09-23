// Minimal test harness to simulate normalization + hashing + perf measurement
const { normalizeTextForOffsets, computeSHA256Hex } = require('../src/services/textNormalizer');
const { measureSync, measureAsync } = require('../src/services/perfInstrumentation');

async function runHarness() {
  const rawDom = '  Algumas [OM+] doenças afetam muitas\n mulheres, como a [SL-] endometriose.  ';
  const normalization = measureSync(() => normalizeTextForOffsets(rawDom));
  const normalized = normalization.result;
  const rawHash = await computeSHA256Hex(rawDom);
  const normalizedHash = await computeSHA256Hex(normalized);

  const payload = {
    startOffset: 0,
    endOffset: normalized.length,
    normalizedText: normalized.substring(0, 200),
    semanticContext: null,
    confidence: 1.0,
    normalizationMismatch: false,
    metadata: {
      rawDomLength: rawDom.length,
      normalizedLength: normalized.length,
      rawHash,
      normalizedHash,
      timings: {
        normalizationTimeMs: normalization.timeMs
      },
      timestamp: new Date().toISOString()
    }
  };

  console.log('=== Integration Harness Payload ===');
  console.log(JSON.stringify(payload, null, 2));
}

if (require.main === module) {
  runHarness().catch(err => { console.error(err); process.exit(1); });
}

module.exports = { runHarness };
