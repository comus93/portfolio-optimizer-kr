## Context

이번 change는 기존 Optimization 제품에 독립적인 Portfolio Backtest capability를 추가한다.

외부 feature/UI 설계 레퍼런스:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/
```

PV snapshot에서 Settings / Portfolio Assets, 최대 3개 portfolio, benchmark, initial amount, periodic rebalancing, advanced options, performance/active/drawdown/rolling/asset 분석 구조를 확인했다.

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

`docs/report-visual-overrides-20260829.md`는 Optimization report correction history로 유지한다. Backtest requirement를 새로 정의하는 source로 사용하지 않는다.

Backtest-specific 신규/변경 사항만 `openspec/changes/bt-module/`에 작성한다.

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

### `portfolio-optimization`

Optimization만 소유한다.

- expected return / covariance / expected volatility / ex-ante Sharpe
- min/max / long-only / fully-invested constraints
- Maximum Sharpe / Target Volatility objective
- solver/residual validation
- Efficient Frontier 및 frontier allocation

Backtest는 weights를 찾는 제품이 아니므로 위 계산을 요구하지 않는다.

### `portfolio-backtest`

Backtest만 소유한다.

- Backtest product mode / run identity
- named portfolio collection
- portfolio별 user-defined target allocation
- v1 사용자-facing 최대 3개 비교
- optional benchmark
- initial balance
- portfolio별 periodic rebalancing policy
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
- rebalancing semantics
- benchmark path
- normalized/actual initial-balance wealth path

동일 weights와 동일 policy라면 weights의 출처가 optimizer인지 user input인지와 무관하게 동일 historical path를 만들어야 한다.

### Shared `portfolio-analytics`

CAGR, realized return/volatility, Sharpe/Sortino, MDD, drawdown, annual/monthly/trailing/rolling, active/TE/IR, Up/Down, correlation, return/risk decomposition은 기존 canonical behavior를 재사용한다.

### Shared `run-artifacts`

YAML runner, `input.yaml`, `result.json`, raw/review, validation evidence, report artifact, existing-run viewer independence는 공유한다. Product-specific result domain만 분리한다.

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

## Confirmed V1 Decisions

- Cashflow: v1 제외
- Rebalance bands: v1 제외
- Leverage: v1 제외
- Portfolio count: v1 UI/validation 최대 3개
- Portfolio model: fixed `portfolio1/2/3`이 아닌 extensible collection
- Dividend handling: 별도 reinvest toggle 없이 shared canonical total return
- PV style/factor/regime/provider exposure/imported portfolio/imported benchmark/lazy preset/non-calendar schedule: v1 제외

## PV Mapping

### Adopt

- Settings와 Portfolio Assets를 개념적으로 분리
- custom portfolio name
- shared asset rows + portfolio별 allocation
- optional benchmark
- initial amount
- 동일 기간 multi-portfolio 비교
- No / Monthly / Quarterly / Semi-annual / Annual rebalancing
- allocation / growth / performance / annual / monthly / drawdown / rolling / asset / benchmark-relative 결과 구조

### Do not copy

- PV 계산값 또는 provider convention
- pixel layout
- hidden/internal field
- provider-dependent exposure
- v1 제외 advanced feature

## Total-return Design

Optimization과 Backtest 모두 distribution reinvestment를 반영한 canonical total-return 의미를 사용한다.

Price-only return을 total return으로 silent fallback하지 않는다. 현재 FDR 구조에서 total return을 신뢰성 있게 만들 수 있는지 구현 단계에서 조사하며, 필요한 data-source 보강은 별도 technical design으로 결정한다.

이 shared 변경은 Optimization historical regression을 요구한다.

## Rebalancing Design

Canonical simulation은 monthly return observations 기준으로 다음 calendar-aligned policy를 지원한다.

- `none`: 첫 active period에 target weights를 적용한 뒤 계속 drift
- `monthly`: 매 active month 시작에 target weights 적용
- `quarterly`: 첫 active period + 1/4/7/10월 첫 available period
- `semiannual`: 첫 active period + 1/7월 첫 available period
- `yearly`: 첫 active period + 각 calendar year 첫 available period

중간 시점에서 analysis가 시작되면 첫 active period에는 target weights를 적용하고 이후 정상 schedule을 따른다.

## Portfolio Comparison Model

비교 portfolio들의 asset union을 common row set으로 표현할 수 있다. 각 portfolio는 각 asset에 독립적인 target weight를 가지며 미사용 asset은 0%로 표현할 수 있다.

각 portfolio target weights 합은 100%다. 각 portfolio는 독립적인 rebalancing/drift/return/wealth path를 가진다.

v1의 3개 제한은 product validation policy다. Canonical schema 자체는 portfolio collection이므로 향후 cardinality만 늘릴 수 있어야 한다.

## Result / Report Design

Backtest canonical result는 최소 다음을 구분한다.

- configuration / product mode
- portfolio definitions / target allocations
- effective data coverage
- portfolio return / weight / wealth paths
- optional benchmark path
- shared historical analytics
- correlations / decomposition
- report-ready comparison data

Backtest는 optimization-specific ex-ante statistics나 Efficient Frontier를 생성하지 않는다.

Backtest report hierarchy:

1. run identity / requested-effective period / benchmark / portfolio / rebalancing
2. target allocation comparison
3. actual initial-balance growth / Performance Summary
4. annual / monthly / trailing / rolling returns
5. drawdown
6. asset performance / correlations / decomposition
7. benchmark가 있을 때 active analytics

Backtest Start Balance는 user input actual initial balance다. Optimization report의 normalized 1.0 → 10,000 presentation convention을 Backtest에 강제하지 않는다.

## Research Execution Draft

기존 `docs/research-operation-pipeline.md`의 Study / Experiment / Run / `control/execute.yaml` 구조를 그대로 재사용하는 방향으로 초안을 작성했다.

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

아직 미확정인 핵심은 **Backtest Experiment identity**다. 아래 Open Decision D1에서 결정한다.

## Research Input Draft

기존 `docs/llm-research-input-contract.md`의 원칙을 유지한다.

- 이미 받은 정보는 다시 묻지 않음
- 기계적 검증은 시스템이 먼저 수행
- 투자/연구 결과를 바꾸는 사용자 결정만 질문
- canonical default는 필요 시 고지 후 자동 적용하고 effective input에 명시
- 사용자가 이미 실행 의도를 밝혔다면 중복 승인 질문을 만들지 않음

Backtest에서는 optimizer min/max/objective/target-vol을 질문하지 않는다. Portfolio 구성/weights가 primary user decision이다.

Benchmark, initial balance, analysis period, rebalancing, default portfolio name의 Research Frontend policy는 아래 D2-D6에서 결정한다.

## Research Analysis Draft

기존 `docs/llm-analysis-framework.md`는 Optimizer/Frontier 해석에 강하게 결합되어 있으므로 Backtest 분석은 다음 순서의 별도 historical-comparison 초안을 작성했다.

```text
1. Effective data coverage
2. Return / risk comparison
3. Drawdown / recovery
4. Annual / rolling consistency
5. Benchmark-relative behavior (when benchmark exists)
6. Contribution / diversification evidence
7. Evidence limitation / next Backtest
```

Backtest 결과만으로 `optimal`, `efficient frontier`, `적정 최적 비중`을 주장하지 않는다. Canonical result facts와 경제적 해석/가설을 분리한다.

문서/Capability 경계는 D7에서 결정한다.

## Agent Verification Draft

Backtest change의 verification은 다음 흐름을 따른다.

```text
Test
→ Real Run
→ Result Verification
→ Browser Verification (if applicable)
→ Fix
→ Re-verify
```

Agent는 requirement/test/acceptance를 통과 목적으로 변경하지 않는다. Shared change는 affected Optimization regression을 포함한다.

Browser verification은 PV pixel parity가 아니라 내부 semantic contract를 검사한다. 정성적 visual polish human-review gate 범위는 D8에서 결정한다.

## Open Decisions

아래 항목만 현재 사용자 결정이 필요하다. 추천안은 초안일 뿐 확정이 아니다.

### D1. Backtest Experiment identity

**A. 비교 portfolio 전체의 union asset ticker set**
- weights, portfolio count/name, rebalancing, benchmark가 바뀌어도 같은 Experiment의 새 Run
- 기존 Optimization의 `Asset Universe = Experiment` 원칙과 가장 유사
- **추천**: 단순하고 기존 운영 습관과 일치

**B. portfolio별 asset membership 구조**
- union이 같더라도 어떤 portfolio에 어떤 asset이 속하는지가 바뀌면 새 Experiment
- Backtest 비교 정의를 더 강하게 보존하지만 identity가 복잡해짐

**C. weights까지 포함한 portfolio definitions**
- weights 변경도 새 Experiment
- Run과 Experiment가 지나치게 세분될 가능성이 커 비추천

### D2. Research Frontend benchmark default

**A. 기본 SPY, 사용자가 명시하면 변경/없음 허용**
- 기존 research frontend와 일치
- active analytics를 기본 제공
- **추천**

**B. Backtest에서는 truly optional, 미지정 시 benchmark 없음**
- core product의 optional semantics와 가장 직접적

### D3. Initial balance default

**A. 10,000을 canonical frontend default로 사용**
- 수익률에는 영향이 없고 PV/reference 및 기존 report scale과 친숙
- **추천**

**B. 매 Backtest마다 사용자에게 입력 요구**

### D4. Analysis period default

**A. 모든 required asset의 전체 common effective period**
- 기존 Optimization research frontend와 일치
- **추천**

**B. 항상 사용자에게 period 요구**

### D5. Rebalancing default

**A. Monthly**
- 기존 canonical default와 일치
- **추천**

**B. 항상 사용자에게 명시 요구**

**C. None**
- buy-and-hold baseline에는 자연스럽지만 기존 project default와 달라짐

### D6. Portfolio name default

**A. 이름이 없으면 `Portfolio 1`, `Portfolio 2`, `Portfolio 3` 자동 생성**
- user 질문을 줄임
- **추천**

**B. 모든 portfolio name을 사용자에게 요구**

### D7. Backtest LLM analysis framework 문서 경계

**A. Optimization용 기존 framework는 그대로 두고 Backtest analysis를 별도 capability/guide로 유지**
- Frontier/Optimizer 해석과 historical comparison을 섞지 않음
- **추천**

**B. 기존 `llm-analysis-framework.md` 개념을 하나의 통합 framework로 일반화**
- 문서 수는 줄지만 기존 문서를 수정해야 하고 mode별 분기가 커짐

### D8. Human visual review completion gate

**A. layout/interaction이 materially 변경된 경우만 human visual review 요구**
- DOM/semantic browser 검증은 항상 applicable scope에서 수행
- 정성적 polish 검토는 필요한 변화에만 사용
- **추천**

**B. 모든 report 변경에서 human visual review 필수**

**C. automated browser verification만 completion gate로 사용**

## After Decisions

D1-D8 확정 후:

1. `research-execution`, `research-input`, `research-analysis`, `agent-verification` draft requirement를 확정한다.
2. `proposal.md`의 draft capability 표시를 정리한다.
3. `tasks.md`의 decision-gated task를 확정한다.
4. OpenSpec strict validation을 수행한다.
5. 구현 전에 total-return data-source feasibility만 별도 technical investigation으로 닫는다.
