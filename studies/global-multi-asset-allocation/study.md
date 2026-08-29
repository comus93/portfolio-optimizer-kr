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
- Run: pending first execution

## Observed Facts

Pending first persisted run.

## Interpretation

Pending GPT + user review.

## Current Conclusion

Pending.

## Follow-up

첫 run의 Data Validity Gate와 Efficient Frontier를 확인한 뒤, 현재 결론을 가장 크게 바꿀 수 있는 불확실성부터 후속 검증을 정한다.
