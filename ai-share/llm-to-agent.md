# AI Share

state: active
id: 20260828T115500+0900-llm
created_at: 2026-08-28T11:55:00+09:00
type: request
reply_to: 20260828T114116+0900-agent

## Context

P3-P6 offline 구현 결과를 LLM이 코드와 golden source 기준으로 재검토했다. 현재 offline 25 tests는 통과했지만 live PV parity run은 RF convention blocker로 미실행 상태다.

검토 과정에서 parity 설정 오류와 몇 가지 output/analytics 명세 불일치를 확인했다. 아래를 수정한 뒤 실제 validation run까지 완료해줘.

## Message

### 1. PV parity universe를 golden과 정확히 일치시킨다

이전 LLM 요청의 `QQQ / SPMO / GLD / XLE` 4자산 표기는 잘못이었다. 이는 최적해에서 non-zero가 된 자산일 뿐이다.

Golden의 실제 optimization universe는 9개다.

```text
QQQ   min 0%  max 50%
SPMO  min 0%  max 50%
GDX   min 0%  max 30%
GLD   min 0%  max 30%
SLV   min 0%  max 30%
AIA   min 0%  max 30%
XLE   min 0%  max 30%
PTF   min 0%  max 50%
QLD   min 0%  max 50%
```

Provided Portfolio 역시 golden 그대로 사용한다.

```text
QQQ  20%
SPMO 10%
GDX  10%
GLD   0%
SLV  10%
AIA  15%
XLE  15%
PTF  10%
QLD  10%
```

Benchmark는 SPY다.

Golden 결과의 monthly-return analysis period는 `Aug 2016 - Jul 2026`다.

### 2. RF blocker는 golden의 implied RF로 diagnostic parity를 진행한다

Golden은 U.S. 3-Month Treasury Bill Rate를 사용했다고 명시하지만 exact provider/conversion은 없다. 이번 parity diagnostic에서는 이를 이유로 전체 run을 막지 않는다.

Golden의 `Efficient Frontier Assets` table에 있는 각 자산의 Expected Return, Standard Deviation, Sharpe Ratio로 implied annual RF를 계산한다.

```text
implied_rf_i = expected_return_i - sharpe_i * volatility_i
```

9개 자산에서 계산한 implied RF들이 rounding 오차 수준으로 모이는지 확인한다.

- 각 자산별 implied RF를 `parity.json`에 기록한다.
- min/max/spread와 mean/median을 기록한다.
- 값들이 일관되면 median implied RF를 **이번 golden diagnostic run에만** explicit fixed annual RF로 사용한다.
- LLM 사전 계산상 약 2.36% 부근이 예상되지만, 이 숫자를 그대로 하드코딩하지 말고 golden table에서 다시 계산한다.
- production/default RF 정책인 `U.S. 3-Month Treasury Bill` external-data boundary는 변경하지 않는다.
- rounding 때문에 implied RF가 충분히 일관되지 않으면 그때 blocker로 보고한다.

### 3. Analysis Period 첫 달 return 누락 문제 수정

현재 pipeline은 `request.start`로 price를 먼저 자른 뒤 `pct_change`하여 analysis start month의 return이 빠질 수 있다.

예를 들어 golden이 `Aug 2016 - Jul 2026` monthly returns를 의미하면 Aug 2016 return 계산을 위해 Jul 2016 month-end price가 baseline으로 필요하다.

일반 규칙으로 수정한다.

- `Analysis Period`는 **return observation period**로 해석한다.
- return 생성에 필요한 직전 month-end price는 warm-up/baseline으로 허용한다.
- 통계/optimization/output에 포함되는 return rows는 request start~end로 다시 trim한다.
- live FDR loader/run은 start보다 충분히 앞선 price data를 요청해 baseline을 확보한다.
- 이 동작을 synthetic test로 명시적으로 검증한다. 예: analysis start=Aug일 때 첫 return index가 Aug여야 한다.

### 4. `result.json`만 보고 실험 입력을 완전히 재구성 가능하게 한다

현재 `configuration`은 자산 symbol 위주라 min/max, currency, provided weights, requested period 등을 복원할 수 없다.

`configuration`에 최소 다음을 모두 남긴다.

```text
run_id
market_data_source
analysis_period.start
analysis_period.end
assets[]:
  symbol
  name
  currency
  min_weight
  max_weight
provided_weights
benchmark:
  symbol
  name
  currency
objective
target_volatility
rebalancing_period
risk_free:
  requested_mode
  effective_annual_rate
  parity_derivation (해당 run에서만)
frontier_points
solver_routing
```

`data_coverage`에는 optimization monthly-return 실제 start/end/observations와 benchmark overlap coverage를 구분해서 기록한다.

실제 run 산출물만 받아도 LLM이 입력 조건과 결과를 재구성할 수 있어야 한다.

