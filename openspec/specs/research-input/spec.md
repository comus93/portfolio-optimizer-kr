## Purpose

LLM/User Research Frontend가 Optimization과 Backtest를 구분해 필요한 사용자 결정을 수집하고, 두 product 모두 explicit `product_mode`를 포함한 canonical input을 생성하는 behavior를 정의한다.

## Requirements

### Requirement: Product-intent-aware input flow
Research Frontend는 사용자의 연구 의도가 Optimization인지 Backtest인지 구분해 해당 product에 필요한 질문만 해야 한다(MUST).

#### Scenario: 명시적 Backtest 요청
- GIVEN 사용자가 이미 정의한 두 portfolio를 과거 데이터로 비교해 달라고 요청한다
- WHEN research input을 구성한다
- THEN Optimization objective나 min/max constraint를 요구하지 않고 Backtest input flow를 사용한다

#### Scenario: 제품 의도가 모호함
- GIVEN 사용자가 Optimization과 Backtest 둘 다 합리적으로 가능한 요청을 한다
- WHEN 현재 대화만으로 product mode를 확정할 수 없다
- THEN 임의로 선택하지 않고 필요한 최소 질문으로 의도를 확인한다

#### Scenario: 고정 비중만 주고 실행 요청
- GIVEN 사용자가 `QQQ 30%, SPY 30%, GLD 30%, IEF 10%로 돌려보자`라고 요청한다
- WHEN Optimization은 이 비중을 Provided Portfolio로 사용할 수 있고 Backtest는 target allocation으로 사용할 수 있다
- THEN 비중이 있다는 이유만으로 Backtest를 선택하지 않고 어느 product인지 사용자에게 확인한다

### Requirement: Explicit product mode is mandatory
Research Frontend가 생성하거나 갱신하는 canonical Experiment YAML은 Optimization과 Backtest 모두 `product_mode`를 명시해야 한다(MUST).

지원값은 canonical하게 다음 둘이다.

```text
optimization
backtest
```

`product_mode` 누락을 Optimization으로 암묵 해석해서는 안 된다(MUST NOT).

#### Scenario: Optimization input 생성
- GIVEN 사용자가 Optimization 의도를 확정했다
- WHEN Experiment YAML을 생성한다
- THEN `product_mode: optimization`을 명시한다

#### Scenario: Backtest input 생성
- GIVEN 사용자가 Backtest 의도를 확정했다
- WHEN Experiment YAML을 생성한다
- THEN `product_mode: backtest`를 명시한다

#### Scenario: product mode 누락
- GIVEN canonical YAML에 `product_mode`가 없다
- WHEN 실행 입력을 검증한다
- THEN Optimization으로 fallback하지 않고 invalid input으로 거부한다

### Requirement: Reuse already-provided information
사용자가 대화에서 이미 제공한 입력은 다시 질문하지 않아야 한다(MUST NOT).

#### Scenario: weights와 기간이 이미 있음
- GIVEN 사용자가 portfolio weights와 analysis period를 이미 명시했다
- WHEN 남은 input을 확인한다
- THEN 해당 값을 다시 묻지 않고 기계적 validation만 수행한다

### Requirement: Mechanical validation before user questions
Ticker 중복, portfolio weight 합, v1 portfolio count, positive initial balance 등 기계적으로 검증할 수 있는 항목은 사용자에게 판단을 떠넘기기 전에 시스템이 검증해야 한다(MUST).

#### Scenario: weight 합 90%
- GIVEN 한 Backtest portfolio의 입력 weights 합이 90%이다
- WHEN research input을 검증한다
- THEN 정상 입력으로 가정하지 않고 명시적으로 오류를 알려 수정이 필요한 값을 식별한다

### Requirement: Backtest-specific user decision surface
Backtest 입력에서 사용자가 결정해야 하는 핵심 값은 portfolio 구성과 target allocation이며, 필요할 때 period, benchmark, rebalancing 및 calendar-alignment option을 사용자 의도에 따라 변경할 수 있어야 한다(MUST).

#### Scenario: portfolio 정의 부족
- GIVEN 사용자가 Backtest를 요청했지만 비교할 portfolio의 구성 또는 weights가 빠져 있다
- WHEN canonical input을 만들 수 없다
- THEN 빠진 portfolio 구성만 질문하고 Optimization 관련 질문을 추가하지 않는다

### Requirement: Time Period mode
Backtest user-facing input은 `Month-to-Month`와 `Year-to-Year` 두 Time Period mode를 제공해야 하며 Research Frontend의 기본값은 `Month-to-Month`여야 한다(MUST).

