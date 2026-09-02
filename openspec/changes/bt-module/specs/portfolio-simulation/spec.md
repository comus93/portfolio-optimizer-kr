## ADDED Requirements

### Requirement: No rebalancing path
`none` rebalancing은 첫 active period 시작 시 target weights를 적용한 뒤 이후 모든 monthly period에서 성과에 따라 weights가 drift하도록 계산해야 한다.

#### Scenario: no-rebalance drift
- GIVEN target weights와 monthly asset returns가 있다
- WHEN `none` rebalancing path를 생성한다
- THEN 첫 active period 이후 target weights로 강제 복귀하지 않고 canonical drift formula를 계속 적용한다

### Requirement: Quarterly rebalancing
Quarterly rebalancing은 첫 active period와 calendar quarter 시작월인 1월, 4월, 7월, 10월의 첫 available active monthly period에서 target weights로 복귀해야 한다.

#### Scenario: 2월 시작 quarterly backtest
- GIVEN analysis가 2월에 시작한다
- WHEN quarterly path를 생성한다
- THEN 2월 첫 active period에 target weights를 적용하고 다음 4월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Semiannual rebalancing
Semiannual rebalancing은 첫 active period와 1월, 7월의 첫 available active monthly period에서 target weights로 복귀해야 한다.

#### Scenario: 8월 시작 semiannual backtest
- GIVEN analysis가 8월에 시작한다
- WHEN semiannual path를 생성한다
- THEN 8월 첫 active period에 target weights를 적용하고 다음 1월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Periodic rebalancing uses common drift semantics
Quarterly와 semiannual schedule 사이의 monthly periods에서는 existing canonical drift formula를 사용해야 한다.

#### Scenario: quarter 내부 drift
- GIVEN 1월에 rebalance한 quarterly portfolio가 있다
- WHEN 2월과 3월 return을 계산한다
- THEN 1월 이후 drifted weights를 순차 적용하고 4월에만 target weights로 복귀한다

### Requirement: Initial-balance wealth path
Portfolio simulation은 positive initial balance와 canonical portfolio return series로 wealth path를 생성할 수 있어야 한다.

#### Scenario: cashflow 없는 wealth path
- GIVEN initial balance `B0`와 monthly portfolio returns `r_t`가 있다
- WHEN wealth path를 생성한다
- THEN cashflow가 없는 범위에서 `B_t = B_(t-1) * (1 + r_t)`로 계산한다

### Requirement: Rebalancing policy is portfolio-specific
한 Backtest run 안의 각 portfolio는 독립적인 periodic rebalancing policy를 가질 수 있어야 한다.

#### Scenario: monthly와 yearly 비교
- GIVEN Portfolio A는 monthly, Portfolio B는 yearly rebalancing을 사용한다
- WHEN 동일 market return matrix에서 simulation한다
- THEN 각 portfolio는 자신의 schedule에 따라 독립적인 weight와 return path를 생성한다
