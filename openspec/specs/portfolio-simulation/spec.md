## Purpose

Provided/Optimized portfolio와 benchmark의 canonical historical monthly return/wealth path 및 기존 rebalancing convention을 정의한다.

## Requirements

### Requirement: Shared historical return matrix
Provided Portfolio와 Optimized Portfolio는 동일 canonical monthly asset return matrix를 사용해 historical path를 계산해야 한다(MUST).

#### Scenario: same run matrix
- GIVEN Provided와 Optimized weights가 서로 다르다
- WHEN historical paths를 계산한다
- THEN weights만 다르고 underlying monthly asset return observations는 동일하다

### Requirement: Monthly rebalancing
Monthly rebalancing은 매 active monthly period 시작 시 target weights로 rebalance한 것으로 계산해야 한다(MUST).

```text
portfolio_return_t = sum(target_weight_i * asset_return_i,t)
```

#### Scenario: monthly target reset
- GIVEN monthly rebalancing portfolio가 있다
- WHEN 두 번째 active month를 계산한다
- THEN 이전 month의 drifted weight가 아니라 target weight를 period-start weight로 사용한다

### Requirement: Yearly rebalancing
Yearly rebalancing은 첫 active period에 target weights를 적용하고 같은 calendar year 안에서는 weights가 realized return에 따라 drift해야 한다(MUST).

```text
portfolio_return_t = sum(weight_i,t * asset_return_i,t)
weight_i,t+1 = weight_i,t * (1 + asset_return_i,t) / (1 + portfolio_return_t)
```

새 calendar year의 첫 available active monthly period에서 target weights로 복귀해야 한다(MUST).

#### Scenario: mid-year analysis start
- GIVEN analysis가 5월에 시작하고 yearly rebalancing이다
- WHEN historical path를 계산한다
- THEN 5월 첫 active period에 target weights를 적용하고 같은 해에는 drift하며 다음 calendar year 첫 available active month에 target weights로 복귀한다

### Requirement: Single-asset benchmark path
Benchmark가 단일 asset이면 동일 base-currency convention의 canonical monthly return series를 benchmark historical path로 사용해야 한다(MUST).

#### Scenario: USD benchmark in KRW-base run
- GIVEN mixed-currency run에서 USD benchmark가 있다
- WHEN benchmark path를 생성한다
- THEN portfolio asset과 동일한 configured currency-normalization convention을 적용한다

### Requirement: Optimization statistics and historical path are separate
Ex-ante Optimization statistics와 realized historical portfolio return/wealth path는 별도 domain으로 계산하고 보존해야 한다(MUST).

#### Scenario: optimized portfolio historical path
- GIVEN optimized target weights가 생성되었다
- WHEN realized historical analytics를 계산한다
- THEN ex-ante expected return을 historical monthly return으로 사용하지 않고 canonical asset history와 rebalancing convention으로 path를 생성한다

### Requirement: Canonical normalized wealth baseline for Optimization history
기존 Optimization historical analytics의 canonical wealth는 `start_balance = 1.0`으로 시작해야 한다(MUST). Presentation layer는 기존 display convention에서 이를 $10,000 기준으로 표현할 수 있다(MAY).

#### Scenario: normalized historical path
- GIVEN portfolio monthly return series가 있다
- WHEN canonical Optimization wealth path를 생성한다
- THEN 첫 wealth 기준값은 1.0이며 이후 realized returns를 복리 적용한다
