## Context

이번 change는 기존 Optimization 제품에 독립적인 Portfolio Backtest capability를 추가한다.

Backtest 기능 및 화면 구조의 외부 설계 레퍼런스:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/
```

PV snapshot에서 Settings / Portfolio Assets, 최대 3개 portfolio, benchmark, initial amount, Time Period, periodic rebalancing, advanced options, performance/active/drawdown/rolling/asset 분석 구조를 확인했다.

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

`docs/report-visual-overrides-20260829.md`는 Optimization report correction history로 유지한다. Backtest-specific 신규/변경 사항만 `openspec/changes/bt-module/`에 작성한다.

## Product and Shared Boundary

핵심 원칙은 **portfolio 생성과 portfolio 평가를 분리**하는 것이다.

```text
Optimization
market-data
  → ex-ante estimation / constraints / objective / efficient frontier
  → optimized or provided target weights
  → portfolio-simulation
  → portfolio-analytics
  → run-artifacts / research-report

Backtest
market-data
  → user-defined target weights
  → portfolio-simulation
  → portfolio-analytics
  → run-artifacts / research-report
```

### Product-specific: `portfolio-optimization`

Optimization만 소유한다.

- expected return / covariance / expected volatility / ex-ante Sharpe
- min/max / long-only / fully-invested constraints
- Maximum Sharpe / Target Volatility objective
- solver/residual validation
- Efficient Frontier 및 frontier allocation

### Product-specific: `portfolio-backtest`

Backtest만 소유한다.

- Backtest product mode / run identity
- named portfolio collection
- portfolio별 user-defined target allocation
- v1 사용자-facing 최대 3개 비교
- Time Period mode와 requested boundaries
- optional benchmark
- initial balance
- periodic rebalancing setting
- optimization objective/constraint 없이 historical comparison 수행

### Shared `market-data`

- market source / normalization
- FX/common currency
- requested/effective period / common coverage
- completed-month filtering
- canonical total-return series
- risk-free configuration/evidence

같은 asset/period는 두 product에서 같은 historical observations를 사용해야 한다.

### Shared `portfolio-simulation`

- target weights + asset returns → portfolio path
- weight drift
- periodic rebalancing semantics
- benchmark path
- normalized/actual initial-balance wealth path

동일 weights와 동일 policy라면 weights의 출처가 optimizer인지 user input인지와 무관하게 동일 historical path를 만들어야 한다.

### Shared `portfolio-analytics`

CAGR, realized return/volatility, Sharpe/Sortino, MDD, drawdown, annual/monthly/trailing/rolling, active/TE/IR, Up/Down, correlation, return/risk decomposition은 기존 canonical behavior를 재사용한다.

### Shared `run-artifacts`

YAML runner, `input.yaml`, `result.json`, raw/review, validation evidence, report artifact, existing-run viewer independence는 공유한다. Product-specific input/result domain만 분리한다.

### Shared `research-report`

기존 report identity/unit/N/A/semantic-axis/tooltip/responsive contract와 shared historical section을 재사용한다. Optimization-only Efficient Frontier와 Backtest-specific overview/allocation/growth는 section applicability로 구분한다.

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
Viewer / report
```

Backtest request는 `OptimizationRequest`에 억지로 끼워 넣지 않는다. Product-specific request model은 분리하되 이후 shared data/simulation/analytics/persistence를 재사용한다.

Backtest UI는 두 번째 finance execution path를 만들지 않는다. 완료된 run은 다시 계산하지 않고 persisted artifact만으로 Viewer에서 열 수 있어야 한다.

## Confirmed Product Decisions

### D1 Experiment identity: union ticker set

Backtest Experiment identity는 비교 portfolio 전체의 union asset ticker set이다.

```text
union ticker set 동일 → 같은 Experiment, 새 Run
union ticker 추가/삭제/교체 → 새 Experiment
```

Portfolio별 asset membership, weights, portfolio count/name, period, rebalancing, benchmark, initial balance가 바뀌어도 union ticker set이 같으면 같은 Experiment다.

### D2 Research Frontend benchmark default: SPY

