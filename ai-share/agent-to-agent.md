# Agent Session Handover — Interactive Report P0 Validation

state: ready
created_at: 2026-08-29T09:35:00+09:00
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

이전 Agent 세션은 context를 모두 소모해 종료되었다. 새 Agent는 interactive report 작업의 **마지막 P0 검증 라운드**를 이어받는다.

사용자/LLM의 현재 방향은 다음과 같다.

```text
LLM이 남은 P0 코드를 직접 수정
→ 새 Agent가 최신 main을 pull
→ tests 실행
→ 성공/실패와 무관하게 실제 end-to-end run 시도
→ report.html 생성
→ run artifact + HTML을 GitHub main에 commit/push
→ PV live/static Golden과 browser 비교
→ agent-to-llm.md에 결과와 GitHub 경로 기록
→ LLM이 HTML을 다시 직접 검증
```

이번 Agent의 기본 역할은 새 기능을 다시 설계하는 것이 아니라 **LLM이 반영한 P0 변경을 실제 환경에서 검증하고 integration/runtime 문제를 드러내는 것**이다.

## Required First Step

반드시 작업 시작 전에:

```text
git pull --ff-only origin main
```

을 실행하고 remote latest 기준으로 작업한다.

그 후 최소 다음을 읽는다.

1. `ai-share/PROTOCOL.md`
2. `AGENTS.md`
3. `docs/specification.md` Section 25
4. `docs/visual-acceptance-contract.md`
5. `tests/test_interactive_report_contract.py`
6. `tests/test_report_presentation_upstream.py`
7. `src/portfolio_optimizer_kr/pipeline.py`
8. `src/portfolio_optimizer_kr/viewer/report_model.py`
9. `src/portfolio_optimizer_kr/viewer/builder.py`
10. `site/report-template.html`

## What the LLM Changed Directly

이전 Agent의 partial P0 결과에서 Frontier curve/marker separation만 닫힌 상태였다. LLM이 이어서 아래 P0를 직접 수정했다.

### Frontier landmark coordinate semantics

`pipeline.py`에 presentation-ready `frontier_landmarks` artifact를 추가했다.

- Provided: optimizer와 동일한 `mu/cov`에서 `w'μ`, `sqrt(w'Σw)` 계산
- Optimized: `optimization_result`의 expected return / volatility / Sharpe 사용
- Benchmark: 같은 analysis period monthly returns를 동일 annualization convention으로 mean/std 계산
- Viewer는 historical `portfolio_performance.summary`를 frontier landmark 좌표로 재사용하지 않고 `review/frontier_landmarks.csv`를 읽음

### Up/Down actual scatter observations

`pipeline.py`에 `up_down_market_scatter` artifact를 추가했다.

각 aligned month에 대해:

```text
date
portfolio
market_type
benchmark_return_pct
portfolio_return_pct
active_return_pct
```

를 제공한다.

Viewer `ReportModel`에는:

```text
up_down_scatter_provided
up_down_scatter_optimized
```

가 추가되었다.

### Up/Down statistics units

summary artifact에 다음 percentage-point fields를 추가했다.

```text
above_active_return_pct
below_active_return_pct
overall_active_return_pct
```

HTML table은 raw decimal fields 대신 이 percentage fields를 사용하도록 수정했다.

### Missing is not zero

`site/report-template.html`에 공통 `finite()` / `numeric()` semantics를 추가했다.

- null/undefined/NaN을 0 observation으로 coercion하지 않음
- generic line은 missing에서 segment를 끊음
- missing bar/marker는 그리지 않음
- 기존 `+r[k] || 0` 제거

### Transition hover

Transition Map hover는 row-index 비례 선택 대신:

```text
pointer X
→ actual volatility X value
→ nearest frontier volatility_pct
```

로 point를 선택하도록 변경했다.

### Growth balance semantics

canonical normalized wealth는 유지한다.

presentation에서:

```text
1.0 → $10,000
```

으로 변환해 Growth chart Y축/tooltip을 동일 dollar balance convention으로 표시한다.

### Contribution / Rolling hover

- Active Return Contribution: Provided/Optimized 별도 panel 유지, ticker legend + date hover tooltip 추가
- Rolling Active: Provided/Optimized 별도 panel 유지, Date / Active Return / Tracking Error hover 추가

### Up/Down chart

기존 summary bar를 제거하고 Provided/Optimized 각각 실제 monthly observation scatter를 렌더링하도록 변경했다.

```text
X = Benchmark Monthly Return %
Y = Portfolio Monthly Return %
```

45-degree reference line과 observation tooltip을 제공한다.

## LLM Change Commits

LLM이 직접 반영한 최근 main commit 흐름:

```text
4bb1e7431a45320c08559470ca3ef2e0962e6dff  report model scatter contract
434a9f374ee8da3a6afe64a1cb62dcb0725b69a0  upstream landmark/scatter artifacts
bc7d88503c77b45cb73223a404ef37c310b83233  viewer consumes upstream data
919c59420da989777f7fb5075b079c9a33793e5f  renderer P0 semantic fixes
ca54dccc77f276f2ebc421e19ca884089bb1e433  interactive report P0 tests
b6f5c92db421a49f29c918e895244ff5cc2381ac  upstream semantic artifact tests
```

