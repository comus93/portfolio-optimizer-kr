## ADDED Requirements

### Requirement: Leave-One-Year-Out optimization robustness
Optimization run은 canonical monthly return sample에 대해 Leave-One-Year-Out(LOYO) robustness 진단을 제공해야 한다(MUST).

각 LOYO scenario는 하나의 calendar year에 속하는 monthly observations를 모두 제거한 뒤 baseline과 동일한 optimization objective, asset bounds, target volatility와 effective annual risk-free rate를 사용해 canonical optimization core를 다시 실행해야 한다(MUST).

Baseline optimized result는 LOYO를 위해 다시 solve하지 않아야 한다(MUST NOT).

#### Scenario: stable allocation under one-year removal
- GIVEN baseline Optimization result와 여러 calendar year의 canonical monthly returns가 있다
- WHEN 각 calendar year를 하나씩 제거해 LOYO를 실행한다
- THEN 각 feasible scenario의 optimized weights와 ex-ante statistics를 baseline과 비교할 수 있다

#### Scenario: partial calendar year
- GIVEN 분석 시작년 또는 종료년이 12개월 미만의 partial year다
- WHEN 해당 year의 LOYO scenario를 계산한다
- THEN 실제 포함된 monthly observations만 제거하고 removed observation count를 기록한다

### Requirement: LOYO allocation sensitivity
각 feasible LOYO scenario는 baseline 대비 asset별 weight 변화와 다음 allocation sensitivity를 제공해야 한다(MUST).

```text
allocation_turnover = 0.5 * sum(abs(loyo_weight_i - baseline_weight_i))
```

또한 최대 absolute weight change와 해당 asset identity를 보존해야 한다(MUST).

이 sensitivity를 자동 overfitting 또는 corner-solution 판정으로 변환해서는 안 된다(MUST NOT).

#### Scenario: one year materially changes allocation
- GIVEN 특정 year 제거 후 optimized allocation이 baseline과 크게 다르다
- WHEN LOYO result를 inspect한다
- THEN allocation turnover와 가장 크게 변한 asset/weight delta를 확인할 수 있다

### Requirement: LOYO objective sensitivity
각 feasible LOYO scenario는 optimized expected annual return, annualized volatility, ex-ante Sharpe와 baseline 대비 각 metric delta를 제공해야 한다(MUST).

#### Scenario: objective metrics change
- GIVEN 특정 year 제거가 expected return/covariance를 변화시킨다
- WHEN 동일 objective로 재최적화한다
- THEN LOYO scenario와 baseline의 ex-ante metric 차이를 확인할 수 있다

### Requirement: LOYO infeasibility is diagnostic evidence
특정 year 제거 후 canonical optimization objective가 infeasible하면 해당 scenario를 infeasible로 기록하고 다른 LOYO scenario와 baseline run은 보존해야 한다(MUST).

LOYO scenario infeasibility를 이유로 정상 baseline Optimization run 전체를 실패시켜서는 안 된다(MUST NOT).

#### Scenario: target volatility becomes infeasible
- GIVEN baseline target-volatility run은 feasible하다
- AND 한 calendar year 제거 후 constrained GMV volatility가 target을 초과한다
- WHEN LOYO를 실행한다
- THEN 해당 year scenario는 infeasible로 기록되고 나머지 robustness result는 계속 생성된다

### Requirement: LOYO uses lightweight repeated optimization
LOYO는 각 year마다 market-data acquisition, canonical FX/return preparation, Efficient Frontier generation, portfolio path simulation, historical/benchmark analytics 또는 report rendering을 반복해서는 안 된다(MUST NOT).

LOYO는 prepared canonical monthly returns와 기존 shared optimization objective-solving boundary를 재사용해야 한다(MUST).

#### Scenario: repeated robustness execution
- GIVEN N개의 calendar year가 있는 Optimization sample이다
- WHEN LOYO를 실행한다
- THEN baseline full analysis를 N회 재실행하지 않고 year-excluded moments와 objective solve만 반복한다
