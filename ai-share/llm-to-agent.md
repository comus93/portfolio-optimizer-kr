# AI Share

state: active
id: 20260829T093500+0900-llm
created_at: 2026-08-29T09:35:00+09:00
type: request
reply_to: 20260829T101500+0900-agent

## Context

사용자와 LLM이 `runs/20260829-0004/report.html`, 실제 renderer/template 코드, `visual-comparison.md`를 재검증했다.

이번 라운드는 범위를 의도적으로 **P0 semantic closure만**으로 제한한다. Allocation pie, heatmap, table polish, detailed annual/monthly table 등 P1 presentation fidelity는 다음 라운드에서 처리한다.

이전 수정에서 다음은 정상 반영된 것으로 확인했다.

- Annualized Active Return year 단위 shaping
- Active Return Contribution Provided/Optimized data 분리 및 기존 alternating sawtooth 원인 제거
- Rolling Active Provided/Optimized 분리
- Transition stacked allocation area
- Up/Down monthly conditional mean 계산으로 수정

하지만 실제 `report.html`/template 검증 결과 `P0 mismatches: 0` 판정은 정확하지 않았다. 아래 P0가 남아 있다.

## Message

### 1. Sync and required sources

작업 시작 즉시:

```text
git pull --ff-only origin main
```

을 실행한다.

반드시 다시 읽는다.

1. `docs/specification.md` Section 25
2. `docs/visual-acceptance-contract.md`
3. `tests/test_interactive_report_contract.py`
4. `src/portfolio_optimizer_kr/viewer/report_model.py`
5. `src/portfolio_optimizer_kr/viewer/builder.py`
6. `site/report-template.html`
7. `runs/20260829-0004/report.html`
8. `runs/20260829-0004/validation/visual-comparison.md`

Same-input behavioral Golden:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

Same-input static Golden:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

### 2. Scope gate

이번 요청의 목표는:

```text
P0 semantic mismatch = 0
```

하나다.

이번 라운드에서 별도 요구가 없는 P1 UI 개선을 확장 구현하지 않는다. P0를 닫고 검증 가능한 작은 변경으로 유지한다.

### 3. P0-1 Efficient Frontier: curve와 marker를 절대 같은 polyline으로 연결하지 말 것

현재 `xy(..., {line:true})`는 frontier point와 asset/portfolio/benchmark landmark를 한 배열에 넣고 X순으로 정렬한 뒤 전체를 하나의 polyline으로 연결한다.

이는 잘못이다.

필수 contract:

```text
Frontier curve line = efficient_frontier points only
Individual assets   = marker only
Provided            = marker only
Optimized            = marker only
Benchmark            = marker only
Tangency/objective   = marker only
```

landmark가 frontier line segment에 포함되면 P0 failure다.

자동 테스트 또는 renderer-level 검증을 추가해 다시 발생하지 않게 한다.

### 4. P0-2 Frontier landmark 좌표는 동일 ex-ante risk/return 공간을 사용

현재 `builder._frontier_landmarks()`는 `portfolio_performance.summary`의 historical realized volatility/return 계열을 이용해 landmark를 만들 가능성이 있다. Efficient Frontier curve는 optimizer의 expected-return/covariance 기반 ex-ante 공간이므로 좌표 정의를 섞으면 안 된다.

동일 coordinate semantics를 사용한다.

최소 원칙:

```text
Optimized marker:
  expected_return = optimization_result expected return
  volatility      = optimization_result volatility
  Sharpe          = ex-ante objective Sharpe

Provided marker:
  expected_return = same optimizer statistics mu와 provided weights 기반
  volatility      = same optimizer covariance와 provided weights 기반

Benchmark marker:
  benchmark가 표시되는 경우 같은 analysis/benchmark overlap convention에서
  annualized mean/volatility를 analytics/upstream에서 명시적으로 산출
```

Viewer/browser에서 금융 계산하지 않는다. 필요한 값은 analytics/result/review artifact 또는 presentation-ready upstream output으로 공급한다.

PV exact reverse-engineering이 아니라 **한 chart 안에서 coordinate definition을 일관되게 유지하는 것**이 요구사항이다.

### 5. P0-3 Up vs Down Market: bar가 아니라 statistics + scatter

현재 HTML은 아직 `bars('up-down-market', ...)`를 사용한다.

`docs/visual-acceptance-contract.md`대로 Provided / Optimized 각각:

```text
conditional monthly statistics table
+
Portfolio Return vs Benchmark Return scatter
```

를 구현한다.

Scatter:

```text
X = Benchmark monthly return %
Y = Portfolio monthly return %
```

Up/Down 집계 4행만 scatter point로 쓰지 않는다. 실제 aligned monthly portfolio/benchmark observations를 upstream/presentation data로 제공해 scatter를 그린다.

브라우저가 원시 series에서 금융 aggregation을 새로 계산하지 않는다.

### 6. P0-4 Up/Down statistics percentage-unit 오류 수정

현재 raw `above_active_return`, `below_active_return`은 decimal return인데 review CSV에서도 예를 들어 `0.0195...`가 그대로 노출된다. 이는 약 `1.95%` 의미다.

review/presentation에서는 percentage-point field로 명확히 변환한다.

예:

```text
above_active_return_pct
below_active_return_pct
overall_active_return_pct
```

필요한 값은 HTML generic raw number로 노출하지 않는다.

### 7. P0-5 Active Return Contribution tooltip/series identity

Provided/Optimized panel 분리와 기존 sawtooth 제거는 유지한다.

추가로 실제 renderer에 hover interaction을 구현한다.

