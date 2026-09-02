## ADDED Requirements

### Requirement: Backtest report applicability
Research report는 `portfolio-backtest` product mode에서 optimization-only section을 요구하지 않고 Backtest-specific overview와 applicable shared analytics section을 구성해야 한다.

#### Scenario: Backtest report
- GIVEN 완료된 Backtest run이 있다
- WHEN report를 생성한다
- THEN Efficient Frontier 없이 Backtest overview, allocation comparison, historical performance와 applicable shared analytics를 표시한다

### Requirement: Backtest overview
Backtest report 상단은 requested/effective period, initial balance, benchmark, portfolio names, 각 portfolio의 rebalancing policy를 확인할 수 있어야 한다.

#### Scenario: 세 portfolio overview
- GIVEN 서로 다른 rebalancing policy의 세 portfolio가 있다
- WHEN report header/overview를 표시한다
- THEN 사용자는 어떤 portfolio가 어떤 policy로 동일 기간에 비교되었는지 식별할 수 있다

### Requirement: Target allocation comparison
Backtest report는 portfolio별 target allocation을 asset Name/Ticker와 함께 비교할 수 있어야 하며 0% asset을 숨기더라도 canonical allocation을 왜곡해서는 안 된다.

#### Scenario: portfolio별 다른 asset
- GIVEN union asset set 중 일부 asset이 특정 portfolio에서 0%이다
- WHEN allocation comparison을 표시한다
- THEN 각 portfolio의 실제 target allocation과 asset identity를 구분할 수 있다

### Requirement: Growth and balance comparison
Backtest report는 동일 initial balance에서 시작한 각 portfolio의 canonical wealth/balance path를 같은 time axis에서 비교할 수 있어야 한다.

#### Scenario: growth chart hover
- GIVEN 여러 portfolio의 monthly wealth path가 있다
- WHEN 특정 month를 inspect한다
- THEN 해당 month의 portfolio identity와 balance를 구분해 확인할 수 있다

### Requirement: Shared historical sections for Backtest
Backtest report는 available canonical result에 대해 shared Performance Summary, trailing returns, annual returns, monthly returns, drawdowns, asset performance, correlations, return/risk decomposition, rolling returns를 적용할 수 있어야 한다.

#### Scenario: shared section reuse
- GIVEN Backtest run에 canonical shared analytics가 존재한다
- WHEN report를 생성한다
- THEN product-specific 재계산 없이 shared report semantics로 해당 section을 표시한다

### Requirement: Benchmark-relative sections are conditional
Benchmark가 존재할 때만 active return, tracking error, information ratio, rolling active/risk, Up/Down 등 benchmark-relative section을 적용해야 한다.

#### Scenario: benchmark 없는 Backtest
- GIVEN Backtest run에 benchmark가 없다
- WHEN report를 생성한다
- THEN benchmark-relative section을 0값으로 꾸며내지 않고 non-applicable로 처리한다

### Requirement: Multi-portfolio series identity
Backtest chart/table은 여러 portfolio를 동시에 비교할 때 portfolio identity를 color만으로 전달하지 않아야 한다.

#### Scenario: rolling returns 비교
- GIVEN 세 portfolio의 rolling return series가 있다
- WHEN chart를 표시한다
- THEN legend/label/tooltip에서 각 portfolio name을 확인할 수 있다
