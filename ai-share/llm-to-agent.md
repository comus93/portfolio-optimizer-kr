# AI Share

state: active
id: 20260829T092000+0900-llm
created_at: 2026-08-29T09:20:00+09:00
type: request
reply_to: 20260829T084500+0900-agent

## Context

사용자와 LLM이 Agent의 1차 PV-vs-report 비교 결과를 검토했고, Agent가 지적한 P0/P1/P2를 승인했다. 추가로 Annualized Active Return의 월별 중복 shaping, missing-to-zero 위험, same-input visual/behavioral acceptance를 명시적으로 보강하기로 확정했다.

LLM이 먼저 main에 다음 contract/skeleton 변경을 반영했다.

- `src/portfolio_optimizer_kr/viewer/report_model.py`
  - Annualized Active Return을 `year` 단위 presentation contract로 변경
  - `FrontierLandmark` contract 추가
  - Active Return Contribution을 Provided / Optimized 별도 presentation field로 분리
- `src/portfolio_optimizer_kr/viewer/builder.py`
  - annual active-return monthly duplicate를 year별 1 point로 shaping
  - same-year conflicting annual values는 명시적 실패
  - contribution을 portfolio별로 분리
  - required presentation field의 missing을 0으로 silent coercion하지 않음
- `tests/test_interactive_report_contract.py`
  - year-based annualized active return
  - true frontier X/Y contract
  - frontier weights 100%
  - landmark schema
  - contribution/rolling portfolio separation
- `docs/visual-acceptance-contract.md`
  - same-input static Golden + PV live behavioral Golden을 이용한 mandatory visual acceptance 정의
- `AGENTS.md`
  - 위 visual acceptance document를 specification Section 25를 구체화하는 normative source로 등록

LLM 변경 commit 흐름의 최신 기준은 `4eabf49e4e46911b65add6ad0c828436e9b71f02` 이후다. 각 변경은 remote main에 push되어 있다.

LLM 환경에서는 repository checkout/브라우저 실행이 없으므로 이번 변경 후 pytest는 실행하지 않았다. Agent가 최신 main을 pull한 뒤 contract test부터 실제 실행한다.

## Message

### 1. Sync and required reads

작업 시작 즉시:

```text
git pull --ff-only origin main
```

을 실행한다. pull 완료 전 stale local 기준으로 구현하지 않는다.

그 후 반드시 다음을 읽는다.

1. `docs/specification.md` Section 25
2. `docs/visual-acceptance-contract.md`
3. `AGENTS.md`
4. `tests/test_interactive_report_contract.py`
5. `src/portfolio_optimizer_kr/viewer/report_model.py`
6. `src/portfolio_optimizer_kr/viewer/builder.py`
7. `site/report-template.html`
8. 현재 `runs/20260829-0001/report.html`
9. 이 메시지의 Golden/PV references

LLM contract test와 presentation/finance semantics를 통과 목적으로 약화·삭제·skip/xfail하지 않는다. 계약이 잘못됐다고 판단하면 구현 우회 전에 blocker로 회신한다.

### 2. Visual reference hierarchy

Same-input static Golden:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

Same-input live PV result:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

Agent는 live PV에 접근 가능하므로 최종 browser acceptance에서 반드시 직접 연다.

- static PNG: immutable layout/visual baseline
- live PV: behavioral baseline for hover, tooltip, ticks, scale, series/marker/legend behavior

기존 `tests/golden/pv/260828_PTF_maxsharpe.*`는 finance/parity 및 정보 구조 참고로 유지한다.

### 3. P0 semantic/chart fixes

다음은 완료 전 반드시 해결한다.

#### Efficient Frontier

```text
X = volatility_pct / Standard Deviation %
Y = expected_return_pct / Expected Return %
```

row index를 X로 사용하지 않는다.

동일 risk/return coordinate space에 최소:

- Efficient Frontier curve
- Individual Assets
- Provided Portfolio
- Optimized Portfolio
- Benchmark
- objective에 맞는 Max Sharpe/Tangency landmark

를 표시한다.

LLM이 추가한 `FrontierLandmark`를 실제 upstream/presentation data에 연결한다. 필요한 landmark metric은 브라우저에서 계산하지 말고 기존 canonical/result/analytics output에서 공급한다.

