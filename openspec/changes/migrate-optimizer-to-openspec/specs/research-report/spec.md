## Purpose

Canonical run artifacts를 사용해 Optimization과 향후 Backtest가 공유할 research report의 presentation, interaction, identity 및 section applicability contract를 정의한다. 금융 계산 공식은 소유 capability의 canonical result를 사용하며 report에서 재정의하지 않는다.

## ADDED Requirements

### Requirement: Report finance boundary
Research report는 persisted canonical/review/raw artifact를 표현해야 하며 browser layer는 finance metric을 다른 convention으로 재계산해서는 안 된다.

#### Scenario: chart rendering
- GIVEN canonical finance series가 persisted되어 있다
- WHEN browser가 chart를 렌더링한다
- THEN formatting, coordinate mapping, grouping, nearest-point selection 같은 presentation transform만 수행한다

### Requirement: Section applicability
각 report section은 `shared`, `optimization-only`, 또는 향후 정의되는 product-specific applicability를 가져야 하며 해당 product에 적용되지 않는 section을 필수로 강제해서는 안 된다.

#### Scenario: Optimization report
- GIVEN portfolio-optimization run을 표시한다
- WHEN report sections를 구성한다
- THEN Efficient Frontier 계열 optimization-only section과 적용 가능한 shared analytics section을 표시한다

### Requirement: Human-readable identity
사용자-facing report는 portfolio, benchmark, asset의 의미를 구분할 수 있는 human-readable identity를 사용해야 하며 asset은 가능한 경우 Name과 Ticker를 함께 제공해야 한다.

#### Scenario: Optimization identities
- GIVEN Provided, optimized portfolio, benchmark가 있다
- WHEN report label을 표시한다
- THEN generic internal key만 노출하지 않고 각각을 구분할 수 있는 이름을 표시한다

### Requirement: Units and missing values
Return, volatility, drawdown, allocation, active metric은 %, ratio는 unitless decimal, balance는 currency로 표시하고 unavailable 값은 `N/A`로 표현해야 한다.

#### Scenario: missing benchmark-relative metric
- GIVEN benchmark 자체의 Tracking Error가 conceptually not applicable이다
- WHEN table을 렌더링한다
- THEN 0이 아니라 `N/A`로 표시한다

### Requirement: Table readability
사용자-facing table은 identity와 numeric value를 비교하기 쉬운 alignment/precision을 사용하고 required information을 보존해야 한다.

#### Scenario: column 보강
- GIVEN 기존 required metric에 identity column을 추가한다
- WHEN table layout을 변경한다
- THEN 기존 required metric을 제거하지 않는다

### Requirement: Chart semantic axes
Chart는 실제 semantic X/Y value와 명확한 unit을 사용해야 하며 row index를 date/year/volatility 같은 실제 의미 대신 사용해서는 안 된다.

#### Scenario: rolling return chart
- GIVEN monthly dated rolling return series가 있다
- WHEN chart를 렌더링한다
- THEN X축은 실제 month/year이고 Y축은 annualized return %이다

### Requirement: Report header applicability
Optimization report header는 실제 completed observations의 effective period와 run identity를 표시해야 하며 risk-free 설명은 실제 run mode와 일치해야 한다.

#### Scenario: effective period 축소
- GIVEN asset availability로 requested period보다 실제 period가 줄어들었다
- WHEN report header/note를 표시한다
- THEN effective period와 limiting asset을 식별할 수 있다

### Requirement: Optimization allocation sections
`optimization-only` allocation section은 Provided Portfolio와 Optimized Portfolio의 asset identity, allocation %, min/max constraint를 표현해야 한다.

#### Scenario: zero allocation
- GIVEN optimized weight가 0%인 asset이 있다
- WHEN primary allocation visualization을 렌더링한다
- THEN 0% allocation은 숨길 수 있지만 canonical allocation information을 왜곡하지 않는다

### Requirement: Efficient Frontier assets section
`optimization-only` Efficient Frontier Assets table은 Name, Ticker, Expected Return, Standard Deviation, Sharpe Ratio, Min Weight, Max Weight를 제공해야 한다.

#### Scenario: frontier asset statistics
- GIVEN optimization asset statistics가 존재한다
- WHEN table을 표시한다
- THEN ex-ante expected return/risk/Sharpe와 constraints를 asset identity와 함께 확인할 수 있다