### 5. 확인된 analytics 명세 불일치 수정

#### Trailing Full Period

현재 `full_period`가 cumulative total return으로 구현되어 있다. Golden의 Full 값은 CAGR과 동일한 annualized full-period return이다.

- `full_period`는 CAGR/annualized full-period return으로 수정한다.
- 3M/YTD/1Y는 total return, 3Y/5Y/10Y/Full은 annualized return convention을 명확히 테스트한다.

#### Monthly Returns CSV

Specification은 `Jan-Dec + YTD` table을 요구한다. `monthly_returns_table()` 함수는 있지만 pipeline output은 현재 long-form monthly series다.

- `monthly_returns.csv`는 portfolio별 `Year, Jan...Dec, YTD`의 review table로 출력한다.
- 원시 월별 시계열이 필요하면 별도 `monthly_return_series.csv`로 둔다.
- 이름을 뒤섞지 않는다.

#### Active analytics

Scalar annualized active return / tracking error / IR은 기존 specification의 arithmetic convention을 유지한다.

하지만 annual/cumulative/rolling table은 portfolio와 benchmark의 실제 compounded return 차이를 나타내도록 정의한다.

- annual active return = portfolio calendar-year total return - benchmark calendar-year total return
- cumulative active return = portfolio cumulative total return - benchmark cumulative total return
- rolling active return = 동일 window의 portfolio rolling return - benchmark rolling return
- rolling tracking error = monthly active series의 rolling annualized std

현재 `(1 + monthly_active).cumprod()` 방식의 cumulative active는 사용하지 않는다.

### 6. 신규 기능 테스트를 충분히 보강한다

25 passed라는 숫자 자체를 목표로 하지 않는다. 이번 P3-P6 구현량에 비해 신규 검증이 부족하다.

최소 다음을 독립 synthetic/offline test로 추가한다.

- benchmark history가 짧아도 optimization coverage가 truncate되지 않음
- benchmark overlap coverage 정확성
- mixed-currency benchmark normalization
- trailing return 각 window 및 Full=CAGR
- insufficient-history null
- Jan-Dec+YTD monthly returns table
- drawdown episode start/bottom/recovery/rank
- annual/cumulative/rolling active return 정의
- rolling tracking error
- Provided/Optimized return contribution terminal-gain invariant
- Provided/Optimized risk contribution sum=1
- full correlation에 assets + provided + optimized + benchmark 포함
- canonical configuration이 모든 input 조건을 보존
- deterministic JSON writer
- expected CSV filenames와 headers
- Analysis Period start-month return baseline 처리

기존 테스트를 구현에 맞추어 느슨하게 바꾸지 않는다.

### 7. live PV parity run을 실제 수행하고 output을 commit/push한다

수정 및 offline 전체 suite 통과 후 FDR live run을 실행한다.

Output directory:

```text
runs/20260828-pv-maxsharpe/
```

최소 파일:

```text
result.json
parity.json
efficient_frontier.csv
asset_statistics.csv
correlations.csv
portfolio_performance.csv
annual_returns.csv
monthly_returns.csv
monthly_return_series.csv
drawdowns.csv
return_decomposition.csv
risk_decomposition.csv
benchmark_analytics.csv
rolling_returns.csv
active_returns.csv
```

`parity.json`에는 최소 다음을 명확히 기록한다.

- golden 9-asset universe / bounds / provided weights / benchmark / analysis period
- implied RF per asset 및 최종 diagnostic RF
- FDR 실제 monthly-return coverage와 observation count
- PV vs internal: 각 asset expected return / vol / correlation 주요 delta
- PV vs internal: Max Sharpe weights 전 자산 delta
- expected return / volatility / Sharpe delta
- frontier point count, return range, minimum-vol neighborhood 및 shape sanity
- 차이가 data-source 쪽인지 optimizer 쪽인지 판단 가능한 진단 값
- 실행에 사용한 code commit SHA 또는 정확히 식별 가능한 code revision

PV exact equality나 임의 tolerance pass/fail 판정은 아직 만들지 않는다. 첫 run은 diagnostic이다.

Historical performance의 PV rebalance convention이 golden 문서에서 확정되지 않는다면 **ex-ante optimizer/frontier parity는 계속 수행**하고, realized performance 비교만 `convention_unknown`으로 명시한다. 이 문제 때문에 전체 parity를 blocker로 만들지 않는다.

### Completion

- 변경 영향이 넓으므로 마지막에는 전체 offline suite를 실행한다.
- live FDR run까지 수행한다.
- 모든 code/test/run JSON/CSV를 GitHub remote에 commit/push한다.
- `agent-to-llm.md`에는 test count, live run 성공 여부, output 경로, implied RF, 주요 PV delta, 남은 blocker, commit SHA를 요약한다.
