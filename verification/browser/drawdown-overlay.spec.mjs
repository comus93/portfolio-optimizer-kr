import path from 'node:path';
import { expect, test } from '@playwright/test';

const reportPath = process.env.DRAWDOWN_REPORT_PATH?.trim();
const sectionSelector = process.env.DRAWDOWN_SECTION?.trim() || '#drawdowns';

function servedPath(value) {
  const relative = path.isAbsolute(value) ? path.relative(process.cwd(), value) : value;
  if (relative.startsWith('..')) throw new Error('DRAWDOWN_REPORT_PATH must be inside repository root');
  const normalized = relative.split(path.sep).join('/');
  return `/${normalized.startsWith('./') ? normalized.slice(2) : normalized}`;
}

test.describe('shared drawdown overlay interaction', () => {
  test.skip(!reportPath, 'set DRAWDOWN_REPORT_PATH to a generated report');

  test('keeps context lines and foregrounds the selected portfolio', async ({ page }) => {
    await page.goto(servedPath(reportPath));
    const section = page.locator(sectionSelector);
    await expect(section).toBeVisible();
    await expect(section.locator('[data-chart="drawdown-comparison"]')).toHaveCount(1);

    const choices = section.locator('.drawdown-choice');
    const labels = section.locator('.drawdown-selector-label');
    const details = section.locator('.drawdown-detail');
    const baseLines = section.locator('.drawdown-base-series');
    const focusLines = section.locator('.drawdown-focus-series');
    const count = await choices.count();
    expect(count).toBeGreaterThanOrEqual(2);
    await expect(labels).toHaveCount(count);
    await expect(details).toHaveCount(count);
    await expect(baseLines).toHaveCount(count);
    await expect(focusLines).toHaveCount(count);

    await expect(choices.first()).toBeChecked();
    await expect(details.first()).toBeVisible();
    await expect(focusLines.first()).toHaveCSS('opacity', '1');
    await expect(baseLines.first()).toHaveCSS('opacity', '0.34');

    await labels.nth(1).click();
    await expect(choices.nth(1)).toBeChecked();
    await expect(details.first()).toBeHidden();
    await expect(details.nth(1)).toBeVisible();
    await expect(focusLines.first()).toHaveCSS('opacity', '0');
    await expect(focusLines.nth(1)).toHaveCSS('opacity', '1');
    await expect(baseLines.first()).toHaveCSS('opacity', '0.34');
    await expect(details.nth(1).getByText('탄성회복도', { exact: true })).toBeVisible();
    await expect(details.nth(1).getByText('Recovery By', { exact: true })).toBeVisible();
  });
});
