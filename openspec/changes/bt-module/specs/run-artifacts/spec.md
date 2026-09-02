## ADDED Requirements

### Requirement: Product mode in run contract
Canonical YAML run contract은 Optimization과 Backtest를 명확히 구분할 수 있는 product mode를 표현해야 한다.

#### Scenario: backtest YAML
- GIVEN 사용자-facing Backtest configuration이 있다
- WHEN YAML contract로 serialize한다
- THEN runner가 Optimization이 아니라 Backtest 실행 경계를 선택할 수 있는 명시적 mode가 존재한다

### Requirement: Backtest portfolio collection in YAML
Backtest YAML은 identity를 가진 portfolio collection과 각 portfolio의 target allocation을 loss 없이 표현해야 한다. v1 사용자-facing validation은 1~3개 portfolio를 허용하지만 YAML schema를 fixed `portfolio1`, `portfolio2`, `portfolio3` field로 설계해서는 안 된다.

#### Scenario: 세 portfolio 입력 보존
- GIVEN 서로 다른 이름과 weights를 가진 세 portfolio가 있다
- WHEN input YAML을 저장하고 다시 읽는다
- THEN portfolio identity와 target weights가 동일하게 복원된다

#### Scenario: 향후 limit 확장
- GIVEN 향후 product policy가 4개 이상의 portfolio를 허용한다
- WHEN YAML contract를 확장한다
- THEN 기존 portfolio representation을 재설계하지 않고 collection cardinality만 확장할 수 있다

### Requirement: Backtest Time Period persistence
Backtest YAML은 `Month-to-Month` 또는 `Year-to-Year` Time Period mode와 해당 requested boundary를 loss 없이 표현해야 한다.

#### Scenario: Month-to-Month round trip
- GIVEN Start Year, First Month, End Year, Last Month가 있는 Month-to-Month input이 있다
- WHEN YAML로 저장하고 다시 읽는다
- THEN mode와 모든 period boundary가 동일하게 복원된다

#### Scenario: Year-to-Year round trip
- GIVEN Start Year와 End Year가 있는 Year-to-Year input이 있다
- WHEN YAML로 저장하고 다시 읽는다
- THEN mode와 year boundaries가 동일하게 복원되고 First/Last Month를 필수값으로 요구하지 않는다

### Requirement: Backtest configuration persistence
Persisted Backtest `input.yaml`은 실제 실행에 사용된 Time Period mode와 requested period, initial balance, portfolio definitions, benchmark configuration, effective rebalancing setting과 shared market-data settings를 보존해야 한다.

#### Scenario: run 재현
- GIVEN 완료된 Backtest run이 있다
- WHEN `runs/<run_id>/input.yaml`을 확인한다
- THEN backtest를 다시 구성하는 데 필요한 canonical user input과 자동 적용된 default를 확인할 수 있다

### Requirement: Backtest defaults are explicit in persisted input
Research Frontend가 SPY benchmark, initial balance 10,000, Month-to-Month mode, generated portfolio name 같은 default를 적용한 경우에도 persisted input에서 실제 effective 값을 생략해서는 안 된다.

#### Scenario: frontend defaults 사용
- GIVEN 사용자가 benchmark와 initial balance를 별도로 지정하지 않았다
- WHEN run이 persist된다
- THEN effective SPY benchmark와 initial balance 10,000을 `input.yaml`에서 확인할 수 있다

### Requirement: Backtest canonical result domains
Backtest run의 `result.json`은 최소 configuration, data_coverage, portfolio_definitions, portfolio_paths, portfolio_performance, optional benchmark_analytics, correlations, return_decomposition, risk_decomposition을 structured domain으로 표현할 수 있어야 한다.

#### Scenario: backtest result inspection
- GIVEN 완료된 Backtest run이 있다
- WHEN `result.json`을 읽는다
- THEN 각 portfolio의 identity와 historical path/analytics를 optimization result 없이 structured하게 확인할 수 있다

### Requirement: Multi-portfolio raw and review identity
Backtest raw/review artifact는 여러 portfolio의 series와 table을 저장할 때 portfolio identity를 loss 없이 유지해야 한다.

#### Scenario: 같은 ticker가 여러 portfolio에 존재
- GIVEN SPY가 Portfolio A와 Portfolio B에 모두 포함되어 있다
- WHEN contribution 또는 weight artifact를 저장한다
- THEN `(portfolio, asset)` identity가 보존되어 서로 다른 series가 혼합되지 않는다
