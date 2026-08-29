# Global Multi-Asset Allocation Study

## Research Question

SPY, QQQ, TLT, GLD, CPER, MCHI, EWY로 구성된 글로벌 멀티자산 포트폴리오에서 각 자산이 Efficient Frontier 전체에서 어떤 역할과 한계 효용을 제공하며, 변동성 대비 기대수익이 가장 좋은 조합은 무엇인가?

특히 다음을 확인한다.

- 현재 Provided Portfolio가 Efficient Frontier 대비 얼마나 효율적인가?
- SPY와 QQQ는 서로 대체 관계인지, 함께 의미 있는 역할을 유지하는지?
- TLT와 GLD는 서로 다른 방어/분산 역할을 제공하는지?
- CPER가 원자재 분산 효과를 실제 포트폴리오 수준에서 제공하는지?
- MCHI와 EWY가 미국 주식과 다른 지역 분산 역할을 제공하는지?
- 각 자산이 어느 위험 구간에서 등장하거나 퇴출하고, 비중 상한에 막히는 구간이 있는지?
- Maximum Sharpe 한 점보다 near-optimal plateau에서 어떤 allocation range가 견고한지?

## Provided Portfolio

| Asset | Weight | Min | Max |
|---|---:|---:|---:|
| SPY | 20% | 0% | 50% |
| QQQ | 30% | 0% | 50% |
| TLT | 10% | 0% | 50% |
| GLD | 10% | 0% | 50% |
| CPER | 10% | 0% | 50% |
| MCHI | 10% | 0% | 50% |
| EWY | 10% | 0% | 50% |

Total = 100%.

## Execution Policy

- Optimization goal: 변동성 대비 기대수익이 가장 좋은 조합 (Maximum Sharpe)
- Analysis period: 별도 기간 지정 없음. 모든 optimization asset의 유효 데이터 공통 교집합 전체 기간
- Rebalancing: project canonical default
- Risk-free: project canonical default
- Internal implementation parameters follow the project specification and are not user research decisions.

## Experiment / Run References

- Experiment: `experiments/001-spy-qqq-tlt-gld-cper-mchi-ewy.yaml`
- First persisted Run: `runs/20260829-0003/`

## Observed Facts

First persisted run facts:

- Effective monthly-return coverage: 2011-12-31 through 2026-07-31, 176 observations.
- CPER price history begins 2011-11-15 and is the limiting asset for the common-period start.
- Maximum-Sharpe allocation: SPY 31.3955%, QQQ 50.0000%, GLD 18.6045%; TLT, CPER, MCHI, EWY 0%.
- QQQ is binding at its user-defined 50% maximum weight.
- Provided Portfolio: Expected Return 12.0392%, Volatility 12.7270%, Sharpe 0.8167.
- Optimized Portfolio: Expected Return 15.7275%, Volatility 13.4863%, Sharpe 1.0442.
- Historical CAGR: Provided 11.8360%, Optimized 15.8794%.
- Maximum Drawdown: Provided -27.7459%, Optimized -25.6321%.

## Interpretation

Pending GPT + user discussion. Initial interpretation is not yet a confirmed Study conclusion.

## Current Conclusion

Pending.

## Follow-up

Review the first run with the user using the LLM analysis framework. Prioritize sensitivity around the binding QQQ cap and any role claims that depend strongly on the 2011-2026 common sample.
