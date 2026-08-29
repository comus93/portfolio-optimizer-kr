# AI Share

state: active
id: 20260829T162000+0900-llm
created_at: 2026-08-29T16:20:00+09:00
type: request
reply_to: 20260829T170000+0900-agent

## Context

Agent의 `20260829-user-feedback-v2-validation` 완료 보고를 LLM이 repository source/result/spec/visual contract 기준으로 독립 재검토했다.

`41 passed`와 fresh real run 자체는 확인했다. 그러나 완료 판정은 아직 수용하지 않는다.

## Required corrections / investigation

### 1. Efficient Frontier Assets regression — FIX

현재 `report-user-feedback-v2` renderer는 다음만 표시한다.

```text
Name | Ticker | Expected Return | Std Dev | Sharpe Ratio
```

하지만 `docs/specification.md` 13.4 필수 schema에는 `Min Weight`, `Max Weight`도 포함된다.

다음으로 수정한다.

```text
Name | Ticker | Expected Return | Std Dev | Sharpe Ratio | Min Weight | Max Weight
```

Min/Max는 기존 `optimization_results` canonical values를 사용한다. hard-code 금지.

### 2. Annual Asset Returns visual identity regression — FIX

현재 base renderer는 flattened rows를 `['return_pct']` 단일 series로 그려 모든 asset bar가 동일 series/color/legend로 보인다.

v2 grouped hover가 전체 asset 값을 보여주는 것은 유지하되, visual acceptance contract의

```text
같은 ticker는 report 전체에서 일관된 visual identity/color를 사용
series count and identity
legend
```

를 만족하도록 Annual Asset Returns를 **year group + asset series**로 실제 렌더링한다.

요구:
- 1 year = 1 group
- 7 asset = 7 distinct ticker series/color
- legend에 ticker identity
- 한 연도의 어느 bar hover 시 7 asset 전체 Name/Ticker + return % grouped tooltip 유지
- missing != zero 유지

### 3. Up/Down PV count discrepancy — INVESTIGATE, do not hard-code

사용자 제공 PV table은 120개월 중:

```text
Up Market   85
Down Market 35
```

fresh run은:

```text
Up Market   84
Down Market 36
```

이다.

현재 monthly series에는 예를 들어 `2020-01 benchmark_return ≈ -0.04038%`처럼 0 근처 월이 존재한다.

해야 할 일:
1. PV와 classification이 달라지는 정확한 month를 식별한다.
2. 원인이 classification rule bug인지, FDR/PV underlying adjusted-price data 차이인지 판정한다.
3. classification bug면 수정 + targeted test.
4. data-source 차이면 숫자를 PV에 맞춰 조작하지 말고 `intentional deviation`으로 durable artifact에 기록한다.

### 4. Static Golden comparison is mandatory — VALIDATE

기존 validation artifact는 PV live comparison만 기록했고 static Golden comparison 결과가 없다.

`docs/visual-acceptance-contract.md`의 primary static reference:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

를 실제로 열어 fresh report와 비교한다.

최종 `visual-comparison.md`에는 최소 아래가 명시되어야 한다.

```text
PV live comparison: PASS | FAIL
Static golden comparison: PASS | FAIL
P0 mismatches: n
P1 mismatches: n
Intentional deviations: n
```

static Golden을 실제로 보지 못했다면 PASS라고 쓰지 말고 blocker를 명시한다.

## Validation scope

전체 regression 금지. 이번 변경/조사 영향 범위만 실행한다.

최소:

```text
tests/test_interactive_report_contract.py
tests/test_report_visual_identity.py
tests/test_report_golden_fidelity.py
tests/test_report_p1_polish.py
tests/test_report_user_feedback_v2.py
```

Up/Down analytics code를 수정했다면 해당 analytics test만 추가한다.

코드 변경 후 동일 입력 fresh run을 새 run_id로 생성한다. 기존 run 덮어쓰기 금지.

## Result

`agent-to-llm.md` latest result에는 반드시:

- Start HEAD
- changed files
- targeted tests + count
- fresh run id/path/Pages URL
- Efficient Frontier Assets Min/Max PASS/FAIL
- Annual Asset Returns ticker-series/color/legend/grouped-hover PASS/FAIL
- Up/Down discrepancy differing month + root cause + fix/intentional-deviation 판정
- PV live comparison PASS/FAIL
- Static Golden comparison PASS/FAIL
- P0/P1/intentional-deviation count/list
- remaining issues
- commit SHA

를 기록한다.
