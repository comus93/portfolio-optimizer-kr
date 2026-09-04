## Purpose

Canonical finance result와 user-facing report 사이의 presentation responsibility boundary를 정의한다. 세부 UI/interaction behavior는 해당 capability가 OpenSpec으로 완전 마이그레이션되기 전까지 `docs/report-ui-specification.md`를 migration baseline으로 유지한다.

## Requirements

### Requirement: Report does not redefine canonical finance semantics
Presentation layer는 canonical result의 finance 의미를 다시 정의하거나 별도 formula로 재계산해서는 안 된다(MUST NOT).

#### Scenario: canonical metric rendering
- GIVEN canonical result에 CAGR가 존재한다
- WHEN report를 렌더링한다
- THEN renderer는 CAGR formula를 별도 구현해 다른 값을 만들지 않고 canonical metric을 표시용으로 변환한다

### Requirement: View-only transformations are allowed
Browser/report layer는 formatting, coordinate mapping, grouping/binning, display ordering과 같은 view-only transformation을 수행할 수 있다(MAY). 해당 transformation은 canonical finance values 또는 observation semantics를 변경해서는 안 된다(MUST NOT).

#### Scenario: chart coordinate mapping
- GIVEN canonical monthly return series가 있다
- WHEN SVG chart를 생성한다
- THEN axis coordinate를 계산할 수 있지만 원래 return observation 값을 다른 finance metric으로 대체하지 않는다

### Requirement: Missing and non-applicable values preserve meaning
Canonical metric이 unavailable 또는 conceptually non-applicable인 경우 user-facing report는 이를 0과 구분해야 한다(MUST). 세부 표기 convention은 current report UI contract를 따른다.

#### Scenario: benchmark-relative metric on benchmark itself
- GIVEN benchmark의 Information Ratio가 conceptually non-applicable이다
- WHEN report를 렌더링한다
- THEN 0.00으로 표시해 실제 계산값처럼 보이게 하지 않는다

### Requirement: Identity and units remain observable
Presentation restructuring이 table/chart layout을 변경하더라도 canonical asset/portfolio identity와 metric unit information을 제거해서는 안 된다(MUST NOT).

#### Scenario: asset performance table redesign
- GIVEN asset performance에 Ticker, Name과 percentage/ratio metrics가 있다
- WHEN table presentation을 변경한다
- THEN 어떤 asset의 어떤 unit metric인지 사용자가 계속 식별할 수 있다

### Requirement: Report semantic validation uses canonical values
Report semantic test는 가능한 경우 canonical value와 rendered value의 대응을 검증해야 하며 단순 문자열 marker 존재만으로 finance semantic correctness를 대신해서는 안 된다(MUST NOT).

#### Scenario: balance display regression
- GIVEN canonical normalized Optimization balance 1.0의 display convention이 $10,000이다
- WHEN report semantic test를 수행한다
- THEN 실제 rendered balance가 그 convention과 일치하는지 검증한다

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

#### Scenario: calendar-aware growth ticks
- GIVEN 여러 calendar year에 걸친 monthly wealth path가 있다
- WHEN x-axis tick을 선택한다
- THEN data row index를 등분해 불규칙한 월 label을 만드는 대신 Jan/Jul, 연초, 분기 시작과 같은 규칙적인 calendar anchor 또는 기간 길이에 맞는 동등한 calendar-aware cadence를 사용한다

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

### Requirement: User-facing report must not expose raw artifact schema
Backtest report는 raw/review artifact를 presentation source로 사용할 수 있지만 사용자-facing section을 내부 CSV/JSON schema의 단순 dump로 렌더링해서는 안 된다(MUST NOT). Internal snake_case field name, debug column, storage-only metadata는 사용자가 분석 의미를 이해하는 데 필요한 label/table/chart로 변환해야 한다(MUST).

#### Scenario: Active Return Series artifact
- GIVEN persisted artifact에 `portfolio_return`, `benchmark_return`, `active_return`, `rolling_tracking_error_pct` 같은 내부 필드가 있다
- WHEN Active Returns section을 렌더링한다
- THEN 전체 raw observation table을 그대로 노출하지 않고 canonical active-return analysis 의미에 맞는 summary/chart/table presentation을 제공한다

#### Scenario: Metrics artifact
- GIVEN portfolio metrics가 `portfolio / metric / value` long-format으로 저장되어 있다
- WHEN Metrics section을 표시한다
- THEN raw long-format storage table을 그대로 사용자-facing primary presentation으로 사용하지 않고 비교 가능한 metric matrix 또는 동등한 분석 presentation으로 변환한다

### Requirement: User-facing labels and units
Backtest report의 column/row label은 사용자-facing 용어를 사용해야 하며 canonical unit은 formatting 또는 header 의미로 표현해야 한다(MUST). `_pct`, snake_case 같은 storage suffix 또는 `unit=pct|balance|ratio` 같은 implementation metadata를 일반 사용자-facing data column으로 노출해서는 안 된다(MUST NOT).

#### Scenario: Trailing Returns
- GIVEN canonical artifact에 `3m_pct`, `1y_pct`, `3y_annualized_volatility_pct` field가 있다
- WHEN Trailing Returns를 표시한다
- THEN `3 Month`, `1 Year`, `3 Year`, `3 Year Annualized Standard Deviation`처럼 읽을 수 있는 label과 `%` formatting을 사용한다

