## Purpose

시장 입력에서 기대수익·위험을 추정하고 제약조건과 objective에 따라 optimization portfolio와 efficient frontier를 산출하는 제품 behavior를 정의한다.

## ADDED Requirements

### Requirement: Canonical optimization inputs
Optimization run은 asset universe, analysis period, provided weights(optional), asset min/max weights, benchmark(optional), objective, target annual volatility(target-vol objective only), rebalancing period, risk-free configuration, frontier points를 표현할 수 있어야 한다.

#### Scenario: Max Sharpe 입력
- GIVEN asset universe와 constraints, period, risk-free configuration이 제공된다
- WHEN Maximum Sharpe optimization을 요청한다
- THEN target volatility 없이 유효한 optimization request를 구성할 수 있다

#### Scenario: Target volatility 입력
- GIVEN target-volatility objective가 선택된다
- WHEN request를 검증한다
- THEN target annual volatility가 반드시 제공되어야 한다

### Requirement: Ex-ante expected return
시스템은 optimization용 annual expected return을 monthly simple return의 arithmetic mean에 12를 곱한 값으로 계산해야 한다.

#### Scenario: 기대수익 계산
- GIVEN completed monthly return observations가 있다
- WHEN annual expected return을 계산한다
- THEN `mu_annual = mean(monthly_returns) * 12`를 사용한다

### Requirement: Ex-ante covariance and volatility
시스템은 sample monthly covariance에 12를 곱해 annual covariance를 만들고 portfolio volatility를 `sqrt(w.T @ Sigma @ w)`로 계산해야 한다.

#### Scenario: portfolio expected volatility
- GIVEN annual covariance matrix와 portfolio weights가 있다
- WHEN ex-ante volatility를 계산한다
- THEN annual covariance quadratic form의 제곱근을 사용한다

### Requirement: Ex-ante Sharpe
시스템은 portfolio의 ex-ante Sharpe를 `(Expected Return - effective annual RF) / Volatility`로 계산해야 한다.

#### Scenario: optimized portfolio Sharpe
- GIVEN expected annual return, annualized volatility, effective annual RF가 있다
- WHEN ex-ante Sharpe를 계산한다
- THEN canonical formula를 사용한다

### Requirement: Long-only fully-invested constraints
Optimization portfolio는 long-only, fully-invested이며 각 asset의 min/max constraint를 만족해야 한다.

#### Scenario: feasible constraints
- GIVEN 각 asset의 min/max 범위가 feasible하다
- WHEN optimization을 수행한다
- THEN 모든 weight는 0 이상이고 min/max를 만족하며 합이 1이다

#### Scenario: infeasible constraints
- GIVEN min/max 조합으로 fully-invested portfolio가 불가능하다
- WHEN request를 검증하거나 optimization을 수행한다
- THEN 명시적 infeasible error를 반환한다

### Requirement: Maximum Sharpe objective
시스템은 constraints 안에서 ex-ante Sharpe Ratio를 최대화하는 portfolio를 산출해야 한다.

#### Scenario: Maximum Sharpe 결과
- GIVEN feasible asset universe와 risk-free rate가 있다
- WHEN Maximum Sharpe objective를 실행한다
- THEN optimized weights, expected annual return, annualized volatility, ex-ante Sharpe와 solver status를 제공한다

### Requirement: Maximum Return at Target Volatility objective
시스템은 annualized volatility가 target 이하인 feasible portfolio 중 expected annual return이 최대인 portfolio를 산출해야 한다.

#### Scenario: feasible target volatility
- GIVEN target annual volatility가 feasible range 안에 있다
- WHEN target-volatility objective를 실행한다
- THEN 결과 portfolio의 volatility는 target constraint를 만족한다

#### Scenario: infeasible low target
- GIVEN target annual volatility가 feasible minimum보다 낮다
- WHEN optimization을 수행한다
- THEN 명시적 infeasible result를 반환한다

### Requirement: Optimization residual verification
Optimization result는 solver status만으로 성공을 판정하지 않고 finite statistics, weight sum, min/max, long-only 및 적용 가능한 target-volatility residual을 만족해야 한다.

#### Scenario: solver가 값을 반환했지만 constraint 위반
- GIVEN solver가 결과 weights를 반환했다
- WHEN canonical residual verification을 수행한다
- THEN 허용 범위를 벗어난 결과를 정상 optimization result로 승인하지 않는다

### Requirement: Efficient frontier boundaries
시스템은 constrained Global Minimum Variance portfolio와 constrained Maximum Expected Return portfolio를 efficient frontier의 경계로 계산해야 한다.

#### Scenario: frontier boundary 생성
- GIVEN feasible optimization universe가 있다
- WHEN efficient frontier를 생성한다
- THEN GMV와 constrained maximum-return boundary를 확인할 수 있다

### Requirement: Efficient frontier points
시스템은 GMV expected return부터 constrained maximum expected return까지 target return을 균등 분할하여 configured number의 frontier points를 생성해야 하며 기본값은 100 points여야 한다.

#### Scenario: 기본 frontier
- GIVEN frontier_points를 별도로 변경하지 않았다
- WHEN frontier를 생성한다
- THEN 100개의 target-return point를 시도하고 각 feasible point에 weights, expected return, volatility, ex-ante Sharpe를 제공한다

### Requirement: Frontier allocation contract
각 feasible efficient-frontier point의 asset allocation은 long-only/min/max/fully-invested constraints를 만족해야 한다.

#### Scenario: frontier point 검증
- GIVEN 생성된 frontier point가 있다
- WHEN point weights를 검증한다
- THEN weights 합은 1이고 모든 asset constraint를 만족한다

### Requirement: Optimization and realized performance separation
Optimization의 ex-ante statistics는 historical realized performance와 별개의 값과 의미로 유지되어야 한다.

#### Scenario: report에서 두 Sharpe를 제공하는 경우
- GIVEN ex-ante Sharpe와 historical ex-post Sharpe가 모두 존재한다
- WHEN canonical result와 report를 만든다
- THEN 두 값을 하나의 metric으로 덮어쓰거나 혼용하지 않는다
