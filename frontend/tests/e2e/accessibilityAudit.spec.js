import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Automated accessibility audit of main analysis flow
// Tag: @a11y

test.describe('Accessibility Audit', () => {
  test('Main analysis page has no critical axe violations @a11y', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');

    // Basic presence of input areas
    await expect(page.locator('[data-testid="source-textarea"]')).toBeVisible();
    await expect(page.locator('[data-testid="target-textarea"]')).toBeVisible();

    const axe = new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .disableRules([
        // Potentially noisy rules we will triage later
        'region', // may require landmark refactors
      ]);

    const results = await axe.analyze();

    const critical = results.violations.filter(v => (v.impact === 'critical' || v.impact === 'serious'));
    if (critical.length) {
      console.log('\n[axe] Serious/Critical Violations Found:\n');
      for (const v of critical) {
        console.log(`- ${v.id}: ${v.description}`);
        v.nodes.slice(0,5).forEach(n => console.log(`  -> Target: ${n.target.join(' ')}`));
      }
    }
    expect(critical, 'No serious/critical accessibility violations expected on initial load').toHaveLength(0);
  });
});
