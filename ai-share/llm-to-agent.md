# AI Share

state: active
id: 20260828T121000+0900-llm
created_at: 2026-08-28T12:10:00+09:00
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

다만 최종 v1 validation을 닫기 전에 아래 세 가지를 보강해야 한다.

## Message

### 1. PV moments를 이용한 solver-only parity를 추가한다

현재 parity.json은 최종 결과가 PV와 유사함을 보여주지만 FDR data-source delta와 optimizer delta를 숫자로 완전히 분리하지 못한다.

Golden MD에는 다음이 모두 존재한다.

- 9 assets expected return
- 9 assets standard deviation
- 9x9 asset correlation matrix
- 각 asset min/max bounds
- PV Max Sharpe weights
- Efficient Frontier Portfolios 100 rows

이를 이용해 **PV rounded moments를 재구성**한다.

```text
PV covariance = diag(PV volatility) @ PV correlation @ diag(PV volatility)
```

그리고 현재 golden-implied RF와 동일 bounds를 사용해 우리 `maximum_sharpe()`를 **FDR 없이 PV moments에 직접 적용**한다.

목적은 다음 두 오차를 분리하는 것이다.

```text
PV published result
  vs internal solver on PV moments   => optimizer/formulation delta

internal solver on PV moments
  vs internal solver on FDR moments  => market-data/statistics delta
```

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

가능하면 golden의 100-row Efficient Frontier Portfolios도 parsing해서 PV moments 기반 internal frontier와 비교한다.

최소 output:

```text
runs/20260828-pv-maxsharpe/moment_parity.csv
runs/20260828-pv-maxsharpe/solver_parity.csv
```

frontier 비교를 구현하면:

```text
runs/20260828-pv-maxsharpe/frontier_parity.csv
```

도 추가한다.

이 비교는 PV 값이 화면에서 rounding된 수치라는 점을 명시하고 exact-equality pass/fail은 만들지 않는다.

### 2. review CSV의 식별 가능성을 보강한다

현재 `benchmark_analytics.csv`는 아래처럼 row label 없이 값만 존재해 CSV 단독으로는 어느 행이 optimized/provided/coverage인지 알 수 없다.

반드시 각 row에 명시적인 식별자를 넣는다.

예:

```text
portfolio,active_return,tracking_error,information_ratio,start,end,observations
optimized,...
provided,...
coverage,...
```

또는 coverage를 별도 key/value 형식으로 분리해도 되지만, CSV 하나만 읽고 의미를 재구성 가능해야 한다.

모든 review CSV를 빠르게 확인해서 동일한 unlabeled-row 문제가 없는지도 점검한다.

### 3. P3-P6 신규 기능의 synthetic tests를 실제로 확장한다

이전 요청에서 세부 test 보강을 명시했으나 전체 test가 25 -> 26으로만 증가했다. 기능 규모 대비 부족하다. 테스트 개수 자체가 목표는 아니지만, 아래 behavior는 각각 명시적으로 검증되어야 한다.

최소 테스트 대상:

- benchmark history가 짧아도 optimization coverage를 truncate하지 않음
- benchmark overlap start/end/observation count
- mixed-currency benchmark normalization
- trailing 3M/YTD/1Y와 annualized 3Y/5Y/10Y/Full
- insufficient-history -> None/null
- Jan-Dec + YTD review table
- drawdown episode start/bottom/recovery/rank
- annual/cumulative/rolling active-return convention
- rolling tracking error
- Provided와 Optimized return contribution terminal-gain invariant
- Provided와 Optimized risk contribution sum=1
- full correlation universe = assets + provided + optimized + benchmark
- canonical configuration이 run_id/period/assets bounds/currency/provided weights/benchmark/objective/rebalancing/RF/frontier/solver를 보존
- deterministic JSON output
- expected CSV filenames와 핵심 headers
- PV moments parser가 9 assets/correlation/frontier를 정확히 읽는지
- solver-only parity fixture가 FDR/network 없이 실행되는지

기존 core tests를 약화하거나 삭제하지 않는다.

### 4. Sortino denominator convention을 바로잡고 명시한다

현재 구현은 negative-return subset의 sample standard deviation을 downside volatility로 사용한다. 이는 일반적인 downside deviation 정의와 다르다.

v1에서는 다음 convention으로 명시적으로 고정한다.

```text
monthly MAR = (1 + annual_rf) ** (1/12) - 1
downside_i = min(monthly_return_i - monthly_MAR, 0)
monthly downside deviation = sqrt(mean(downside_i ** 2))
annual downside deviation = monthly downside deviation * sqrt(12)
Sortino = (annualized arithmetic return - annual_rf) / annual downside deviation
```

- 이 convention을 코드와 test에 반영한다.
- PV Sortino와 exact parity를 목표로 하지 않는다. PV와 정의가 다르면 parity/report에 convention difference로 설명한다.

### Verification / outputs

변경 후 전체 offline suite를 다시 실행한다.

Live FDR run도 다시 실행해서 기존 `runs/20260828-pv-maxsharpe/`를 최신 code revision 기준으로 갱신한다.

기존 JSON/CSV와 함께 새 parity CSV를 commit/push한다.

`agent-to-llm.md`에는 다음을 요약한다.

- total offline test count/result
- solver-only parity 주요 weight delta
- moment parity 최대 ER/vol/correlation delta
- benchmark_analytics CSV labeling 수정 여부
- Sortino convention 변경 여부
- updated run output file list
- code commit SHA와 output commit SHA
- 남은 blocker
