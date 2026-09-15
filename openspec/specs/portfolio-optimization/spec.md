## Purpose

`portfolio-optimizer-kr`의 기존 Optimization product가 제공하는 mean-variance optimization 입력, constraint, objective, Efficient Frontier와 product scope를 정의한다.

## Requirements

### Requirement: Optimization product scope
Optimization은 canonical monthly return/statistics를 사용해 long-only mean-variance portfolio research를 수행하고 optimized allocation과 Efficient Frontier를 생성할 수 있어야 한다(MUST).

v1 optimization objective는 Maximum Sharpe Ratio와 Maximum Return subject to Target Annual Volatility를 지원해야 한다(MUST). Sortino, CVaR, MDD, Risk Parity, Omega, Kelly를 optimization objective로 제공해서는 안 된다(MUST NOT). Black-Litterman, Monte Carlo, factor model, tax simulation, forecasting, robust/resampled optimization은 v1 scope가 아니다(MUST NOT).

#### Scenario: supported objective
- GIVEN 유효한 asset universe와 constraints가 있다
- WHEN Maximum Sharpe Ratio optimization을 요청한다
- THEN canonical optimization result와 Efficient Frontier를 생성할 수 있다

#### Scenario: unsupported objective
- GIVEN 사용자가 MDD 최소화를 optimization objective로 요청한다
- WHEN v1 canonical input을 검증한다
- THEN 지원되는 objective로 조용히 치환하지 않고 unsupported input으로 처리한다

### Requirement: Canonical Optimization input
Optimization의 canonical executable configuration은 YAML이어야 하며 최소 asset universe, analysis period, portfolio rebalancing period, optional provided portfolio weights, asset min/max weights, optional benchmark, optimization objective, target-vol objective일 때 target annual volatility, risk-free configuration과 frontier point count를 표현할 수 있어야 한다(MUST).

Interface가 CLI, UI 또는 Research Frontend여도 동일 YAML/request 의미론으로 수렴해야 한다(MUST).

#### Scenario: multiple input surfaces
- GIVEN 동일한 연구 조건을 CLI와 Research Frontend에서 입력한다
- WHEN canonical request를 생성한다
- THEN interface 차이 때문에 finance semantics가 달라지지 않는다

### Requirement: Optimization defaults
기존 Optimization baseline은 market-data source FDR, monthly return frequency, monthly portfolio rebalancing, 100 frontier points, `us_3m_tbill` risk-free mode를 기본으로 사용해야 한다(MUST).

Asset constraint 기본값은 `min_weight=0`, `max_weight=1`이어야 한다(MUST).

#### Scenario: optional settings omitted
- GIVEN 사용자가 frontier points와 asset bounds를 별도 지정하지 않았다
- WHEN Optimization input을 구성한다
- THEN 100 frontier points와 asset별 0~100% bounds를 사용한다

### Requirement: Long-only fully-invested constraints
Optimization portfolio는 long-only이고 fully invested여야 한다(MUST).

```text
sum(weights) = 1
weight_i >= min_weight_i
weight_i <= max_weight_i
weight_i >= 0
```

Constraint set이 infeasible하면 optimizer를 정상 결과로 완료해서는 안 된다(MUST NOT).

#### Scenario: infeasible bounds
- GIVEN 모든 asset min weight 합이 1을 초과한다
- WHEN input을 검증하거나 optimization을 수행한다
- THEN 명시적인 infeasible/validation failure를 반환한다

### Requirement: Solver result residual validation
Solver status만으로 Optimization result를 승인해서는 안 되며 finite weights/statistics, weight sum, min/max, long-only와 applicable target-volatility residual을 재검증해야 한다(MUST).

#### Scenario: solver success but residual violation
- GIVEN solver status는 success이나 한 weight가 max bound를 의미 있게 초과한다
- WHEN result validation을 수행한다
- THEN canonical valid result로 승인하지 않는다

### Requirement: Maximum Sharpe Ratio objective
Maximum Sharpe Ratio는 다음 ex-ante 의미를 가져야 한다(MUST).

```text
maximize (Expected Return - annual RF) / Volatility
```

Canonical output은 optimized weights, expected annual return, annualized volatility, ex-ante Sharpe Ratio와 solver/status를 포함할 수 있어야 한다(MUST).

#### Scenario: maximum Sharpe run
- GIVEN 유효한 expected return, covariance, annual RF와 constraints가 있다
- WHEN Maximum Sharpe Ratio를 실행한다
- THEN constraint를 만족하는 optimized weights와 ex-ante statistics를 반환한다

### Requirement: Maximum Return at Target Annual Volatility objective
Target-volatility objective는 다음 의미를 가져야 한다(MUST).

```text
maximize Expected Return
subject to Volatility <= Target Annual Volatility
```

Target volatility가 feasible minimum보다 낮으면 infeasible로 처리해야 한다(MUST).

#### Scenario: infeasible target volatility
- GIVEN target annual volatility가 constrained GMV volatility보다 낮다
- WHEN target-volatility optimization을 수행한다
- THEN target을 임의 완화하지 않고 infeasible로 처리한다

