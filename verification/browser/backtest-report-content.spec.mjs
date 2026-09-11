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
    const block = blocks.find(candidate => candidate.querySelector('b')?.textContent?.trim() === expectedLabel);
    return block?.textContent?.replace(expectedLabel, '').trim() ?? '';
  }, label);
}

async function assertTooltipWorks(section) {
  const mark = section.locator('.chart-mark[data-tooltip]').first();
  await expect(mark).toHaveCount(1);
  await mark.hover({ force: true });
  const tooltip = mark.locator('xpath=ancestor::*[contains(@class,"chart-wrap")][1]').locator('.chart-tooltip');
  await expect(tooltip).toBeVisible();
  await expect(tooltip).not.toHaveText('');
}

test.describe('Backtest PV visual acceptance contract', () => {
  test.skip(!externalReport, 'set BACKTEST_REPORT_PATH to a generated report');

  test('renders the user-reviewed Backtest information and interaction hierarchy', async ({ page }) => {
    await page.goto(servedPath(externalReport));
    const overview = page.locator('#overview');
    const benchmark = await metaValue(overview, 'Benchmark');

    const allocation = overview.locator('#allocation-matrix');
    await expect(allocation).toBeVisible();

    const growth = overview.locator('#growth');
    const growthTicks = (await growth.locator('.growth-chart .x-tick-label').allTextContents()).map(value => value.trim());
    expect(growthTicks.length).toBeGreaterThan(1);
    expect(new Set(growthTicks).size).toBe(growthTicks.length);
    await expect(growth.locator('[data-chart="portfolio-growth"]')).toBeVisible();
    await expect(growth.locator('.growth-hover-zone')).not.toHaveCount(0);
    await expect(growth.locator('[data-chart="annual-returns-chart"]')).toBeVisible();
    await assertTooltipWorks(growth);

    const trailing = overview.locator('#trailing');
    for (const header of ['Total Return', 'Annualized Return', 'Annualized Standard Deviation']) {
      await expect(trailing.getByText(header, { exact: true })).toBeVisible();
    }
    await expect(trailing.locator('.as-of-note')).toBeVisible();

    const annual = page.locator('#annualReturns');
    await expect(annual.locator('[data-chart="annual-returns-chart"]')).toBeVisible();
    await expect(annual.locator('.grouped-hover-zone')).not.toHaveCount(0);
    await assertTooltipWorks(annual);

    const drawdowns = page.locator('#drawdowns');
    await expect(drawdowns.locator('[data-chart="drawdown-comparison"]')).toHaveCount(1);
    await expect(drawdowns.locator('.drawdown-selector-label')).not.toHaveCount(0);
    await expect(drawdowns.locator('.drawdown-base-series')).not.toHaveCount(0);
    await expect(drawdowns.locator('.drawdown-focus-series')).not.toHaveCount(0);
    const firstChoice = drawdowns.locator('.drawdown-choice').first();
    const secondChoice = drawdowns.locator('.drawdown-choice').nth(1);
    await expect(firstChoice).toBeChecked();
    await expect(drawdowns.locator('.drawdown-detail').first()).toBeVisible();
    await expect(drawdowns.locator('.drawdown-detail').nth(1)).toBeHidden();
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '1');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '0');
    await drawdowns.locator('.drawdown-selector-label').nth(1).click();
    await expect(secondChoice).toBeChecked();
    await expect(drawdowns.locator('.drawdown-detail').first()).toBeHidden();
    const activeDetail = drawdowns.locator('.drawdown-detail').nth(1);
    await expect(activeDetail).toBeVisible();
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '0');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '1');
    await expect(activeDetail.getByText('Recovery By', { exact: true })).toBeVisible();
    await expect(activeDetail.getByText('Recovery Time', { exact: true })).toBeVisible();
    await expect(activeDetail.getByText('Underwater Period', { exact: true })).toBeVisible();

    const assets = page.locator('#assets');
    await expect(assets.locator('#portfolio-assets')).toBeVisible();
    for (const header of ['Ticker', 'Name', 'CAGR', 'Stdev', 'Best Year', 'Worst Year', 'Max Drawdown', 'Sharpe Ratio', 'Sortino Ratio']) {
      await expect(assets.locator('#portfolio-assets').getByText(header, { exact: true })).toBeVisible();
    }
    await expect(assets.locator('#portfolio-asset-performance')).toBeVisible();
    for (const header of ['Total Return', 'Annualized Return', '3 Month', 'Year To Date', '1 Year', '3 Year', '5 Year']) {
      await expect(assets.locator('#portfolio-asset-performance').getByText(header, { exact: true })).toBeVisible();
    }
    await expect(assets.locator('[data-chart="annual-asset-returns-chart"]')).toBeVisible();
    await expect(assets.locator('[data-chart="annual-asset-returns-chart"] .grouped-hover-zone')).not.toHaveCount(0);
    await expect(assets.locator('#correlations-heatmap .heatmap-cell')).not.toHaveCount(0);
    await expect(assets.locator('#portfolio-return-decomposition')).toBeVisible();
    await expect(assets.locator('#portfolio-risk-decomposition')).toBeVisible();

    const rolling = page.locator('#rollingReturns');
    await expect(rolling.locator('#rolling-returns-summary')).toBeVisible();
    for (const header of ['Average', 'High', 'Low']) {
      await expect(rolling.getByText(header, { exact: true }).first()).toBeVisible();
    }
    await expect(rolling.locator('[data-chart="rolling-3y-annualized-return"]')).toBeVisible();
    await expect(rolling.locator('[data-chart="rolling-5y-annualized-return"]')).toBeVisible();
    await expect(rolling.locator('.line-hover-zone')).not.toHaveCount(0);
    await assertTooltipWorks(rolling);

    if (benchmark === 'None') {
      await expect(page.locator('#activeReturns')).toHaveCount(0);
    } else {
      const active = page.locator('#activeReturns');
      await expect(active).toBeVisible();
      await expect(active.locator('[data-chart="annual-active-return-chart"]')).toBeVisible();
      await expect(active.locator('.grouped-hover-zone')).not.toHaveCount(0);
      await expect(active.locator('.active-contribution-panel')).not.toHaveCount(0);
      await expect(active.locator('.active-contribution-bar.stacked-bar')).not.toHaveCount(0);
      await expect(active.locator('.active-contribution-hover-zone')).not.toHaveCount(0);
      await expect(active.locator('.active-contribution-summary')).not.toHaveCount(0);
      await expect(active.locator('.rolling-active-risk-panel')).not.toHaveCount(0);
      await expect(active.getByText('Active Return %', { exact: true }).first()).toBeVisible();
      await expect(active.getByText('Tracking Error %', { exact: true }).first()).toBeVisible();
      await expect(active.locator('.rolling-active-hover-zone')).not.toHaveCount(0);
      const upDown = active.locator('.up-down-panel').first();
      for (const header of ['Occurrences', 'Above Benchmark', 'Below Benchmark', 'Total', '% Above Benchmark', 'Average Active Return']) {
        await expect(upDown.getByText(header, { exact: true }).first()).toBeVisible();
      }
      await expect(upDown.getByText('Return vs. Benchmark', { exact: true })).toBeVisible();
      await expect(upDown.locator('[data-chart^="return-vs-benchmark-"]')).toBeVisible();
      await assertTooltipWorks(active);
    }
  });
});