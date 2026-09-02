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

const fixtureWithBenchmark = '/.playwright/backtest-browser/with-benchmark/report.html';
const fixtureWithoutBenchmark = '/.playwright/backtest-browser/without-benchmark/report.html';

async function assertCoreReport(page, reportUrl, testInfo, screenshotPrefix) {
  await page.goto(reportUrl);
  await expect(page.locator('.result-header')).toContainText('Portfolio Analysis Results');

  const overview = page.locator('#overview');
  await expect(overview).toBeVisible();
  await expect(overview.locator('h2')).toHaveText('Summary');
  for (const label of [
    'Run ID',
    'Time Period',
    'Requested',
    'Effective',
    'Initial Amount',
    'Benchmark',
    'Rebalancing',
    'Calendar Aligned',
    'Return Semantics',
  ]) {
    await expect(overview.getByText(label, { exact: true })).toBeVisible();
  }

  await expect(page.locator('#allocation h3')).toHaveText('Target Allocation');
  const allocationHeaders = await page.locator('#allocation th').allTextContents();
  expect(allocationHeaders.map(value => value.trim().toLowerCase())).toContain('asset');
  expect(await page.locator('#allocation tbody tr').count()).toBeGreaterThan(0);

  await expect(page.locator('#performance h3')).toHaveText('Performance Summary');
  await expect(page.locator('#trailing h3')).toHaveText('Trailing Returns');

  const growth = page.locator('#growth');
  await expect(growth.locator('svg[role="img"]')).toHaveAttribute(
    'aria-label',
    'Portfolio balance growth over time',
  );
  expect(await growth.locator('.legend-item').count()).toBeGreaterThan(0);
  expect(await growth.locator('.x-tick-label').count()).toBeGreaterThanOrEqual(4);
  expect(await growth.locator('.y-tick-label').count()).toBeGreaterThanOrEqual(4);
  expect(await growth.locator('.grid-line').count()).toBeGreaterThanOrEqual(4);
  await expect(growth.getByText('Year', { exact: true })).toBeVisible();
  await expect(growth.getByText('Portfolio Balance ($)', { exact: true })).toBeVisible();

  const firstPoint = growth.locator('circle[aria-label]').first();
  const firstPointLabel = await firstPoint.getAttribute('aria-label');
  expect(firstPointLabel).toMatch(/^\d{4}-\d{2}-\d{2} \| .+: \$[\d,]+$/);
  await firstPoint.hover({ force: true });
  await expect(growth.locator('#growth-tooltip')).toBeVisible();
  await expect(growth.locator('#growth-tooltip')).toContainText(firstPointLabel.split(' | ')[0]);
  await firstPoint.focus();
  await expect(growth.locator('#growth-tooltip')).toBeVisible();

  for (const id of [
    'metrics',
    'annualReturns',
    'monthlyReturns',
    'drawdowns',
    'assets',
    'rollingReturns',
  ]) {
    await expect(page.locator(`#${id}`)).toBeVisible();
  }

  for (const label of [
    'Summary',
    'Metrics',
    'Annual Returns',
    'Monthly Returns',
    'Drawdowns',
    'Assets',
    'Rolling Returns',
  ]) {
    await expect(page.locator('.sidebar').getByText(label, { exact: true })).toBeVisible();
  }

  expect(await page.getByText(/Efficient Frontier/i).count()).toBe(0);
  expect(await page.getByText(/Optimized Portfolio/i).count()).toBe(0);
  expect(await page.getByText(/Style Analysis/i).count()).toBe(0);
  expect(await page.getByText(/Factor Regression/i).count()).toBe(0);

  const benchmarkBlock = overview.locator('.meta div').filter({ hasText: 'Benchmark' }).first();
  const benchmarkText = (await benchmarkBlock.innerText()).replace('Benchmark', '').trim();
  if (benchmarkText === 'None') {
    expect(await page.locator('#activeReturns').count()).toBe(0);
    expect(await page.locator('.sidebar').getByText('Active Returns', { exact: true }).count()).toBe(0);
  } else {
    await expect(page.locator('#activeReturns')).toBeVisible();
    await expect(page.locator('#activeReturns h2')).toHaveText('Active Returns');
    await expect(page.locator('.sidebar').getByText('Active Returns', { exact: true })).toBeVisible();
  }

  await page.screenshot({
    path: testInfo.outputPath(`${screenshotPrefix}-desktop.png`),
    fullPage: true,
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('#overview')).toBeVisible();
  const documentOverflow = await page.evaluate(() =>
    document.documentElement.scrollWidth > window.innerWidth + 1,
  );
  expect(documentOverflow).toBe(false);

  const inaccessibleScrollableTables = await page.locator('.table-wrap').evaluateAll(wrappers =>
    wrappers.filter(element => {
      if (element.scrollWidth <= element.clientWidth + 1) return false;
      const overflowX = getComputedStyle(element).overflowX;
      return overflowX !== 'auto' && overflowX !== 'scroll';
    }).length,
  );
  expect(inaccessibleScrollableTables).toBe(0);

  const chartOverflow = await page.locator('.chart-wrap').evaluateAll(wrappers =>
    wrappers.filter(element => {
      if (element.scrollWidth <= element.clientWidth + 1) return false;
      const overflowX = getComputedStyle(element).overflowX;
      return overflowX !== 'auto' && overflowX !== 'scroll';
    }).length,
  );
  expect(chartOverflow).toBe(0);

  await page.screenshot({
    path: testInfo.outputPath(`${screenshotPrefix}-mobile.png`),
    fullPage: true,
  });
}

test.describe('deterministic Backtest browser fixture', () => {
  test.skip(Boolean(externalReport), 'external report mode checks only the supplied real-run report');

  test('benchmark report exposes applicable semantics', async ({ page }, testInfo) => {
    await assertCoreReport(page, fixtureWithBenchmark, testInfo, 'fixture-benchmark');
    await expect(page.locator('#activeReturns')).toBeVisible();
    await expect(page.locator('#allocation')).toContainText('Growth Tilt');
    await expect(page.locator('#allocation')).toContainText('Balanced');
    await expect(page.locator('#allocation')).toContainText('QQQ');
    await expect(page.locator('#allocation')).toContainText('GLD');
  });

  test('benchmark-none report omits benchmark-relative analytics', async ({ page }, testInfo) => {
    await assertCoreReport(page, fixtureWithoutBenchmark, testInfo, 'fixture-no-benchmark');
    expect(await page.locator('#activeReturns').count()).toBe(0);
    await expect(page.locator('#overview')).toContainText('None');
  });
});

test.describe('real-run Backtest report', () => {
  test.skip(!externalReport, 'set BACKTEST_REPORT_PATH to verify a real generated report');

  test('satisfies Backtest semantic and responsive acceptance', async ({ page }, testInfo) => {
    await assertCoreReport(page, servedPath(externalReport), testInfo, 'real-run');
  });
});
