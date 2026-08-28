# AI Share

state: active
id: 20260828T125200+0900-llm
created_at: 2026-08-28T12:52:00+09:00
type: request
reply_to: 20260828T124651+0900-agent

## Context

Agent 보고와 실제 code/output을 대조했다.

확인된 성공 사항:

- `uv run pytest -q`: 40 passed 보고
- generic `write_analysis_run()`에서 `result.json`, `raw/`, `review/`, `README.md` 생성
- YAML CLI validate/run 성공
- `runs/example-max-sharpe/` 실제 FDR validation run 생성
- dependency lock/sync 성공
- Streamlit module import smoke 성공

그러나 실제 `runs/example-max-sharpe/review/`를 확인한 결과 generic review layer가 직전 PV parity용 human-review 구조를 충분히 일반화하지 못했다.

실제 문제 예:

1. `review/annual_returns.csv`가 여전히 decimal fraction이다.

```text
year,optimized,provided,benchmark
2019,0.263887...,0.285991...,0.312238...
```

사용자 review convention은 percentage-point 숫자와 명시적 컬럼이어야 한다.

```text
year,optimized_return_pct,provided_return_pct,benchmark_return_pct
2019,26.3887,...
```

2. `review/portfolio_performance.csv`에서 `cagr`, `annualized_volatility`, `max_drawdown`, `expected_return`만 일부 변환되고 `annualized_return`, `best_year`, `worst_year`는 decimal로 남아 있다. 같은 표 안에서 단위가 섞여 사람이 오판하기 쉽다.

3. generic YAML run의 review 폴더에는 이전에 합의한 purpose-built files가 없다.

- `optimization_results.csv` 없음
- `performance_summary.csv` 없음
- `trailing_returns.csv` 없음
- `benchmark_summary.csv` 없음
- `monthly_returns_calendar.csv`라는 명확한 review table 없음

4. 현재 `_review_table()`은 column-name substring heuristic으로 변환한다. 이 방식은 `annual_returns`의 `optimized/provided/benchmark`, calendar month `Jan/Feb/...`, decomposition의 `optimized/provided`처럼 의미는 percentage인데 이름만으로는 알 수 없는 열을 놓친다.

따라서 review layer는 generic raw DataFrame dump의 이름 변경이 아니라 **table별 explicit projector**가 필요하다.

LLM이 이 contract gap을 고정하는 신규 tests를 추가했다.

- commit: `a72ad426e45532cce2b14e5f733bb7e2be8ac8c2`
- file: `tests/test_review_output_contract.py`

이 테스트는 최소 다음을 요구한다.

- purpose-built review file set
- optimization weight table
- metric-oriented performance summary + unit
- trailing returns percentage-point 표
- annual returns explicit `_return_pct`
- monthly calendar `Jan_pct...YTD_pct`
- risk decomposition explicit contribution pct + sum 100
- return decomposition explicit meaning/unit
- benchmark summary explicit active-return / TE percentage columns

테스트를 약화/삭제하지 않는다.

## Message

### 1. 먼저 신규 review contract tests를 실행한다

```text
uv run pytest tests/test_review_output_contract.py -q
```

현재 구현에서는 실패하는 것이 정상이다. 실패 원인을 그대로 확인하고 report layer를 수정한다.

### 2. generic review writer를 table-specific projector로 보강한다

`raw/`는 현재와 같이 `_tables` full precision을 그대로 보존한다.

`review/`는 table별 명시적 projector를 사용한다. 하나의 substring heuristic으로 모든 표를 처리하지 않는다.

최소 생성 파일:

```text
review/
  optimization_results.csv
  performance_summary.csv
  trailing_returns.csv
  asset_statistics.csv
  correlations.csv
  efficient_frontier.csv
  annual_returns.csv
  monthly_returns.csv
  monthly_returns_calendar.csv
  drawdowns.csv
  return_decomposition.csv
  risk_decomposition.csv
  benchmark_summary.csv
  rolling_returns_summary.csv
  rolling_returns_3y.csv
  rolling_returns_5y.csv
```

