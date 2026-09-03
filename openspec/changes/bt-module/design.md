## Context

이번 change는 기존 Optimization 제품에 독립적인 Portfolio Backtest capability를 추가한다.

Backtest 기능 및 화면 구조의 외부 설계 레퍼런스:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/
```

PV는 비규범 reference다. PV의 계산값, 구현 방식, hidden field, 문구, pixel layout은 acceptance criterion이 아니다.

## Internal Baseline

기존 문서는 수정하지 않고 Backtest 설계 baseline으로 사용한다.

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

Backtest-specific 신규/변경 사항만 `openspec/changes/bt-module/`에 작성한다.

## Product and Shared Boundary

핵심 원칙은 **portfolio 생성은 제품별로 분리하고, portfolio simulation과 평가는 공유**하는 것이다.

```text
Optimization
market-data / shared statistics
  → objective / constraints / solver / efficient frontier
  → optimized or provided target weights
  → shared portfolio-simulation
  → shared portfolio-analytics
  → shared run-artifacts
  → product composition + shared historical report components

Backtest
market-data / shared statistics as applicable
  → user-defined target weights
  → shared portfolio-simulation
  → shared portfolio-analytics
  → shared run-artifacts
  → product composition + shared historical report components
```

제품별 차이는 capability 자체가 아니라 **어떤 capability를 호출하고 어떤 입력/UI policy와 report composition을 제공하는가**에 둔다.

### Product-specific: `portfolio-optimization`

Optimization만 objective, min/max constraint, target volatility 같은 optimization search policy, solver/residual, optimized-weight generation, Efficient Frontier를 소유한다.

Expected return, covariance, volatility, correlation 같은 statistics 계산 capability 자체는 shared다. Optimization은 이 shared statistics를 ex-ante weight 탐색에 사용한다. Backtest가 현재 특정 statistics를 사용하지 않더라도 shared capability 접근을 금지하거나 Optimization 전용 구현으로 복제하지 않는다.

### Product-specific: `portfolio-backtest`

Backtest만 product mode, named portfolio collection, user-defined target allocations, v1 3개 비교 한도, Time Period, optional benchmark, initial balance, Calendar Aligned와 historical-comparison input/composition contract를 소유한다.

Backtest Research Frontend는 v1에서 하나의 run-level rebalancing setting을 받아 모든 비교 portfolio에 동일하게 적용한다. 이것은 UI/input policy이며, backend rebalancing engine과 portfolio path generation은 shared `portfolio-simulation` capability를 재사용한다.

### Shared capabilities

- `market-data`: source/normalization, FX/common currency, coverage, total return, RF
- `statistics`: expected return, covariance, volatility, correlation 등 재사용 가능한 statistics 계산
- `portfolio-simulation`: target weights → return/weight/wealth path, drift, rebalancing engine/semantics, benchmark path
- `portfolio-analytics`: realized CAGR/risk/drawdown/trailing/rolling/active/correlation/decomposition, asset performance와 conditional benchmark analytics
- `run-artifacts`: YAML runner, input/result/raw/review/validation/report persistence, existing-run viewer independence
- `research-report`: identity/unit/N/A/semantic-axis/tooltip/responsive contract와 shared historical report components

동일 target weights와 동일 market-data/simulation setting이면 weights의 출처가 Optimization인지 Backtest인지와 무관하게 동일 historical path와 analytics를 만들어야 한다.

또한 Optimization과 Backtest에 동일한 의미로 존재하는 historical section은 동일 canonical analytics/artifact와 동일 shared report component를 사용해야 한다. Annual Returns, Drawdowns, Trailing/Rolling Returns, Asset Performance, Correlations, Return/Risk Decomposition, Annual Asset Returns, applicable benchmark-relative analytics처럼 의미가 같은 section을 product별 renderer에서 별도 계산하거나 별도 구현하여 divergence를 만들지 않는다.

Product-specific renderer/report layer는 전체 section 선택, 순서, overview, product-only section 같은 **composition**을 담당한다. Shared report component는 persisted canonical result/raw/review artifact를 소비하며 금융 metric/series를 product-specific하게 재계산하지 않는다.

## Input / Runner / Viewer Design

기존 YAML execution architecture를 유지한다.

```text
Input UI / CLI / Agent
        ↓
      YAML
        ↓
YAML adapter + validator
        ↓
product-specific canonical request
        ↓
shared runner / pipeline
        ↓
canonical result + raw/review
        ↓
product report composition
        ↓
