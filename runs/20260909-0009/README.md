# 006-core-max-sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0009` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `006-core-max-sharpe` |
| Period | 2021-11-01 ~ 2026-08-31 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-09-09 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | EEM 17%, EWJ 5%, EWY 8%, GLD 20%, QQQ 10%, SPY 10%, TLT 30% |
| Optimized Portfolio | EEM 0%, EWJ 0%, EWY 0%, GLD 55.08%, QQQ 0%, SPY 44.92%, TLT 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 12.11% | 12.23% | 12.23% | 12.19% | -16.58% | 0.688 | 1.009 |
| optimized | 21.69% | 20.39% | 20.39% | 11.10% | -11.12% | 1.492 | 2.684 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0009/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
