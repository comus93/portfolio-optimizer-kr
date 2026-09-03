# PV Backtest user visual acceptance contract — 2026-09-03

## Purpose

This document records the user's direct visual verification findings against the captured Portfolio Visualizer Backtest reference. These are implementation/validation requirements, not optional polish.

Reference material:

- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- extracted `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-*.html`
- content comparison: `docs/validation/20260903-1356-KST-pv-backtest-content-comparison-run-20260903-backtest-qqq-gld-spy-presentation-validation-v2.md`
- user-supplied PV screenshots in the ChatGPT visual-review thread

Canonical rule remains: finance analytics are calculated upstream; renderer/browser code may perform presentation-only transforms but must not invent or recalculate canonical financial results.

## Accepted requirements

### 1. Target Allocation comparison

- Support the normal 1–3 portfolio comparison flow.
- Build one matrix from the union of all assets.
- A given asset occupies one row across all portfolio columns.
- A portfolio that does not hold the asset must remain semantically 0% but be visually muted, preferably `—`.
- Preserve input portfolio order.

### 2. Portfolio Growth shared month hover

- Portfolio/benchmark wealth paths share one time axis.
- Hovering any series/nearest x-region for a month must show one tooltip containing the month and every displayed portfolio plus benchmark balance.
- The user must not need to precisely hit a point on an individual line.
- Keep readable calendar-aware x ticks and currency-aware y ticks/grid.

### 3. Annual Returns under Portfolio Growth

- Summary must show the Annual Returns grouped bar chart directly below Portfolio Growth.
- The dedicated Annual Returns section may remain for detailed review.

### 4. Trailing Returns PV grouped table

Use a two-level header:

- Total Return: 3 Month / Year To Date / 1 Year
- Annualized Return: 3 Year / 5 Year / Full
- Annualized Standard Deviation: 3 Year / 5 Year

Add an as-of note for the last completed calendar month.

### 5. Annualized Active Return

- Grouped annual bars by portfolio.
- Readable percent y-axis, ticks, zero/reference grid.
- Shared year hover showing all compared portfolios in one structured tooltip.
- Benchmark comparison context must be visible.

### 6. Cumulative Active Return / contribution

- Separate panel for each portfolio vs benchmark.
- Monthly asset contributions use diverging stacked bars, not line charts and not side-by-side grouped bars.
- Positive contributions stack above zero; negative contributions stack below zero.
- Shared month hover lists all asset contribution values for that month.
- Where the PV reference provides compact 1Y/3Y/5Y contribution information, keep it below the chart.

### 7. Rolling Active Return and Risk

Per portfolio:

- Active Return = bars, left percent y-axis.
- Tracking Error = line, right percent y-axis.
- Both scales and grid/ticks must remain readable and unclipped.
- Shared month hover shows Active Return and Tracking Error together.

### 8. Up / Down Market Performance

Use grouped headers:

- Occurrences: Above Benchmark / Below Benchmark / Total / % Above Benchmark
- Average Active Return: Above / Below / Total

Also:

- Add a `Total` row across Up + Down observations.
- Keep Return vs Benchmark paired bars.
- Shared hover must show portfolio/benchmark values and observation count where available.

### 9. Drawdown chart axes

Each portfolio/benchmark drawdown chart must include:

- calendar-aware x-axis ticks
- Drawdown % y-axis ticks
- horizontal grid
- clear 0% baseline
- month inspect/hover

### 10. Drawdown episode recovery detail

Portfolio-specific worst drawdown table must include:

- Rank
- Start
- End (trough)
- Length
- Recovery By
- Recovery Time
- Underwater Period
- Drawdown

Unrecovered episodes display `N/A` for recovery fields. Limit the default presentation to the worst 10 episodes.

### 11. Assets section split

Replace the former all-in-one asset performance presentation with two purposeful tables.

**Portfolio Assets**

- Ticker
- Name
- CAGR
- Stdev
- Best Year
- Worst Year
- Max Drawdown
- Sharpe Ratio
- Sortino Ratio

**Portfolio Asset Performance**

Grouped trailing performance:

- Total Return: 3 Month / Year To Date / 1 Year
- Annualized Return: 3 Year / 5 Year

Add a trailing-return as-of note.

Do not fabricate Expense Ratio. It requires external product metadata and is outside this Backtest v1 scope.

### 12. Monthly Correlations

- PV-style correlation heatmap matrix.
- Ticker and Name identity columns where available.
- Assets, portfolios and benchmark remain distinguishable.
- Two-decimal coefficients.
- Blue intensity heatmap, readable text contrast.
- Wide tables may horizontally scroll; header/readability must be preserved.

### 13. Portfolio Return / Risk Decomposition

Keep both:

- Portfolio Return Decomposition
- Portfolio Risk Decomposition

Use Ticker + Name rows and portfolio comparison columns. Non-held/non-applicable cells should not be visually confused with a meaningful measured zero. Keep concise explanatory text.

### 14. Annual Asset Returns replacement

The prior Annual Asset Returns UI is replaced by the PV screenshot style:

- grouped bars by year
- fixed asset colors
- readable percent y-axis/grid
- bottom legend
- shared year hover listing every asset return for that year

Reuse the canonical annual asset return artifact. Do not keep a duplicate legacy UI beside it.

### 15. Rolling Returns

Top summary:

- rows: 1 Year / 3 Years / 5 Years
- each portfolio and benchmark: Average / High / Low
- negative Low values may be visually differentiated

Below the summary:

- Annualized Rolling Return - 3 Years
- Annualized Rolling Return - 5 Years
- readable axes/grid/legend
- shared month hover showing all portfolios and benchmark for the inspected month

Do not dump the raw rolling time-series tables as the primary UI.

## Cross-cutting visual interaction rules

- Same x-period => one shared tooltip containing all relevant series for that chart.
- Tooltip color dots must correspond to chart/legend colors.
- Tooltips must be visible in an actual browser, not only encoded as accessibility labels.
- Axis labels/ticks must not be clipped at desktop or mobile widths.
- Horizontal grid lines align to y ticks and do not obscure the data marks.
- Portfolio identity must not rely on color alone.
- Benchmark is displayed after compared portfolios.
- No-benchmark Backtest must omit benchmark-relative Active sections rather than fabricating zero values.
- Preserve ticker strings such as `069500` without numeric coercion.

## LLM implementation baseline

After direct implementation and shared-component reconciliation, affected Python regression on `bt-module` completed with:

```text
104 passed in 3.43s
```

GitHub Actions validation run: `33726674460`.

The Agent validation that follows this document must regenerate representative reports and verify the requirements in a real browser. Python/DOM green status alone is not sufficient visual acceptance.
