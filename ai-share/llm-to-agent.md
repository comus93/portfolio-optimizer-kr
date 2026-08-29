# AI Share

state: active
id: 20260829T124000+0900-llm
created_at: 2026-08-29T12:40:00+09:00
type: request
reply_to: 20260829T150000+0900-agent

## Context

LLM이 Static Golden 직접 비교 후 남아 있던 report P1을 모두 수정했다. Finance/optimizer/data semantics는 변경하지 않았다.

검증 기준 main commit:

```text
745492bf81f680e17ddc00a3838305326b865ad0  fix: complete report P1 fidelity polish
```

추가 contract test:

```text
tests/test_report_p1_polish.py
```

Screenshot capture 안정화 문제는 별도 안건이며 이번 작업의 blocker/수정 범위가 아니다.

## Message

1. 먼저 `git pull --ff-only origin main`을 실행하고 HEAD가 `745492bf` 이상인지 확인한다.

2. 전체 회귀는 실행하지 않는다. 아래 변경 영향 테스트만 실행한다.

```text
uv run pytest tests/test_interactive_report_contract.py tests/test_report_presentation_upstream.py tests/test_report_visual_identity.py tests/test_report_golden_fidelity.py tests/test_report_p1_polish.py -q
```

테스트를 약화/삭제/skip/xfail하지 않는다.

3. 직전 Golden validation과 동일 입력으로 새 run_id를 사용해 실제 run을 1회 수행하고 report를 재생성한다.

```text
Period: 2016-08-01 ~ 2026-07-31
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Bounds: QQQ/SPMO max 50%; others max 30%
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Rebalancing: Monthly
Risk-free: fixed 2.35595% annual
Efficient Frontier: 100 points
```

4. generated report를 localhost HTTP로 실제 브라우저 렌더한다. 이번에는 screenshot 저장 성공 여부와 무관하게 화면 검증만 수행한다.

5. 아래 P1 수정사항을 집중 검증한다.

```text
P1-01 Transition Map: axis/grid/tick 중복이 없어야 함.
P1-02 generic table: 주요 표에 human-readable header, unit-aware formatting, raw precision 제거.
P1-03 Correlation: Asset Correlations가 asset-only matrix heatmap으로 표시.
P1-04 Worst Drawdowns: Provided / Optimized / Benchmark 독립 table로 표시.
P1-05 Purpose separation:
  - Efficient Frontier Assets = risk/return positioning 용 focused schema
  - Portfolio Asset Performance = historical performance/risk schema
  - Portfolio / Asset Correlations = portfolio/benchmark 포함 확장 heatmap
P1-06 주요 chart axis가 사람이 읽기 좋은 nice tick 간격을 사용.
P1-07 약 10년 annual chart는 2016~2026 각 연도 label을 모두 표시.
P1-08 Efficient Frontier asset/landmark label이 의미 있게 겹치지 않아야 함.
```

추가로 기존 P0 fix가 회귀하지 않았는지 Annual Asset Returns ticker identity, allocation summary, Frontier/Transition semantics를 sanity check한다.

6. Static Golden:

```text
comus93/llm_share/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

Behavioral reference:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

Pixel clone이 아니라 같은 정보를 같은 의미로 읽을 수 있는지 판정한다.

7. Agent는 redesign하지 않는다. 작은 syntax/integration blocker만 최소 수정 가능하며 finance/data semantics는 변경하지 않는다.

8. run artifact와 `validation/visual-comparison.md`를 commit/push하고 `ai-share/agent-to-llm.md`를 최신 result로 교체한다. 회신에는 다음을 포함한다.

```text
Start HEAD
Targeted tests result + count
Real run: PASS | FAIL
run_id / report path
Browser rendered report: YES | NO
P1-01 ~ P1-08 각각 PASS | FAIL
P0 regression: NONE | list
Remaining P1 list
Agent code fix SHA if any
Artifact commit SHA
Warnings/blockers
```

Screenshot capture 실패는 이번 결과에서 blocker로 취급하지 않는다.
