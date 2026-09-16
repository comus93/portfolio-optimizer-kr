## ADDED Requirements

### Requirement: LOYO Asset-Year Influence projection reuses existing results
Default Optimization LOYO output은 이미 계산된 annual asset returns, baseline optimized weights와 LOYO scenario asset weights/deltas를 결합한 Asset-Year Influence projection을 제공해야 한다(MUST).

Projection 생성을 위해 annual asset return, baseline optimization 또는 LOYO optimization을 다시 계산해서는 안 된다(MUST NOT).

각 feasible `year × asset` observation은 최소 다음 의미를 보존해야 한다(MUST).

```text
calendar year
asset identity
asset annual realized return for that year
full-sample baseline optimized weight
optimized weight after excluding that year
signed weight delta vs baseline
```

Asset-Year Influence는 causal attribution 또는 corner-solution 자동 판정이 아니라 LOYO sensitivity와 같은 진단 evidence여야 한다(MUST NOT 자동 판정).

#### Scenario: 2022 QQQ projection
- GIVEN annual asset return, baseline QQQ weight와 2022-excluded LOYO QQQ weight/delta가 이미 존재한다
- WHEN Asset-Year Influence projection을 생성한다
- THEN 기존 값들을 그대로 결합하고 optimizer 또는 annual-return calculation을 다시 실행하지 않는다

#### Scenario: infeasible LOYO year
- GIVEN 특정 excluded year가 infeasible 또는 insufficient-data 상태다
- WHEN Asset-Year Influence projection을 생성한다
- THEN asset annual return과 baseline weight는 보존할 수 있고 LOYO weight/delta는 unavailable 의미를 유지하며 임의의 0으로 채우지 않는다

### Requirement: Asset-Year Influence artifact persistence
Default Optimization persisted run은 Asset-Year Influence projection을 `asset_year_influence.csv`로 raw/review layer에 제공해야 한다(MUST).

Raw layer는 return/weight를 decimal unit으로 보존하고 review layer는 사용자/LLM inspect를 위한 percentage-point unit으로 변환해야 한다(MUST).

#### Scenario: raw and review units
- GIVEN raw QQQ annual return이 `-0.2782`이고 baseline weight가 `0.3106`이다
- WHEN run artifact를 persist한다
- THEN raw artifact는 decimal 값을 보존하고 review artifact는 각각 약 `-27.82`, `31.06` percentage-point 값으로 표현한다
