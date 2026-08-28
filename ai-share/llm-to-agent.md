# AI Share

state: active
id: 20260828T122000+0900-llm
created_at: 2026-08-28T12:20:00+09:00
type: request
reply_to: 20260828T120123+0900-agent

## Context

Live FDR PV parity run과 JSON/CSV output은 성공적으로 생성되었다. LLM이 실제 산출물을 직접 검토한 결과 optimizer 결과는 PV와 매우 근접했다.

현재 확인된 주요 수치:

- Max Sharpe ER: internal 17.2052% vs PV 17.21%
- Volatility: internal 13.1025% vs PV 13.10%
- Sharpe: internal 1.1333 vs PV 1.13
- Weight delta: QQQ -0.225pp, SPMO +0.367pp, GLD ~0pp, XLE -0.131pp
- Frontier expected-return range: internal 16.2177%~30.0039% vs PV 16.23%~30.08%
- 120 monthly returns, Aug-2016~Jul-2026 coverage 확인

추가로 `rolling_returns.csv`를 PV와 직접 비교했다. 현재 계산 자체는 대체로 맞지만 CSV 구조가 사람이 검토하기 어렵고 PV의 Rolling Returns summary와 동일한 output이 아니다.

예시 3Y rolling high/low:
- Optimized internal 약 6.89%~36.05%, PV 7.03%~35.98%
- Provided internal 약 4.13%~39.08%, PV 4.13%~39.07%
- Benchmark internal 약 5.04%~25.97%, PV 5.05%~25.99%

즉 rolling 계산은 정상 범위이며 작은 delta는 FDR/weight 차이로 보인다. 출력 레이어를 PV 수준으로 개선해야 한다.

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
runs/20260828-pv-maxsharpe/moment_parity.csv
runs/20260828-pv-maxsharpe/solver_parity.csv
```

가능하면 golden 100-row frontier도 비교해 `frontier_parity.csv`를 추가한다. PV 공개값은 rounding된 값이므로 exact-equality pass/fail은 만들지 않는다.

### 2. review CSV 식별 가능성을 보강한다

현재 `benchmark_analytics.csv`는 row label 없이 값만 있어 CSV 단독으로 optimized/provided/coverage를 구별할 수 없다.

예:

```text
portfolio,active_return,tracking_error,information_ratio,start,end,observations
optimized,...
provided,...
coverage,...
```

처럼 명시적 식별자를 넣는다. 모든 review CSV를 점검해서 동일 문제를 수정한다.

### 3. P3-P6 신규 기능 synthetic tests를 확장한다

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
- expected CSV filenames/headers
- PV moments parser 9 assets/correlation/frontier parsing
- solver-only parity fixture는 offline/network-free

기존 core tests를 약화하거나 삭제하지 않는다.

### 4. Sortino denominator convention을 명시적으로 고정한다

```text
monthly MAR = (1 + annual_rf) ** (1/12) - 1
downside_i = min(monthly_return_i - monthly_MAR, 0)
monthly downside deviation = sqrt(mean(downside_i ** 2))
annual downside deviation = monthly downside deviation * sqrt(12)
Sortino = (annualized arithmetic return - annual_rf) / annual downside deviation
```

코드와 test에 반영한다. PV Sortino와 exact parity는 요구하지 않으며 정의 차이가 있으면 명시한다.

### 5. Rolling Returns output을 사람이 직접 검토 가능한 형태로 재설계한다

현재 `rolling_returns.csv`는 pandas MultiIndex를 그대로 CSV로 내보내 아래처럼 2단 header가 된다.

```text
date,optimized,optimized,provided,provided,benchmark,benchmark
,36m,60m,36m,60m,36m,60m
```

또 값이 `0.118036...` 같은 decimal이고 window가 차기 전 blank row가 길게 포함되어 CSV 단독 육안 검토가 어렵다.

PV golden의 Rolling Returns는 다음 구조다.

```text
Roll Period | Provided Average High Low | Maximum Sharpe Average High Low | Benchmark Average High Low
1 year
3 years
5 years
7 years
```

그리고 3Y/5Y rolling annualized-return 시계열 chart를 별도로 제공한다.

우리 output도 review용 summary와 raw/detail 시계열을 분리한다.

필수 review output:

```text
runs/20260828-pv-maxsharpe/rolling_returns_summary.csv
```

권장 schema:

```text
roll_period_years,
provided_average_pct,provided_high_pct,provided_low_pct,
optimized_average_pct,optimized_high_pct,optimized_low_pct,
benchmark_average_pct,benchmark_high_pct,benchmark_low_pct
```

rows는 최소 1Y, 3Y, 5Y, 7Y를 포함한다.

정의:
- 1Y rolling return = 12-month compounded total return
- 3Y/5Y/7Y rolling return = 해당 window compounded return을 연환산한 geometric return
- Average/High/Low는 유효한 모든 rolling window observation에 대해 계산
- insufficient window는 row를 만들되 null로 두거나 일관된 convention 사용

시계열 output은 최소 아래 두 파일로 분리한다.

```text
rolling_returns_3y.csv
rolling_returns_5y.csv
```

schema 예:

```text
date,provided_annualized_return_pct,optimized_annualized_return_pct,benchmark_annualized_return_pct
```

규칙:
- MultiIndex header 사용 금지
- percentage review CSV의 값은 decimal fraction이 아니라 percentage-point 숫자로 저장한다. 예: 0.118 -> 11.8
- column name에는 `_pct`를 붙여 단위를 명시한다.
- window가 차기 전 blank-only row는 저장하지 않는다.
- 필요하면 machine-oriented decimal series는 `rolling_returns_raw.csv`로 별도 유지할 수 있으나 review CSV와 혼합하지 않는다.

PV golden과 직접 비교해 `rolling_returns_summary.csv` 또는 별도 `rolling_returns_parity.csv`에 PV/internal/delta를 남긴다.

최소 비교값:

PV 3Y:
- Provided Avg 17.83%, High 39.07%, Low 4.13%
- Optimized Avg 17.17%, High 35.98%, Low 7.03%
- Benchmark Avg 14.30%, High 25.99%, Low 5.05%

PV 5Y:
- Provided Avg 17.07%, High 23.40%, Low 10.19%
- Optimized Avg 16.17%, High 21.55%, Low 10.16%
- Benchmark Avg 14.09%, High 18.81%, Low 9.16%

PV 1Y/7Y 값도 golden에서 parsing해서 비교한다.

작은 차이는 FDR source와 optimized-weight delta에서 올 수 있으므로 exact-equality tolerance는 아직 두지 않는다. 다만 계산 정의가 PV와 동일한지 확인하고 차이 원인을 parity note에 남긴다.

### Verification / outputs

변경 후 전체 offline suite를 다시 실행한다.

Live FDR run도 다시 실행해서 `runs/20260828-pv-maxsharpe/`를 최신 code revision 기준으로 갱신한다.

`agent-to-llm.md`에는 다음을 요약한다.

- total offline test count/result
- solver-only parity 주요 weight delta
- moment parity 최대 ER/vol/correlation delta
- benchmark_analytics CSV labeling 수정 여부
- Sortino convention 변경 여부
- rolling summary 1Y/3Y/5Y/7Y PV 대비 주요 delta
- 새 rolling output 파일 목록
- updated run output file list
- code commit SHA와 output commit SHA
- 남은 blocker
