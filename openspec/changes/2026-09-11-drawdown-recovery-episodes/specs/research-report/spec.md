## ADDED Requirements

### Requirement: Drawdown recovery presentation uses canonical analytics
Shared Drawdowns report는 canonical drawdown episode timing과 recovery analytics를 소비해야 하며 renderer/browser에서 Recovery Rate 또는 Normalized Underwater Duration finance formula를 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: Worst Drawdowns recovery fields
- GIVEN canonical drawdown episode에 recovery_months와 annualized recovery rate가 있다
- WHEN Worst Drawdowns table을 표시한다
- THEN 기존 Recovery Time/Underwater 정보를 유지하고 Recovery Rate를 사용자-facing percentage로 확인할 수 있다

### Requirement: Elastic recovery summary compares every portfolio at once
Shared Drawdowns report는 overlay chart 바로 아래에 모든 configured portfolio와 benchmark의 portfolio-level `Normalized Underwater Duration`을 한 개의 compact comparison table로 표시해야 한다(MUST).

사용자-facing label은 `탄성회복도`를 사용하고 값은 `x.x개월 / 10% DD` 형식으로 표시하며 `낮을수록 좋음`을 함께 안내해야 한다(MUST). 각 row는 canonical summary의 completed episode count를 함께 표시해야 하며 값이 unavailable이면 `N/A`를 표시해야 한다(MUST).

Optimization의 기본 표시 순서는 `Provided Portfolio`, `Optimized Portfolio`, `Benchmark`여야 한다(MUST). Backtest는 configured portfolio order 뒤에 benchmark를 둔다(MUST).

#### Scenario: compare elastic recovery summaries
- GIVEN Provided/Optimized/Benchmark canonical drawdown resilience summary가 있다
- WHEN Drawdowns section을 표시한다
- THEN overlay chart 아래 한 table에서 세 portfolio의 탄성회복도와 completed episode count를 동시에 확인할 수 있다
- AND portfolio 선택 state와 무관하게 세 row가 항상 표시된다

### Requirement: Drawdown comparison uses one shared overlay chart
Shared Drawdowns report는 Provided/Optimized/Benchmark 또는 Backtest의 configured portfolios/benchmark drawdown series를 동일한 X/Y 축의 단일 overlay chart에서 비교해야 한다(MUST). Portfolio마다 별도 drawdown chart를 반복 렌더링해서는 안 된다(MUST NOT).

각 series는 고유 색을 유지해야 하며, 사용자가 portfolio identity를 선택하면 선택 series는 foreground에서 굵고 불투명하게 강조되고 나머지 series는 동일 chart 안에서 비교 가능한 명확한 context line으로 남아야 한다(MUST). 선택 동작은 canonical finance 값을 재계산하지 않고 presentation state만 변경해야 한다(MUST NOT).

Drawdown comparison에서만 series color order는 첫 configured portfolio `blue`, 두 번째 configured portfolio `green`, benchmark `orange` 순서를 사용해야 한다(MUST). 세 series가 있을 때 legend/selector도 동일한 identity/color 순서를 유지해야 한다(MUST).

Portfolio 선택 state는 chart foreground 강조에만 영향을 주어야 한다(MUST). 탄성회복도 comparison table이나 Worst Drawdowns episode tables의 가시성을 변경해서는 안 된다(MUST NOT).

#### Scenario: compare three drawdown paths
- GIVEN two configured portfolios와 benchmark drawdown series가 있다
- WHEN Drawdowns section을 표시한다
- THEN 세 series가 하나의 chart에 blue/green/orange 순서로 겹쳐 보이고 chart는 하나만 존재한다

#### Scenario: foreground selected portfolio
- GIVEN overlay chart에서 두 번째 portfolio를 선택한다
- WHEN 선택 state가 변경된다
- THEN 두 번째 portfolio line은 foreground 굵기와 full opacity로 강조된다
- AND 다른 line들은 비교 가능한 context opacity로 계속 보인다
- AND chart 아래의 탄성회복도 및 Worst Drawdowns tables는 그대로 모두 표시된다

### Requirement: Worst Drawdowns details are always listed for every portfolio
Shared Drawdowns report는 overlay chart와 탄성회복도 comparison table 아래에 각 portfolio의 Worst Drawdowns episode table을 모두 표시해야 한다(MUST).

Optimization은 `Provided Portfolio`, `Optimized Portfolio`, `Benchmark` 순서로 section을 나열해야 한다(MUST). Backtest는 configured portfolio order 뒤에 benchmark를 둔다(MUST). Portfolio 선택으로 다른 portfolio의 table을 숨겨서는 안 된다(MUST NOT).

#### Scenario: inspect all drawdown episode tables
- GIVEN Provided/Optimized/Benchmark episode data가 있다
- WHEN Drawdowns section을 표시한다
- THEN 세 portfolio의 Drawdowns heading과 Worst Drawdowns table이 순서대로 모두 보인다

#### Scenario: shared product coverage
- GIVEN Optimization과 Backtest가 shared Drawdowns component를 사용한다
- WHEN overlay presentation을 변경한다
- THEN 두 product의 generated report regression에서 동일 presentation contract를 검증한다
