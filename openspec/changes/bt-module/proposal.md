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
- Backtest v1은 PV의 핵심 구조를 참고해 1~3개 named portfolio, portfolio별 target allocation, optional benchmark, initial balance, 동일 기간 비교, periodic rebalancing, historical analytics/report를 정의한다.
- v1 사용자-facing 비교 한도는 3개 portfolio이지만 canonical portfolio representation은 collection 기반으로 두어 향후 한도 확장이 schema 재설계 없이 가능해야 한다.
- v1에서는 cashflow, rebalance bands, leverage를 제외한다.
- 배당 재투자 toggle은 두지 않고 Optimization과 Backtest 모두 shared `market-data`의 canonical total-return semantics를 사용한다.
- 기존 optimizer의 data, portfolio simulation, analytics, artifact, report/viewer 자산은 의미가 동일한 범위에서 재사용한다.
- Backtest 때문에 shared capability behavior가 변경되면 해당 OpenSpec delta와 Optimization 영향 검토를 함께 수행한다.
- Agent가 Test → Real Run → Result Verification → Browser Verification → Fix → Re-verify 흐름으로 검증할 수 있는 프로젝트별 검증 구조를 추가한다.

## Capabilities

### New Capabilities

- `portfolio-backtest`: 사용자가 v1에서 1~3개의 고정 target-allocation portfolio를 동일 기간과 optional benchmark 기준으로 backtest하고 realized performance, risk, allocation, asset/benchmark-relative analytics를 비교할 수 있는 기능. Portfolio collection model은 향후 3개 초과 확장을 허용하는 구조로 정의한다.

### Modified Shared Capabilities

- `market-data`: Optimization과 Backtest가 동일한 canonical total-return series를 사용하도록 return semantics를 명시한다.
- `portfolio-simulation`: 기존 monthly/yearly 외에 no-rebalance, quarterly, semiannual path와 initial-balance wealth path를 추가한다.
- `run-artifacts`: Backtest product mode, multi-portfolio collection input/result identity와 canonical Backtest result domain을 추가한다.
- `research-report`: Backtest-specific overview/allocation/growth comparison과 shared historical section applicability를 추가한다.

### Reused Without Behavior Delta

- `portfolio-analytics`

Backtest는 existing canonical historical analytics behavior를 그대로 재사용한다. 단순 재사용은 modified capability로 간주하지 않는다.

## V1 Scope Boundary

PV snapshot에 존재하더라도 다음 기능은 v1 normative requirement에서 제외한다.

- fixed contribution / withdrawal / percentage withdrawal 및 inflation adjustment
- rebalance bands의 absolute / relative deviation
- leverage, debt interest, maintenance margin, leveraged benchmark
- style analysis, factor regression, regime performance
- provider 기반 equity size/sector/style exposure
- imported benchmark / imported portfolio / lazy portfolio preset
- non-calendar periodic schedule

배당은 별도 Backtest option으로 모델링하지 않고 shared market-data total-return semantics로 처리한다.

## Dependency

기존 Optimization baseline은 `migrate-optimizer-to-openspec` change에서 먼저 capability별로 이관한다. 이관 완료 시 shared capability 변경이 기존 `portfolio-optimization`에 미치는 영향을 OpenSpec 기준으로 검토한다.

## Impact

- 입력/YAML contract와 runner에 Backtest 실행 경계가 추가된다.
- portfolio simulation에 새로운 periodic rebalancing mode와 wealth path가 추가된다.
- market-data의 total-return semantics는 Optimization과 Backtest 모두에 영향을 주므로 Optimization affected regression이 필요하다.
- report/viewer는 Backtest multi-portfolio identity와 product applicability를 처리해야 한다.
- Agent verification용 실행 진입점과 profile/browser 검증 구조가 추가된다.
- PV 결과와 화면은 reference이며 최종 acceptance는 내부 OpenSpec requirement와 검증 기준을 따른다.