shared historical report components + product-specific sections
```

Backtest request는 `OptimizationRequest`에 억지로 끼워 넣지 않는다. Product request boundary는 분리하되 이후 shared data/statistics/simulation/analytics/persistence/report component를 재사용한다. 완료된 run은 재계산 없이 persisted artifact만으로 Viewer에서 열 수 있어야 한다.

## Confirmed Decisions

### D1 Experiment identity

Backtest Experiment identity는 비교 portfolio 전체의 union ticker set이다.

```text
union ticker set 동일 → 같은 Experiment, 새 Run
union ticker 추가/삭제/교체 → 새 Experiment
```

Portfolio별 membership, weights, portfolio count/name, period, rebalancing, benchmark, initial balance가 바뀌어도 union ticker set이 같으면 같은 Experiment다.

### D2 Benchmark default

Core Backtest benchmark는 optional이다. Research Frontend에서는 미지정 시 SPY를 기본 적용하며 다른 benchmark 또는 benchmark 없음으로 override할 수 있다.

### D3 Initial balance default

Core Backtest는 positive initial balance를 받는다. Research Frontend 미지정 기본값은 10,000이다. Report는 actual input balance를 사용한다.

### D4 Analysis period default

사용자가 구체 기간을 지정하지 않으면 required portfolio assets와 적용 가능한 benchmark의 전체 common effective period를 사용한다.

### D5 Time Period mode

```text
Month-to-Month  ← Research Frontend default
Year-to-Year
```

Month-to-Month은 Start Year / First Month / End Year / Last Month를, Year-to-Year는 Start Year / End Year를 사용한다. Year selector는 특정 PV 연도 목록을 hard-code하지 않고 supported data range에서 동적으로 구성한다.

### D6 Portfolio name default

이름이 없으면 입력 순서대로 `Portfolio 1`, `Portfolio 2`, `Portfolio 3`을 자동 생성한다.

### D7 Backtest LLM analysis boundary

기존 `docs/llm-analysis-framework.md`는 Optimization/Frontier 분석 전용으로 유지한다. Backtest는 별도 `research-analysis` capability/guide에서 historical comparison을 다룬다.

```text
1. Effective data coverage
2. Return / risk comparison
3. Drawdown / recovery
4. Annual / rolling consistency
5. Benchmark-relative behavior when applicable
6. Contribution / diversification evidence
7. Evidence limitation / next Backtest
```

Backtest 결과만으로 optimal/efficient frontier/적정 최적 비중을 주장하지 않는다.

### D8 Human visual review gate

Machine-judgeable browser semantic verification은 applicable report change에서 수행한다. Human visual review는 layout/interaction이 materially 변경된 경우에만 completion gate로 요구한다.

### D9 Calendar Aligned

`Yes/No`를 모두 v1에서 지원한다. Research Frontend 미지정 기본값은 기존 calendar-aligned behavior를 보존하기 위해 `Yes`로 둔다.

- `Yes`: calendar boundary 기준
  - yearly = Jan
  - semiannual = Jan / Jul
  - quarterly = Jan / Apr / Jul / Oct
- `No`: 첫 active month를 anchor로 interval 기준
  - yearly = 12개월
  - semiannual = 6개월
  - quarterly = 3개월
- monthly와 none은 alignment에 영향을 받지 않는다.

### D10 Rebalancing scope/default

Backtest Research Frontend는 한 run 전체에 하나의 rebalancing setting을 입력받아 모든 비교 portfolio에 동일하게 적용한다. Portfolio별 독립 rebalancing 입력은 v1 UI에서 지원하지 않는다.

```text
No rebalancing
Annually
Semi-annually
Quarterly
Monthly  ← Research Frontend default
```

이 제한은 Backtest input/UI policy다. 실제 portfolio path 생성과 rebalancing 계산은 Optimization과 Backtest가 동일한 shared `portfolio-simulation` capability를 사용한다. Rebalance Bands는 v1 제외다.

### D11 Display Income

v1에서 제외한다. Canonical total return은 유지하되 dividend/distribution income 자체를 별도 series/report로 분해하지 않는다.

## PV Settings Mapping

| PV setting | Backtest v1 |
|---|---|
| Time Period | 채택: Month-to-Month / Year-to-Year |
| Start Year | 채택 |
| First Month | Month-to-Month에서 채택 |
| End Year | 채택 |
| Last Month | Month-to-Month에서 채택 |
| Calendar Aligned | 채택: Yes / No, default Yes |
| Initial Amount | 채택: frontend default 10,000 |
| Cashflows | 제외 |
| Rebalancing | 채택: bands 제외, run-level input, default Monthly; backend engine은 shared |
| Leverage Type | 제외 |
| Reinvest Dividends | toggle 제외, canonical total return 사용 |
| Display Income | 제외 |
| Style Analysis | 제외 |
| Factor Regression | 제외 |
| Show Regime Performance | 제외 |

## Total-return Design

Optimization과 Backtest 모두 distribution reinvestment를 반영한 canonical total-return 의미를 사용한다. Price-only return을 total return으로 silent fallback하지 않는다.

현재 FDR 구조에서 total return을 신뢰성 있게 만들 수 있는지 구현 전에 조사한다. 필요한 data-source 보강은 최소 변경으로 설계하며 shared change이므로 Optimization historical regression을 포함한다.

## Rebalancing Design

Backtest의 run-level rebalancing input과 Calendar Aligned setting은 모든 비교 portfolio에 동일하게 전달되며, 실제 계산은 shared portfolio-simulation/rebalancing engine이 담당한다.

`Calendar Aligned = Yes`:

```text
yearly      → Jan
semiannual  → Jan / Jul
quarterly   → Jan / Apr / Jul / Oct
monthly     → every active month
none        → initial target 이후 drift
```

`Calendar Aligned = No`:

```text
yearly      → first active month + 12개월 간격
semiannual  → first active month + 6개월 간격
quarterly   → first active month + 3개월 간격
monthly     → every active month
none        → initial target 이후 drift
```

첫 active period에는 항상 target weights를 적용한다. Rebalance event 사이에서는 canonical drift semantics를 사용한다.

## Portfolio Comparison Model

비교 portfolio들의 asset union을 common row set으로 표현한다. 각 portfolio는 각 asset에 독립적인 target weight를 가지며 미사용 asset은 0%로 표현할 수 있다.

각 portfolio target weights 합은 100%다. Canonical schema는 collection 구조이며 v1 3개 제한은 validation policy다.

## Result / Report Design

Backtest canonical result는 최소 다음을 구분한다.

- configuration / product mode / Time Period
- Calendar Aligned / run-level rebalancing input
- portfolio definitions / target allocations
- effective data coverage
- portfolio return / weight / wealth paths
- optional benchmark path
- shared historical analytics
- correlations / decomposition
- report-ready comparison data

Backtest는 optimization-specific objective/constraints/solver/optimized-weight/Efficient Frontier 결과를 생성하지 않는다. Shared statistics capability가 존재하더라도 Backtest가 필요하지 않은 ex-ante statistics output을 억지로 report에 노출하지 않는다.

Report hierarchy:

1. run identity / Time Period / requested-effective period / benchmark / Calendar Aligned / rebalancing / portfolio identities
2. target allocation comparison
3. actual initial-balance growth / Performance Summary
4. annual / monthly / trailing / rolling returns
5. drawdown
6. asset performance / correlations / decomposition
7. benchmark가 있을 때 active analytics

이 중 Optimization과 동일 의미를 가진 historical section은 shared report component를 사용하고, Backtest-specific overview/target-allocation comparison 및 Optimization-only section의 포함/제외는 product report composition이 결정한다.

Display Income section은 v1에서 제공하지 않는다.

## Research Execution / Input / Analysis

기존 Study / Experiment / Run / `control/execute.yaml` 구조를 재사용한다. Backtest 전용 orchestration DB, opaque request id, 별도 Agent execution engine은 만들지 않는다.

Research Frontend는 이미 받은 값을 다시 묻지 않고 mechanical validation을 먼저 수행한다. Backtest에서 optimizer objective/min/max/target-vol 질문은 하지 않는다. Canonical defaults는 effective YAML/input에 명시적으로 persist한다.

## Agent Verification

```text
Test
→ Real Run
→ Result Verification
→ Browser Verification (if applicable)
→ Fix
→ Re-verify
```

Shared capability change는 해당 capability를 소비하는 Optimization/Backtest affected-scope regression을 포함한다. Shared report component change는 두 product 중 applicable한 historical section의 semantic regression을 포함한다. Browser verification은 PV pixel parity가 아니라 internal OpenSpec semantic contract를 검사한다. Material layout/interaction change일 때만 human visual review를 추가한다.

## Remaining Technical Gate

사용자 product decision은 D1-D11까지 모두 확정되었다. 구현 전 남은 technical gate는 다음이다.

1. OpenSpec strict validation
2. total-return data-source feasibility 및 필요한 최소 market-data 보강 결정

## Asset name snapshot impact

- changed shared capability: market-data / research-input metadata handoff
- reason: replace manually authored instrument names with FDR provider names while retaining the shared `AssetSpec.name` contract
- affected products: portfolio-optimization, portfolio-backtest
- affected regression: FDR metadata resolution, shared config hydration, report-level asset ordering/name rendering

