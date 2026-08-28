# AI Share

state: active
id: 20260828T122800+0900-llm
created_at: 2026-08-28T12:28:00+09:00
type: request
reply_to: 20260828T120123+0900-agent

## Context

Live FDR PV parity run과 JSON/CSV output은 성공했고 optimizer 결과는 PV와 매우 근접하다.

확인된 주요 수치:

- Max Sharpe ER: internal 17.2052% vs PV 17.21%
- Volatility: internal 13.1025% vs PV 13.10%
- Sharpe: internal 1.1333 vs PV 1.13
- Weight delta: QQQ -0.225pp, SPMO +0.367pp, GLD ~0pp, XLE -0.131pp
- Frontier expected-return range: internal 16.2177%~30.0039% vs PV 16.23%~30.08%
- 120 monthly returns, Aug-2016~Jul-2026 coverage 확인

LLM이 실제 run CSV 전체를 검토한 결과 계산값은 대체로 충분하지만, 현재 CSV는 내부 DataFrame을 그대로 dump한 개발자용 산출물 성격이 강하다. 사용자가 육안으로 검토하거나 다른 LLM이 run 폴더만 받아 의미를 재구성하기에는 percentage 단위, column naming, table orientation, MultiIndex header, unlabeled row 등이 불친절하다.

`result.json`은 계속 full-precision canonical source of truth로 유지한다. CSV는 **사람/LLM review용 표현 계층과 machine/raw 계층을 분리**해 개선한다. Review 표현을 위해 원본 계산 precision이나 raw series를 잃으면 안 된다.

## Message

### 1. PV moments를 이용한 solver-only parity를 추가한다

Golden MD의 9 assets expected return, standard deviation, 9x9 correlation, bounds를 이용해 PV rounded moments를 재구성한다.

```text
PV covariance = diag(PV volatility) @ PV correlation @ diag(PV volatility)
```

현재 golden-implied RF와 동일 bounds로 `maximum_sharpe()`를 FDR 없이 PV moments에 직접 적용한다.

`parity.json`에 최소 다음 section을 추가한다.

```text
moment_parity:
  per_asset expected_return_delta
  per_asset volatility_delta
  correlation max_abs_delta
  correlation mean_abs_delta

solver_only_parity:
  internal_weights_from_pv_moments
  weight_delta_vs_pv
  expected_return
  volatility
  sharpe
  note_on_golden_rounding
```

최소 output:

```text
moment_parity.csv
solver_parity.csv
```

가능하면 golden 100-row frontier도 비교해 `frontier_parity.csv`를 추가한다. PV 공개값은 rounding된 값이므로 exact-equality pass/fail은 만들지 않는다.

### 2. P3-P6 신규 기능 synthetic tests를 확장한다

최소 다음 behavior를 독립적으로 검증한다.

- benchmark history가 짧아도 optimization coverage를 truncate하지 않음
- benchmark overlap start/end/observation count
- mixed-currency benchmark normalization
- trailing 3M/YTD/1Y 및 annualized 3Y/5Y/10Y/Full
- insufficient-history -> None/null
- Jan-Dec + YTD review table
- drawdown episode start/bottom/recovery/rank
- annual/cumulative/rolling active-return convention
- rolling tracking error
- Provided/Optimized return contribution terminal-gain invariant
- Provided/Optimized risk contribution sum=1
- full correlation universe = assets + provided + optimized + benchmark
- canonical configuration input 보존
- deterministic JSON output
- expected review/raw CSV filenames 및 핵심 headers
- PV moments parser 9 assets/correlation/frontier parsing
- solver-only parity fixture는 offline/network-free
- review 값이 raw 값의 display transform과 일치하고 raw precision이 보존됨

기존 core tests를 약화하거나 삭제하지 않는다.

### 3. Sortino denominator convention을 명시적으로 고정한다