#### Scenario: 기본 Time Period
- GIVEN 사용자가 Time Period mode를 별도로 지정하지 않았다
- WHEN Research Frontend가 Backtest input을 구성한다
- THEN `Month-to-Month`를 effective mode로 사용하고 persisted input에 명시한다

### Requirement: Month-to-Month period input
`Month-to-Month` mode에서는 Start Year, First Month, End Year, Last Month를 사용자-facing period input으로 표현할 수 있어야 한다(MUST).

#### Scenario: 월 단위 기간 지정
- GIVEN Start Year=2020, First Month=Mar, End Year=2025, Last Month=Aug가 입력된다
- WHEN requested analysis period를 구성한다
- THEN 2020-03부터 2025-08까지의 월 단위 requested period로 해석한다

### Requirement: Year-to-Year period input
`Year-to-Year` mode에서는 Start Year와 End Year를 사용자-facing period input으로 사용하고 해당 calendar year 전체를 requested period로 해석해야 한다(MUST). First Month와 Last Month는 이 mode에서 non-applicable이다.

#### Scenario: 연 단위 기간 지정
- GIVEN Start Year=2020, End Year=2025가 입력된다
- WHEN `Year-to-Year` requested period를 구성한다
- THEN 2020년 시작부터 2025년 종료까지 full-calendar-year period로 해석한다

### Requirement: Dynamic period choices
Year/month selector의 실제 선택 가능 범위는 canonical market-data availability와 current supported date range를 기반으로 구성해야 하며 PV snapshot에 보이는 특정 연도 목록을 product contract로 hard-code해서는 안 된다(MUST NOT).

#### Scenario: 새로운 calendar year
- GIVEN 지원되는 market data가 새로운 연도까지 확장된다
- WHEN Backtest period selector를 구성한다
- THEN spec 변경 없이 해당 연도를 선택 가능 범위에 반영할 수 있다

### Requirement: Default analysis period
사용자가 구체적인 period를 지정하지 않으면 모든 required portfolio asset과 적용 가능한 benchmark가 함께 관측 가능한 전체 common effective period를 기본 분석기간으로 사용해야 한다(MUST).

#### Scenario: period 미지정
- GIVEN 사용자가 portfolio만 정의하고 기간은 지정하지 않았다
- WHEN Research Frontend가 canonical input을 만든다
- THEN common available period 전체를 사용하고 실제 requested/effective boundaries를 persisted input/result에 기록한다

### Requirement: Default benchmark
Research Frontend는 benchmark 미지정 시 S&P 500(SPY)을 기본 benchmark로 사용해야 하며 사용자가 명시적으로 다른 benchmark 또는 benchmark 없음으로 override할 수 있어야 한다(MUST).

#### Scenario: benchmark 미지정
- GIVEN 사용자가 benchmark를 지정하지 않았다
- WHEN Backtest research input을 구성한다
- THEN SPY를 effective benchmark로 사용하고 입력에 명시한다

#### Scenario: benchmark 없음 요청
- GIVEN 사용자가 benchmark 없이 절대성과만 보겠다고 명시했다
- WHEN canonical input을 구성한다
- THEN SPY default를 강제하지 않고 benchmark를 none으로 기록한다

### Requirement: Default initial balance
사용자가 initial balance를 지정하지 않으면 Research Frontend는 10,000을 기본값으로 사용해야 한다(MUST).

#### Scenario: initial amount 미지정
- GIVEN 사용자가 initial amount를 지정하지 않았다
- WHEN canonical Backtest input을 만든다
- THEN initial balance 10,000을 사용하고 persisted input에 명시한다

### Requirement: Default portfolio names
사용자가 portfolio name을 지정하지 않으면 입력 순서에 따라 `Portfolio 1`, `Portfolio 2`, `Portfolio 3`을 자동 생성해야 한다(MUST).

#### Scenario: 두 portfolio 이름 미지정
- GIVEN 두 portfolio의 구성과 weights는 있지만 이름이 없다
- WHEN canonical input을 만든다
- THEN 각각 `Portfolio 1`, `Portfolio 2` identity를 부여한다

### Requirement: Calendar alignment input and default
Research Frontend는 `Calendar Aligned = Yes/No`를 선택할 수 있게 해야 하며 사용자가 별도 지정하지 않으면 기존 calendar-aligned behavior를 보존하기 위해 `Yes`를 기본값으로 사용해야 한다(MUST).

