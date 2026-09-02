## ADDED Requirements

### Requirement: No rebalancing path
`none` rebalancing은 첫 active period 시작 시 target weights를 적용한 뒤 이후 모든 monthly period에서 성과에 따라 weights가 drift하도록 계산해야 한다(MUST).

#### Scenario: no-rebalance drift
- GIVEN target weights와 monthly asset returns가 있다
- WHEN `none` rebalancing path를 생성한다
- THEN 첫 active period 이후 target weights로 강제 복귀하지 않고 canonical drift formula를 계속 적용한다

### Requirement: Calendar-aligned quarterly rebalancing
`Calendar Aligned = Yes`인 quarterly rebalancing은 첫 active period와 calendar quarter 시작월인 1월, 4월, 7월, 10월의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 2월 시작 quarterly backtest
- GIVEN analysis가 2월에 시작하고 Calendar Aligned가 Yes이다
- WHEN quarterly path를 생성한다
- THEN 2월 첫 active period에 target weights를 적용하고 다음 4월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Calendar-aligned semiannual rebalancing
`Calendar Aligned = Yes`인 semiannual rebalancing은 첫 active period와 1월, 7월의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 8월 시작 semiannual backtest
- GIVEN analysis가 8월에 시작하고 Calendar Aligned가 Yes이다
- WHEN semiannual path를 생성한다
- THEN 8월 첫 active period에 target weights를 적용하고 다음 1월 첫 available active period에 다시 target weights를 적용한다

### Requirement: Calendar-aligned yearly rebalancing
`Calendar Aligned = Yes`인 yearly rebalancing은 첫 active period와 각 calendar year의 1월 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 5월 시작 yearly backtest
- GIVEN analysis가 5월에 시작하고 Calendar Aligned가 Yes이다
- WHEN yearly path를 생성한다
- THEN 5월 첫 active period에 target weights를 적용하고 다음 1월 첫 available active period에 다시 target weights를 적용한다

### Requirement: First-active-month anchored quarterly rebalancing
`Calendar Aligned = No`인 quarterly rebalancing은 첫 active month를 anchor로 하여 이후 3개월 간격의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 2월 시작 non-calendar quarterly backtest
- GIVEN 첫 active month가 2월이고 Calendar Aligned가 No이다
- WHEN quarterly path를 생성한다
- THEN 2월에 target weights를 적용하고 이후 5월, 8월, 11월처럼 3개월 간격의 available period에서 rebalance한다

### Requirement: First-active-month anchored semiannual rebalancing
`Calendar Aligned = No`인 semiannual rebalancing은 첫 active month를 anchor로 하여 이후 6개월 간격의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 8월 시작 non-calendar semiannual backtest
- GIVEN 첫 active month가 8월이고 Calendar Aligned가 No이다
- WHEN semiannual path를 생성한다
- THEN 8월에 target weights를 적용하고 이후 6개월 간격의 available period에서 rebalance한다

### Requirement: First-active-month anchored yearly rebalancing
`Calendar Aligned = No`인 yearly rebalancing은 첫 active month를 anchor로 하여 이후 12개월 간격의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: 5월 시작 non-calendar yearly backtest
- GIVEN 첫 active month가 5월이고 Calendar Aligned가 No이다
- WHEN yearly path를 생성한다
- THEN 5월에 target weights를 적용하고 이후 매 12개월 간격의 available period에서 rebalance한다

### Requirement: Monthly rebalancing is alignment-independent
Monthly rebalancing은 Calendar Aligned 설정과 무관하게 매 active monthly period 시작에 target weights로 복귀해야 한다(MUST).

#### Scenario: monthly with Calendar Aligned No
- GIVEN rebalancing이 monthly이고 Calendar Aligned가 No이다
- WHEN portfolio path를 생성한다
- THEN 모든 active month 시작에 target weights를 적용한다

### Requirement: No-rebalancing is alignment-independent
No rebalancing은 Calendar Aligned 설정과 무관하게 최초 target 적용 이후 계속 drift해야 한다(MUST).

#### Scenario: none with Calendar Aligned Yes
- GIVEN rebalancing이 none이고 Calendar Aligned가 Yes이다
- WHEN portfolio path를 생성한다
- THEN calendar boundary에서 추가 rebalance를 수행하지 않는다

### Requirement: Periodic rebalancing uses common drift semantics
Rebalance event 사이의 monthly periods에서는 existing canonical drift formula를 사용해야 한다(MUST).

#### Scenario: rebalance interval 내부 drift
- GIVEN 특정 rebalance event에서 target weights가 적용되었다
- WHEN 다음 rebalance event 전 monthly returns를 계산한다
- THEN drifted weights를 순차 적용하고 다음 event에서만 target weights로 복귀한다

### Requirement: Initial-balance wealth path
Portfolio simulation은 positive initial balance와 canonical portfolio return series로 wealth path를 생성할 수 있어야 한다(MUST).

#### Scenario: cashflow 없는 wealth path
- GIVEN initial balance `B0`와 monthly portfolio returns `r_t`가 있다
- WHEN wealth path를 생성한다
- THEN cashflow가 없는 범위에서 `B_t = B_(t-1) * (1 + r_t)`로 계산한다