```text
monthly MAR = (1 + annual_rf) ** (1/12) - 1
downside_i = min(monthly_return_i - monthly_MAR, 0)
monthly downside deviation = sqrt(mean(downside_i ** 2))
annual downside deviation = monthly downside deviation * sqrt(12)
Sortino = (annualized arithmetic return - annual_rf) / annual downside deviation
```

코드와 test에 반영한다. PV Sortino와 exact parity는 요구하지 않으며 정의 차이가 있으면 명시한다.

### 4. 전체 run output을 Review Layer와 Raw Layer로 재설계한다

특정 `rolling_returns.csv`만 수정하지 말고 **현재 생성되는 전체 CSV output을 사용자 인식성/검토 용이성 관점에서 검토하고 일관된 구조로 정리한다.**

원칙:

1. `result.json`은 canonical machine-readable source of truth이며 full precision을 유지한다.
2. `raw/` CSV는 현재 계산 결과와 시계열을 full precision decimal로 보존한다.
3. `review/` CSV는 사람이 직접 읽고 PV golden과 비교하기 쉬운 표 구조로 제공한다.
4. PV에 대응 표가 있는 경우 가능한 한 PV의 orientation/metric grouping을 따른다. 단, PV를 맹목적으로 복제하지 않고 의미와 단위가 더 명확하면 개선 가능하다.
5. Review 때문에 raw data나 precision을 삭제하지 않는다.
6. MultiIndex CSV header, duplicate column name, unlabeled row, 단위가 불명확한 ratio column은 금지한다.
7. percentage review value는 decimal fraction이 아니라 percentage-point 숫자를 사용한다. 예: raw `0.172052` -> review `17.2052`. 컬럼에 `_pct`를 붙이거나 `unit` column으로 단위를 명확히 한다.
8. Sharpe/Sortino/correlation/IR 등 무차원 ratio는 `%`로 바꾸지 않는다.
9. null/N/A와 실제 0을 구분한다.
10. review용 rounding은 표시 계층에서만 수행하고 raw/result.json에는 적용하지 않는다.
11. 날짜와 기간 표기는 파일별로 일관되게 한다.

권장 디렉터리:

```text
runs/<run_id>/
├─ result.json
├─ parity.json
├─ README.md
├─ review/
│  ├─ optimization_results.csv
│  ├─ performance_summary.csv
│  ├─ trailing_returns.csv
│  ├─ asset_statistics.csv
│  ├─ correlations.csv
│  ├─ efficient_frontier.csv
│  ├─ annual_returns.csv
│  ├─ monthly_returns.csv
│  ├─ monthly_returns_calendar.csv
│  ├─ drawdowns.csv
│  ├─ return_decomposition.csv
│  ├─ risk_decomposition.csv
│  ├─ benchmark_summary.csv
│  ├─ rolling_returns_summary.csv
│  ├─ rolling_returns_3y.csv
│  └─ rolling_returns_5y.csv
└─ raw/
   ├─ efficient_frontier.csv
   ├─ asset_statistics.csv
   ├─ correlations.csv
   ├─ portfolio_performance.csv
   ├─ annual_returns.csv
   ├─ monthly_return_series.csv
   ├─ monthly_returns_calendar.csv
   ├─ drawdowns.csv
   ├─ return_decomposition.csv
   ├─ risk_decomposition.csv
   ├─ benchmark_analytics.csv
   ├─ active_returns.csv
   └─ rolling_returns.csv
```

기존 top-level CSV 경로와의 backward compatibility가 필요하면 한 revision 동안 유지하거나 명확한 migration을 선택하되, 중복의 source of truth는 만들지 않는다. 최종 구조는 `README.md`에서 설명한다.

### 5. Review CSV별 구체적 형태

#### optimization_results.csv

PV의 Provided Portfolio / Maximum Sharpe allocation을 한 번에 비교하기 쉽게 한다.

예:

```text
ticker,name,min_weight_pct,max_weight_pct,provided_weight_pct,optimized_weight_pct
QQQ,...,0.0,50.0,20.0,24.3845
...
```

zero-weight asset도 universe 확인을 위해 유지한다.

#### performance_summary.csv

