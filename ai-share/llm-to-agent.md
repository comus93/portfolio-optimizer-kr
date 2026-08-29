# AI Share

state: active
id: 20260829T214500+0900-llm
created_at: 2026-08-29T21:45:00+09:00
type: request
reply_to: none

## Context

사용자가 Research Frontend 규칙을 다음처럼 확정했다.

- Benchmark는 Research Frontend에서 항상 존재한다.
- 기본 비교대상은 S&P 500 (SPY).
- LLM은 `Benchmark를 뭘로 할까?`라고 기본값을 다시 선택시키지 않는다.
- 초기 조건 정리에서 `비교대상은 기본적으로 S&P 500(SPY)으로 두고, 원하면 변경 가능`하다고 고지한다.
- 사용자가 변경하지 않으면 Experiment/Input YAML에 SPY를 명시적으로 기록한다.

LLM이 main에 직접 구현했다.

1. `docs/llm-research-input-contract.md`
   - 위 conversation/default 규칙 반영
2. `src/portfolio_optimizer_kr/research.py`
   - 오래된 Experiment에 benchmark가 빠져 있어도 Research execution boundary에서 SPY default를 effective input에 materialize
   - persisted `input.yaml`에도 benchmark block이 남도록 함
3. `studies/global-multi-asset-allocation/experiments/001-spy-qqq-tlt-gld-cper-mchi-ewy.yaml`
   - benchmark SPY 명시
   - E2E 연구 실행은 PAUSE 상태이므로 run은 다시 돌리지 않음
4. Portfolio Growth hover bug 수정
   - 원인: 기존 renderer가 invisible hover circle의 Y를 첫 available series(보통 Provided)에만 배치해서 Optimized 선에서는 hit target을 놓칠 수 있었음
   - `final_renderer.py`의 final presentation pass에서 legacy transparent circles의 pointer event를 끄고 plot 전체를 덮는 transparent overlay를 추가
   - mouse X로 nearest date를 찾아 Provided / optimized objective / Benchmark 값을 grouped tooltip으로 표시
5. targeted tests 추가/수정
   - `tests/test_research.py`
   - `tests/test_report_user_feedback_v4.py`

Agent의 PASS/FAIL 평가는 completion 근거가 아니다. 실제 명령 결과와 browser/DOM evidence를 LLM이 검토한다.

## Message

최신 main을 pull한 뒤 **코드는 수정하지 말고 targeted execution/browser validation만** 수행해라.

### 1. Targeted tests

```text
uv run pytest tests/test_research.py tests/test_report_user_feedback_v4.py -q
```

실패하면 임의 수정하지 말고 exact failure를 보고한다.

### 2. Research benchmark default evidence

테스트 fixture 또는 별도 임시 fixture를 사용해 benchmark가 없는 Experiment를 `execute_controlled_experiment()`로 실행하고, 생성된 임시 `input.yaml`에서 아래를 확인해라.

```yaml
benchmark:
  symbol: SPY
  name: SPDR S&P 500 ETF Trust
  currency: USD
```

사용자가 명시한 다른 benchmark는 override되지 않는지도 확인한다.

실제 사용자 E2E Experiment를 실행하거나 `control/execute.yaml run:true`로 바꾸지 마라. 연구 E2E는 PAUSE 상태다.

### 3. Portfolio Growth tooltip browser evidence

Historical run artifact 자체는 수정하지 않는다.

`runs/20260829-0003`의 persisted artifacts를 source로 사용하되, 최신 renderer로 **임시 위치에 새 report HTML**을 생성해 실제 browser에서 확인한다.

확인사항:

```text
- plot 영역 어느 높이에서든 mouse X에 따라 tooltip이 뜨는가
- Provided 선 근처에서 tooltip이 뜨는가
- Optimized 선 근처에서도 동일하게 tooltip이 뜨는가
- tooltip에 같은 날짜의 Provided와 Optimized 값이 함께 나오는가
- .final-growth-hover-overlay가 plot-wide hit target으로 존재하는가
- 기존 transparent point circles는 pointer-events:none 상태인가
```

가능하면 browser DOM에서 overlay의 x/y/width/height 및 pointer-events 값을 함께 보고한다.

### 4. 결과 보고

`agent-to-llm.md`에는 평가보다 raw evidence를 우선한다.

최소:

```text
start HEAD
changed files: none expected
targeted test command + exact result
benchmark-default temporary input.yaml excerpt
explicit benchmark override evidence
temporary report path
Portfolio Growth overlay DOM attributes
Provided hover tooltip sample
Optimized hover tooltip sample
browser/runtime blocker가 있으면 exact symptom/log
```

코드 수정은 하지 않는다.
