# Interactive Report P0 Validation

Validation date: 2026-08-29

## Inputs

- Run ID: `20260829-p0-final-validation`
- Analysis period: `2016-08-01` through `2026-07-31`
- Objective: Maximum Sharpe Ratio
- Rebalancing: Monthly
- Benchmark: SPY
- Risk-free: fixed 2.35595% annual
- Command: `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r03-p0-validation.yaml`

## Automated Validation

- `uv run pytest tests/test_interactive_report_contract.py tests/test_report_presentation_upstream.py -q`: PASS (16 passed)
- `uv run pytest -q`: PASS (92 passed)

## Artifact Checks

- `report.html` is generated and self-contained.
- `review/frontier_landmarks.csv` supplies provided, optimized, and benchmark coordinates in optimizer risk/return space.
- `review/up_down_market_scatter.csv` supplies aligned monthly observations for both portfolios.
- `review/up_down_market_performance.csv` supplies percentage-point active-return fields.

## PV Live / Static Golden Comparison

PV live reference was opened and executed with its linked configuration. It reports the same period (Aug 2016 through Jul 2026), asset inputs, bounds, SPY benchmark, and Maximum Sharpe objective. Its optimized allocation is directionally aligned with this FDR run: QQQ about 24.9%, SPMO about 40.6%, GLD 30.0%, and XLE about 4.5%; the FDR run is QQQ 24.38%, SPMO 41.09%, GLD 30.0%, and XLE 4.53%.

The static Golden image was opened from the requested GitHub reference.

The browser policy blocks opening the local `file://` generated report. Therefore no visual claim requiring a rendered local report is marked PASS solely from this run; no workaround was attempted.

PV live comparison: PARTIAL (live reference inspected; local-report rendering blocked)

Static golden comparison: PARTIAL (static reference inspected; local-report rendering blocked)

P0 mismatches detected: 0

P1 mismatches: not assessed

## P0 Evidence From Contracts and Artifacts

- Efficient Frontier curve data and landmarks are distinct presentation inputs.
- Transition-map hover maps pointer X to nearest frontier volatility.
- Contribution and rolling-active data are partitioned by portfolio.
- Up/Down uses two monthly-observation scatter panels, not summary bars.
- Missing values are not coerced to zero by the renderer contract.
- Growth chart uses the `$10,000` display convention.

## Limitation

The required generated HTML and all source data are committed for independent browser review. The blocked `file://` browser policy is the only remaining validation limitation from this Agent run.
