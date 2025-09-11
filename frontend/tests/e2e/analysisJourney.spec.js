import { test, expect } from '@playwright/test';

test('Submit texts and view analysis results', async ({ page }) => {
  // Console/network diagnostics
  page.on('console', msg => console.log('[browser]', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('[pageerror]', err.message));
  
  // Stub backend analysis endpoints for fast, deterministic E2E
  const fulfillMock = async (route) => {
    const mock = {
      analysis_id: 'e2e-mock-123',
      overall_score: 0.82,
      timestamp: new Date().toISOString(),
      semantic_analysis: { semantic_similarity: 0.92 },
      readability_improvement: 7.5,
      simplification_strategies: [
        {
          code: 'SL+',
          name: 'Simplificação Lexical',
          description: 'Substitui palavras complexas por simples',
          impact: 'medium',
          confidence: 0.9,
          examples: [{ original: 'felino', simplified: 'gato' }],
        },
        {
          code: 'MT+',
          name: 'Mudança de Termos',
          description: 'Substitui termos técnicos por comuns',
          impact: 'low',
          confidence: 0.7,
          examples: [],
        },
      ],
    };
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mock) });
  };
  await page.route('**/api/v1/comparative-analysis', async (route, request) => {
    if (request.method() === 'POST') return fulfillMock(route);
    return route.continue();
  });
  await page.route('**/api/v1/comparative-analysis/', async (route, request) => {
    if (request.method() === 'POST') return fulfillMock(route);
    return route.continue();
  });
  await page.route('**/api/v1/comparative-analysis/analyze', async (route, request) => {
    if (request.method() === 'POST') return fulfillMock(route);
    return route.continue();
  });

  // Navigate to application using baseURL from config
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  
  // Enter source and target texts
  await page.fill('[data-testid="source-textarea"]', 'O gato preto pulou o muro alto enquanto observava atentamente o movimento no quintal vizinho.');
  await page.fill('[data-testid="target-textarea"]', 'O felino escuro saltou a parede alta, atento ao que ocorria no quintal ao lado.');
  
  // Submit for analysis
  await page.click('[data-testid="analyze-button"]');
  
  // Wait for results to load (heading or container)
  await Promise.race([
    page.waitForSelector('[data-testid="results-container"]', { timeout: 90000 }),
    page.waitForSelector('text=Resultados da Análise Comparativa', { timeout: 90000 })
  ]);
  // Open estratégias tab (cards live there)
  await page.click('button:has-text("Estratégias")');
  const results = page.locator('[data-testid="strategy-result"]');
  await expect(results.first()).toBeVisible();
  const count = await results.count();
  expect(count).toBeGreaterThan(0);
  const strategyNames = await page.locator('[data-testid="strategy-name"]').allTextContents();
  expect(strategyNames.length).toBe(count);
});