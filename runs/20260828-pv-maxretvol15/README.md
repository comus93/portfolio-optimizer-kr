# Optimization run: Provided Portfolio vs Optimized Portfolio

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260828-pv-maxretvol15` |
| Product | Optimization |
| Study | `N/A` |
| Experiment | `N/A` |
| Period | 2016-08-01 ~ 2026-07-31 |
| Benchmark | SPY |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-08-28 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | AIA 15%, GDX 10%, GLD 0%, PTF 10%, QLD 10%, QQQ 20%, SLV 10%, SPMO 10%, XLE 15% |
| Optimized Portfolio | AIA 0%, GDX 0%, GLD 30%, PTF 0%, QLD 9.87%, QQQ 13.15%, SLV 0%, SPMO 45%, XLE 1.98% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 19.18% | 19.40% | 19.40% | 18.73% | -24.62% | 0.91 | 1.549 |
| optimized | 19.26% | 18.85% | 18.85% | 15.00% | -22.67% | 1.099 | 1.937 |
| benchmark | 14.90% | 15.14% | 15.14% | 15.33% | -23.93% | 0.833 | 1.313 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Input](input.yaml)
- [Result](result.json)
- [Raw tables](raw/)
- [Review tables](review/)
