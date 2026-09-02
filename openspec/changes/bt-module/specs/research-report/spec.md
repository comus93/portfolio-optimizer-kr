## ADDED Requirements

### Requirement: Backtest report applicability
Research report는 `portfolio-backtest` product mode에서 optimization-only section을 요구하지 않고 Backtest-specific overview와 applicable shared analytics section을 구성해야 한다(MUST).

#### Scenario: Backtest report
- GIVEN 완료된 Backtest run이 있다
- WHEN report를 생성한다
- THEN Efficient Frontier 없이 Backtest overview, allocation comparison, historical performance와 applicable shared analytics를 표시한다

### Requirement: Existing report interaction contract inheritance
Backtest report는 기존 internal report contract의 identity, unit, missing/N/A, semantic axis, tooltip, responsive/readability 원칙을 그대로 적용해야 한다(MUST). Backtest delta가 명시적으로 바꾸지 않은 shared presentation behavior를 별도 convention으로 재정의해서는 안 된다(MUST NOT).

#### Scenario: missing historical metric
- GIVEN Backtest portfolio의 어떤 trailing metric이 observation 부족으로 unavailable이다
- WHEN report를 렌더링한다
- THEN 0으로 표시하지 않고 기존 shared `N/A` semantics를 유지한다

### Requirement: Backtest overview
Backtest report 상단은 Time Period mode, requested/effective period, initial balance, benchmark, portfolio names, run-level rebalancing policy와 Calendar Aligned setting을 확인할 수 있어야 한다(MUST).

#### Scenario: 세 portfolio overview
- GIVEN 세 portfolio가 같은 run-level quarterly rebalancing과 Calendar Aligned=No를 사용한다
- WHEN report header/overview를 표시한다
- THEN 사용자는 portfolio identities와 공통 schedule setting을 구분해 확인할 수 있다

### Requirement: Target allocation comparison
Backtest report는 portfolio별 target allocation을 asset Name/Ticker와 함께 비교할 수 있어야 하며 0% asset을 숨기더라도 canonical allocation을 왜곡해서는 안 된다(MUST).

#### Scenario: portfolio별 다른 asset
- GIVEN union asset set 중 일부 asset이 특정 portfolio에서 0%이다
- WHEN allocation comparison을 표시한다
- THEN 각 portfolio의 실제 target allocation과 asset identity를 구분할 수 있다

### Requirement: Backtest balance semantics
Backtest report의 Start Balance와 wealth/balance chart는 run에 입력된 actual initial balance를 사용해야 하며 Optimization report의 normalized-wealth display convention을 Backtest initial balance로 덮어써서는 안 된다(MUST).

#### Scenario: initial balance 50,000
- GIVEN Backtest initial balance가 50,000이다
- WHEN Performance Summary와 growth/balance chart를 표시한다
- THEN 각 portfolio의 시작 balance는 50,000이며 임의의 10,000 normalized display로 바꾸지 않는다

### Requirement: Growth and balance comparison
Backtest report는 동일 initial balance에서 시작한 각 portfolio의 canonical wealth/balance path를 같은 time axis에서 비교할 수 있어야 한다(MUST).

#### Scenario: growth chart hover
- GIVEN 여러 portfolio의 monthly wealth path가 있다
- WHEN 특정 month를 inspect한다
- THEN 해당 month의 portfolio identity와 balance를 구분해 확인할 수 있다

### Requirement: Growth chart semantic axes and readable ticks
Backtest Portfolio Growth chart는 x축의 time 의미와 y축의 portfolio balance 단위를 명시해야 하며, 두 끝점만 표시하는 축이 아니라 기간과 값 범위를 읽을 수 있는 복수의 중간 tick/grid reference를 제공해야 한다(MUST).

#### Scenario: multi-year growth chart
- GIVEN 5년 이상의 monthly wealth path가 있다
- WHEN Portfolio Growth chart를 표시한다
- THEN 시작/종료 지점 외에도 중간 기간을 식별할 수 있는 x-axis tick labels가 존재하고 y-axis에도 중간 balance tick labels와 horizontal reference grid가 존재한다

#### Scenario: growth axis units
- GIVEN balance path가 통화 단위로 표시된다
- WHEN chart를 읽는다
- THEN x-axis는 time/year 의미를, y-axis는 Portfolio Balance와 통화 단위를 식별할 수 있다

### Requirement: Growth chart inspect interaction
Growth chart는 screenshot에만 의존하지 않고 실제 browser interaction에서 point 또는 nearest-period inspect 시 date, portfolio identity, balance가 화면에 표시되어야 한다(MUST). Accessibility용 label만 있고 사용자에게 보이는 inspect feedback이 없는 구현은 충분하지 않다(MUST NOT).

#### Scenario: mouse hover
- GIVEN 여러 portfolio의 growth series가 있다
- WHEN 사용자가 chart point 또는 inspect target에 hover한다
- THEN visible tooltip 또는 동등한 visible interaction으로 date, portfolio name, balance를 확인할 수 있다

#### Scenario: keyboard focus
- GIVEN 사용자가 keyboard로 inspect 가능한 chart target에 focus한다
- WHEN focus가 이동한다
- THEN mouse hover와 동등한 핵심 identity/date/balance 정보를 확인할 수 있다

