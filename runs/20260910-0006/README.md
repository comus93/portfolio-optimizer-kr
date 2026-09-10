# Provided Portfolio v1 - Maximum Sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260910-0006` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `001-max-sharpe` |
| Period | 2017-09-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-10 |

## Purpose

Optimize the provided six-asset portfolio for maximum ex-ante Sharpe ratio over 2017-09 through 2026-08.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 144600 5%, 277540 15%, GLD 15%, QQQ 30%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 144600 0%, 277540 0%, GLD 48.39%, QQQ 17.04%, SPMO 28.8%, XLE 5.77% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 20.56% | 19.80% | 19.80% | 13.93% | -15.29% | 1.146 | 1.905 |
| optimized | 20.58% | 19.54% | 19.54% | 11.69% | -11.52% | 1.343 | 2.412 |
| benchmark | 17.88% | 17.69% | 17.69% | 15.06% | -17.41% | 0.919 | 1.466 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr//home/runner/work/portfolio-optimizer-kr/portfolio-optimizer-kr/runs/20260910-0006/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
