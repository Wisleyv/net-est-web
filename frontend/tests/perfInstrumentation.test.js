import { measureSync, measureAsync } from '../src/services/perfInstrumentation';

describe('perfInstrumentation', () => {
  test('measureSync returns time and result', () => {
    const { result, timeMs } = measureSync(() => {
      let s = 0;
      for (let i = 0; i < 1000; i++) s += i;
      return s;
    });
    expect(result).toBeGreaterThanOrEqual(0);
    expect(typeof timeMs).toBe('number');
    expect(timeMs).toBeGreaterThanOrEqual(0);
  });

  test('measureAsync measures async function', async () => {
    const { result, timeMs } = await measureAsync(async () => {
      await new Promise(r => setTimeout(r, 10));
      return 'ok';
    });
    expect(result).toBe('ok');
    expect(typeof timeMs).toBe('number');
    expect(timeMs).toBeGreaterThanOrEqual(0);
  });
});
