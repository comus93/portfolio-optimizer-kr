## Purpose

Target weights와 asset return series로부터 historical portfolio path를 생성하는 공통 simulation behavior를 정의한다.

## ADDED Requirements

### Requirement: Common simulation input
Portfolio simulation은 target asset weights와 해당 asset들의 canonical monthly return matrix를 입력으로 사용해야 한다.

#### Scenario: target weights 적용
- GIVEN asset별 target weights와 monthly return matrix가 있다
- WHEN historical portfolio path를 생성한다
- THEN 동일한 asset return observations를 기준으로 portfolio return series를 만든다

### Requirement: Default rebalancing period
사용자가 rebalancing period를 별도로 지정하지 않으면 Monthly를 기본값으로 사용해야 한다.

#### Scenario: 기본 rebalancing
- GIVEN rebalancing period가 생략된 유효한 run configuration이 있다
- WHEN effective simulation configuration을 확정한다
- THEN Monthly rebalancing을 적용한다

### Requirement: Monthly rebalancing
Monthly rebalancing에서는 각 monthly period 시작 시 target weights로 복귀한 것으로 계산해야 한다.

#### Scenario: 월별 rebalance return
- GIVEN target weights와 한 달의 asset returns가 있다
- WHEN monthly rebalancing portfolio return을 계산한다
- THEN `portfolio_return_t = sum(target_weight_i * asset_return_i,t)`를 사용한다

### Requirement: Yearly rebalancing
Yearly rebalancing에서는 첫 active period와 새 calendar year의 첫 available monthly period에 target weights를 적용하고 같은 calendar year 내부에서는 weights가 drift해야 한다.

#### Scenario: 연중 weight drift
- GIVEN annual rebalancing portfolio가 한 calendar year 안에서 여러 monthly periods를 가진다
- WHEN 첫 period 이후 다음 monthly return을 계산한다
- THEN 직전 period 성과를 반영한 drifted weights를 사용한다

#### Scenario: 새해 rebalance
- GIVEN annual rebalancing portfolio가 새 calendar year에 진입한다
- WHEN 해당 연도의 첫 available monthly period를 계산한다
- THEN target weights로 다시 rebalance한다

### Requirement: Drift update formula
Yearly rebalancing의 drifted weight는 `weight_i,t+1 = weight_i,t * (1 + asset_return_i,t) / (1 + portfolio_return_t)`로 계산해야 한다.

#### Scenario: drifted weights 합
- GIVEN 유효한 long-only weights와 asset returns가 있다
- WHEN drift update를 수행한다
- THEN 다음 period weights는 canonical drift formula를 따르며 합이 1로 유지된다

### Requirement: Mid-year analysis start
Analysis period가 calendar year 중간에 시작하면 첫 active period에서 target weights를 적용하고 다음 calendar year부터 정상 annual schedule을 따라야 한다.

#### Scenario: 8월 시작 annual rebalance
- GIVEN analysis가 8월부터 시작한다
- WHEN yearly rebalancing path를 생성한다
- THEN 8월 첫 active period에는 target weights를 적용하고 다음 1월 첫 available period에 다시 target weights를 적용한다

### Requirement: Portfolio path identity
서로 다른 portfolio는 동일 asset return matrix를 사용할 수 있어도 각자의 target weights와 rebalancing schedule에 따라 독립된 return/weight path를 가져야 한다.

#### Scenario: Provided와 Optimized 비교
- GIVEN Provided와 Optimized portfolio가 동일한 monthly asset return matrix를 사용한다
- WHEN historical paths를 생성한다
- THEN 각 portfolio의 weights와 returns는 서로 독립적으로 계산된다

### Requirement: Benchmark return path
Benchmark가 단일 asset이면 동일 base-currency convention의 canonical monthly return series를 benchmark path로 사용해야 한다.

#### Scenario: SPY benchmark
- GIVEN benchmark asset의 common-base monthly return series가 있다
- WHEN benchmark path를 생성한다
- THEN 별도 portfolio rebalancing 없이 해당 canonical return series를 사용한다
