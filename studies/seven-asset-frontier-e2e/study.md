# Seven-Asset Frontier E2E Study

## Research Question

현재 제공 포트폴리오를 기준으로 QQQ, SPMO, GDX, GLD, SLV, AIA, XLE 각 자산이 Efficient Frontier 전체에서 어떤 한계 효용과 역할을 제공하는가?

특히 다음을 확인한다.

- Maximum Sharpe 한 점보다 frontier 전체에서 각 자산의 allocation trajectory가 어떻게 나타나는가?
- 후보 자산이 기존 자산을 대체하는지, 독립적인 역할을 추가하는지?
- Sharpe-Return plateau가 존재하는지?
- min/max constraint에 의해 allocation이 제한되는 구간이 있는지?
- 제공 포트폴리오 대비 optimized portfolio가 위험/수익/Sharpe/Drawdown/Contribution 측면에서 어떻게 달라지는지?

## Background / Hypothesis

첫 정식 Research Interaction Layer E2E 연구다.

사용자가 확정한 실행 조건은 다음과 같다.

- Optimization objective: Maximum Sharpe
- Rebalancing: Monthly
- Analysis period: QQQ, SPMO, GDX, GLD, SLV, AIA, XLE 7개 자산의 실제 데이터가 모두 존재하는 공통 교집합 전체 기간
- Benchmark: SPY
- Efficient Frontier: 100 points
- Risk-free: U.S. 3-Month Treasury Bill (`us_3m_tbill`)

가설은 미리 KEEP/DROP을 정하지 않는다. 각 자산의 단독 성과가 아니라 portfolio marginal utility와 frontier 상의 지속적 역할을 중심으로 판정한다.

## Provided Portfolio

| Asset | Weight | Min | Max |
|---|---:|---:|---:|
| QQQ | 40% | 0% | 50% |
| SPMO | 10% | 0% | 50% |
| GDX | 10% | 0% | 30% |
| GLD | 0% | 0% | 30% |
| SLV | 10% | 0% | 30% |
| AIA | 15% | 0% | 30% |
| XLE | 15% | 0% | 30% |

Total = 100%.

## Experiment / Run References

- Draft experiment, not executed: `experiments/001-base-r01.yaml`
- Confirmed experiment: `experiments/001-base-r02.yaml`
- Run: pending

## Observed Facts

Pending first persisted E2E run.

## Interpretation

Pending GPT + user review of the first persisted run.

## Current Conclusion

Pending.

## Follow-up

After the first run, inspect Efficient Frontier first and derive the next sensitivity experiment from the observed uncertainty rather than predefining a batch.