Core Backtest capability의 benchmark는 optional이다. 다만 Research Frontend에서 사용자가 별도 지정하지 않으면 SPY를 기본 적용한다. 사용자는 다른 benchmark 또는 benchmark 없음으로 override할 수 있다.

### D3 Initial balance default: 10,000

Core capability는 positive initial balance를 받는다. Research Frontend에서 미지정 시 10,000을 적용한다. Report는 actual input balance를 사용하며 Optimization report의 normalized 10,000 convention으로 덮어쓰지 않는다.

### D4 Analysis period default: full common period

사용자가 구체 기간을 지정하지 않으면 required asset과 적용 가능한 benchmark의 전체 common effective period를 사용한다. 실제 requested/effective boundaries는 artifact에 기록한다.

### D5 Time Period mode

사용자-facing Time Period는 다음 두 mode를 제공한다.

```text
Month-to-Month  ← default
Year-to-Year
```

`Month-to-Month`:

```text
Start Year
First Month
End Year
Last Month
```

`Year-to-Year`:

```text
Start Year
End Year
```

Year selector에 PV snapshot의 1985~2026 목록을 hard-code하지 않는다. 실제 supported date range에 따라 동적으로 구성한다.

### D6 Portfolio name default

이름이 없으면 입력 순서대로 `Portfolio 1`, `Portfolio 2`, `Portfolio 3`을 자동 생성한다.

### D7 Backtest LLM analysis boundary

기존 `docs/llm-analysis-framework.md`는 Optimization/Frontier 분석 전용으로 그대로 둔다. Backtest는 별도 `research-analysis` capability/guide에서 historical comparison을 다룬다.

분석 기본 순서:

```text
1. Effective data coverage
2. Return / risk comparison
3. Drawdown / recovery
4. Annual / rolling consistency
5. Benchmark-relative behavior (when benchmark exists)
6. Contribution / diversification evidence
7. Evidence limitation / next Backtest
```

Backtest 결과만으로 optimal/efficient frontier/적정 최적 비중을 주장하지 않는다.

### D8 Human visual review gate

Machine-judgeable browser semantic verification은 applicable report change에서 수행한다. Human visual review는 layout/interaction이 materially 변경된 경우에만 completion gate로 요구한다.

## PV Settings Mapping

사용자가 제공한 PV Settings 요소를 v1 관점에서 다음처럼 매핑한다.

| PV setting | v1 상태 |
|---|---|
| Time Period | 채택, Month-to-Month / Year-to-Year |
| Start Year | 채택 |
| First Month | Month-to-Month에서 채택 |
| End Year | 채택 |
| Last Month | Month-to-Month에서 채택 |
| Calendar Aligned | 추가 결정 필요 |
| Initial Amount | 채택, frontend default 10,000 |
| Cashflows | v1 제외 |
| Rebalancing | 채택, bands 제외. scope/default 추가 결정 필요 |
| Leverage Type | v1 제외 |
| Reinvest Dividends | 별도 toggle 제외, canonical total return으로 대체 |
| Display Income | 추가 결정 필요 |
| Style Analysis | v1 제외 |
| Factor Regression | v1 제외 |
| Show Regime Performance | v1 제외 |

## Total-return Design

Optimization과 Backtest 모두 distribution reinvestment를 반영한 canonical total-return 의미를 사용한다.

Price-only return을 total return으로 silent fallback하지 않는다. 현재 FDR 구조에서 total return을 신뢰성 있게 만들 수 있는지 구현 전에 조사하며, 필요한 data-source 보강은 최소 변경으로 설계한다.

이 shared 변경은 Optimization historical regression을 요구한다.

## Rebalancing Design

v1은 다음 policy를 지원한다.

```text
none
yearly
semiannual
quarterly
monthly
```

`rebalance bands`는 v1 제외다.

현재 shared simulation delta에는 `Calendar Aligned = Yes`일 때의 calendar schedule을 정의한다.

```text
yearly      → Jan
semiannual  → Jan / Jul
quarterly   → Jan / Apr / Jul / Oct
monthly     → every active month
none        → initial target 이후 drift
```

Analysis가 schedule 중간에서 시작하면 첫 active period에 target weights를 적용하고 이후 해당 schedule을 따른다.

