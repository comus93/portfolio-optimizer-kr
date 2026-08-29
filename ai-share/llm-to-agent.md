# AI Share

state: active
id: 20260829T220000+0900-llm
created_at: 2026-08-29T22:00:00+09:00
type: request
reply_to: none

## Context

사용자가 Research Frontend 및 report 동작을 다음처럼 확정했다.

### Benchmark

- Benchmark는 Research Frontend에서 항상 존재한다.
- 기본 비교대상은 S&P 500 (SPY).
- LLM은 기본값을 다시 선택시키지 않고 `비교대상은 기본적으로 S&P 500(SPY)이며 원하면 변경 가능`하다고 고지한다.
- 사용자가 변경하지 않으면 Experiment/Input YAML에 SPY를 명시적으로 기록한다.
- 오래된 Experiment에 benchmark가 빠져 있어도 Research execution boundary가 SPY default를 effective input에 materialize한다.

### Portfolio Growth hover

- 기존 invisible hover point가 Provided series 높이에만 있어 Optimized line hover가 실패할 수 있었다.
- final renderer가 plot 전체 transparent overlay로 mouse X의 nearest date를 선택해 grouped tooltip을 표시하도록 수정했다.

### Partial calendar years

PV reference에서 partial year도 결과에서 제거하지 않고 실제 available completed months로 annual result를 계산/표시한다.

예:

```text
2016 = Aug-Dec
2026 = Jan-Jul
```

사용자가 같은 방향을 확정했다.

- partial year를 Annual Returns에서 제거하지 않는다.
- Monthly Returns에서 없는 월은 N/A로 유지한다.
- Annual Returns와 Monthly Returns 양쪽에 partial year가 어느 completed months를 기반으로 하는지 note를 표시한다.
- Best/Worst Year의 partial-year 포함 여부는 이번 변경 범위가 아니며 별도 validation 대상으로 유지한다.

LLM이 main에 직접 구현했다.

- `docs/llm-research-input-contract.md`
- `src/portfolio_optimizer_kr/research.py`
- `studies/global-multi-asset-allocation/experiments/001-spy-qqq-tlt-gld-cper-mchi-ewy.yaml`
- `src/portfolio_optimizer_kr/viewer/final_renderer.py`
- `tests/test_research.py`
- `tests/test_report_user_feedback_v4.py`
- `docs/report-visual-overrides-20260829.md`

Research E2E는 PAUSE 상태다. 실제 사용자 Experiment를 다시 실행하지 않는다.

Agent의 PASS/FAIL 평가는 completion 근거가 아니다. 실제 명령 결과와 browser/DOM evidence를 보고한다.

## Message

최신 main을 pull한 뒤 **코드는 수정하지 말고 targeted execution/browser validation만** 수행해라.

### 1. Targeted tests

```text
uv run pytest tests/test_research.py tests/test_report_user_feedback_v4.py -q
```

실패하면 임의 수정하지 말고 exact failure를 보고한다.

### 2. Research benchmark default evidence

benchmark가 없는 임시 Research Experiment/fixture를 `execute_controlled_experiment()`로 실행하고 생성된 임시 `input.yaml`에 아래가 materialize되는지 확인한다.

```yaml
benchmark:
  symbol: SPY
  name: SPDR S&P 500 ETF Trust
  currency: USD
```

명시적 다른 benchmark가 override되지 않는지도 확인한다.

실제 사용자 E2E Experiment를 실행하거나 `control/execute.yaml run:true`로 바꾸지 않는다.

### 3. Portfolio Growth tooltip browser evidence

`runs/20260829-0003` persisted artifacts를 source로 최신 renderer를 사용해 **임시 report HTML**을 생성하고 browser에서 확인한다.

확인사항:

```text
- .final-growth-hover-overlay가 plot-wide hit target으로 존재
- Provided 선 근처에서 tooltip 표시
- Optimized 선 근처에서도 tooltip 표시
- plot 내 다른 Y 높이에서도 같은 mouse X 기준 tooltip 표시
- tooltip에 같은 날짜의 Provided와 Optimized 값이 함께 표시
- 기존 transparent point circles는 pointer-events:none
```

가능하면 overlay x/y/width/height/pointer-events 실제 DOM 값을 보고한다.

### 4. Partial-year note browser evidence

같은 임시 report에서 `runs/20260829-0003`의 2011 partial year를 확인한다.

기대 동작:

```text
Annual Returns:
- 2011 partial return 자체는 계속 표시
- section 아래 partial-year note 존재

Monthly Returns:
- 2011 Jan-Nov = N/A
- 2011 Dec = 기존 실제 return
- 기존 annual/YTD aggregate 값은 유지
- section 아래 partial-year note 존재
- note가 `2011 is based on Dec only` 의미를 전달
```

해당 run에 다른 partial year가 있으면 note가 같이 표시되는지도 실제 문자열로 보고한다.

### 5. 결과 보고

`agent-to-llm.md`에는 raw evidence를 우선한다.

최소:

```text
start HEAD
changed files: none expected
targeted test command + exact result
benchmark-default input.yaml excerpt
explicit benchmark override evidence
temporary report path
Portfolio Growth overlay DOM attributes
Provided/Optimized hover tooltip samples
Annual Returns partial-year note exact text
Monthly Returns partial-year note exact text
2011 monthly row values 확인
browser/runtime blocker exact symptom/log
```

코드 수정은 하지 않는다.
