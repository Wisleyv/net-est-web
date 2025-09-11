import { test, expect } from '@playwright/test';

// E2E verification of enableFeedbackActions feature flag
// Assumes analysis stub network like analysisJourney; we reuse interception.

async function stubAnalysis(page, strategies = []) {
  const base = {
    analysis_id: 'fflag-1',
    overall_score: 0.5,
    timestamp: new Date().toISOString(),
    semantic_analysis: { semantic_similarity: 0.8 },
    readability_improvement: 3.2,
    simplification_strategies: strategies.length ? strategies : [
      { strategy_id: 'st1', code: 'SL+', name: 'Simplificação Lexical', description: 'Desc', confidence: 0.93, explanation: 'Substituição simplificada' }
    ],
  };
  const fulfill = async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(base) });
  };
  // Intercept relative paths
  await page.route('**/api/v1/comparative-analysis', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('**/api/v1/comparative-analysis/', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('**/api/v1/comparative-analysis/analyze', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('**/api/v1/comparative-analysis/validate-texts', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  // Intercept absolute API baseURL as configured in Playwright (127.0.0.1:8000)
  await page.route('http://127.0.0.1:8000/api/v1/comparative-analysis', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('http://127.0.0.1:8000/api/v1/comparative-analysis/', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('http://127.0.0.1:8000/api/v1/comparative-analysis/analyze', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
  await page.route('http://127.0.0.1:8000/api/v1/comparative-analysis/validate-texts', async (route, request) => {
    if (request.method() === 'POST') return fulfill(route);
    return route.continue();
  });
}

async function runAnalysis(page) {
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('[data-testid="analyze-button"]', { state: 'visible', timeout: 30000 });
  await page.fill('[data-testid="source-textarea"]', 'Texto original complexo com mais de cinquenta caracteres para passar na validação.');
  await page.fill('[data-testid="target-textarea"]', 'Texto simplificado com mais de vinte caracteres.');
  await page.click('[data-testid="analyze-button"]');
  // Wait for results to render before interacting with tabs
  await Promise.race([
    page.waitForSelector('[data-testid="results-container"]', { timeout: 90000 }),
    page.waitForSelector('button:has-text("Comparação")', { timeout: 90000 }),
  ]);
  await page.click('button:has-text("Comparação")');
  await expect(page.locator('[data-testid="strategy-marker"]').first()).toBeVisible();
  await page.locator('[data-testid="strategy-marker"]').first().click();
  await expect(page.locator('[role="dialog"]')).toBeVisible();
}

// Disabled flag case
test('feedback actions hidden when enableFeedbackActions=false', async ({ page }) => {
  await stubAnalysis(page);
  await runAnalysis(page);
  // Ensure buttons absent
  await expect(page.locator('button:has-text("Aceitar")')).toHaveCount(0);
  await expect(page.locator('button:has-text("Rejeitar")')).toHaveCount(0);
});

// Enabled flag case using App.jsx test-only hook and data-status attribute for robustness
test('feedback actions visible and functional when enableFeedbackActions=true', async ({ page }) => {
  await page.addInitScript(() => { window.__ENABLE_FEEDBACK_FLAG__ = true; });
  await stubAnalysis(page);
  // Stub annotation PATCH endpoint to simulate success
  await page.route('**/api/v1/annotations/*', async (route, request) => {
    if (request.method() === 'PATCH') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) });
    }
    return route.continue();
  });
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForSelector('[data-testid="analyze-button"]', { state: 'visible', timeout: 30000 });
  await page.fill('[data-testid="source-textarea"]', 'Texto original complexo com mais de cinquenta caracteres para passar na validação.');
  await page.fill('[data-testid="target-textarea"]', 'Texto simplificado com mais de vinte caracteres.');
  await page.click('[data-testid="analyze-button"]');
  await Promise.race([
    page.waitForSelector('[data-testid="results-container"]', { timeout: 90000 }),
    page.waitForSelector('button:has-text("Comparação")', { timeout: 90000 }),
  ]);
  await page.click('button:has-text("Comparação")');
  const marker = page.locator('[data-testid="strategy-marker"]').first();
  await marker.click();
  await expect(page.locator('[role="dialog"]')).toBeVisible();
  // Ensure feedback section is present
  await expect(page.locator('[data-testid="feedback-collection"]')).toHaveAttribute('data-enabled', 'true');
  const accept = page.locator('button:has-text("Aceitar")').first();
  await expect(accept).toBeVisible();
  // Click accept and assert PATCH request fired
  const [patchReq] = await Promise.all([
    page.waitForRequest(req => req.method() === 'PATCH' && /\/api\/v1\/annotations\//.test(req.url())),
    accept.click(),
  ]);
  expect(patchReq).toBeTruthy();
});