#### Scenario: Calendar Aligned 미지정
- GIVEN 사용자가 calendar alignment를 지정하지 않았다
- WHEN Backtest input을 구성한다
- THEN `Calendar Aligned = Yes`를 effective setting으로 사용하고 persisted input에 명시한다

#### Scenario: Calendar Aligned No 지정
- GIVEN 사용자가 Calendar Aligned를 No로 지정한다
- WHEN canonical input을 구성한다
- THEN first-active-month anchored schedule을 사용하도록 setting을 보존한다

### Requirement: Run-level rebalancing input and default
Research Frontend는 한 Backtest run 전체에 공통으로 적용되는 rebalancing setting을 제공해야 하며 `No rebalancing`, `Annually`, `Semi-annually`, `Quarterly`, `Monthly`를 지원하고 기본값은 `Monthly`여야 한다(MUST).

#### Scenario: rebalancing 미지정
- GIVEN 사용자가 rebalancing을 지정하지 않았다
- WHEN canonical Backtest input을 만든다
- THEN run-level `Monthly`를 effective setting으로 사용하고 모든 portfolio에 동일하게 적용한다

#### Scenario: quarterly 지정
- GIVEN 사용자가 Quarterly를 지정한다
- WHEN 한 run에 세 portfolio를 구성한다
- THEN 세 portfolio 모두 동일한 quarterly setting을 사용한다

### Requirement: V1 comparison limit communication
Research Frontend는 v1에서 동시에 비교 가능한 portfolio가 최대 3개임을 적용하고 초과 요청을 조용히 잘라내지 않아야 한다(MUST NOT).

#### Scenario: 네 portfolio 비교 요청
- GIVEN 사용자가 네 portfolio를 한 run에서 비교하려 한다
- WHEN v1 input을 구성한다
- THEN 일부 portfolio를 임의 제거하지 않고 v1 한도를 명시한다

### Requirement: V1 excluded advanced settings
Backtest v1 Research Frontend는 Cashflows, Rebalance Bands, Leverage, Display Income, Style Analysis, Factor Regression, Regime Performance를 supported input으로 요구하지 않아야 한다(MUST NOT). Dividend reinvestment는 별도 toggle이 아니라 shared canonical total-return semantics로 처리해야 한다(MUST).

#### Scenario: 기본 settings surface
- GIVEN 사용자가 Backtest v1 settings를 구성한다
- WHEN Research Frontend가 supported controls를 제시한다
- THEN 제외된 advanced option을 필수 또는 지원되는 v1 입력으로 노출하지 않는다

### Requirement: No redundant approval after explicit execution intent
사용자가 이미 실행 의도를 명시했고 필요한 입력과 사용자 결정이 모두 해소되면 다시 불필요한 승인 질문을 만들어서는 안 된다(MUST NOT).

#### Scenario: `이 조건으로 백테스트해줘`
- GIVEN 유효한 Backtest input이 모두 확정되었다
- WHEN 사용자가 실행을 명시적으로 요청했다
- THEN 조건을 짧게 확인할 수는 있지만 `진행할까?` 같은 중복 승인으로 실행을 막지 않는다

### Requirement: Canonical input persistence
Research Frontend가 default를 자동 적용한 경우에도 실제 effective 값은 canonical YAML과 persisted `input.yaml`에 명시적으로 남겨야 한다(MUST).

#### Scenario: default 적용
- GIVEN benchmark, initial balance, Time Period mode, Calendar Aligned, rebalancing 또는 portfolio name에 canonical default가 적용된다
- WHEN run input을 persist한다
- THEN 실행에 실제 사용된 effective 값을 생략하지 않고 기록한다

### Requirement: Source-backed asset names in canonical input
Research Frontend가 asset 또는 benchmark의 `name`을 canonical YAML에 기록할 때는 v1 market-data provider가 제공한 종목명을 초기 설정 시점의 snapshot으로 사용해야 한다(MUST). 이 `name` field는 Optimization과 Backtest가 공유하며 run 실행마다 provider에서 다시 해석하지 않는다(MUST NOT).

#### Scenario: ETF ticker로 canonical input 생성
- GIVEN 사용자가 ETF ticker와 portfolio 조건을 확정했다
- WHEN canonical YAML을 최초 생성한다
- THEN FDR ETF listing metadata의 해당 종목명을 `name`에 기록하고 이후 Optimization/Backtest와 report가 동일한 persisted name을 사용한다
