import { normalizeTextForOffsets, computeSHA256Hex } from '../src/services/textNormalizer';

describe('textNormalizer', () => {
  test('strips bracketed markers', async () => {
    const input = 'Algumas [OM+] doenças [SL-] afetam [RF+] muitas mulheres.';
    const normalized = normalizeTextForOffsets(input);
    expect(normalized).toBe('Algumas doenças afetam muitas mulheres.');
  });

  test('normalizes whitespace', async () => {
    const input = '  Esta  é\n\tuma    string   com   espa\u00E7os.  ';
    const normalized = normalizeTextForOffsets(input);
    expect(normalized).toBe('Esta é uma string com espaços.');
  });

  test('hash is consistent', async () => {
    const s = 'Consistent string for hashing.';
    const h1 = await computeSHA256Hex(s);
    const h2 = await computeSHA256Hex(s);
    expect(h1).toBe(h2);
    expect(typeof h1).toBe('string');
    expect(h1.length).toBeGreaterThan(0);
  });

  test('computeSHA256Hex handles empty and non-string', async () => {
    const h = await computeSHA256Hex(null);
    expect(typeof h).toBe('string');
    expect(h.length).toBeGreaterThan(0);
  });
});
