## Why

현재 시스템은 optimization 중심으로 구성되어 있어 독립적인 portfolio backtest 실행 경계가 없다. 이번 변경에서 Portfolio Visualizer Backtest Portfolio를 레퍼런스로 Backtest 기능을 추가하고, OpenSpec 및 Agent 검증 체계를 실제 개발 흐름에 적용한다.

## What Changes

- 독립적인 portfolio backtesting 기능을 추가한다.
- Optimization과 Backtest는 별도 product capability로 관리한다.
- 기존 optimizer의 data, portfolio simulation, analytics, artifact, report/viewer 자산은 의미가 동일한 범위에서 재사용한다.
- Backtest 때문에 shared capability behavior가 변경되면 해당 OpenSpec delta와 Optimization 영향 검토를 함께 수행한다.
- Agent가 Test → Real Run → Result Verification → Browser Verification → Fix → Re-verify 흐름으로 검증할 수 있는 프로젝트별 검증 구조를 추가한다.

## Capabilities

### New Capabilities

- `portfolio-backtest`: 사용자가 하나 이상의 고정 비중 포트폴리오를 동일 기간과 benchmark 기준으로 백테스트하고 성과·위험·자산별 분석 결과를 비교할 수 있는 기능.

### Shared Capabilities

Backtest spec 구체화 과정에서 실제 behavior 변경이 필요한 capability만 delta를 작성한다.

후보:

- `market-data`
- `portfolio-simulation`
- `portfolio-analytics`
- `run-artifacts`
- `research-report`

단순 재사용은 modified capability로 간주하지 않는다.

## Dependency

기존 Optimization baseline은 `migrate-optimizer-to-openspec` change에서 먼저 capability별로 이관한다. 이관이 완료되면 shared capability 변경이 기존 `portfolio-optimization`에 미치는 영향을 OpenSpec 기준으로 검토한다.

## Impact

- 입력/YAML contract와 runner에 Backtest 실행 경계가 추가될 수 있다.
- 공통 capability 변경 시 Backtest 구현 검증과 함께 Optimization affected regression이 필요할 수 있다.
- Agent verification용 실행 진입점과 profile/browser 검증 구조가 추가된다.
- PV 결과와 화면은 reference이며 최종 acceptance는 내부 OpenSpec requirement와 검증 기준을 따른다.