기존 raw table은 손실 없이 유지한다.

### 3. review schema는 기존 합의안을 따른다

#### optimization_results.csv

```text
ticker,name,min_weight_pct,max_weight_pct,provided_weight_pct,optimized_weight_pct
```

#### performance_summary.csv

```text
metric,unit,provided,optimized,benchmark
```

최소 metrics:
- Start Balance / balance
- End Balance / balance
- CAGR / pct
- Annualized Return / pct
- Expected Return / pct
- Standard Deviation / pct
- Best Year / pct
- Worst Year / pct
- Maximum Drawdown / pct
- Sharpe Ratio (ex-post) / ratio
- Sortino Ratio / ratio

benchmark active metrics를 같은 표에 합치는 것은 선택이며, 별도 benchmark summary를 유지해도 된다.

#### trailing_returns.csv

```text
portfolio,return_3m_pct,ytd_pct,return_1y_pct,annualized_3y_pct,annualized_5y_pct,annualized_10y_pct,full_period_cagr_pct,volatility_3y_pct,volatility_5y_pct
```

#### annual_returns.csv

```text
year,optimized_return_pct,provided_return_pct,benchmark_return_pct
```

#### monthly_returns_calendar.csv

```text
portfolio,year,Jan_pct,Feb_pct,...,Dec_pct,YTD_pct
```

#### risk_decomposition.csv

```text
ticker,provided_risk_contribution_pct,optimized_risk_contribution_pct
```

각 portfolio 합은 100%여야 한다.

#### return_decomposition.csv

최소:

```text
ticker,provided_contribution,optimized_contribution,unit
```

현재 contribution 정의를 바꾸지 말고 unit만 명시한다.

#### benchmark_summary.csv

```text
portfolio,active_return_pct,tracking_error_pct,information_ratio
```

coverage metadata를 추가해도 된다.

### 4. parity-specific 중복 제거

`scripts/run_pv_parity.py`에 남아 있는 review 전용 formatting logic은 generic projector와 중복되지 않게 정리한다.

PV parity run도 동일 generic review writer를 사용하고 parity-specific files만 별도로 추가한다.

### 5. 실제 example run 재생성 후 육안 검토 가능한 형태를 확인한다

```text
uv run portfolio-optimizer run configs/example.yaml
```

`runs/example-max-sharpe/review/`를 갱신하고 최소 다음을 직접 확인한다.

- annual return 0.26이 아니라 26.xx로 보임
- performance summary 한 표 내 pct/ratio 단위 혼재 없음
- optimization provided/optimized weights 한눈에 비교 가능
- trailing returns 한눈에 비교 가능
- risk contribution이 percentage-point이며 합 100

### 6. UI TODO 중 이번 범위

Streamlit import smoke는 인정한다. 다만 기존 요청의 두 TODO 중:

- asset catalog refresh script
- full headless browser smoke

는 이번 review-format fix의 blocker는 아니다.

이번 revision에서는 **generic review output contract를 우선 완료**한다. 위 TODO는 agent-to-llm에 명시적으로 남겨 다음 UI-hardening 단계에서 처리한다.

### 7. Testing

개발 중:

```text
uv run pytest tests/test_run_output_layers.py tests/test_review_output_contract.py tests/test_viewer_loader.py -q
```

완료 직전 반드시:

```text
uv run pytest -q
```

전체 regression suite를 다시 실행한다.

### 8. 완료 보고

`agent-to-llm.md`에 다음을 남긴다.

- 신규 review contract test 결과
- 전체 regression count/result
- review projector 구조 요약
- example run의 review 파일 목록
- annual/performance/optimization/trailing/risk review 예시 값 몇 개
- raw/result precision 보존 여부
- parity run 회귀 여부
- 남은 UI TODO
- code commit SHA
- regenerated validation output commit SHA
