# AI Share

state: active
id: 20260829T163500+0900-llm
created_at: 2026-08-29T16:35:00+09:00
type: request
reply_to: 20260829T170000+0900-agent

## Context

사용자가 실제 PV browser screenshot을 추가 제공했고 LLM이 직접 corrective renderer v3를 구현했다.

이번 기준은 이전 `UF-11 scatter PASS` 해석을 폐기한다. 충돌 시 반드시 아래 문서를 우선한다.

```text
docs/report-visual-overrides-20260829.md
```

LLM 구현 commits는 최신 main에 포함되어 있다.

핵심 변경:

```text
src/portfolio_optimizer_kr/viewer/feedback_v3.py
src/portfolio_optimizer_kr/viewer/final_renderer.py
src/portfolio_optimizer_kr/viewer/__init__.py
tests/test_report_user_feedback_v3.py
docs/report-visual-overrides-20260829.md
```

목적:

1. Efficient Frontier Assets의 Min/Max Weight regression 복구
2. Efficient Frontier viewport를 curve 중심 + 충분한 context + outward nice-domain으로 수정
3. outsider 판정을 raw curve min/max가 아니라 최종 display domain 기준으로 수정
4. Annual Asset Returns를 실제 ticker별 series/color/legend로 복구하면서 year grouped hover 유지
5. Up/Down 하단을 scatter에서 PV-style `Return vs. Benchmark` paired bar로 재구성
6. missing Frontier asset ex-ante Sharpe는 canonical effective RF로 보완

## 1. Sync

먼저:

```text
git pull --ff-only origin main
```

최신 main에서 시작한다. 임의로 이전 commit으로 checkout하지 않는다.

다음을 반드시 읽는다.

```text
docs/report-visual-overrides-20260829.md
ai-share/user-to-llm.md
```

## 2. Affected-scope tests only

전체 regression은 실행하지 않는다.

최소:

```text
uv run pytest \
  tests/test_reporting.py \
  tests/test_interactive_report_contract.py \
  tests/test_report_visual_identity.py \
  tests/test_report_golden_fidelity.py \
  tests/test_report_p1_polish.py \
  tests/test_report_user_feedback_v2.py \
  tests/test_report_user_feedback_v3.py -q
```

기존 테스트를 약화/삭제/skip/xfail하지 않는다.

작고 명백한 syntax/integration blocker만 최소 수정 가능하다. Finance semantics나 renderer design을 임의 재설계하지 않는다.

## 3. Fresh same-input run

동일 Golden 입력으로 새 run을 만든다. 기존 run 덮어쓰기 금지.

권장 run_id:

```text
20260829-report-review-v3-validation
```

입력:

```text
Period: 2016-08-01 ~ 2026-07-31
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Bounds: QQQ/SPMO max 50%; GDX/GLD/SLV/AIA/XLE max 30%
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Rebalancing: Monthly
Risk-free: fixed 2.35595% annual
Efficient Frontier: 100 points
```

localhost HTTP로 generated report를 실제 browser render한다. `file://` 금지.

PV live도 실제 browser에서 연다.

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

## 4. Efficient Frontier validation — critical

### A. Asset table

다음 schema가 실제 화면에 모두 있어야 한다.

```text
Name | Ticker | Expected Return | Std Dev | Sharpe Ratio | Min Weight | Max Weight
```

Sharpe가 N/A/NaN으로 비지 않는지 확인한다.

### B. Display domain

이번 run의 curve raw X range는 대략 12.7% ~ 17.7%지만 chart를 여기에 딱 붙이지 않는다.

검증:

- curve가 chart 전체를 꽉 채우지 않고 주변 context가 충분한가
- X축 lower bound가 자연스러운 nice tick으로 curve보다 충분히 낮은가. PV screenshot은 10%부터 시작한다.
- Y축도 curve 아래 자산 위치를 읽을 수 있을 정도의 context가 있는가
- hard-coded 10%인지가 아니라 curve + padding + nice-domain 원칙으로 나온 결과인지 확인한다

### C. Visible / outsider classification

