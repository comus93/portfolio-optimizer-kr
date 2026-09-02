## Purpose

사용자가 하나 이상의 고정 target-allocation portfolio를 동일한 historical period와 optional benchmark에서 backtest하고 realized performance/risk를 비교하는 독립 product capability를 정의한다.

## ADDED Requirements

### Requirement: Independent Backtest product mode
Backtest run은 Optimization run과 구분되는 독립 product mode여야 하며 optimization objective나 Efficient Frontier 계산 없이 실행될 수 있어야 한다.

#### Scenario: Backtest-only run
- GIVEN 유효한 backtest configuration이 있다
- WHEN backtest를 실행한다
- THEN optimization objective를 요구하지 않고 historical portfolio simulation과 analytics를 수행한다

### Requirement: V1 portfolio comparison limit
Backtest v1 사용자-facing input은 1개 이상 3개 이하의 named portfolio를 동시에 비교할 수 있어야 한다.

#### Scenario: 세 portfolio 비교
- GIVEN Portfolio A, Portfolio B, Portfolio C가 정의되어 있다
- WHEN backtest를 실행한다
- THEN 세 portfolio의 identity가 결과와 report 전체에서 구분되어 유지된다

#### Scenario: v1에서 네 portfolio 요청
- GIVEN 사용자-facing v1 configuration에 네 portfolio가 입력된다
- WHEN input validation을 수행한다
- THEN v1 comparison limit을 초과한 명시적 validation error를 반환한다

### Requirement: Extensible portfolio collection model
Canonical Backtest configuration과 result는 portfolio를 fixed `portfolio1`, `portfolio2`, `portfolio3` schema field가 아니라 identity를 가진 collection으로 표현해야 한다. v1의 최대 3개 제한은 product validation policy이며 canonical model 자체의 구조적 최대치로 고정해서는 안 된다.

#### Scenario: 향후 portfolio limit 확장
- GIVEN 향후 product policy가 3개보다 많은 portfolio를 허용하도록 변경된다
- WHEN canonical schema를 확장한다
- THEN 기존 portfolio identity/weight representation을 재설계하지 않고 collection limit 변경으로 확장할 수 있어야 한다

### Requirement: Shared asset universe with portfolio-specific weights
비교 portfolio는 asset row의 union을 공유할 수 있어야 하며 각 portfolio는 각 asset에 독립적인 target weight를 가져야 한다. 사용하지 않는 asset은 0% weight로 표현할 수 있어야 한다.

#### Scenario: portfolio별 사용 asset이 다름
- GIVEN Portfolio A는 SPY/GLD를 사용하고 Portfolio B는 SPY/TLT를 사용한다
- WHEN canonical backtest input을 구성한다
- THEN union asset set SPY/GLD/TLT를 유지하면서 각 portfolio에 독립적인 target weights를 표현할 수 있다

### Requirement: Fully invested target allocations
각 portfolio의 target weight 합은 100%여야 한다.

#### Scenario: allocation 합 오류
- GIVEN 한 portfolio의 target weights 합이 95%이다
- WHEN input validation을 수행한다
- THEN valid backtest configuration으로 받아들이지 않는다

### Requirement: Time Period mode selection
Backtest settings는 `Month-to-Month`와 `Year-to-Year` Time Period mode를 선택할 수 있어야 한다.

#### Scenario: Month-to-Month 선택
- GIVEN 사용자가 `Month-to-Month`를 선택한다
- WHEN period controls를 구성한다
- THEN Start Year, First Month, End Year, Last Month를 사용해 requested period를 표현할 수 있다

#### Scenario: Year-to-Year 선택
- GIVEN 사용자가 `Year-to-Year`를 선택한다
- WHEN period controls를 구성한다
- THEN Start Year와 End Year를 사용하고 First/Last Month는 non-applicable로 처리한다

### Requirement: Common analysis period
동일 Backtest run의 모든 portfolio와 benchmark는 동일 requested analysis period를 사용해야 한다.

#### Scenario: 동일 기간 비교
- GIVEN 여러 portfolio와 benchmark가 있다
- WHEN backtest를 실행한다
- THEN shared market-data coverage에서 결정된 동일 effective period를 기준으로 비교한다

### Requirement: Initial balance
Backtest run은 positive initial balance를 입력받아 각 portfolio의 wealth/balance path를 동일 시작금액에서 생성할 수 있어야 한다.

#### Scenario: 동일 초기금액 비교
- GIVEN initial balance가 10,000이고 세 portfolio가 있다
- WHEN wealth path를 생성한다
- THEN 각 portfolio는 10,000에서 시작하며 이후 자신의 realized return path에 따라 독립적으로 변한다

### Requirement: Optional benchmark
Backtest run은 optional benchmark asset을 지정할 수 있어야 한다.

#### Scenario: benchmark 없음
- GIVEN benchmark를 지정하지 않았다
- WHEN backtest를 실행한다
- THEN absolute performance analytics는 제공하고 benchmark-relative analytics는 N/A 또는 non-applicable로 처리한다

#### Scenario: benchmark 있음
- GIVEN benchmark ticker가 지정되어 있다
- WHEN backtest를 실행한다
- THEN shared benchmark path와 benchmark-relative analytics를 모든 applicable portfolio에 대해 생성한다