`Calendar Aligned = No` 지원 여부와 anchor semantics, rebalancing setting의 run/global vs portfolio-specific scope, 미지정 default는 아래 Remaining Decisions에서 확정한다.

## Portfolio Comparison Model

비교 portfolio들의 asset union을 common row set으로 표현할 수 있다. 각 portfolio는 각 asset에 독립적인 target weight를 가지며 미사용 asset은 0%로 표현할 수 있다.

각 portfolio target weights 합은 100%다. 각 portfolio는 독립적인 return/wealth/weight path를 가진다.

v1의 3개 제한은 product validation policy다. Canonical schema 자체는 portfolio collection이므로 향후 cardinality만 늘릴 수 있어야 한다.

## Result / Report Design

Backtest canonical result는 최소 다음을 구분한다.

- configuration / product mode / Time Period
- portfolio definitions / target allocations
- effective data coverage
- portfolio return / weight / wealth paths
- optional benchmark path
- shared historical analytics
- correlations / decomposition
- report-ready comparison data

Backtest는 optimization-specific ex-ante statistics나 Efficient Frontier를 생성하지 않는다.

Backtest report hierarchy:

1. run identity / Time Period / requested-effective period / benchmark / portfolio / rebalancing
2. target allocation comparison
3. actual initial-balance growth / Performance Summary
4. annual / monthly / trailing / rolling returns
5. drawdown
6. asset performance / correlations / decomposition
7. benchmark가 있을 때 active analytics

## Research Execution

기존 Study / Experiment / Run / `control/execute.yaml` 구조를 재사용한다.

```text
User <-> ChatGPT
       ↓
Study + Experiment YAML (explicit product mode)
       ↓
control/execute.yaml
       ↓
GitHub Actions / canonical runner
       ↓
runs/<run_id>/
```

Backtest 전용 orchestration DB, request id, 별도 Agent execution engine은 만들지 않는다.

## Research Input

기존 Research Frontend 원칙을 유지한다.

- 이미 받은 정보는 다시 묻지 않음
- 기계적 검증은 시스템이 먼저 수행
- portfolio 구성/weights 같은 실제 연구결정만 필요한 경우 질문
- canonical default는 자동 적용하되 effective input에 명시
- explicit execution intent 후 중복 승인 질문 없음
- Backtest에서 optimizer objective/min/max/target-vol 질문 없음

## Agent Verification

```text
Test
→ Real Run
→ Result Verification
→ Browser Verification (if applicable)
→ Fix
→ Re-verify
```

Shared capability change는 affected Optimization regression을 포함한다. Browser verification은 PV pixel parity가 아니라 internal OpenSpec semantic contract를 검사한다.

## Remaining Decisions

### D9. Calendar Aligned

**A. Yes/No 모두 v1 지원**

추천 semantics:

- `Yes`: calendar year/quarter 기준. Yearly=Jan, Semiannual=Jan/Jul, Quarterly=Jan/Apr/Jul/Oct
- `No`: 첫 active month를 anchor로 Yearly=12개월, Semiannual=6개월, Quarterly=3개월 주기

**B. v1은 Yes만 지원**

구현과 검증은 단순하지만 PV settings 일부를 줄인다.

### D10. Rebalancing setting scope/default

**A. run 전체에 하나의 rebalancing setting 적용, default=Monthly**
- PV Settings 구조와 동일
- 여러 portfolio를 같은 조건에서 비교하기 쉬움
- 추천

**B. portfolio별 독립 rebalancing 허용, default=Monthly**
- 한 run에서 전략 차이까지 비교 가능
- input/report 복잡도 증가

**C. run 전체 공통이지만 default 없이 사용자 선택 필수**

### D11. Display Income

**A. v1 제외**
- canonical total return은 유지하되 dividend/income breakdown은 별도 data contract가 필요함
- 추천

**B. v1 지원**
- distribution income series와 report presentation contract를 추가 정의해야 함

## After Decisions

D9-D11 확정 후:

1. `portfolio-backtest`, `portfolio-simulation`, `research-input`, `research-report`의 pending 문구를 최종 requirement로 치환한다.
2. `tasks.md` decision gate를 닫는다.
3. OpenSpec strict validation을 수행한다.
4. 구현 전에 total-return data-source feasibility를 technical investigation으로 닫는다.