#### Scenario: Performance Summary unit metadata
- GIVEN Performance Summary artifact가 metric별 unit metadata를 가진다
- WHEN summary table을 렌더링한다
- THEN `unit` 자체를 일반 data column으로 표시하지 않고 balance는 currency, return/risk는 %, ratio는 decimal로 표현한다

### Requirement: Stable portfolio display order
Backtest report는 canonical input에서 정의된 portfolio collection 순서를 사용자-facing 비교 순서로 보존해야 한다(MUST). Target Allocation, Performance Summary, chart legend, trailing/annual/monthly/rolling comparison 사이에서 같은 portfolio들이 임의로 재정렬되어서는 안 된다(MUST NOT).

#### Scenario: 두 portfolio 순서
- GIVEN canonical input portfolio 순서가 `Growth 70/30`, `Balanced 50/50`이다
- WHEN Summary와 이후 comparison section을 표시한다
- THEN 모든 사용자-facing portfolio comparison에서 Growth가 Balanced보다 먼저 표시되고 benchmark는 portfolio collection 뒤의 비교 reference로 유지된다

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
Backtest report는 available canonical result에 대해 shared Performance Summary, portfolio growth, trailing returns, annual returns, monthly returns, drawdowns, asset performance, correlations, return/risk decomposition, annual asset returns, rolling returns와 applicable benchmark-relative analytics를 적용할 수 있어야 한다(MUST).

#### Scenario: shared section reuse
- GIVEN Backtest run에 canonical shared analytics가 존재한다
- WHEN report를 생성한다
- THEN product-specific 재계산 없이 shared report semantics로 해당 section을 표시한다

### Requirement: Shared historical report component implementation
Optimization과 Backtest에 동일한 canonical 의미로 존재하는 historical section은 product별로 별도 renderer/component를 복제 구현하지 않고 동일 shared report component를 재사용해야 한다(MUST). Product-specific report layer는 section의 포함/제외, 순서, overview와 product-only section을 조합하는 composition을 담당해야 하며(MUST), shared historical finance metric/series를 product-specific renderer에서 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: Annual Returns shared component
- GIVEN Optimization과 Backtest 모두 canonical annual-return series를 가진다
- WHEN 각 product report에서 Annual Returns를 렌더링한다
- THEN 동일 shared Annual Returns component와 동일 identity/unit/tooltip semantics를 사용하고 product별 별도 계산 또는 별도 chart convention을 만들지 않는다

#### Scenario: Drawdowns shared component
- GIVEN 두 product 모두 canonical drawdown series와 episodes를 가진다
- WHEN Drawdowns section을 렌더링한다
- THEN 동일 shared Drawdowns component가 canonical artifact를 소비하고 product report는 해당 component의 배치만 결정한다

#### Scenario: product-only report composition
- GIVEN Optimization에는 Efficient Frontier가 있고 Backtest에는 Time Period와 named portfolio comparison이 있다
- WHEN report를 구성한다
- THEN 해당 product-only section은 각 composition layer에서만 포함되고 shared historical component 자체를 fork하지 않는다

#### Scenario: presentation-only transform
- GIVEN canonical historical series를 SVG/chart로 표시해야 한다
- WHEN renderer가 axis domain, chart coordinates, display ordering, tooltip nearest-point 또는 presentation-only binning을 계산한다
- THEN canonical finance 의미를 변경하지 않는 view transform으로 허용되며 finance metric/series 자체를 재계산하지 않는다

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


### Requirement: Combined asset identity uses stacked name and ticker
사용자-facing report에서 asset `Name`과 `Ticker`를 하나의 label/header/legend item으로 함께 표시할 때는 종목명을 첫 줄에, 괄호로 감싼 ticker를 다음 줄에 표시해야 한다(MUST). `Name (TICKER)`를 한 줄 문자열로 반복해서 사용해서는 안 된다(MUST NOT). Name이 unavailable이면 ticker만 표시할 수 있다(MAY).

#### Scenario: annual/monthly return asset header
- GIVEN asset name이 `Invesco QQQ Trust Series 1`이고 ticker가 `QQQ`이다
- WHEN Annual Returns 또는 Monthly Returns의 asset identity header를 표시한다
- THEN `Invesco QQQ Trust Series 1` 다음 줄에 `(QQQ)`를 표시한다

#### Scenario: chart legend asset identity
- GIVEN 여러 constituent asset의 Name/Ticker를 chart legend에 함께 표시한다
- WHEN legend를 렌더링한다
- THEN 각 item은 Name과 `(Ticker)`를 두 줄 identity로 표시해 긴 한 줄 label이 연속되지 않게 한다

### Requirement: Backtest Monthly Correlations presentation is constituent-only
Backtest report의 `Monthly Correlations`는 canonical Backtest constituent-asset correlation matrix만 표시해야 하며 portfolio return series 또는 별도 benchmark series를 row/column으로 추가해서는 안 된다(MUST NOT). Benchmark ticker가 constituent asset이기도 한 경우에는 constituent asset으로 한 번 표시해야 한다(MUST).

#### Scenario: benchmark is also SPY constituent
- GIVEN portfolio constituents가 QQQ/SPY/GLD/IEF이고 benchmark도 SPY이다
- WHEN Monthly Correlations를 표시한다
- THEN QQQ/SPY/GLD/IEF asset matrix만 표시하고 `Portfolio 1` 또는 별도 `Benchmark` row/column을 추가하지 않는다
