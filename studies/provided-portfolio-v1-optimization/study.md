# Provided Portfolio v1 Optimization Study

사용자와 대화를 통해 정의한 장기 포트폴리오 초안을 동일 자산군 안에서 최적화한다.

## Baseline portfolio

| Code / Ticker | Asset | Provided weight |
|---|---|---:|
| `QQQ` | Invesco QQQ Trust | 30% |
| `SPMO` | Invesco S&P 500 Momentum ETF | 20% |
| `277540` | ACE 아시아TOP50 | 15% |
| `GLD` | SPDR Gold Shares | 15% |
| `XLE` | State Street Energy Select Sector SPDR ETF | 15% |
| `144600` | KODEX 은선물(H) | 5% |
| **Total** |  | **100%** |

## Common experiment conditions

- Product: Optimization
- Analysis period: 2017-09-01 through 2026-08-31
- Portfolio rebalancing: monthly
- Long-only, fully invested
- Asset bounds: 0% to 100% unless an experiment explicitly overrides them
- Reporting currency: KRW; USD assets follow the shared USD/KRW conversion rule
- Research Frontend risk-free and benchmark defaults are materialized into persisted run input

## Research questions

1. What allocation maximizes ex-ante Sharpe ratio over the common historical sample?
2. What allocation maximizes expected return subject to annualized standard deviation <= 10.0%?

The provided 30/20/15/15/15/5 allocation is the baseline for historical comparison, not an optimization constraint.
