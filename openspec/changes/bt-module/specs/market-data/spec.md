## ADDED Requirements

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