### Requirement: Calendar alignment selection
Backtest settings는 `Calendar Aligned = Yes`와 `Calendar Aligned = No`를 모두 지원해야 한다. Calendar alignment는 periodic rebalancing schedule의 anchor semantics를 결정하며 모든 비교 portfolio에 동일하게 적용된다.

#### Scenario: calendar aligned yes
- GIVEN Calendar Aligned가 Yes이고 quarterly rebalancing이 선택되었다
- WHEN historical path를 생성한다
- THEN shared `portfolio-simulation`의 calendar-quarter schedule을 사용한다

#### Scenario: calendar aligned no
- GIVEN Calendar Aligned가 No이고 quarterly rebalancing이 선택되었다
- WHEN historical path를 생성한다
- THEN shared `portfolio-simulation`의 first-active-month anchored 3-month schedule을 사용한다

### Requirement: Run-level periodic rebalancing setting
한 Backtest run의 모든 portfolio는 동일한 periodic rebalancing setting을 사용해야 하며 `none`, `yearly`, `semiannual`, `quarterly`, `monthly` 중 하나를 선택할 수 있어야 한다. Rebalance bands는 v1에서 제외한다.

#### Scenario: quarterly policy
- GIVEN run-level effective rebalancing policy가 quarterly이다
- WHEN 여러 portfolio의 historical path를 생성한다
- THEN 모든 portfolio는 동일한 calendar-alignment setting과 quarterly schedule semantics를 사용한다

### Requirement: Independent portfolio paths
같은 asset return matrix와 같은 run-level rebalancing setting을 사용하는 여러 portfolio라도 각 portfolio의 target allocation에 따라 독립적인 weight, return, wealth path를 가져야 한다.

#### Scenario: 같은 자산 다른 비중
- GIVEN Portfolio A와 Portfolio B가 같은 asset들을 사용하지만 weights가 다르다
- WHEN 같은 기간을 backtest한다
- THEN 각 portfolio의 path와 analytics는 서로 독립적으로 계산된다

### Requirement: Canonical total-return input
Backtest는 asset return을 별도의 dividend reinvestment option으로 재정의하지 않고 shared `market-data` capability가 제공하는 canonical total-return series를 사용해야 한다.

#### Scenario: 배당 지급 asset
- GIVEN distribution을 지급하는 asset이 Backtest portfolio에 포함된다
- WHEN historical return path를 생성한다
- THEN price-only return이 아니라 shared canonical total-return semantics를 사용한다

### Requirement: Historical analytics only
Backtest product의 primary result는 realized historical analytics여야 하며 optimization-specific expected return, expected covariance frontier, optimized weight 같은 ex-ante 결과를 Backtest 결과로 요구해서는 안 된다.

#### Scenario: Backtest result inspection
- GIVEN 완료된 backtest run이 있다
- WHEN canonical result를 확인한다
- THEN realized portfolio/benchmark analytics와 historical paths를 확인할 수 있고 Efficient Frontier는 required result가 아니다

### Requirement: Shared analytics reuse
Backtest에서 기존 shared historical analytics와 동일한 의미를 사용하는 metric은 `portfolio-analytics`의 canonical behavior를 재사용해야 하며 product spec에서 다른 계산 convention을 정의해서는 안 된다.

#### Scenario: CAGR와 MDD
- GIVEN portfolio return path가 생성되었다
- WHEN CAGR와 MDD를 계산한다
- THEN shared portfolio-analytics requirement와 동일한 convention을 사용한다

### Requirement: Backtest input surface
사용자-facing Backtest 입력은 최소 Time Period mode와 period boundaries, Calendar Aligned, initial balance, 1~3개의 portfolio name, asset/ticker, portfolio별 allocation, optional benchmark, run-level rebalancing policy를 구성할 수 있어야 한다.

#### Scenario: UI에서 Backtest 구성
- GIVEN 사용자가 Backtest product mode를 선택했다
- WHEN 입력을 구성한다
- THEN Optimization objective/min-max constraint 없이 Backtest에 필요한 portfolio comparison input을 설정할 수 있다

### Requirement: V1 scope exclusions
Backtest v1은 cashflow contribution/withdrawal, rebalance bands, leverage, display income, style analysis, factor regression, regime performance를 canonical input 또는 required calculation behavior로 제공하지 않아야 한다. Dividend reinvestment는 별도 toggle로 제공하지 않는다.

#### Scenario: v1 input surface
- GIVEN 사용자가 Backtest v1을 구성한다
- WHEN input controls와 YAML contract를 확인한다
- THEN 제외된 advanced setting을 required/supported v1 field로 노출하지 않는다

### Requirement: PV reference is non-normative
Portfolio Visualizer snapshot은 feature/information-architecture reference로만 사용해야 하며 PV의 값이나 UI 구현 차이 자체를 acceptance failure로 간주해서는 안 된다.

#### Scenario: internal report layout 차이
- GIVEN 내부 report가 OpenSpec requirement를 충족하지만 PV와 pixel layout이 다르다
- WHEN acceptance를 판단한다
- THEN PV와의 시각적 차이만으로 failure로 판단하지 않는다
