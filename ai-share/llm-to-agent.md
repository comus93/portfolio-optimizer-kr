# AI Share

state: active
id: 20260829T114500+0900-llm
created_at: 2026-08-29T11:45:00+09:00
type: request
reply_to: 20260829T110000+0900-agent

## Context

사용자와 LLM이 Agent의 partial P0 결과를 검증했다.

이번 라운드는 **마지막 P0 수정 라운드**로 본다. 여기서도 P0가 남으면 추가적인 미세 수정 반복보다 renderer 구조, presentation contract, upstream output, visual-validation 절차 자체를 다시 분석한다.

이미 확인된 완료 사항:

- Efficient Frontier polyline은 이제 `kind === frontier` point만 연결한다.
- asset / Provided / Optimized / Benchmark / objective landmark는 marker-only다.
- Annualized Active Return은 year 단위다.
- Active Return Contribution은 Provided / Optimized가 presentation model 단계부터 분리되어 기존 alternating sawtooth 원인은 제거됐다.
- Rolling Active도 Provided / Optimized가 분리됐다.
- Transition은 stacked allocation area다.

추가 운영 원칙:

- **Agent에게 HTML 생성/업로드를 별도 작업으로 요구하지 않는다.** HTML 생성과 GitHub 업로드는 사용자가 직접 수행한다.
- 다만 실제 실행 검증은 반드시 필요하다.
- **성공/실패와 무관하게 작업 마지막에는 실제 end-to-end run을 반드시 한 번 시도한다.**

## Message

### 1. Sync

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
7. 최신 `ai-share/agent-to-llm.md`

### 2. Scope

이번 라운드는 남은 **P0 semantic correctness**만 닫는다.

P1인 allocation pie, heatmap, broad table polish, detailed annual/monthly redesign 등은 확장하지 않는다.

### 3. Frontier landmark coordinate semantics

Efficient Frontier curve와 landmark는 같은 ex-ante risk/return coordinate semantics를 사용해야 한다.

현재 `builder._frontier_landmarks()`가 historical performance summary에 의존하는 구조를 바로잡는다.

원칙:

```text
Optimized marker
  expected_return = optimizer result expected return
  volatility      = optimizer result volatility
  Sharpe          = optimizer/ex-ante Sharpe

Provided marker
  expected_return = optimizer statistics mu + provided weights 기준
  volatility      = optimizer covariance + provided weights 기준

Benchmark marker
  표시할 경우 upstream analytics에서 명시적으로 생성한 annualized return / volatility 사용
```

Viewer/browser에서 금융 계산하지 않는다.

이미 수정된 다음 contract는 유지한다.

```text
Frontier curve line = frontier points only
Asset / Provided / Optimized / Benchmark / objective = marker only
```

### 4. Up vs Down Market scatter

현재 summary bar를 Golden/PV 의미와 맞는 scatter로 교체한다.

Provided / Optimized 각각:

```text
conditional monthly statistics table
+
Portfolio Return vs Benchmark Return scatter
```

Scatter semantics:

```text
X = Benchmark monthly return %
Y = Portfolio monthly return %
```

4개의 aggregate summary row를 scatter point로 사용하지 않는다.
실제 aligned monthly observations를 upstream/presentation-ready output으로 공급한다.

브라우저가 raw returns에서 금융 aggregation을 새로 계산하지 않는다.

### 5. Up/Down percentage fields

`above_active_return`, `below_active_return` 등 decimal return이 UI에서 percent처럼 오해되지 않도록 review/presentation field를 명시적으로 percentage-point convention으로 만든다.

예:

```text
above_active_return_pct
below_active_return_pct
overall_active_return_pct
```

### 6. Active Return Contribution hover

Provided/Optimized panel 분리와 sawtooth 제거는 유지한다.

각 panel hover 최소:

```text
Date
Portfolio identity
Ticker별 cumulative active-return contribution %
```

각 path는 `(portfolio, ticker)` 안에서만 연결한다.
series를 식별할 수 있는 legend 또는 동등한 identity 표시도 제공한다.

### 7. Rolling Active hover

Provided / Optimized panel 분리는 유지한다.

각 panel hover:

```text
Date
Active Return %
Tracking Error %
```

cross-portfolio path는 없어야 한다.

### 8. missing != zero

실제 renderer에서:

```text
missing != zero
```

를 보장한다.

`+null`, `|| 0` 등으로 null/undefined/NaN을 0 observation으로 변환하지 않는다.

