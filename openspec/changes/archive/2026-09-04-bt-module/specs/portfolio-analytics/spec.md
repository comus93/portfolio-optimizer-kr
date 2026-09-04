## Purpose

Backtest가 shared portfolio analytics를 재사용할 때 product-specific applicability와 canonical correlation scope를 정의한다.

## ADDED Requirements

### Requirement: Backtest monthly correlations are constituent-asset only
Backtest의 canonical monthly correlation matrix는 Backtest run의 union constituent asset monthly returns 사이의 Pearson correlation만 포함해야 한다(MUST). Portfolio return series와 별도 benchmark series를 correlation matrix의 row/column으로 추가해서는 안 된다(MUST NOT).

Benchmark ticker가 동시에 portfolio constituent인 경우에는 benchmark 역할 때문이 아니라 constituent asset identity로 한 번 포함해야 한다(MUST).

#### Scenario: benchmark가 portfolio constituent이기도 함
- GIVEN Backtest portfolio가 `QQQ`, `SPY`, `GLD`, `IEF`를 포함하고 benchmark도 `SPY`이다
- WHEN canonical monthly correlations를 계산한다
- THEN matrix의 row/column은 `QQQ`, `SPY`, `GLD`, `IEF`만 포함하고 `Portfolio 1` 또는 별도 `benchmark` series는 포함하지 않는다

#### Scenario: benchmark가 constituent가 아님
- GIVEN Backtest portfolio union은 `QQQ`, `GLD`, `IEF`이고 benchmark는 `SPY`이다
- WHEN canonical monthly correlations를 계산한다
- THEN matrix는 `QQQ`, `GLD`, `IEF`만 포함하고 SPY benchmark series를 추가하지 않는다

### Requirement: Backtest correlation preserves shared calculation convention
Backtest constituent-asset correlation은 shared monthly simple-return Pearson correlation convention을 사용해야 하며 product-specific 별도 correlation formula를 정의해서는 안 된다(MUST NOT).

#### Scenario: 동일 asset return matrix
- GIVEN 동일한 canonical asset monthly return matrix가 있다
- WHEN shared asset correlation과 Backtest monthly correlation을 계산한다
- THEN 동일 asset pair의 correlation 값은 동일해야 한다