### Requirement: Efficient Frontier boundary portfolios
Efficient Frontier는 최소 Global Minimum Variance portfolio와 constraints 아래 Maximum Expected Return portfolio를 boundary로 식별할 수 있어야 한다(MUST).

#### Scenario: frontier boundaries
- GIVEN 유효한 asset statistics와 constraints가 있다
- WHEN frontier를 계산한다
- THEN GMV와 constrained maximum-return boundary를 식별할 수 있다

### Requirement: Efficient Frontier points
기본 100 frontier points는 GMV expected return부터 constrained maximum expected return까지 target return을 분할하고 각 target에서 다음 문제를 만족해야 한다(MUST).

```text
minimize w.T @ Sigma @ w
subject to
    w.T @ mu = target_return
    sum(w) = 1
    min_weight_i <= w_i <= max_weight_i
```

각 point는 point identity, asset weights, expected annual return, annualized volatility와 ex-ante Sharpe Ratio를 보존해야 한다(MUST).

#### Scenario: frontier point integrity
- GIVEN 생성된 frontier point가 있다
- WHEN canonical point를 검증한다
- THEN weights 합과 bounds가 유효하고 return/volatility/Sharpe가 해당 weights의 canonical ex-ante statistics와 일치한다

### Requirement: Efficient Frontier asset statistics
각 Optimization asset에 대해 Ticker, Name, Expected Return, Standard Deviation, Sharpe Ratio, Min Weight, Max Weight를 제공할 수 있어야 한다(MUST).

#### Scenario: frontier asset inspection
- GIVEN Optimization run이 완료되었다
- WHEN asset-level frontier statistics를 inspect한다
- THEN identity와 ex-ante risk/return/bounds를 함께 확인할 수 있다

### Requirement: Optimization ex-ante and historical results remain distinct
Optimization expected return/covariance/Sharpe와 realized historical portfolio analytics는 서로 다른 의미로 유지되어야 한다(MUST). Realized metric을 optimizer objective statistic으로 재명명하거나 반대로 사용해서는 안 된다(MUST NOT).

#### Scenario: ex-ante Sharpe vs ex-post Sharpe
- GIVEN 한 optimized portfolio에 ex-ante Sharpe와 realized ex-post Sharpe가 모두 존재한다
- WHEN canonical result를 저장하거나 표시한다
- THEN 두 값을 동일 metric으로 합치지 않는다

### Requirement: Leave-One-Year-Out optimization robustness
Default Optimization run은 canonical monthly return sample에 대해 Leave-One-Year-Out(LOYO) robustness 진단을 제공해야 한다(MUST). Backtest와 custom analyzer에는 이 Optimization-specific 진단을 자동 적용해서는 안 된다(MUST NOT).

각 LOYO scenario는 하나의 calendar year에 속하는 monthly observations를 모두 제거한 뒤 baseline과 동일한 optimization objective, asset bounds, applicable target annual volatility와 effective annual risk-free rate를 사용해 canonical optimization core를 다시 실행해야 한다(MUST).

Baseline optimized result는 LOYO를 위해 다시 solve하지 않고 기존 baseline result를 비교 기준으로 재사용해야 한다(MUST).

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

이 sensitivity를 자동 overfitting, robustness pass/fail 또는 corner-solution 판정으로 변환해서는 안 된다(MUST NOT).

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

남은 observations가 canonical moment 계산에 부족하면 해당 scenario를 insufficient-data 상태로 기록할 수 있어야 한다(MUST).

LOYO scenario infeasibility 또는 insufficient data를 이유로 정상 baseline Optimization run 전체를 실패시켜서는 안 된다(MUST NOT). 예상하지 못한 programming/runtime exception은 기존 run failure semantics를 따라야 한다(MUST).

#### Scenario: target volatility becomes infeasible
- GIVEN baseline target-volatility run은 feasible하다
- AND 한 calendar year 제거 후 constrained GMV volatility가 target을 초과한다
- WHEN LOYO를 실행한다
- THEN 해당 year scenario는 infeasible로 기록되고 나머지 robustness result는 계속 생성된다

### Requirement: LOYO uses lightweight repeated optimization
LOYO는 각 year마다 market-data acquisition, canonical FX/return preparation, Efficient Frontier generation, portfolio path simulation, historical/benchmark analytics 또는 report rendering을 반복해서는 안 된다(MUST NOT).

LOYO는 prepared canonical monthly returns와 기존 shared optimization objective-solving boundary를 재사용해야 한다(MUST). Baseline의 effective annual risk-free rate는 year omission 사이에서 고정해 asset-return sample influence와 RF 변경 효과를 섞지 않아야 한다(MUST).

Canonical result는 `optimization_robustness.loyo`에 LOYO 결과를 보존할 수 있어야 하며(MUST), persisted raw/review artifact는 `loyo_robustness.csv`를 제공해야 한다(MUST).

#### Scenario: repeated robustness execution
- GIVEN N개의 calendar year가 있는 Optimization sample이다
- WHEN LOYO를 실행한다
- THEN baseline full analysis를 N회 재실행하지 않고 year-excluded moments와 objective solve만 반복한다
