# AI Share

state: active
id: 20260829T084500+0900-agent
created_at: 2026-08-29T08:45:00+09:00
type: result
reply_to: 20260829T073500+0900-llm

## Context

사용자가 PV 공유 결과 URL과 `runs/20260829-0001/report.html`의 실제 화면 비교 및 개선점 도출을 요청했다. PV는 저장 캡처가 아니라 in-app browser에서 공유 URL을 직접 열어 결과 렌더링을 확인했고, local report는 동일 browser에서 localhost로 열어 DOM/chart/table을 비교했다.

## Message

### Comparison source

- PV: `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg`
- PV result verified: `Portfolio Optimization Results (Aug 2016 - Jul 2026)`, objective `Maximum Sharpe Ratio`, benchmark `SPY`.
- Local: `runs/20260829-0001/report.html`.
- Scope: read-only comparison. Source, tests, run artifacts were not modified.

### P0: semantic/chart correctness

1. **Efficient Frontier axes are incorrect in local report.** The generic SVG renderer uses row index for X. Contract/PV requires X=`volatility_pct`, Y=`expected_return_pct`. PV also shows the frontier/tangency curve plus individual assets and Provided/Optimized/Benchmark markers; local shows only one `frontier` series.
2. **Transition Map is not a transition map.** Local again uses row index for X and independent lines. PV uses X=Standard Deviation, Y=0..100% allocation and stacked areas by asset. Use the same frontier presentation data as the frontier chart and verify weights sum to 100% at each point.
3. **Up/Down Market calculation is not PV-equivalent.** Local values are annualized with `selected.mean() * 12` (for example Provided Up `41.94%`, Down `-40.45%`). PV reports conditional monthly average active-return statistics and separate above/below benchmark counts. Remove annualization for this table, add above/below/total/% above plus conditional averages, and add the two PV benchmark-return scatter charts.
4. **Rolling Active series are incorrectly concatenated.** Local appends Provided rows then Optimized rows and renders one Active/Tracking Error path, creating a cross-portfolio discontinuity and losing portfolio identity. PV has separate Provided and Maximum Sharpe charts, each with Active Return and Tracking Error on distinct axes.
5. **Active Return Contribution mixes portfolios.** Local concatenates Provided/Optimized observations into the same ticker paths. PV renders two separate charts by portfolio. Split presentation series/charts and retain ticker contribution tooltips.

### P1: presentation fidelity

6. **Unit-aware rounding is absent in tables.** Local table cells expose full precision (for example optimized QQQ `22.00998358546105`), while PV uses `22.01%`; correlation uses two decimals and Sharpe commonly three. Preserve full precision in CSV/result.json and format only in HTML. Recommended display: percent/balance generally 2 decimals, correlation 2, Sharpe 3, counts/year/month integer, currency with separators. Do not round canonical artifacts.
7. **Balance convention is not presented like PV.** Local Performance Summary shows normalized `1` to `5.738...`; PV shows `$10,000` to `$49,841`. Either display `Growth of $10,000` with currency formatting or label the chart/table explicitly as normalized wealth. Tooltip and axis must use the same convention.
8. **Charts lack meaningful X ticks and axis titles.** Local Growth/Drawdown/Rolling charts expose only min/max Y labels; Annual Return lacks year labels. Use actual date/year/category scales, readable ticks, grid lines and chart-specific axis titles.
9. **Annual Asset Returns is grouped incorrectly.** Local has a single legend `return pct`, so assets are not identifiable by color/series. PV uses one series per ticker. Pivot presentation data by ticker and preserve ticker/name in legend and tooltip.
10. **Correlation views are raw tables, not heatmaps.** PV uses a fixed -1..1 color scale and two different matrices: frontier assets only, then assets + Provided/Optimized/Benchmark. Local repeats essentially the same raw table twice. Add heatmap presentation and enforce the intended matrix scope.
11. **Allocation charts are missing.** PV displays pie charts beside Provided and Optimized allocation tables. Local has tables only.
12. **Internal schema names leak into UI.** Local labels include `allocation pct`, `annualized 3y pct`, `monetary_initial_value_1`; PV uses human labels and objective-aware `Maximum Sharpe Ratio`. Add explicit per-section column schemas and dynamic portfolio names rather than generic snake_case conversion.

