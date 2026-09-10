# Optimization run: Provided Portfolio vs Optimized Portfolio

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260829-p0-final-validation` |
| Product | Optimization |
| Study | `N/A` |
| Experiment | `N/A` |
| Period | 2016-08-01 ~ 2026-07-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-08-29 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | AIA 15%, GDX 10%, GLD 0%, QQQ 40%, SLV 10%, SPMO 10%, XLE 15% |
| Optimized Portfolio | AIA 0%, GDX 0%, GLD 30%, QQQ 24.38%, SLV 0%, SPMO 41.09%, XLE 4.53% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 17.40% | 17.48% | 17.48% | 16.48% | -22.48% | 0.918 | 1.56 |
| optimized | 17.65% | 17.21% | 17.21% | 13.10% | -18.30% | 1.133 | 2.005 |
| benchmark | 14.90% | 15.14% | 15.14% | 15.33% | -23.93% | 0.834 | 1.313 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-p0-final-validation/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Raw tables](raw/)
- [Review tables](review/)
- [Validation](validation/)
