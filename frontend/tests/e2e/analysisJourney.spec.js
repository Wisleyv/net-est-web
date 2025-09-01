import { test, expect } from '@playwright/test';

test('Submit texts and view analysis results', async ({ page }) => {
  // Navigate to application
  await page.goto('http://localhost:5173');
  
  // Enter source and target texts
  await page.fill('[data-testid="source-textarea"]', 'O gato preto pulou o muro alto.');
  await page.fill('[data-testid="target-textarea"]', 'O felino escuro saltou sobre a parede elevada.');
  
  // Submit for analysis
  await page.click('[data-testid="analyze-button"]');
  
  // Wait for results to load
  await page.waitForSelector('[data-testid="results-container"]', { timeout: 15000 });
  
  // Verify results are displayed
  const results = await page.locator('[data-testid="strategy-result"]');
  await expect(results).toHaveCount(3);
  
  // Verify strategy detection
  const strategyNames = await page.locator('[data-testid="strategy-name"]').allTextContents();
  expect(strategyNames).toContain('SL+');
  expect(strategyNames).toContain('MT+');
});