현재 row-per-portfolio 구조보다 PV처럼 metric 중심으로 읽기 쉽게 한다.

권장:

```text
metric,unit,provided,optimized,benchmark
Start Balance,balance,...
End Balance,balance,...
CAGR,pct,...
Expected Return,pct,...
Standard Deviation,pct,...
Best Year,pct,...
Worst Year,pct,...
Maximum Drawdown,pct,...
Sharpe Ratio (ex-post),ratio,...
Sortino Ratio,ratio,...
Active Return,pct,...
Tracking Error,pct,...
Information Ratio,ratio,...
```

ex-ante/ex-post가 동시에 존재하면 이름으로 구분한다.

#### trailing_returns.csv

PV Trailing Returns 구조를 따라 portfolio가 row가 되도록 한다.

최소 columns:

```text
portfolio,return_3m_pct,ytd_pct,return_1y_pct,annualized_3y_pct,annualized_5y_pct,annualized_10y_pct,full_period_cagr_pct,volatility_3y_pct,volatility_5y_pct
```

#### asset_statistics.csv

PV Efficient Frontier Assets와 대응되도록 한다.

```text
ticker,name,expected_return_pct,standard_deviation_pct,sharpe_ratio,min_weight_pct,max_weight_pct
```

필요하면 trailing asset performance는 별도 `portfolio_asset_performance.csv`로 분리한다.

#### correlations.csv

row ticker/name + matrix 형태로 유지한다. correlation은 -1~1 ratio 그대로 둔다. assets + provided + optimized + benchmark가 포함됐는지 식별 가능해야 한다.

#### efficient_frontier.csv

100개 point를 유지하되 review에서는 단위를 명확히 한다.

```text
point,expected_return_pct,standard_deviation_pct,sharpe_ratio,weight_QQQ_pct,...
```

raw에는 기존 full precision decimal을 보존한다.

#### annual_returns.csv

```text
year,provided_return_pct,optimized_return_pct,benchmark_return_pct
```

partial year임을 README/result configuration에서 알 수 있어야 한다.

#### monthly_returns.csv

PV의 월별 상세표에 가깝게 사람이 검토 가능한 long form을 제공한다.

예:

```text
year,month,provided_return_pct,optimized_return_pct,benchmark_return_pct,QQQ_return_pct,SPMO_return_pct,...
```

raw month-end series는 별도 유지한다.

#### monthly_returns_calendar.csv

현재 Jan-Dec+YTD 표는 useful하므로 별도 review table로 유지한다.

```text
portfolio,year,Jan_pct,Feb_pct,...,Dec_pct,YTD_pct
```

#### drawdowns.csv

PV worst drawdown table에 가깝게 검토 가능하게 한다.

최소:

```text
portfolio,rank,start,bottom,recovery,length_months,recovery_months,underwater_months,drawdown_pct
```

필요하면 현재 internal `duration_months`와 PV의 Length/Recovery Time/Underwater Period 정의 차이를 명확히 분리한다. Review에는 우선 worst 10을 제공하고 raw에는 전체 episode를 보존해도 좋다.

#### return_decomposition.csv

현재 `asset=contribution_QQQ` 같은 구조는 수정한다.

```text
ticker,name,provided_contribution,optimized_contribution,unit
```

현재 계산이 initial portfolio value=1 기준 monetary contribution이라면 unit을 명시한다. 사용자/PV 검토용으로 initial balance 10,000 기준 contribution을 추가하는 것이 자연스럽다면 별도 columns로 제공하되 raw 정의를 바꾸지 않는다.

#### risk_decomposition.csv

```text
ticker,name,provided_risk_contribution_pct,optimized_risk_contribution_pct
```

합계가 각각 100%가 되는지 test한다.

#### benchmark_summary.csv

현재 unlabeled rows를 제거한다.

```text
portfolio,active_return_pct,tracking_error_pct,information_ratio,overlap_start,overlap_end,observations
optimized,...
provided,...
```

