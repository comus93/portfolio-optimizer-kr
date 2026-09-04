## Purpose

Optimization과 이후 product가 공유하는 market-data, return observation, coverage, currency conversion과 risk-free input 의미론을 정의한다.

## Requirements

### Requirement: Canonical market-data pipeline
기존 baseline market-data pipeline은 FinanceDataReader(FDR) 기반 price series에서 optional FX conversion, common price alignment, calendar month-end prices, monthly simple returns, completed-month filtering, requested analysis period 순서로 canonical monthly return matrix를 구성해야 한다(MUST).

#### Scenario: monthly return preparation
- GIVEN daily 또는 irregular price observations가 있다
- WHEN canonical monthly returns를 준비한다
- THEN calendar month-end price를 기준으로 monthly simple returns를 생성한다

### Requirement: Analysis Period is return-observation period
`Analysis Period`는 price fetch 기간이 아니라 return observation period로 해석해야 한다(MUST). 첫 requested month의 return을 만들기 위해 직전 month-end price를 warm-up data로 사용할 수 있어야 한다(MUST).

#### Scenario: first requested month
- GIVEN requested analysis start가 2020-01이다
- WHEN January return을 계산한다
- THEN 필요한 경우 2019-12 month-end price를 warm-up observation으로 사용할 수 있다

### Requirement: Incomplete terminal month exclusion
Requested end가 해당 calendar month의 completed month-end를 포함하지 않으면 terminal incomplete month를 canonical monthly return observation으로 포함해서는 안 된다(MUST NOT).

#### Scenario: mid-month end date
- GIVEN requested end가 2025-08-15이다
- WHEN monthly return matrix를 만든다
- THEN 아직 완료되지 않은 2025-08 monthly return을 포함하지 않는다

### Requirement: Common Optimization coverage
Optimization universe는 모든 Optimization asset이 함께 관측 가능한 common monthly return matrix를 사용해야 한다(MUST).

실제 usable period가 asset availability로 requested period보다 짧아지면 effective period와 limiting asset을 식별할 수 있어야 한다(MUST).

#### Scenario: late-listed asset
- GIVEN 한 asset의 usable history가 다른 asset보다 늦게 시작한다
- WHEN Optimization matrix를 align한다
- THEN 모든 asset이 공통으로 관측 가능한 period로 줄이고 limiting asset/effective start를 추적할 수 있다

### Requirement: Coverage metadata
Canonical run은 최소 optimization monthly-return coverage, benchmark overlap과 asset별 price coverage의 start/end/observation evidence를 보존할 수 있어야 한다(MUST).

#### Scenario: coverage inspection
- GIVEN completed Optimization run이 있다
- WHEN canonical coverage metadata를 확인한다
- THEN requested period와 실제 usable period 차이를 설명할 수 있는 observation evidence가 존재한다

### Requirement: Currency normalization
혼합 KRW/USD universe에서는 USD asset을 USD/KRW로 환산해 common base currency에서 분석해야 한다(MUST). 지원하지 않는 currency를 암묵적으로 USD 또는 KRW로 취급해서는 안 된다(MUST NOT).

#### Scenario: mixed KRW/USD universe
- GIVEN KRW asset과 USD asset이 같은 universe에 있다
- WHEN canonical price/return matrix를 만든다
- THEN USD asset을 configured USD/KRW series로 환산한 common-currency basis를 사용한다

#### Scenario: unsupported currency
- GIVEN supported conversion contract가 없는 currency가 입력된다
- WHEN canonical market data를 준비한다
- THEN 명시적 validation/data error를 반환한다

### Requirement: Monthly simple-return convention
Canonical monthly asset return은 simple return을 사용해야 한다(MUST).

```text
r_t = P_t / P_(t-1) - 1
```

#### Scenario: two consecutive month-end prices
- GIVEN month-end prices 100과 110이 있다
- WHEN monthly return을 계산한다
- THEN canonical simple return은 10%이다