### Requirement: Efficient Frontier chart
`optimization-only` Efficient Frontier chart는 X=Annualized Standard Deviation %, Y=Expected Annual Return %로 frontier curve와 적용 가능한 asset/portfolio/benchmark landmark를 표현해야 한다.

#### Scenario: frontier hover
- GIVEN frontier point를 hover한다
- WHEN tooltip을 표시한다
- THEN Expected Return, Standard Deviation, Sharpe Ratio와 asset allocations를 함께 제공한다

#### Scenario: outside-scale asset
- GIVEN asset이 최종 readable display domain 밖에 있다
- WHEN chart를 구성한다
- THEN chart와 별도 outside-scale table 사이에서 asset이 중복되거나 누락되지 않는다

### Requirement: Efficient Frontier transition section
`optimization-only` transition section은 X=frontier annualized volatility, Y=asset allocation %의 stacked allocation transition을 표현하고 각 frontier point allocation 합이 100%임을 유지해야 한다.

#### Scenario: transition tooltip
- GIVEN 특정 frontier point를 hover한다
- WHEN tooltip을 표시한다
- THEN point statistics와 모든 asset allocations를 확인할 수 있다

### Requirement: Shared Performance Summary
`shared` Performance Summary는 해당 product가 제공하는 portfolio/benchmark identities에 대해 적용 가능한 performance metrics를 비교할 수 있어야 하며 unavailable metric은 N/A 의미를 유지해야 한다.

#### Scenario: Optimization performance summary
- GIVEN Provided, Optimized, Benchmark analytics가 존재한다
- WHEN summary를 표시한다
- THEN Start/End Balance, CAGR, realized risk, Best/Worst Year, MDD, applicable Sharpe/Sortino/active metrics를 비교할 수 있다

### Requirement: Shared trailing returns section
`shared` trailing section은 canonical trailing metrics를 identity별로 표시하고 observation이 부족한 window는 N/A로 표시해야 한다.

#### Scenario: 10Y history 부족
- GIVEN 10년 미만의 observations가 있다
- WHEN trailing returns를 표시한다
- THEN 10Y value를 임의 extrapolation하지 않고 N/A로 표시한다

### Requirement: Shared annual returns section
`shared` Annual Returns는 calendar year별 series identity를 유지하고 같은 year의 비교 대상 값을 함께 읽을 수 있어야 한다.

#### Scenario: partial year
- GIVEN 첫해 또는 마지막 해가 partial calendar year이다
- WHEN annual returns를 표시한다
- THEN canonical partial-year return을 유지하고 available completed months 기준임을 사용자가 알 수 있다

### Requirement: Shared monthly returns section
`shared` Monthly Returns는 portfolio identity별 Year, Jan-Dec, YTD calendar table을 제공하고 unavailable month를 0%로 채우지 않아야 한다.

#### Scenario: partial first year
- GIVEN 첫해에는 12월 return만 존재한다
- WHEN monthly calendar를 표시한다
- THEN Jan-Nov는 N/A, Dec는 actual return으로 표시한다

### Requirement: Shared drawdown section
`shared` Drawdowns는 identity별 drawdown series와 episode table을 독립적으로 표현해야 한다.

#### Scenario: 여러 portfolio drawdown
- GIVEN 서로 다른 portfolio drawdown episodes가 있다
- WHEN table을 구성한다
- THEN 서로 다른 portfolio의 episode를 의미 없이 하나의 series로 연결하지 않는다

### Requirement: Shared asset performance section
`shared` Asset Performance는 Ticker, Name과 canonical asset performance/trailing metrics를 제공해야 한다.

#### Scenario: asset identity 유지
- GIVEN 여러 asset이 있다
- WHEN asset performance table을 표시한다
- THEN 각 metric이 올바른 asset identity와 연결된다

### Requirement: Shared correlations section
`shared` Correlations는 적용 가능한 asset/portfolio/benchmark identity의 correlation coefficient를 읽을 수 있는 matrix로 표현해야 하며 color만으로 의미를 전달해서는 안 된다.

#### Scenario: heatmap coefficient
- GIVEN correlation matrix가 있다
- WHEN report에 표시한다
- THEN numeric coefficient와 identity를 확인할 수 있다

### Requirement: Shared return decomposition section
`shared` Return Decomposition은 portfolio identity를 구분하여 asset별 realized contribution을 표시해야 한다.

#### Scenario: 두 portfolio decomposition
- GIVEN Provided와 Optimized contribution 결과가 있다
- WHEN report를 표시한다
- THEN 두 portfolio의 contribution이 혼합되지 않고 구분된다