coverage를 별도 row로 억지로 섞지 말고 portfolio row에 overlap metadata를 반복하거나 별도 `benchmark_coverage.csv`로 분리해도 된다.

### 6. Rolling Returns는 PV summary + detail 시계열로 분리한다

현재 `rolling_returns.csv`는 pandas MultiIndex 2단 header와 decimal 값을 그대로 써 사람이 검토하기 어렵다.

Review summary:

```text
review/rolling_returns_summary.csv
```

```text
roll_period_years,
provided_average_pct,provided_high_pct,provided_low_pct,
optimized_average_pct,optimized_high_pct,optimized_low_pct,
benchmark_average_pct,benchmark_high_pct,benchmark_low_pct
```

rows: 1Y, 3Y, 5Y, 7Y.

정의:
- 1Y = 12-month compounded total return
- 3Y/5Y/7Y = 해당 window compounded return의 annualized geometric return
- Average/High/Low는 유효 rolling observations 기준

Review detail:

```text
review/rolling_returns_3y.csv
review/rolling_returns_5y.csv
```

```text
date,provided_annualized_return_pct,optimized_annualized_return_pct,benchmark_annualized_return_pct
```

window가 차기 전 blank-only row는 review file에서 제외한다. 기존 full-precision raw 시계열은 `raw/rolling_returns.csv`에 유지한다.

PV golden summary와 직접 비교한다.

PV 3Y:
- Provided Avg 17.83%, High 39.07%, Low 4.13%
- Optimized Avg 17.17%, High 35.98%, Low 7.03%
- Benchmark Avg 14.30%, High 25.99%, Low 5.05%

PV 5Y:
- Provided Avg 17.07%, High 23.40%, Low 10.19%
- Optimized Avg 16.17%, High 21.55%, Low 10.16%
- Benchmark Avg 14.09%, High 18.81%, Low 9.16%

PV 1Y/7Y도 golden에서 parsing해 비교한다. 작은 delta는 FDR/optimized-weight 차이로 설명 가능하므로 exact tolerance pass/fail은 아직 만들지 않는다.

### 7. Run README.md를 생성한다

`runs/<run_id>/README.md`는 해당 run의 사람이 읽는 index 역할을 한다.

최소 포함:

- run_id / objective / analysis period / benchmark / RF convention
- `result.json`과 `parity.json` 역할
- `review/`와 `raw/` 차이
- 각 review CSV의 한 줄 설명과 단위 convention
- percentage-point review vs decimal raw convention
- PV parity diagnostic 파일 설명
- code revision / output revision

다른 LLM이나 사용자가 이 README와 review 폴더만 보고 결과 구조를 이해할 수 있어야 한다.

### 8. Review/Raw 무손실 invariant

표현 개선 때문에 데이터가 손실되지 않았음을 검증한다.

예:

```text
raw CAGR = 0.17645725759759445
review CAGR = 17.6457 pct
```

처럼 review rounding 전 값이 raw/result.json에서 항상 복원 가능해야 한다.

- review table 생성은 canonical/raw 데이터의 projection/formatting이어야 한다.
- review table에서 제거한 detail은 반드시 raw/result.json에 남아 있어야 한다.
- raw CSV에는 display rounding을 하지 않는다.
- JSON과 raw CSV 사이 핵심 계산값 consistency를 테스트한다.

### Verification / outputs

변경 후 전체 offline suite를 다시 실행한다.

Live FDR run도 다시 실행해서 `runs/20260828-pv-maxsharpe/`를 최신 code revision 기준으로 갱신한다.

`agent-to-llm.md`에는 다음을 요약한다.

- total offline test count/result
- solver-only parity 주요 weight delta
- moment parity 최대 ER/vol/correlation delta
- Sortino convention 변경 여부
- 전체 CSV review/raw 분리 완료 여부
- review CSV 파일 목록
- raw CSV 파일 목록
- rolling summary 1Y/3Y/5Y/7Y PV 대비 주요 delta
- README 생성 여부
- code commit SHA와 output commit SHA
- 남은 blocker
