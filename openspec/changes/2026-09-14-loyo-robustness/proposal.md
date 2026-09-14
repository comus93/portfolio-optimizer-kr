# Proposal: Leave-One-Year-Out Optimization Robustness

## Why

Optimization 결과가 특정 calendar year의 성과에 과도하게 의존하면, 해당 자산의 우월성이 전체 표본에서 안정적인지 특정 연도에 의해 만들어진 것인지 구분하기 어렵다.

Start/end 기간 탐색은 사용자가 유리한 기간을 다시 선택하는 체리피킹 위험을 만들 수 있으므로, v1 robustness 진단은 기간 탐색이 아니라 각 연도를 하나씩 제거하는 Leave-One-Year-Out(LOYO) 방식으로 제한한다.

## Scope

Optimization run에 LOYO robustness 분석을 추가한다.

- canonical monthly returns와 기존 baseline optimized result를 재사용한다.
- 각 calendar year의 관측치를 하나씩 제거하고 같은 objective, bounds, target volatility, effective annual risk-free rate로 shared Optimization Core를 다시 실행한다.
- 각 scenario의 optimized weights와 ex-ante expected return, volatility, Sharpe를 baseline과 비교한다.
- allocation 변화는 baseline 대비 최소 재배분 비율(`0.5 * sum(abs(delta weights))`)과 최대 단일 asset weight 변화로 기록한다.
- 특정 연도 제거 후 objective가 infeasible하면 run 전체를 실패시키지 않고 해당 scenario를 infeasible로 기록한다.
- LOYO는 Efficient Frontier, portfolio path, historical analytics, benchmark analytics, report rendering을 연도별로 재실행하지 않는다.

## Non-goals

- start/end year matrix 또는 기간 탐색
- rolling-window 최적화
- 자동 overfitting/corner-solution 판정 점수
- LOYO 결과를 이용한 자동 asset 제거 또는 weight 수정
- Backtest product 적용

## OpenSpec impact

`portfolio-optimization` capability에 LOYO robustness 진단 requirement를 추가한다.

Shared finance semantics는 변경하지 않는다. LOYO는 기존 canonical monthly returns, annualized moments, solver objective/constraint semantics와 shared Optimization Core를 재사용한다.
