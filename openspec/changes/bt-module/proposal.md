## Why

현재 시스템은 optimization 중심으로 구성되어 있어 독립적인 portfolio backtest 실행 경계가 없고, 요구사항과 변경 상태도 여러 문서와 대화에 분산되어 있다. 이번 변경에서 Backtest 기능 추가와 함께 요구사항/변경 관리 및 Agent 검증 흐름을 정돈한다.

## What Changes

- Portfolio Visualizer Backtest Portfolio를 레퍼런스로 독립적인 portfolio backtesting 기능을 추가한다.
- OpenSpec을 신규 변경의 요구사항과 진행 상태 관리 기준으로 도입한다.
- Agent가 Test → Real Run → Result Verification → Browser Verification → Fix → Re-verify 흐름으로 검증할 수 있는 프로젝트별 검증 구조를 추가한다.
- 기존 optimizer의 data, portfolio path, analytics, report/viewer 자산은 의미가 동일한 범위에서 재사용한다.

## Capabilities

### New Capabilities

- `portfolio-backtest`: 사용자가 하나 이상의 고정 비중 포트폴리오를 동일 기간과 benchmark 기준으로 백테스트하고 성과·위험·자산별 분석 결과를 비교할 수 있는 기능.

### Modified Capabilities

없음. 기존 optimization behavior 변경이 필요해지면 해당 capability를 별도 delta로 추가한다.

## Impact

- 입력/YAML contract와 runner에 backtest 실행 mode가 추가될 수 있다.
- portfolio/analytics/report/viewer의 공통 영역을 Backtest에서도 재사용한다.
- `openspec/`가 변경 계획과 상태의 기준 경로가 된다.
- Agent verification용 실행 진입점과 profile/browser 검증 구조가 추가된다.
- PV 결과와 화면은 reference이며 최종 acceptance는 내부 spec과 검증 기준을 따른다.
