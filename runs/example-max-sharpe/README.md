# Optimization run: Provided Portfolio vs Optimized Portfolio

## Metadata

| Field | Value |
|---|---|
| Run ID | `example-max-sharpe` |
| Product | Optimization |
| Study | `N/A` |
| Experiment | `N/A` |
| Period | 2019-01-01 ~ 2025-12-31 |
| Benchmark | SPY |
| Rebalancing | monthly |
| Currency | USD |
| Created | N/A |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | GLD 50%, QQQ 50% |
| Optimized Portfolio | GLD 60.39%, QQQ 39.61% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 21.38% | 20.38% | 20.38% | 13.17% | -21.18% | 1.395 | 2.599 |
| optimized | 20.91% | 19.92% | 19.92% | 12.64% | -18.78% | 1.418 | 2.766 |
| benchmark | 17.31% | 17.43% | 17.43% | 16.57% | -23.93% | 0.931 | 1.488 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Input](input.yaml)
- [Result](result.json)
- [Raw tables](raw/)
- [Review tables](review/)