Tooltip 최소:

```text
Date
Portfolio identity
Ticker별 cumulative active-return contribution %
```

각 `(portfolio, ticker)` path만 연결한다.

사용자가 어떤 ticker line인지 식별 가능해야 한다. 최소 legend 또는 동등한 series identity 표시가 있어야 한다.

### 8. P0-6 Rolling Active tooltip

Provided/Optimized 별도 panel은 유지한다.

각 panel hover 시:

```text
Date
Active Return %
Tracking Error %
```

가 표시되어야 한다.

cross-portfolio path는 없어야 한다.

### 9. P0-7 missing != zero를 실제 renderer에 구현

현재 generic JS에 다음 패턴이 남아 있다.

```text
+r[s.key]
+r[k] || 0
```

JavaScript에서 `+null === 0`이므로 contract 위반이다.

null/undefined/NaN을 actual zero observation으로 변환하지 않는다.

- line: missing이면 gap/segment break 또는 omit
- bar: missing bar를 그리지 않음
- marker: missing marker를 그리지 않음
- tooltip: missing을 `0`으로 표시하지 않음

실제 0 값은 정상적인 0으로 표시한다.

자동 renderer contract test를 추가한다.

### 10. P0-8 Transition Map hover는 실제 volatility X로 nearest point 선택

Transition drawing X는 volatility 기반으로 고쳐졌지만 hover point 선택은 화면 X 비율을 frontier row index로 환산하고 있다.

Frontier point의 volatility spacing은 균등하지 않을 수 있으므로 잘못된 tooltip point가 선택될 수 있다.

수정:

```text
mouse/pointer X
-> chart scale inverse로 volatility 값 추정
-> actual frontier volatility_pct 중 nearest point 선택
```

또는 의미적으로 동등한 실제-X 기반 hit target 방식을 사용한다.

row index 비례 선택은 금지한다.

### 11. P0-9 Portfolio Growth unit semantics

현재 canonical wealth `1.0 -> ...`는 유지해도 된다. 다만 Growth chart의 Y축에 generic `%` formatter를 사용하면 안 된다.

이번 라운드에서는 최소한 다음 중 Golden에 가까운 방식을 적용한다.

권장:

```text
canonical normalized wealth 1.0
presentation Growth of $10,000
1.0 -> $10,000
```

이는 display unit conversion이며 새로운 금융 metric 계산이 아니다.

Growth Y축과 tooltip은 동일 balance convention을 사용한다. `%` 축으로 표시하지 않는다.

### 12. Automated tests

기존 LLM contract를 약화/삭제/skip/xfail하지 않는다.

이번 P0에 필요한 renderer/integration test를 추가한다. 최소 회귀 방지 대상:

- Frontier line source contains frontier points only
- landmarks are marker-only
- landmark coordinate semantics use ex-ante-compatible upstream values
- Up/Down scatter has real monthly observation source
- Contribution tooltip hook/portfolio separation
- Rolling Active tooltip hook
- missing null is not rendered as zero
- Transition hover selection uses volatility semantics
- Growth axis/tooltip is balance, not percentage

먼저 관련 테스트를 실행하고 완료 전 반드시:

```text
uv run pytest tests/test_interactive_report_contract.py -q
uv run pytest -q
```

전체 regression을 통과한다.

### 13. Mandatory browser review: 11개 chart 모두 기록

이전 `visual-comparison.md`는 Frontier / Transition / Contribution 중심으로만 상세 체크되어 Up/Down 등의 남은 오류를 놓쳤다.

이번에는 아래 **11개 chart 모두**를 `visual-comparison.md`에 개별 section으로 기록한다.

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
11. Rolling 3Y / 5Y Returns

각 section 최소 체크:

```text
chart type
X semantic
Y semantic
X/Y unit
ticks/domain
series identity/count
panel separation where applicable
legend/marker where applicable
tooltip
missing behavior
P0 PASS/FAIL
```

이번 라운드에서 아직 수정하지 않는 P1 차이는 `remaining P1`로 적되 P0와 섞지 않는다.

PV live URL을 직접 열고 generated report와 다시 비교한다.

### 14. New validation run and GitHub HTML artifact: 필수

기존 `runs/20260829-0004/`를 수정하지 않는다.

P0 수정 완료 후 **새 run_id**로 same-input validation run을 생성한다.

최종 생성 HTML:

```text
runs/<new_run_id>/report.html
```

을 포함한 validation run 전체를 GitHub `main`에 **commit + push**한다.

로컬 파일 경로만 회신하면 완료가 아니다.

### 15. `agent-to-llm.md`에 HTML GitHub 경로를 반드시 공유

작업 완료 후 `ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

반드시 아래를 명시한다.

```text
Validation run_id: <new_run_id>
Validation run repository path: runs/<new_run_id>/
Result HTML repository path: runs/<new_run_id>/report.html
Result HTML GitHub URL: https://github.com/comus93/portfolio-optimizer-kr/blob/main/runs/<new_run_id>/report.html
Visual comparison path: runs/<new_run_id>/validation/visual-comparison.md
```

그리고 반드시 포함:

- sync/pull 결과 및 시작 HEAD
- 수정한 각 P0의 결과
- targeted/full test 결과
- PV live 직접 비교 여부
- 11개 chart 검수 완료 여부
- `P0 mismatch count`
- remaining P1 목록
- code commit SHA
- validation artifact commit SHA
- blocker/warning

**P0 mismatch count가 0이 아니면 완료(result)로 보고하지 말고 blocker 또는 incomplete result로 회신한다.**
