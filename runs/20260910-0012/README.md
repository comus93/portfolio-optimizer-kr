# Provided Portfolio v1 - AIA + SCHD Maximum Sharpe Same Period

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260910-0012` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `005-aia-schd-max-sharpe-same-period` |
| Period | 2017-09-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-10 |

## Purpose

Compare the AIA + SCHD seven-asset universe against the prior 277540 six-asset Maximum Sharpe run on the identical 2017-09 through 2026-08 sample, isolating universe-composition effects from sample-period effects.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 144600 5%, AIA 15%, GLD 15%, QQQ 20%, SCHD 10%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 144600 0%, AIA 0%, GLD 47.77%, QQQ 16.5%, SCHD 2.71%, SPMO 28.06%, XLE 4.95% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 19.94% | 19.21% | 19.21% | 13.40% | -15.67% | 1.147 | 1.886 |
| optimized | 20.46% | 19.42% | 19.42% | 11.60% | -11.36% | 1.344 | 2.414 |
| benchmark | 17.88% | 17.69% | 17.69% | 15.06% | -17.41% | 0.919 | 1.466 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0012/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
