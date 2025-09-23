import { disambiguateWithContext } from '../fallbackDisambiguation';

describe('disambiguateWithContext', () => {
  const full = 'Sentence one. Reused phrase here. Another line. Reused phrase here. Final sentence with Reused phrase here.';
  const needle = 'Reused phrase here.';

  test('returns null when needle not found', () => {
    expect(disambiguateWithContext(full, 'not present')).toBeNull();
  });

  test('selects last occurrence when no approximate position provided', () => {
    const res = disambiguateWithContext(full, needle);
    expect(res).not.toBeNull();
    const { start, end } = res;
    expect(full.slice(start, end)).toBe(needle);
    // last occurrence should be near the end
    expect(start).toBeGreaterThan(full.indexOf(needle));
  });

  test('selects closest occurrence to approximate position', () => {
    const firstIdx = full.indexOf(needle);
    const lastIdx = full.lastIndexOf(needle);
    // approximate position near the beginning
    const res1 = disambiguateWithContext(full, needle, firstIdx + 2);
    expect(res1.start).toBe(firstIdx);

    // approximate position near the end
    const res2 = disambiguateWithContext(full, needle, lastIdx + 2);
    expect(res2.start).toBe(lastIdx);
  });

  test('validates boundaries and prefers contextual matches', () => {
    const tricky = 'abcReused phrase here.xyz Reused phrase here. Reused phrase here!';
    const needle2 = 'Reused phrase here';
    const res = disambiguateWithContext(tricky, needle2, 30);
    expect(res).not.toBeNull();
    const matched = tricky.slice(res.start, res.end);
    expect(matched).toBe(needle2);
  });
});
