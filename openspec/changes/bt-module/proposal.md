## Why

현재 시스템은 optimization 중심으로 구성되어 있어 독립적인 portfolio backtest 실행 경계가 없다. 이번 변경에서 Portfolio Visualizer Backtest Portfolio를 외부 비규범 설계 레퍼런스로 사용해 Backtest 기능을 추가하고, OpenSpec 및 Agent 검증 체계를 실제 개발 흐름에 적용한다.

PV reference snapshot은 다음 위치에 보관한다.

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
```

PV는 기능, 정보구조, interaction 연구자료이며 내부 계산 contract나 acceptance criterion이 아니다.

## What Changes

- 독립적인 portfolio backtesting 기능을 추가한다.
- Optimization과 Backtest는 별도 product capability로 관리한다.
- Backtest initial specification은 PV의 핵심 구조를 참고해 1~3개 named portfolio, portfolio별 target allocation, optional benchmark, initial balance, 동일 기간 비교, periodic rebalancing, historical analytics/report를 정의한다.
- 기존 optimizer의 data, portfolio simulation, analytics, artifact, report/viewer 자산은 의미가 동일한 범위에서 재사용한다.
- Backtest 때문에 shared capability behavior가 변경되면 해당 OpenSpec delta와 Optimization 영향 검토를 함께 수행한다.
- Agent가 Test → Real Run → Result Verification → Browser Verification → Fix → Re-verify 흐름으로 검증할 수 있는 프로젝트별 검증 구조를 추가한다.

## Capabilities

### New Capabilities

- `portfolio-backtest`: 사용자가 1~3개의 고정 target-allocation portfolio를 동일 기간과 optional benchmark 기준으로 backtest하고 realized performance, risk, allocation, asset/benchmark-relative analytics를 비교할 수 있는 기능.

### Modified Shared Capabilities

- `portfolio-simulation`: 기존 monthly/yearly 외에 no-rebalance, quarterly, semiannual path와 initial-balance wealth path를 추가한다.
- `run-artifacts`: Backtest product mode, multi-portfolio input/result identity와 canonical Backtest result domain을 추가한다.
- `research-report`: Backtest-specific overview/allocation/growth comparison과 shared historical section applicability를 추가한다.

### Reused Without Behavior Delta

- `market-data`
- `portfolio-analytics`

Backtest는 위 capability의 existing canonical behavior를 그대로 재사용한다. 단순 재사용은 modified capability로 간주하지 않는다.

## Initial Scope Boundary

PV snapshot에 존재하더라도 cashflow, rebalance bands, leverage, dividend/income option, style/factor/regime analysis, provider exposure, imported portfolio/benchmark 등은 internal semantics 또는 scope 결정이 필요한 항목이므로 현재 initial normative requirement에는 포함하지 않는다. 사용자 결정 후 필요한 항목만 delta를 추가한다.

## Dependency

기존 Optimization baseline은 `migrate-optimizer-to-openspec` change에서 capability별로 이관한다. 이관 완료 시 shared capability 변경이 기존 `portfolio-optimization`에 미치는 영향을 OpenSpec 기준으로 검토한다.

## Impact

- 입력/YAML contract와 runner에 Backtest 실행 경계가 추가된다.
- portfolio simulation에 새로운 periodic rebalancing mode와 wealth path가 추가된다.
- 공통 capability 변경 시 Backtest 구현 검증과 함께 Optimization affected regression이 필요하다.
- report/viewer는 Backtest multi-portfolio identity와 product applicability를 처리해야 한다.
- Agent verification용 실행 진입점과 profile/browser 검증 구조가 추가된다.
- PV 결과와 화면은 reference이며 최종 acceptance는 내부 OpenSpec requirement와 검증 기준을 따른다.