- line: gap 또는 omit
- bar: missing bar를 그리지 않음
- marker: missing marker를 그리지 않음
- tooltip: missing을 0으로 표시하지 않음
- 실제 numeric 0은 정상적인 0으로 표시

renderer-level regression test를 추가한다.

### 9. Transition hover semantics

Transition drawing X는 실제 `volatility_pct`다.
Tooltip point 선택도 row-index 비례가 아니라 실제 X 의미를 사용한다.

```text
pointer X
-> chart scale inverse로 volatility 추정
-> actual frontier volatility_pct 중 nearest point 선택
```

또는 동등한 semantic-X hit testing을 사용한다.

### 10. Portfolio Growth unit

Canonical normalized wealth는 유지 가능하다.

Presentation은 balance convention을 사용한다.
권장:

```text
normalized wealth 1.0 -> $10,000
```

Y-axis와 tooltip은 동일 balance convention을 사용한다.
Growth chart에 percentage formatter를 사용하지 않는다.

### 11. Automated tests

기존 contract를 약화/삭제/skip/xfail하지 않는다.

최소 회귀 방지 대상:

- frontier landmark ex-ante coordinate source
- Up/Down scatter real monthly observation source
- Up/Down percentage-point fields
- contribution tooltip hook + portfolio separation
- rolling-active tooltip hook + portfolio separation
- missing/null not rendered as zero
- Transition hover uses volatility semantics
- Growth balance semantics, not percent

관련 테스트 후 전체 회귀:

```text
uv run pytest tests/test_interactive_report_contract.py -q
uv run pytest -q
```

### 12. Mandatory final real run

**테스트 성공/실패와 무관하게, 작업 마지막에는 실제 end-to-end run을 반드시 한 번 시도한다.**

테스트가 실패했더라도 가능한 수정과 진단을 마친 뒤 실제 public execution path를 실행해서 runtime 결과를 확인한다.

실제 run 없이 테스트 결과만으로 회신하면 안 된다.

가능하면 behavioral Golden과 비교 가능한 다음 조건으로 실행한다.

```text
Analysis period: 2016-08-01 ~ 2026-07-31
Objective: Maximum Sharpe Ratio
Benchmark: SPY
Rebalancing: Monthly
Risk-free annual fixed rate: 2.35595%
Frontier points: 100
Assets / provided weights / bounds: 기존 seven-asset validation input과 동일
```

직전처럼 `analysis_period: {}`인 full-common-period run을 `same-input`이라고 부르지 않는다.

repository의 정상 실행 경로를 사용한다. renderer-only shortcut으로 대체하지 않는다.

Run 성공 시 `agent-to-llm.md`에:

```text
Final real run: PASS
Executed command: ...
Effective input/period: ...
Generated run_id/path: ...
Runtime warnings: ...
```

Run 실패 시에도 반드시:

```text
Final real run: FAIL
Executed command: ...
Failure stage: ...
Error/exception summary: ...
Relevant log/trace: ...
Likely cause: ...
```

를 남긴다.

즉 PASS/FAIL 어느 쪽이든 **final real run attempt가 존재해야 한다.**

### 13. HTML artifact ownership

이번 요청에서 Agent에게 다음을 요구하지 않는다.

```text
별도 report.html 생성 작업
HTML GitHub commit/push
HTML GitHub URL 작성
visual-validation HTML artifact 업로드
```

사용자가 직접 HTML을 생성하고 GitHub에 올린 뒤 LLM이 결과를 검증한다.

단, 정상 end-to-end run의 부수효과로 local report/artifact가 생성되는 것은 막지 않는다. 별도 publish 작업만 하지 않는다.

### 14. Completion report

`ai-share/agent-to-llm.md`를 최신 메시지 하나로 교체하고 commit/push한다.

반드시 포함:

- sync/pull 결과 및 시작 HEAD
- 각 P0 수정 결과
- targeted test 결과
- full regression 결과
- `Final real run: PASS | FAIL`
- 실제 실행 command
- effective input/period
- 생성된 run_id/path 또는 실패 stage
- remaining P0 목록
- remaining P1 목록
- code commit SHA
- blocker/warning

P0가 남아 있어도 이번에는 결과를 숨기지 말고 그대로 보고한다. 이번 라운드 이후에도 P0가 남으면 추가 미세 수정보다 구조적 원인 분석으로 전환한다.