### Requirement: Risk-free modes
Risk-free configuration은 `us_3m_tbill`과 `fixed` mode를 지원해야 하고 기존 default는 `us_3m_tbill`이어야 한다(MUST).

`fixed` mode는 입력 annual rate를 그대로 사용해야 한다(MUST). External provider가 runtime boundary에 있는 경우 runner가 analysis period에 일관된 effective annual U.S. 3M T-Bill rate를 공급할 수 있어야 한다(MUST).

#### Scenario: fixed risk-free rate
- GIVEN `fixed` annual rate 3%가 입력된다
- WHEN run을 실행한다
- THEN effective annual RF는 3%를 사용한다

### Requirement: Persist effective risk-free metadata
Canonical run은 requested risk-free mode와 실제 effective annual rate를 구분해 기록해야 한다(MUST). User-facing 설명은 실제 effective mode/rate semantics와 충돌해서는 안 된다(MUST NOT).

#### Scenario: us_3m_tbill run
- GIVEN default T-Bill mode로 run이 완료된다
- WHEN persisted metadata를 확인한다
- THEN requested mode와 실제 계산에 사용된 effective annual rate를 복원할 수 있다

### Requirement: Canonical total-return semantics
Optimization과 Backtest의 historical asset return은 price change와 cash distribution의 reinvestment를 반영하는 canonical total-return 의미를 사용해야 한다(MUST). Price-only return을 total return으로 조용히 취급해서는 안 된다(MUST NOT).

#### Scenario: distribution-paying asset
- GIVEN 분석 asset이 dividend 또는 distribution을 지급한다
- WHEN canonical historical return series를 생성한다
- THEN distribution reinvestment가 반영된 total-return series를 사용한다

#### Scenario: total-return data unavailable
- GIVEN configured market-data source와 derivation으로 해당 asset의 total-return series를 신뢰성 있게 만들 수 없다
- WHEN canonical return matrix를 준비한다
- THEN price-only return으로 silent fallback하지 않고 명시적인 unsupported/data-coverage failure를 반환한다

### Requirement: FDR adjusted-series resolution is source-aware
FinanceDataReader의 total-return-capable series 판정은 `Adj Close`라는 컬럼명의 존재 여부만으로 결정해서는 안 된다(MUST NOT). Data source와 asset type의 반환 semantics를 함께 판정해야 한다(MUST).

#### Scenario: FDR Korean default/NAVER ETF
- GIVEN 국내 ETF가 FDR의 default Korean path 또는 명시적 `NAVER:` path로 조회되고 반환 schema가 `Open/High/Low/Close/Volume/Change`이며 별도 `Adj Close` 컬럼이 없다
- WHEN canonical adjusted series를 선택한다
- THEN `Adj Close` 부재만으로 unsupported 처리하지 않고, 해당 Korean ETF/NAVER `Close`를 adjusted/distribution-aware series로 취급하여 canonical return input으로 사용할 수 있다

#### Scenario: explicit KRX source
- GIVEN 국내 asset을 명시적 `KRX:` source로 조회한다
- WHEN 반환 `Close`의 adjusted/distribution semantics가 FDR source contract에서 보장되지 않는다
- THEN 해당 `Close`를 canonical total return으로 자동 승인해서는 안 된다

#### Scenario: Korean common stock
- GIVEN 국내 일반 주식의 FDR default/NAVER `Close`가 존재하지만 cash dividend reinvestment semantics가 확인되지 않았다
- WHEN canonical total-return series를 선택한다
- THEN ETF에 대한 source-specific 판단을 일반 주식에 자동 확장해서는 안 된다

### Requirement: Shared return identity across products
동일 asset, currency conversion, requested period와 effective coverage 조건에서 Optimization과 Backtest는 동일 canonical total-return observations를 사용해야 한다(MUST).

#### Scenario: same asset in Optimization and Backtest
- GIVEN 동일 asset과 analysis period가 Optimization과 Backtest에 사용된다
- WHEN historical return matrix를 준비한다
- THEN product mode에 따라 별도의 return convention을 사용하지 않는다
