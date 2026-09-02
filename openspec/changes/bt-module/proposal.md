## Why

현재 시스템은 Optimization 중심으로 구성되어 있어 독립적인 portfolio Backtest 실행 경계가 없다. 이번 변경에서 Portfolio Visualizer Backtest Portfolio를 외부 비규범 설계 레퍼런스로 사용해 Backtest 제품 기능을 추가하고, 기존 내부 finance/UI/runner/architecture contract를 재사용하며 OpenSpec과 Agent verification 흐름을 실제 개발 계약으로 사용한다.

PV reference snapshot:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
```

PV는 feature/information-architecture reference이며 내부 calculation contract나 acceptance criterion이 아니다.

## What Changes

- 독립적인 `portfolio-backtest` product mode를 추가한다.
- Backtest v1은 1~3개 named portfolio, portfolio별 target allocation, optional benchmark, initial balance, 동일 기간 비교, periodic rebalancing, realized historical analytics/report를 지원한다.
- v1 사용자-facing 한도는 3개이지만 canonical portfolio representation은 extensible collection으로 둔다.
- Time Period는 `Month-to-Month` / `Year-to-Year`를 지원하고 Research Frontend 기본 mode는 `Month-to-Month`로 둔다.
- `Month-to-Month`는 Start Year / First Month / End Year / Last Month, `Year-to-Year`는 Start Year / End Year를 사용한다.
- `Calendar Aligned = Yes/No`를 모두 지원한다. Yes는 calendar boundary, No는 첫 active month를 anchor로 3/6/12개월 periodic schedule을 만든다.
- Rebalancing은 한 run 전체에 공통으로 적용하며 `No rebalancing / Annually / Semi-annually / Quarterly / Monthly`를 지원하고 기본값은 `Monthly`다.
- Research Frontend 기본 benchmark는 SPY이며 사용자가 다른 benchmark 또는 benchmark 없음으로 override할 수 있다.
- Research Frontend 기본 initial balance는 10,000, 기간 미지정 시 전체 common effective period, portfolio name 미지정 시 `Portfolio 1..3`을 사용한다.
- Backtest Experiment identity는 비교 portfolio 전체의 union ticker set으로 정의한다.
- v1에서 cashflow, rebalance bands, leverage, Display Income, style analysis, factor regression, regime performance는 제외한다.
- dividend reinvestment toggle은 두지 않고 Optimization/Backtest 모두 shared `market-data`의 canonical total-return semantics를 사용한다.
- 기존 market-data, simulation, analytics, YAML runner, artifact, report/viewer architecture를 의미가 같은 범위에서 재사용한다.
- 기존 Research Frontend / Study-Experiment-Run 흐름에 Backtest를 통합한다.
- Backtest 결과 분석은 optimizer 전용 framework와 분리된 historical-comparison capability/guide로 유지한다.
- Agent verification은 Test → Real Run → Result Verification → Browser Verification(if applicable) → Fix → Re-verify 흐름을 사용한다.
- Human visual review는 layout/interaction이 materially 변경된 경우에만 completion gate로 사용한다.

## Capabilities

### New Product Capability

- `portfolio-backtest`: 사용자가 v1에서 1~3개의 고정 target-allocation portfolio를 동일 historical period와 optional benchmark에서 비교하고 realized performance/risk/asset analytics를 확인하는 기능. Canonical portfolio model은 향후 3개 초과 확장이 가능한 collection 구조다.

### Modified Shared Capabilities

- `market-data`: Optimization과 Backtest가 동일 canonical total-return series를 사용하도록 return semantics를 추가한다.
- `portfolio-simulation`: 기존 monthly/yearly 외에 no-rebalance, quarterly, semiannual path와 initial-balance wealth path를 추가하고 calendar-aligned / first-active-month anchored schedule semantics를 정의한다.
- `run-artifacts`: explicit product mode, Backtest portfolio collection, Time Period, Calendar Aligned, run-level rebalancing input/result identity와 canonical Backtest result domain을 추가한다.
- `research-report`: Backtest overview/allocation/growth, actual initial-balance semantics, realized-only Performance Summary applicability와 shared historical section 적용을 추가한다.

### Reused Without Behavior Delta

- `portfolio-analytics`: 기존 realized/historical analytics behavior를 그대로 재사용한다.

### Research / Tooling Capabilities

- `research-execution`: Backtest를 기존 Study / Experiment / Run / execution-control 흐름에 통합하고 union ticker set을 Experiment identity로 사용한다.
- `research-input`: LLM/User Research Frontend가 product intent에 따라 Backtest 입력만 수집하고 확정된 canonical defaults를 적용한다.
- `research-analysis`: Backtest 결과를 Optimization/optimality와 혼동하지 않고 historical comparison으로 분석한다.
- `agent-verification`: Agent가 requirement를 변경하지 않고 test/real-run/result/browser evidence를 남기며 material visual change에만 human review gate를 적용한다.

## Existing Internal Baseline

기존 문서는 수정하지 않고 Backtest OpenSpec의 baseline/reference로 사용한다.

```text
Finance / calculation behavior   docs/specification.md
Report UI / interaction          docs/report-ui-specification.md
Input / YAML / runner / viewer   docs/input-ui-contract.md
Architecture / responsibility    docs/architecture.md
Validation procedure             docs/visual-acceptance-contract.md
Research execution               docs/research-operation-pipeline.md
LLM research input               docs/llm-research-input-contract.md
Optimizer result analysis        docs/llm-analysis-framework.md
```

Backtest-specific delta만 이 change에 작성한다. `docs/report-visual-overrides-20260829.md`는 Optimization report correction history로 유지하며 Backtest requirement source로 승격하지 않는다.

## V1 Scope Boundary

PV snapshot에 존재하더라도 다음은 v1 normative requirement에서 제외한다.

- fixed contribution / withdrawal / percentage withdrawal 및 inflation adjustment
- rebalance bands의 absolute / relative deviation
- leverage, debt interest, maintenance margin, leveraged benchmark
- Display Income / distribution-income breakdown
- style analysis, factor regression, regime performance
- provider 기반 equity size/sector/style exposure
- imported benchmark / imported portfolio / lazy portfolio preset

Dividend reinvestment는 별도 setting이 아니라 canonical total-return semantics로 처리한다.

## Dependency

기존 Optimization baseline은 `migrate-optimizer-to-openspec` change에서 capability별로 이관한다. Backtest가 shared capability behavior를 변경하면 해당 capability를 사용하는 Optimization affected regression을 수행한다.

## Impact

- YAML/input model과 runner에 explicit Backtest product boundary와 Time Period / Calendar Aligned / run-level rebalancing setting이 추가된다.
- portfolio simulation에 추가 periodic rebalancing mode, calendar/non-calendar schedule과 initial-balance path가 추가된다.
- canonical total-return semantics는 Optimization historical analysis에도 영향을 준다.
- report/viewer는 multi-portfolio Backtest identity와 product-specific section applicability를 처리해야 한다.
- Research workflow는 Optimization과 같은 execution boundary를 사용하면서 Backtest-specific input/analysis branch를 가진다.
- Agent verification용 최소 실행/결과/browser evidence 구조가 추가된다.

## Decision Status

Backtest v1의 product/research/verification decision gate D1-D11은 모두 확정되었다. 구현 전 남은 설계 검토는 OpenSpec strict validation과 total-return data-source feasibility 확인이다.