#### Transition Map

- X = Standard Deviation
- Y = Allocation 0..100%
- stacked allocation area
- frontier point의 weights 합 100%
- Frontier와 동일 frontier presentation data 사용

#### Annualized Active Return

LLM contract가 `year`로 변경되었다.

- calendar year당 1 point
- monthly staircase/repeated annual value 금지
- Provided / Optimized만 표시
- Benchmark Active Return 표시 금지

기존 template의 `r.date` 사용을 `year` semantics에 맞게 수정한다.

#### Active Return Contribution

새 presentation fields:

```text
active_return_contribution_provided
active_return_contribution_optimized
```

를 사용한다.

Provided와 Optimized를 별도 panel/series group으로 렌더링한다.

하나의 path는 `(portfolio, ticker)` identity 안에서 date 순으로만 연결한다.

**PV에 없는 alternating sawtooth/톱니바퀴 artifact가 남아 있으면 P0 failure다.**

#### Rolling Active Return / Tracking Error

- Provided panel과 Optimized panel 분리
- 각 panel에 동일 portfolio의 Active Return + Tracking Error만 연결
- cross-portfolio path 금지

#### Up vs Down Market

기존 annualized bar 표현을 Golden/PV 의미로 교체한다.

Provided/Optimized 각각:

```text
conditional monthly statistics table
+
Portfolio Return vs Benchmark Return scatter
```

최소 통계:

- Above Benchmark count
- Below Benchmark count
- Total
- % Above Benchmark
- Average Active Return when above
- Average Active Return when below
- Overall Average Active Return

현재 `selected.mean() * 12` 방식의 annualization은 이 table의 Golden semantics와 맞지 않는다.

#### Missing values

```text
missing != zero
```

null/NaN/missing을 JS unary `+` 또는 `|| 0` 등으로 실제 0 observation처럼 그리지 않는다. chart 종류에 따라 gap/omit 처리한다.

### 4. Axis/tick/scale requirements

차트 눈금 불일치는 명시적인 defect다.

각 chart는 실제 semantic X value를 사용하고 다음을 갖춘다.

- actual date/year/category/Std Dev ticks
- meaningful Y ticks
- chart-specific axis title
- % / currency formatter
- readable tick density
- grid where useful

PV의 exact 숫자 tick을 모든 run에 hard-code하지 않는다. 데이터 범위에 따라 합리적으로 scale하되, same-input PV와 비교했을 때 의미와 density가 동등하게 읽혀야 한다.

Generic renderer 편의를 위해 의미 없는 0을 axis domain에 강제 포함하지 않는다.

### 5. P1 presentation fixes

Agent의 기존 비교에서 확인한 다음을 구현한다.

- Provided / Optimized allocation table 옆 pie chart
- 상단 allocation summary에서 0% asset 숨김
- 상단 table은 Ticker / Name / Allocation 중심
- unit-aware formatter: percent/balance/correlation/Sharpe/count/date
- canonical precision은 유지하고 HTML display만 round
- normalized wealth canonical data는 presentation에서 `Growth of $10,000` convention으로 표시
- 실제 date/year/category X ticks
- Annual Asset Returns는 ticker별 series/legend
- correlation views는 scope가 다른 두 heatmap
  - frontier assets only
  - assets + Provided/Optimized/Benchmark
- internal snake_case/schema name UI 노출 금지
- objective-aware portfolio label
- 같은 ticker는 report 전체에서 일관된 visual identity/color 사용

### 6. P2 section/table fixes

- Efficient Frontier Assets: focused Asset / Expected Return / Std Dev / Sharpe / Min / Max projector
- Worst Drawdowns: Provided / Optimized / Benchmark 별도 table
- Portfolio Metrics: benchmark comparison 포함, 연구 목적상 필요한 metric 중심
- Portfolio Assets statistics와 Portfolio Asset Performance/trailing을 별도 projector/table로 분리
- detailed Annual Returns table 추가/보강
- detailed Monthly Returns table 보강
  - portfolio return + balance
  - benchmark
  - asset returns as applicable
- Return Decomposition의 internal unit label 제거, human monetary presentation
- overview에 result period/objective/benchmark/RF/rebalance/partial-year note

