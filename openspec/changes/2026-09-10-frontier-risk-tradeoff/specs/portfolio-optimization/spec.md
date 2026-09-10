## ADDED Requirements

### Requirement: Efficient Frontier realized risk overlay
Optimization Efficient Frontier의 각 point는 기존 ex-ante statistics/weights를 보존한 채 동일 canonical monthly asset-return sample과 portfolio rebalancing convention을 사용한 realized risk overlay를 계산할 수 있어야 한다(MUST).

Overlay는 최소 다음 field를 포함해야 한다.

- ex-ante Sharpe Ratio
- realized ex-post Sharpe Ratio
- Maximum Drawdown
- MDD depth (positive magnitude)
- Time Under Water percentage
- Pain Area in percentage-point months
- Pain Index percentage
- Maximum consecutive underwater months

#### Scenario: overlay preserves solver frontier
- GIVEN 기존 100-point Efficient Frontier가 있다
- WHEN realized risk overlay를 계산한다
- THEN 기존 point identity, expected return, volatility, ex-ante Sharpe와 weights를 변경하지 않는다

### Requirement: Frontier marginal diagnostics are descriptive only
Frontier point order에서 이전 point 대비 delta를 계산할 수 있어야 한다(MUST).

```text
delta_sharpe = ex_post_sharpe_i - ex_post_sharpe_(i-1)
delta_mdd_depth_pct = mdd_depth_pct_i - mdd_depth_pct_(i-1)
delta_tuw_pct = tuw_pct_i - tuw_pct_(i-1)
delta_pain_index_pct = pain_index_pct_i - pain_index_pct_(i-1)
```

Sharpe가 증가하는 interval에서는 비교 편의를 위해 Sharpe +0.10당 local marginal cost를 계산할 수 있다(MAY).

```text
mdd_cost_per_0_10_sharpe = delta_mdd_depth_pct / delta_sharpe * 0.10
tuw_cost_per_0_10_sharpe = delta_tuw_pct / delta_sharpe * 0.10
pain_cost_per_0_10_sharpe = delta_pain_index_pct / delta_sharpe * 0.10
```

`delta_sharpe <= epsilon`인 interval은 cost ratio를 유효한 decision metric으로 만들어서는 안 된다(MUST NOT).

이 change는 해당 diagnostics로 sweet spot을 자동 선택해서는 안 된다(MUST NOT).

#### Scenario: post-Max-Sharpe interval
- GIVEN frontier point 순서상 ex-post Sharpe가 이전 point보다 감소한다
- WHEN marginal diagnostics를 생성한다
- THEN raw deltas는 보존하되 Sharpe +0.10 cost ratio는 unavailable로 처리한다
