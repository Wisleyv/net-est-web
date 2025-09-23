// perfInstrumentation.js
// Lightweight helper to measure timings using performance.now()

function nowMs() {
  if (typeof performance !== 'undefined' && performance.now) return performance.now();
  return Date.now();
}

function measureSync(fn) {
  const start = nowMs();
  const result = fn();
  const end = nowMs();
  return { result, timeMs: end - start };
}

async function measureAsync(fn) {
  const start = nowMs();
  const result = await fn();
  const end = nowMs();
  return { result, timeMs: end - start };
}

export { nowMs, measureSync, measureAsync };
