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
  await expect(page.locator('header h1')).toHaveText('Portfolio Backtest');

  const overview = page.locator('#overview');
  await expect(overview).toBeVisible();
  for (const label of [
    'Time Period Mode',
    'Requested Period',
    'Effective Period',
    'Initial Amount',
    'Benchmark',
    'Rebalancing',
    'Calendar Aligned',
    'Return Semantics',
  ]) {
    await expect(overview.getByText(label, { exact: true })).toBeVisible();
  }

  await expect(page.locator('#allocation h2')).toHaveText('Target Allocation');
  const allocationHeaders = await page.locator('#allocation th').allTextContents();
  expect(allocationHeaders.map(value => value.trim().toLowerCase())).toEqual(
    expect.arrayContaining(['portfolio', 'ticker', 'target_weight_pct']),
  );
  expect(await page.locator('#allocation tbody tr').count()).toBeGreaterThan(0);

  const growth = page.locator('#growth');
  await expect(growth.locator('svg[role="img"]')).toHaveAttribute(
    'aria-label',
    'Portfolio balance growth over time',
  );
  expect(await growth.locator('.legend-item').count()).toBeGreaterThan(0);
  const firstPointLabel = await growth.locator('circle[aria-label]').first().getAttribute('aria-label');
  expect(firstPointLabel).toMatch(/^\d{4}-\d{2}-\d{2} \| .+: \$[\d,]+$/);

  for (const id of [
    'performance',
    'annual',
    'monthly',
    'drawdowns',
    'rolling',
    'correlations',
    'decomposition',
  ]) {
    await expect(page.locator(`#${id}`)).toBeVisible();
  }

  expect(await page.getByText(/Efficient Frontier/i).count()).toBe(0);
  expect(await page.getByText(/Optimized Portfolio/i).count()).toBe(0);

  const benchmarkBlock = overview.locator('.meta div').filter({ hasText: 'Benchmark' }).first();
  const benchmarkText = (await benchmarkBlock.innerText()).replace('Benchmark', '').trim();
  if (benchmarkText === 'None') {
    expect(await page.locator('#active').count()).toBe(0);
  } else {
    await expect(page.locator('#active')).toBeVisible();
    await expect(page.locator('#active h2')).toHaveText('Benchmark-relative Analytics');
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
    await expect(page.locator('#active')).toBeVisible();
    await expect(page.locator('#allocation')).toContainText('Growth Tilt');
    await expect(page.locator('#allocation')).toContainText('Balanced');
    await expect(page.locator('#allocation')).toContainText('QQQ');
    await expect(page.locator('#allocation')).toContainText('GLD');
  });

  test('benchmark-none report omits benchmark-relative analytics', async ({ page }, testInfo) => {
    await assertCoreReport(page, fixtureWithoutBenchmark, testInfo, 'fixture-no-benchmark');
    expect(await page.locator('#active').count()).toBe(0);
    await expect(page.locator('#overview')).toContainText('None');
  });
});

test.describe('real-run Backtest report', () => {
  test.skip(!externalReport, 'set BACKTEST_REPORT_PATH to verify a real generated report');

  test('satisfies Backtest semantic and responsive acceptance', async ({ page }, testInfo) => {
    await assertCoreReport(page, servedPath(externalReport), testInfo, 'real-run');
  });
});
