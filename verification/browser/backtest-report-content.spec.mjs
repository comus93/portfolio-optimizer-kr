import path from 'node:path';
import { expect, test } from '@playwright/test';

const externalReport = process.env.BACKTEST_REPORT_PATH?.trim();

function servedPath(reportPath) {
  const relative = path.isAbsolute(reportPath)
    ? path.relative(process.cwd(), reportPath)
    : reportPath;
  if (relative.startsWith('..')) {
    throw new Error('BACKTEST_REPORT_PATH must be inside the repository root');
  }
  return `/${relative.replaceAll('\\', '/').replace(/^\.\//, '')}`;
}

async function metaValue(overview, label) {
  return overview.locator('.meta > div').evaluateAll((blocks, expectedLabel) => {
    const block = blocks.find(
      candidate => candidate.querySelector('b')?.textContent?.trim() === expectedLabel,
    );
    return block?.textContent?.replace(expectedLabel, '').trim() ?? '';
  }, label);
}

async function assertTooltipWorks(section) {
  const mark = section.locator('.chart-mark[data-tooltip]').first();
  await expect(mark).toHaveCount(1);
  await mark.hover({ force: true });
  const tooltip = mark
    .locator('xpath=ancestor::*[contains(@class,"chart-wrap")][1]')
    .locator('.chart-tooltip');
  await expect(tooltip).toBeVisible();
  await expect(tooltip).not.toHaveText('');
}

test.describe('Backtest changed-content contract', () => {
  test.skip(!externalReport, 'set BACKTEST_REPORT_PATH to a generated report');

  test('renders canonical historical analytics rather than table-only reductions', async ({ page }) => {
    await page.goto(servedPath(externalReport));
    const overview = page.locator('#overview');
    const benchmark = await metaValue(overview, 'Benchmark');

    const growthTicks = (await page.locator('#growth .x-tick-label').allTextContents())
      .map(value => value.trim());
    expect(growthTicks.length).toBeGreaterThan(1);
    expect(new Set(growthTicks).size).toBe(growthTicks.length);

    const annual = page.locator('#annualReturns');
    await expect(annual.locator('[data-chart="annual-returns-chart"]')).toBeVisible();
    await expect(annual.locator('.grouped-bar')).not.toHaveCount(0);
    await assertTooltipWorks(annual);

    const drawdowns = page.locator('#drawdowns');
    const drawdownPanels = drawdowns.locator('.drawdown-panel');
    await expect(drawdownPanels).not.toHaveCount(0);
    const drawdownCount = await drawdownPanels.count();
    for (let i = 0; i < drawdownCount; i += 1) {
      await expect(drawdownPanels.nth(i).locator('[data-chart^="drawdown-"]')).toBeVisible();
      await expect(
        drawdownPanels.nth(i).getByText('Drawdown Episodes', { exact: true }),
      ).toBeVisible();
    }

    const assets = page.locator('#assets');
    const performanceHeaders = (
      await assets.locator('#portfolio-asset-performance th').allTextContents()
    ).map(value => value.trim());
    for (const header of [
      'Ticker', 'Name', 'CAGR', 'Annualized Return', 'Standard Deviation',
      'Best Year', 'Worst Year', 'Maximum Drawdown', 'Sharpe Ratio', 'Sortino Ratio',
      '3M', 'YTD', '1Y', '3Y Annualized', '5Y Annualized', '10Y Annualized',
    ]) {
      expect(performanceHeaders).toContain(header);
    }
    await expect(assets.locator('[data-chart="annual-asset-returns-chart"]')).toBeVisible();
    await expect(assets.locator('#correlations-heatmap .heatmap-cell')).not.toHaveCount(0);

    const rolling = page.locator('#rollingReturns');
    await expect(rolling.locator('[data-chart="rolling-3y-annualized-return"]')).toBeVisible();
    await expect(rolling.locator('[data-chart="rolling-5y-annualized-return"]')).toBeVisible();

    if (benchmark === 'None') {
      await expect(page.locator('#activeReturns')).toHaveCount(0);
    } else {
      const active = page.locator('#activeReturns');
      await expect(active).toBeVisible();
      await expect(active.locator('[data-chart="annual-active-return-chart"]')).toBeVisible();
      await expect(active.locator('.active-contribution-panel')).not.toHaveCount(0);
      await expect(active.locator('.rolling-active-risk-panel')).not.toHaveCount(0);
      await expect(active.getByText('Active Return %', { exact: true }).first()).toBeVisible();
      await expect(active.getByText('Tracking Error %', { exact: true }).first()).toBeVisible();
      const upDown = active.locator('.up-down-panel').first();
      for (const header of [
        'Above Benchmark Count', 'Below Benchmark Count', 'Total', '% Above Benchmark',
        'Average Active Return Above', 'Average Active Return Below',
        'Average Active Return Total',
      ]) {
        await expect(upDown.getByText(header, { exact: true })).toBeVisible();
      }
      await expect(upDown.getByText('Return vs. Benchmark', { exact: true })).toBeVisible();
      await expect(upDown.locator('[data-chart^="return-vs-benchmark-"]')).toBeVisible();
      await assertTooltipWorks(active);
    }
  });
});