### Requirement: Backtest summary information hierarchy
Backtest report는 PV snapshot을 pixel-copy하지 않더라도 Backtest 결과의 정보 성격을 보존해야 하며, canonical data가 존재하는 Summary의 핵심 비교 정보인 portfolio allocation identity, Performance Summary, Portfolio Growth, Trailing Returns를 결과 상단의 한 흐름에서 파악할 수 있도록 구성해야 한다(MUST).

#### Scenario: first-pass result inspection
- GIVEN 완료된 multi-portfolio Backtest run이 있다
- WHEN 사용자가 report의 Summary를 처음 확인한다
- THEN 별도 내부 artifact를 찾아다니지 않고 portfolio 구성, 주요 performance matrix, growth comparison, trailing performance를 순차적으로 확인할 수 있다

### Requirement: Backtest section grouping follows result semantics
Backtest report navigation/section grouping은 available canonical data의 성격에 맞춰 Summary, benchmark가 있을 때 Active Returns, Metrics, Annual Returns, Monthly Returns, Drawdowns, Assets, Rolling Returns와 같은 결과 영역을 구분해야 한다(MUST). PV에만 존재하고 v1에서 지원하지 않는 style/factor/regime/provider-specific exposure 기능을 외형 유사성을 위해 임의 생성해서는 안 된다(MUST NOT).

#### Scenario: supported Backtest result domains
- GIVEN canonical result에 portfolio metrics, annual/monthly returns, drawdowns, asset/correlation/decomposition, rolling returns가 있다
- WHEN report navigation을 구성한다
- THEN 해당 결과 영역을 사용자가 의미별로 찾을 수 있고 서로 무관한 단일 flat section으로 축약하지 않는다

#### Scenario: unsupported PV-only exposure data
- GIVEN v1 canonical result에 holdings-style category/yield/expense/factor data가 없다
- WHEN PV MHTML과 report를 비교한다
- THEN 해당 값을 추정하거나 fabricated section으로 채우지 않는다

### Requirement: Backtest Performance Summary applicability
Backtest Performance Summary는 historical/realized metric을 중심으로 구성하고 Optimization 전용 ex-ante Expected Return, ex-ante Sharpe, optimized-weight 결과를 required row로 요구해서는 안 된다(MUST NOT).

#### Scenario: benchmark 있는 Backtest summary
- GIVEN benchmark가 있는 Backtest run이 있다
- WHEN Performance Summary를 표시한다
- THEN 최소 Start Balance, End Balance, CAGR, realized Annualized Return, Standard Deviation, Best Year, Worst Year, Maximum Drawdown, ex-post Sharpe, Sortino와 applicable Active Return/Tracking Error/Information Ratio를 portfolio별로 비교할 수 있다

#### Scenario: benchmark 없는 Backtest summary
- GIVEN benchmark가 없는 Backtest run이 있다
- WHEN Performance Summary를 표시한다
- THEN absolute historical metrics를 표시하고 benchmark-relative metrics는 non-applicable 의미를 유지한다

### Requirement: Shared historical sections for Backtest
Backtest report는 available canonical result에 대해 shared Performance Summary, trailing returns, annual returns, monthly returns, drawdowns, asset performance, correlations, return/risk decomposition, annual asset returns, rolling returns를 적용할 수 있어야 한다(MUST).

#### Scenario: shared section reuse
- GIVEN Backtest run에 canonical shared analytics가 존재한다
- WHEN report를 생성한다
- THEN product-specific 재계산 없이 shared report semantics로 해당 section을 표시한다

### Requirement: Benchmark-relative sections are conditional
Benchmark가 존재할 때만 active return, tracking error, information ratio, active contribution, rolling active/risk, Up/Down 등 benchmark-relative section을 적용해야 한다(MUST).

#### Scenario: benchmark 없는 Backtest
- GIVEN Backtest run에 benchmark가 없다
- WHEN report를 생성한다
- THEN benchmark-relative section을 0값으로 꾸며내지 않고 non-applicable로 처리한다

### Requirement: Multi-portfolio series identity
Backtest chart/table은 여러 portfolio를 동시에 비교할 때 portfolio identity를 color만으로 전달하지 않아야 한다(MUST NOT).

#### Scenario: rolling returns 비교
- GIVEN 세 portfolio의 rolling return series가 있다
- WHEN chart를 표시한다
- THEN legend/label/tooltip에서 각 portfolio name을 확인할 수 있다

### Requirement: Product-specific section exclusion
Backtest report는 Efficient Frontier, Frontier Transition, optimization constraints, optimized allocation 같은 `optimization-only` section을 빈 placeholder로 표시하지 않아야 한다(MUST NOT).

#### Scenario: Backtest report navigation
- GIVEN Backtest run에 optimization result domain이 없다
- WHEN report section/navigation을 구성한다
- THEN optimization-only section을 N/A card로 채우지 않고 적용 대상에서 제외한다

### Requirement: Display Income is not a v1 report section
Backtest v1 report는 distribution income breakdown 또는 `Display Income` section을 required/supported section으로 제공하지 않아야 한다(MUST NOT). Canonical total return은 유지하되 income decomposition을 임의로 price data에서 추정해서는 안 된다(MUST NOT).

#### Scenario: distribution-paying asset
- GIVEN Backtest portfolio에 dividend/distribution을 지급하는 asset이 있다
- WHEN v1 report를 생성한다
- THEN total-return performance는 표시하되 별도 income amount/series를 추정하여 표시하지 않는다
