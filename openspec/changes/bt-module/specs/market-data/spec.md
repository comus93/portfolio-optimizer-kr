## ADDED Requirements

### Requirement: Canonical total-return semantics
Optimization과 Backtest의 historical asset return은 price change와 cash distribution의 reinvestment를 반영하는 canonical total-return 의미를 사용해야 한다. Price-only return을 total return으로 조용히 취급해서는 안 된다.

#### Scenario: distribution-paying asset
- GIVEN 분석 asset이 dividend 또는 distribution을 지급한다
- WHEN canonical historical return series를 생성한다
- THEN distribution reinvestment가 반영된 total-return series를 사용한다

#### Scenario: total-return data unavailable
- GIVEN configured market-data source와 derivation으로 해당 asset의 total-return series를 신뢰성 있게 만들 수 없다
- WHEN canonical return matrix를 준비한다
- THEN price-only return으로 silent fallback하지 않고 명시적인 unsupported/data-coverage failure를 반환한다

### Requirement: Shared return identity across products
동일 asset, currency conversion, requested period와 effective coverage 조건에서 Optimization과 Backtest는 동일 canonical total-return observations를 사용해야 한다.

#### Scenario: same asset in Optimization and Backtest
- GIVEN 동일 asset과 analysis period가 Optimization과 Backtest에 사용된다
- WHEN historical return matrix를 준비한다
- THEN product mode에 따라 별도의 return convention을 사용하지 않는다