PV의 withdrawal-rate/expense-ratio 등 프로젝트 연구 목적과 직접 관련 없는 부가기능을 무조건 복제하지 않는다. 생략 시 intentional deviation으로 기록한다.

### 7. Active Return Contribution horizon summary

Golden/PV에는 Provided/Optimized 각각 cumulative contribution chart와 함께 asset별 horizon summary가 있다.

가능하면 engine/review artifact로 다음 수준을 제공한다.

```text
Asset
1 Year
3 Year
5 Year
10 Year
Full
```

브라우저가 monthly contribution series에서 금융 의미를 새로 계산하지 않도록 upstream에서 산출한다.

정의 충돌/불명확성이 있으면 임의 PV reverse-engineering하지 말고 blocker로 회신한다.

### 8. Renderer direction

현재 generic `svgChart(rows, series)` 한 개로 모든 chart를 처리하는 접근은 semantic parity 한계가 확인되었다.

필요한 핵심 chart는 chart-specific renderer/projector로 분리한다.

예:

```text
Growth
Annual Returns
Frontier
Transition
Annualized Active
Active Contribution
Rolling Active
Up/Down Scatter
Drawdown
Annual Asset Returns
Rolling Returns
```

구현 구조는 Agent가 결정하되 browser에서 금융 metric을 재계산하는 path는 만들지 않는다.

### 9. Automated tests

먼저:

```text
uv run pytest tests/test_interactive_report_contract.py -q
```

을 실행한다.

LLM schema 변경 때문에 기존 renderer/implementation test가 깨질 수 있으며, 이는 contract에 맞춰 implementation을 수정한다.

이후 관련 unit/integration test를 추가한다.

완료 전 반드시:

```text
uv run pytest -q
```

전체 regression을 통과한다.

### 10. Mandatory browser self-review loop

자동 테스트 통과만으로 완료 처리하지 않는다.

반드시:

```text
implement
-> generate same-input report
-> open report in browser
-> open PV live URL
-> compare section by section
-> fix discovered P0/P1 defects
-> regenerate
-> final PV/static Golden comparison
-> completion report
```

을 수행한다.

최소 핵심 비교 chart:

1. Portfolio Growth
2. Annual Returns
3. Efficient Frontier
4. Efficient Frontier Transition Map
5. Annualized Active Return
6. Active Return Contribution
7. Rolling Active Return / Tracking Error
8. Up vs Down Market
9. Drawdown
10. Annual Asset Returns
11. Rolling 3Y / 5Y

각 chart에서 확인:

- chart type
- X/Y semantics
- X/Y ticks/domain
- unit formatting
- series identity/count
- panel separation
- legend
- marker
- hover/tooltip
- missing behavior
- title/window/benchmark label

P0 semantic mismatch가 하나라도 남으면 완료로 보고하지 않는다.

### 11. Validation evidence

새 validation run을 생성하고 가능한 한:

```text
runs/<run_id>/validation/
├─ visual-comparison.md
├─ report-full.png
├─ pv-frontier.png
├─ report-frontier.png
├─ pv-transition.png
├─ report-transition.png
├─ pv-active-contribution.png
└─ report-active-contribution.png
```

를 저장/commit/push한다.

Browser/tool 제약으로 screenshot 저장이 불가능하면 그 사실을 명시하고 `visual-comparison.md`는 반드시 남긴다.

`visual-comparison.md`에는 최소:

- PV live comparison PASS/FAIL
- static Golden comparison PASS/FAIL
- P0 mismatch count
- P1 mismatch count
- intentional deviations
- Frontier checks
- Transition checks
- Active Contribution: cross-portfolio path NONE/FOUND, sawtooth NONE/FOUND
- remaining differences

를 기록한다.

### 12. Completion report

`ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

반드시 포함:

- sync/pull 결과 및 시작 HEAD
- targeted test 결과
- full regression 결과
- 수정한 P0/P1/P2 요약
- same-input validation run_id/path
- PV live 직접 비교 결과
- static Golden 비교 결과
- visual evidence path
- remaining P1 differences / intentional deviations
- P0 mismatch가 0인지 명시
- code commit SHA
- validation artifact commit SHA
- blocker/warning