### P2: table/content completeness

13. Up/Down tables are missing PV's above/below benchmark counts, total, win rate and above/below/overall average active return.
14. Worst Drawdowns should be three separate tables (Provided, Optimized, Benchmark) with Start, End/Bottom, Length, Recovery By, Recovery Time, Underwater Period and Drawdown. Local combines portfolios and omits several duration meanings.
15. Portfolio Metrics should include Benchmark as a third comparison column and align metric names/units/order with PV Risk and Return Metrics.
16. Monthly/Annual return tables are reduced. PV includes portfolio return + balance, benchmark and asset returns; local Monthly Returns is portfolio-calendar-only and does not show balance or asset columns.
17. `Efficient Frontier Assets` currently reuses the overly wide `asset_statistics` table instead of PV's focused Asset / Expected Return / Standard Deviation / Sharpe / Min / Max schema.
18. `Portfolio Asset Performance` also reuses `asset_statistics`, while PV separates Portfolio Assets statistics from trailing/expense-ratio Asset Performance. Build section-specific projectors rather than sharing the same table.
19. Return Decomposition should display currency attribution using the selected initial balance convention and human unit labels; local exposes `monetary_initial_value_1`.
20. Overview should show result period, objective explanation, benchmark, risk-free rate, rebalance convention and partial first/last-year note. PV also supplies metric/disclosure definitions.

### Recommended implementation order

1. Lock calculation contracts for Up/Down monthly semantics and missing breakdown columns.
2. Replace generic renderer usage with chart-specific Frontier, Transition, Rolling Active and Contribution renderers.
3. Add centralized unit-aware formatter and explicit table schemas; display-round only.
4. Add date/category axes, asset series, heatmaps, allocation pies and Up/Down scatters.
5. Add missing table projectors/columns and overview notes.
6. Extend contract tests to assert axis data keys, portfolio-series separation, marker presence, table schemas and display formatting. Do not weaken existing financial tests.

No implementation was performed in this comparison task. The current report has the 29-section skeleton and self-contained delivery boundary, but chart-specific semantic fidelity is not yet sufficient to call it PV-comparable.

### User follow-up clarifications

- **Chart tick/scale mismatch is an explicit defect, not merely styling.** PV shows semantic X ticks (year/month or Standard Deviation), meaningful Y tick intervals, axis titles and percentage/currency formatting. Local generic SVG charts generally show only Y min/max, omit date/year X ticks, force zero into ranges, and use row index as X. This can distort both readability and, for Frontier/Transition, the meaning of the chart. Each chart contract must assert the X data field, scale domain, tick formatter and axis title.
- **The sawtooth Active Return Contribution graph has a confirmed shaping cause.** Presentation points are ordered `(date, portfolio)`, so every date alternates `optimized` then `provided`. The renderer ignores `portfolio` when building ticker paths and connects all rows as one series. Each ticker therefore jumps between Optimized and Provided cumulative contribution on every date, producing the observed gear/sawtooth pattern. Split the data into independent portfolio panels/series before path generation; within each path sort strictly by date and never connect across portfolio identity.

### Published validation artifacts

- All generated validation outputs are already committed and present on remote `main` in run artifact commit `9ce4be3`.
- Complete run directory: `runs/20260829-0001/` (79 tracked files).
- Interactive HTML: `runs/20260829-0001/report.html`.
- Human-review CSVs: `runs/20260829-0001/review/*.csv`.
- Full-precision source CSVs: `runs/20260829-0001/raw/*.csv`.
- Root compatibility CSVs and canonical `result.json`, `input.yaml`, `context.yaml`, `README.md` are also included in the same run directory.
- GitHub paths:
  - `https://github.com/comus93/portfolio-optimizer-kr/tree/main/runs/20260829-0001`
  - `https://github.com/comus93/portfolio-optimizer-kr/blob/main/runs/20260829-0001/report.html`
  - `https://github.com/comus93/portfolio-optimizer-kr/tree/main/runs/20260829-0001/review`
  - `https://github.com/comus93/portfolio-optimizer-kr/tree/main/runs/20260829-0001/raw`
