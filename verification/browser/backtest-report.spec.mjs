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

async function metaValue(overview, label) {
  return overview.locator('.meta > div').evaluateAll((blocks, expectedLabel) => {
    const block = blocks.find(
      candidate => candidate.querySelector('b')?.textContent?.trim() === expectedLabel,
    );
    return block?.textContent?.replace(expectedLabel, '').trim() ?? '';
  }, label);
}

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
  expect(await metaValue(overview, 'Time Period')).toMatch(/^(Month-to-Month|Year-to-Year)$/);
  expect(await metaValue(overview, 'Rebalancing')).toMatch(
    /^(None|Yearly|Semiannual|Quarterly|Monthly)$/,
  );
  expect(await metaValue(overview, 'Return Semantics')).toBe('Total Return');

  await expect(page.locator('#allocation h3')).toHaveText('Target Allocation');
  const allocationHeaders = (await page.locator('#allocation th').allTextContents()).map(value => value.trim());
  expect(allocationHeaders[0].toLowerCase()).toBe('asset');
  expect(await page.locator('#allocation tbody tr').count()).toBeGreaterThan(0);

  await expect(page.locator('#performance h3')).toHaveText('Performance Summary');
  const performanceHeaders = (await page.locator('#performance th').allTextContents()).map(value => value.trim());
  expect(performanceHeaders.map(value => value.toLowerCase())).not.toContain('unit');

  await expect(page.locator('#trailing h3')).toHaveText('Trailing Returns');
  const trailingHeaders = (await page.locator('#trailing th').allTextContents()).map(value => value.trim());
  for (const header of [
    'Name',
    'Total Return',
    'Annualized Return',
    'Annualized Standard Deviation',
    '3 Month',
    'Year To Date',
    '1 Year',
    '3 Year',
    '5 Year',
    'Full',
  ]) {
    expect(trailingHeaders).toContain(header);
  }
  expect(trailingHeaders.some(value => value.includes('_pct') || value.includes('_'))).toBe(false);

  const growth = page.locator('#growth');
  const growthChart = growth.locator('[data-chart="portfolio-growth"]');
  await expect(growthChart.locator('svg')).toHaveAttribute(
    'aria-label',
    'Portfolio balance growth over time',
  );
  expect(await growth.locator('.legend-item').count()).toBeGreaterThan(0);
  expect(await growthChart.locator('.x-tick-label').count()).toBeGreaterThanOrEqual(4);
  expect(await growthChart.locator('.y-tick-label').count()).toBeGreaterThanOrEqual(4);
  expect(await growthChart.locator('.grid-line').count()).toBeGreaterThanOrEqual(4);
  await expect(growthChart.getByText('Year', { exact: true })).toBeVisible();
  await expect(growthChart.getByText(/^Portfolio Balance \((\$|₩|[A-Z]{3})\)$/)).toBeVisible();
  const xTickLabels = (await growthChart.locator('.x-tick-label').allTextContents()).map(value => value.trim());
  for (const label of xTickLabels) {
    expect(label).toMatch(/^(Jan|Jul) \d{4}$/);
  }

  const firstPoint = growthChart.locator('.growth-hover-zone').first();
  const firstPointLabel = await firstPoint.getAttribute('aria-label');
  expect(firstPointLabel).toMatch(/^\d{4}-\d{2}-\d{2} \| .+: (\$|₩|[A-Z]{3} )[\d,]+$/);
  await firstPoint.hover({ force: true });
  await expect(growth.locator('#growth-tooltip')).toBeVisible();
  await expect(growth.locator('#growth-tooltip')).toContainText(/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}/);
  await firstPoint.focus();
  await expect(growth.locator('#growth-tooltip')).toBeVisible();

  const metricsHeaders = (await page.locator('#metrics th').allTextContents()).map(value => value.trim());
  expect(metricsHeaders[0]).toBe('Metric');
  expect(metricsHeaders.map(value => value.toLowerCase())).not.toContain('portfolio');
  expect(metricsHeaders.map(value => value.toLowerCase())).not.toContain('value');

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

  const annualAssetChart = page.locator('#assets [data-chart="annual-asset-returns-chart"]');
  await expect(annualAssetChart).toBeVisible();
  expect(await annualAssetChart.locator('.grouped-bar').count()).toBeGreaterThan(0);
  expect(await annualAssetChart.locator('.y-tick-label').count()).toBeGreaterThanOrEqual(3);
  expect(await annualAssetChart.locator('.grid-line').count()).toBeGreaterThanOrEqual(3);
  expect(await page.locator('#assets h3:has-text("Annual Asset Returns") + .table-wrap').count()).toBe(0);

  const correlationsTable = page.locator('#correlations-heatmap');
  const correlationValues = await correlationsTable.locator('.heatmap-cell').allTextContents();
  expect(correlationValues.length).toBeGreaterThan(0);
  for (const value of correlationValues) expect(value.trim()).toMatch(/^-?\d+\.\d{2}$|^N\/A$/);
  const assetText = await page.locator('#assets').innerText();
  expect(assetText).not.toMatch(/\b(?:0|-?\d+)\.\d{6,}\b/);
  expect(assetText).not.toContain('contribution_');
  expect(assetText).not.toContain('_pct');
  expect(assetText).not.toContain('_balance');

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

  const benchmarkText = await metaValue(overview, 'Benchmark');
  if (benchmarkText === 'None') {
    expect(await page.locator('#activeReturns').count()).toBe(0);
    expect(await page.locator('.sidebar').getByText('Active Returns', { exact: true }).count()).toBe(0);
  } else {
    await expect(page.locator('#activeReturns')).toBeVisible();
    await expect(page.locator('#activeReturns h2')).toHaveText('Active Returns');
    await expect(page.locator('.sidebar').getByText('Active Returns', { exact: true })).toBeVisible();
    for (const heading of ['Benchmark Summary', 'Annualized Active Return', 'Cumulative Active Return', 'Up / Down Market Performance']) {
      await expect(page.locator('#activeReturns').getByText(heading, { exact: true }).first()).toBeVisible();
    }
    const activeText = await page.locator('#activeReturns').innerText();
    for (const storageName of [
      'portfolio_return',
      'benchmark_return',
      'active_return',
      'rolling_tracking_error_pct',
      'cumulative_active_contribution_pct',
    ]) {
      expect(activeText).not.toContain(storageName);
    }
    await expect(growth.locator('.legend').first()).toContainText(benchmarkText);
    await expect(correlationsTable).toContainText(benchmarkText);
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
    const allocationHeaders = (await page.locator('#allocation th').allTextContents()).map(value => value.trim());
    expect(allocationHeaders.slice(1, 3)).toEqual(['Growth Tilt', 'Balanced']);
    const performanceHeaders = (await page.locator('#performance th').allTextContents()).map(value => value.trim());
    expect(performanceHeaders.slice(1, 4)).toEqual(['Growth Tilt', 'Balanced', 'SPDR S&P 500 ETF Trust']);
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
