## ADDED Requirements

### Requirement: No rebalancing path
`none` rebalancing은 첫 active period 시작 시 target weights를 적용한 뒤 이후 모든 monthly period에서 성과에 따라 weights가 drift하도록 계산해야 한다.

#### Scenario: no-rebalance drift
- GIVEN target weights와 monthly asset returns가 있다
- WHEN `none` rebalancing path를 생성한다
- THEN 첫 active period 이후 target weights로 강제 복귀하지 않고 canonical drift formula를 계속 적용한다

### Requirement: Calendar-aligned quarterly rebalancing
Calendar-aligned quarterly rebalancing은 첫 active period와 calendar quarter 시작월인 1월, 4월, 7월, 10월의 첫 available active monthly period에서 target weights로 복귀해야 한다.

#### Scenario: 2월 시작 quarterly backtest
- GIVEN analysis가 2월에 시작하고 calendar-aligned quarterly policy가 적용된다
- WHEN quarterly path를 생성한다
- THEN 2월 첫 active period에 target weights를 적용하고 다음 4월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Calendar-aligned semiannual rebalancing
Calendar-aligned semiannual rebalancing은 첫 active period와 1월, 7월의 첫 available active monthly period에서 target weights로 복귀해야 한다.

#### Scenario: 8월 시작 semiannual backtest
- GIVEN analysis가 8월에 시작하고 calendar-aligned semiannual policy가 적용된다
- WHEN semiannual path를 생성한다
- THEN 8월 첫 active period에 target weights를 적용하고 다음 1월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Calendar-aligned yearly rebalancing
Calendar-aligned yearly rebalancing은 첫 active period와 각 calendar year의 1월 첫 available active monthly period에서 target weights로 복귀해야 한다.

#### Scenario: 5월 시작 yearly backtest
- GIVEN analysis가 5월에 시작하고 calendar-aligned yearly policy가 적용된다
- WHEN yearly path를 생성한다
- THEN 5월 첫 active period에 target weights를 적용하고 다음 1월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Periodic rebalancing uses common drift semantics
Rebalance event 사이의 monthly periods에서는 existing canonical drift formula를 사용해야 한다.

#### Scenario: quarter 내부 drift
- GIVEN 1월에 rebalance한 quarterly portfolio가 있다
- WHEN 2월과 3월 return을 계산한다
- THEN 1월 이후 drifted weights를 순차 적용하고 다음 rebalance event에서만 target weights로 복귀한다

### Requirement: Initial-balance wealth path
Portfolio simulation은 positive initial balance와 canonical portfolio return series로 wealth path를 생성할 수 있어야 한다.

#### Scenario: cashflow 없는 wealth path
- GIVEN initial balance `B0`와 monthly portfolio returns `r_t`가 있다
- WHEN wealth path를 생성한다
- THEN cashflow가 없는 범위에서 `B_t = B_(t-1) * (1 + r_t)`로 계산한다

## Decision Pending

`Calendar Aligned = No`를 v1에서 지원한다면 quarterly/semiannual/yearly schedule을 첫 active month 기준으로 anchor할지 별도 semantics를 확정해야 한다. 또한 하나의 run에서 rebalancing setting을 모든 portfolio에 공통 적용할지 portfolio별로 독립 적용할지는 product decision 후 이 capability의 호출 contract에 반영한다.