**최종 display domain 안의 asset은 반드시 plot에 보여야 한다.**

이번 fresh run에서 실제 chart X/Y domain을 기록하고, 각 ticker에 대해:

```text
ticker | std dev | expected return | visible/outside
```

를 validation artifact에 남긴다.

특히 QQQ/SPMO/GLD/AIA 등 화면 domain 안에 들어오는 자산이 `Assets outside chart scale` table로 잘못 내려가지 않는지 확인한다.

Outsider table에는 최종 domain 밖 asset만 있어야 한다.

### D. Curve hover

curve hover tooltip에서 nearest frontier portfolio의:

- all asset allocation %
- Expected Return %
- Standard Deviation %
- Sharpe Ratio

를 확인한다.

## 5. Annual Asset Returns validation

- 7 ticker가 실제로 서로 다른 chart series/color인가
- legend에 7 ticker identity가 있는가
- generic single `return_pct` series처럼 보이지 않는가
- 한 연도의 어느 bar hover 시 전체 asset Name/Ticker/return %가 한 tooltip에 보이는가

## 6. Up vs. Down validation — previous scatter requirement superseded

하단 chart는 scatter가 아니다.

각 Provided / Maximum Sharpe block은:

```text
conditional statistics table
+
Return vs. Benchmark paired bar chart
```

여야 한다.

paired bar chart 검증:

- monthly observations를 Benchmark Return 오름차순으로 정렬
- 약 20 equal-frequency groups
- 이 run은 120 months이므로 20 groups × 6 observations/group
- 각 group에 Portfolio / Benchmark 두 bar
- X tick = group mean Benchmark Return %
- Y = Return %
- hover = group Portfolio Return %, Benchmark Return %, observation count
- scatter point chart가 남아 있으면 FAIL

가능하면 PV screenshot/live의 x-axis representative values와 몇 개 group을 비교해서 grouping 해석이 맞는지 검산한다. 다르면 구현을 임의 수정하지 말고 evidence와 함께 FAIL/remaining issue로 보고한다.

## 7. 84/36 vs PV 85/35 investigation

UI 숫자를 PV에 맞춰 hard-code하지 않는다.

fresh local canonical monthly benchmark series 기준 count와 PV count가 다르면:

1. classification 차이를 만드는 exact month를 식별
2. local SPY monthly return 값을 기록
3. 가능한 경우 PV 해당 monthly return과 비교
4. local classification logic defect인지 FDR/PV price-data 차이인지 판정

logic defect면 수정 가능하되 관련 targeted test를 추가한다.

data-source 차이면 수정하지 않고 `intentional deviation`으로 기록한다.

## 8. Golden / PV comparison

둘 다 반드시 기록한다.

```text
PV live comparison: PASS | FAIL
Static golden comparison: PASS | FAIL
P0 mismatches: n
P1 mismatches: n
Intentional deviations: n
```

Static Golden:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

실제로 열지 못했다면 PASS라고 쓰지 않는다.

## 9. Artifacts / result

fresh run과 최소 다음을 commit/push한다.

```text
runs/<run_id>/report.html
runs/<run_id>/validation/visual-comparison.md
```

`agent-to-llm.md`는 최신 result 하나로 교체한다.

반드시 기록:

- Start HEAD
- Agent changed files, if any
- targeted tests + count
- fresh run command / run_id / path / Pages URL
- browser report YES/NO
- browser PV YES/NO
- Frontier Assets schema PASS/FAIL
- Frontier actual X/Y display domain
- ticker별 visible/outside 판정
- Frontier curve hover PASS/FAIL
- Annual Asset 7-series/color/legend/grouped-hover PASS/FAIL
- Up/Down paired bars / 20 groups / 6 observations PASS/FAIL
- 84/36 vs 85/35 exact-month/root-cause assessment
- PV live comparison PASS/FAIL
- Static Golden comparison PASS/FAIL
- P0/P1/intentional-deviation count/list
- remaining issues
- commit SHA

사용자-facing report URL은 GitHub blob이 아니라 Pages URL을 기록한다.
