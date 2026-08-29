# U.S. 3-Month T-Bill runtime and report-series contrast evidence

## Execution

- Run command: `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r11-us3m-tbill-validation.yaml`
- Run ID: `20260829-us3m-tbill-validation`
- Report HTTP URL: `http://localhost:8000/runs/20260829-us3m-tbill-validation/report.html`
- GitHub Pages URL: `https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-us3m-tbill-validation/report.html`
- Targeted tests: `uv run pytest tests/test_runner.py tests/test_report_series_contrast.py -q`
- Result: **6 passed**.

## RF runtime evidence

The run used `risk_free.mode: us_3m_tbill`.

| Field | Actual value |
| --- | --- |
| Source | FDR `FRED:TB3MS` |
| Required / used months | 120 |
| First month | 2016-08, TB3MS 0.30% |
| Last month | 2026-07, TB3MS 3.73% |
| Arithmetic mean quoted annual rate | 2.37350% |
| Persisted effective annual RF | 2.37350% (`0.023735`) |
| Difference from former 2.35595% calibration | +0.01755 percentage points |

## Optimized result and PV numerical context

| Field | Local FDR / TB3MS | PV live | Local minus PV |
| --- | ---: | ---: | ---: |
| Expected return | 17.20583% | 17.19% | +0.01583%p |
| Volatility | 13.10305% | 13.08% | +0.02305%p |
| Ex-ante Sharpe | 1.13198 | 1.134 | -0.00202 |
| QQQ weight | 24.39765% | 24.21% | +0.18765%p |
| SPMO weight | 41.08251% | 40.86% | +0.22251%p |
| GLD weight | 30.00000% | 30.00% | 0.00000%p |
| XLE weight | 4.51983% | 4.94% | -0.42017%p |

PV reference was opened live at `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5`; its maximum-Sharpe row was portfolio #26. The local up/down benchmark-month count is 84 positive / 36 negative; the known PV 85/35 difference remains July 2026 local FDR SPY -0.68027% versus PV +0.03%.

## Browser color evidence

The report was opened over localhost HTTP. The browser DOM showed the following actual marks and computed legend pseudo-element colors. In every target section, first portfolio series is blue `#2563eb` and the second is green `#22c55e`.

| Section | First series | Second series | Second legend color |
| --- | --- | --- | --- |
| Portfolio Growth | polyline `stroke=#2563eb` | polyline `stroke=#22c55e` | `rgb(34, 197, 94)` |
| Annual Returns | rect `fill=#2563eb` | rect `fill=#22c55e` | `rgb(34, 197, 94)` |
| Annualized Active Return | rect `fill=#2563eb` | rect `fill=#22c55e` | `rgb(34, 197, 94)` |
| Drawdowns | polyline `stroke=#2563eb` | polyline `stroke=#22c55e` | `rgb(34, 197, 94)` |
| Rolling 3Y Returns | polyline `stroke=#2563eb` | polyline `stroke=#22c55e` | `rgb(34, 197, 94)` |
| Rolling 5Y Returns | polyline `stroke=#2563eb` | polyline `stroke=#22c55e` | `rgb(34, 197, 94)` |

No screen blocker occurred during browser validation.