새 Agent는 위 SHA를 로컬 기준으로 가정하지 말고 반드시 `git pull` 후 실제 HEAD를 확인한다.

## Important Constraints

- 기존 LLM contract test를 약화/삭제/skip/xfail하지 않는다.
- 금융 의미를 browser JS에서 새로 계산하지 않는다.
- landmark/scatter semantics를 historical summary나 집계 row로 되돌리지 않는다.
- 이번 라운드의 우선순위는 P0 검증이다. pie/heatmap/table polish 등 P1을 확장 구현하지 않는다.
- 테스트 또는 real run에서 LLM 코드의 syntax/integration blocker가 나오면 원인을 먼저 확인한다.
- run을 가능하게 하는 **작고 명백한 integration fix**는 Agent가 수행할 수 있으나 금융/제품 의미 변경은 임의로 하지 않는다. 수정했다면 commit과 이유를 정확히 기록한다.
- 이번 라운드 이후에도 의미 오류가 남으면 반복 patch를 계속하기보다 LLM/User가 구조적 원인 분석을 진행할 예정이다.

## Required Tests

먼저 targeted:

```text
uv run pytest tests/test_interactive_report_contract.py tests/test_report_presentation_upstream.py -q
```

그 후 반드시 full regression:

```text
uv run pytest -q
```

테스트 실패 시에도 여기서 끝내지 않는다. 가능한 범위에서 원인을 진단한 후 **최종 real run을 반드시 시도**한다.

## Mandatory Final Real Run

성공/실패와 무관하게 작업 마지막에는 existing runner/CLI를 사용해 실제 end-to-end run을 최소 1회 시도한다.

이번 PV comparison validation은 반드시 **정확한 same-input period**를 사용한다.

### Validation input

```text
Assets / provided weights / bounds
QQQ  40%   0-50%
SPMO 10%   0-50%
GDX  10%   0-30%
GLD   0%   0-30%
SLV  10%   0-30%
AIA  15%   0-30%
XLE  15%   0-30%

Benchmark: SPY
Objective: Maximum Sharpe Ratio
Rebalancing: Monthly
Risk-free: fixed 2.35595% annual
Frontier points: 100
Analysis period: 2016-08-01 through 2026-07-31
```

주의: 이전 `runs/20260829-0002`는 `analysis_period: {}`라 full-common period였으므로 PV live와 exact same-input run이 아니었다. 이번에는 반드시 위 기간을 explicit하게 넣는다.

PV live behavioral reference:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

Static reference:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

## HTML / GitHub Artifact Requirement

이 새 validation pass에서는 사용자가 **Agent가 real run을 수행하고 생성된 HTML을 GitHub에 올리는 방식**을 명시적으로 승인했다.

새 unique run_id를 사용한다. 기존 run directory를 덮어쓰지 않는다.

real run이 성공하면 생성된:

```text
runs/<run_id>/report.html
```

을 포함한 validation run artifact를 GitHub `main`에 commit/push한다.

최소한 다음은 remote에서 LLM이 읽을 수 있어야 한다.

```text
runs/<run_id>/input.yaml
runs/<run_id>/result.json
runs/<run_id>/review/*
runs/<run_id>/report.html
runs/<run_id>/validation/visual-comparison.md
```

필요한 raw artifact도 기존 run-output policy에 따라 함께 보존한다.

run 자체가 실패해 HTML이 생성되지 않으면 실패 stage/exception을 durable하게 `agent-to-llm.md`에 기록한다. HTML이 없는데 있는 것처럼 보고하지 않는다.

## Browser Validation

real run 성공 후 generated `report.html`과 PV live를 브라우저에서 직접 비교한다.

최소 11개 chart:

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

특히 이번 P0에서 반드시 확인:

- Frontier curve에는 frontier points만 연결되고 marker는 marker-only
- Provided/Optimized/Benchmark landmark가 risk/return space에서 자연스럽게 위치
- Transition hover가 실제 pointer volatility와 맞는 nearest frontier point를 보여줌
- Contribution sawtooth 없음, portfolio 분리, ticker hover 정상
- Rolling Active portfolio 분리, hover 정상
- Up/Down은 summary bar가 아니라 실제 monthly scatter 2개 panel
- missing point가 0으로 떨어지는 artifact 없음
- Growth Y축/tooltip이 `$10,000` balance convention

P1 차이는 P0 failure로 부풀리지 말고 별도 remaining P1으로 기록한다.

## Completion / Handoff to LLM

작업 결과는 `ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

반드시 포함:

```text
Start HEAD after pull
Any Agent integration-fix commit SHA
Targeted test result
Full regression result
Final real run: PASS | FAIL
Actual run command
Effective validation input / period
Run ID and repository path
Result HTML repository path
Result HTML GitHub URL
Visual comparison path
PV live comparison result
P0 mismatch count
Remaining P1 list
Artifact commit SHA
Blocker/warning
```

성공/실패 어느 경우든 **real run을 시도했다는 사실과 결과**가 반드시 있어야 한다.

## Next

새 Agent는 pull → required reads → tests → 필요 시 최소 integration fix → final real run → HTML/artifact push → browser comparison → `agent-to-llm.md` push 순서로 진행한다.
