import { test, expect } from '@playwright/test';

test.describe('Superscript marker -> StrategyDetailPanel explanation', () => {
  test('opens panel and displays explanation on marker click', async ({ page }) => {

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Enter source/target (must satisfy validation length thresholds to reach analysis)
    await page.getByTestId('source-textarea').fill('Texto fonte complexo original com conteúdo suficiente para validação e teste E2E.');
    await page.getByTestId('target-textarea').fill('Texto alvo simples reduzido com conteúdo suficiente.');

  // Intercept comparative-analysis POST used by EnhancedTextInput and return expected payload
  await page.route('**/api/v1/comparative-analysis/**', async (route, request) => {
      if (request.method() === 'POST') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: 'a1',
            source_text: 'Texto fonte complexo original com conteúdo suficiente para validação e teste E2E.',
            target_text: 'Texto alvo simples reduzido com conteúdo suficiente.',
            simplification_strategies: [
              { strategy_id: 's1', code: 'SL+', status: 'created', origin: 'human', target_offsets: [{ start: 0, end: 5 }], explanation: 'Adequação de Vocabulário: substituições léxicas sugerem simplificação.' },
              { strategy_id: 's2', code: 'RP+', status: 'created', origin: 'human', target_offsets: [{ start: 6, end: 12 }], explanation: 'Fragmentação Sintática: redução do comprimento médio das frases.' }
            ],
            strategies_count: 2,
            overall_score: 0,
            compression_ratio: 0.5,
            semantic_preservation: 0.9,
            readability_improvement: 0.2
          })
        });
      }
      return route.continue();
    });

    await page.getByTestId('analyze-button').click();

  // Wait until the results view is visible and the superscript layer wrapper is present
  const comparisonTab = page.getByRole('button', { name: 'Comparação' });
  await expect(comparisonTab).toBeVisible({ timeout: 10000 });
  await comparisonTab.click();
  await expect(page.getByLabel('Marcadores de estratégias detectadas')).toBeVisible({ timeout: 10000 });

  // Poll for markers (robust against slower React render)
  await expect.poll(async () => await page.getByTestId('strategy-marker').count(), { timeout: 8000 }).toBeGreaterThan(0);
    const markers = page.getByTestId('strategy-marker');
    await expect(await markers.count()).toBeGreaterThanOrEqual(2);

  // Click first marker
  await markers.nth(0).click();

  // Panel should appear with explanation
  const panel = page.getByRole('dialog', { name: /Detalhes da estratégia/i });
    await expect(panel).toBeVisible();
    const explanation = panel.getByTestId('strategy-explanation');
    await expect(explanation).toBeVisible();
    await expect(explanation).toContainText(/Adequação de Vocabulário/);

  // Close panel to allow clicking another marker (overlay intercepts pointer events)
  await panel.getByRole('button', { name: /Fechar painel de detalhes/i }).click();
  await expect(panel).toBeHidden();

  // Click second marker; panel reopens and shows its explanation
  await markers.nth(1).click();
    await expect(explanation).toContainText(/Fragmentação Sintática/);
  });
});
