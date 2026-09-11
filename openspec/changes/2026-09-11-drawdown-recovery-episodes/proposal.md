# Proposal: Drawdown Recovery Episodes

## Why

현재 Drawdown report는 episode별 Start, Bottom, Recovery와 화면상 Recovery Time을 제공하지만, 회복 속도는 canonical analytics로 보존되지 않고 recovery path도 직접 비교할 수 없다. 사용자는 낙폭의 깊이뿐 아니라 바닥 이후 얼마나 빠르게 이전 고점을 회복하는지, 즉 회복탄력성을 별도 축으로 검토하려 한다.

## What changes

- shared `portfolio-analytics`의 drawdown episode에 명시적 recovery timing과 annualized recovery rate를 추가한다.
- Bottom 이후 Recovery까지의 normalized recovery progress monthly series를 canonical artifact로 보존한다.
- shared Drawdowns presentation은 기존 episode table에 Recovery Rate를 추가하고, portfolio별 worst episodes의 Recovery Progress curve를 표시한다.
- episode들을 하나의 portfolio-level recovery score로 aggregation하는 규칙은 이번 change에 포함하지 않는다.

## Shared capability impact

- changed shared capability: `portfolio-analytics`, `research-report`
- reason: Optimization/Backtest가 동일 drawdown/recovery 의미를 공유한다.
- affected product capabilities: `portfolio-optimization`, `portfolio-backtest`
- affected regression: shared analytics synthetic tests, Optimization pipeline artifact/report, Backtest artifact/report shared Drawdowns component

## Non-goals

- Frontier sweet-spot 자동 판정
- 여러 episode의 평균/median/depth-weighted recovery score
- asset별 recovery ranking 또는 asset-level aggregation
