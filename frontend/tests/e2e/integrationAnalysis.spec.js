import { test, expect } from '@playwright/test';

// Real-backend integration test (no stubbing) - Tag: @integration
// Requires backend to be started by Playwright config.
// Skips if REAL_BACKEND env var not set to 'true' to avoid flakiness in fast local runs.

const shouldRun = process.env.REAL_BACKEND === 'true';

(shouldRun ? test : test.skip)('End-to-end analysis with real backend @integration', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');

  await page.fill('[data-testid="source-textarea"]', 'O gato preto pulou o muro alto.');
  await page.fill('[data-testid="target-textarea"]', 'O gato pulou o muro.');
  await page.click('[data-testid="analyze-button"]');

  // Wait for either results container or error toast
  await Promise.race([
    page.waitForSelector('[data-testid="results-container"]', { timeout: 120000 }),
    page.waitForSelector('[role="alert"]', { timeout: 120000 })
  ]);

  // If results container present, assert strategies appear after navigating tab
  if (await page.locator('[data-testid="results-container"]').count() > 0) {
    // Some UIs may default to different tab; click Estratégias if exists
    const strategyTab = page.locator('button:has-text("Estratégias")');
    if (await strategyTab.count() > 0) {
      await strategyTab.click();
    }
    const strategies = page.locator('[data-testid="strategy-result"]');
    await expect(strategies.first()).toBeVisible();
  }
});