### Requirement: Shared risk decomposition section
`shared` Risk Decomposition은 applicable portfolio별 asset component risk contribution을 표시하고 canonical contribution 합 100%를 표현해야 한다.

#### Scenario: contribution identity
- GIVEN Provided와 Optimized risk contribution이 있다
- WHEN report에 표시한다
- THEN Name/Ticker와 portfolio별 contribution을 구분할 수 있다

### Requirement: Shared annual asset returns section
`shared` Annual Asset Returns는 ticker별 independent series를 유지하고 같은 year의 모든 asset return을 비교할 수 있는 grouped interaction을 제공해야 한다.

#### Scenario: grouped year hover
- GIVEN 여러 asset의 같은 calendar year return이 있다
- WHEN 한 asset mark를 hover한다
- THEN 같은 year의 모든 asset Name/Ticker/Return을 확인할 수 있다

### Requirement: Shared active analytics section
Benchmark-relative analytics를 사용하는 product에서는 annualized active return과 active return contribution을 portfolio identity별로 분리해 표시해야 한다.

#### Scenario: cumulative active contribution
- GIVEN `(portfolio, ticker)`별 contribution paths가 있다
- WHEN chart를 렌더링한다
- THEN 서로 다른 portfolio의 같은 ticker path를 하나로 이어 붙이지 않는다

### Requirement: Shared rolling active return and risk section
Rolling Active Return과 Rolling Tracking Error를 함께 표시할 때 서로 다른 scale 의미를 보존하고 identity/benchmark/window를 명확히 해야 한다.

#### Scenario: 36-month panel
- GIVEN 36개월 rolling active return과 tracking error가 있다
- WHEN panel을 렌더링한다
- THEN Active Return은 한 scale, Tracking Error는 별도 scale로 읽을 수 있고 같은 month tooltip에서 두 값을 확인할 수 있다

### Requirement: Shared Up vs Down market section
Up/Down Market section은 canonical conditional statistics와 report용 paired comparison을 구분해 표현해야 하며 외부 reference count에 맞추기 위해 canonical observations를 변경해서는 안 된다.

#### Scenario: paired bar view transform
- GIVEN monthly portfolio/benchmark observations가 있다
- WHEN report용 grouped bars를 만든다
- THEN canonical statistics는 유지하면서 benchmark-return 순 정렬과 equal-frequency grouping을 presentation transform으로만 사용할 수 있다

### Requirement: Shared rolling returns section
`shared` Rolling Returns는 기본 3Y와 5Y annualized return series의 portfolio/benchmark identity와 실제 Month/Year X축을 유지해야 한다.

#### Scenario: rolling 5Y chart
- GIVEN canonical 60-month rolling return series가 있다
- WHEN report를 표시한다
- THEN 각 series identity와 annualized return %를 시간축에서 비교할 수 있다

### Requirement: Responsive meaning preservation
Desktop과 mobile layout은 chart/table의 의미와 required information을 보존해야 하며 clipping이나 과도한 축소로 필수 정보를 읽을 수 없게 해서는 안 된다.

#### Scenario: mobile wide table
- GIVEN 넓은 analytical table이 mobile viewport에 표시된다
- WHEN responsive layout을 적용한다
- THEN horizontal scroll 등으로 information loss 없이 접근할 수 있다

### Requirement: Accessibility and readability
Report는 color 하나만으로 series identity를 전달하지 않고 label, legend, tooltip 등 추가 identity 수단과 명확한 units를 제공해야 한다.

#### Scenario: multiple chart series
- GIVEN 여러 portfolio/asset series가 있다
- WHEN chart를 표시한다
- THEN color 외에도 series를 구분할 수 있는 textual identity가 존재한다

### Requirement: UI regression severity
Report defect는 금융 의미 또는 필수정보 훼손을 P0, 분석/비교를 현저히 어렵게 하는 semantic/readability regression을 P1, 정보 의미에 영향 없는 visual polish 차이를 P2로 분류해야 한다.

#### Scenario: missing을 0으로 표시
- GIVEN canonical value가 unavailable이다
- WHEN report가 이를 0으로 표시한다
- THEN P0 regression으로 분류한다

#### Scenario: 핵심 chart가 읽기 어려울 정도로 작아짐
- GIVEN finance value는 맞지만 핵심 분석 chart의 비교가 현저히 어려워졌다
- WHEN regression severity를 판단한다
- THEN P1로 분류한다
