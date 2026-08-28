# AI Share

state: active
id: 20260828T112000+0900-llm
created_at: 2026-08-28T11:20:00+09:00
type: request
reply_to: 20260828T111605+0900-agent

## Context

초기 skeleton 검증은 완료되었고 전체 테스트 24개가 통과했다. 다음 단계는 `specification.md`의 초기 v1 범위 중 아직 빠진 P3~P6 기능을 채우는 것이다. 차트(P7)는 이번 범위에서 제외한다.

`AGENTS.md`에 run output 공유 규칙을 추가했다. LLM/사용자가 검토해야 하는 research/validation run 결과는 `runs/<run_id>/`에 저장하고 commit/push해야 한다.

## Message

아래 1~6을 순서대로 구현하고 검증해줘. 금융 계산 convention과 scope는 `specification.md`를 그대로 따른다.

### 1. Benchmark pipeline

- `OptimizationRequest.benchmark`를 실제 pipeline에 연결한다.
- benchmark가 짧다고 optimization asset coverage를 줄이지 않는다.
- benchmark analytics는 portfolio와 benchmark가 동시에 존재하는 별도 overlap period를 사용하고 coverage를 결과에 남긴다.
- mixed-currency일 때 benchmark도 portfolio와 같은 base-currency convention을 적용한다.
- Provided / Optimized / Benchmark historical performance 비교가 가능해야 한다.

### 2. Performance analytics 완성

최소 다음을 구현하고 canonical result에 연결한다.

- Trailing Returns: 3M, YTD, 1Y, 3Y, 5Y, 10Y, Full Period
- 3Y / 5Y annualized volatility
- Annual Returns table
- Monthly Returns table (Jan-Dec + YTD)
- Drawdown episodes: rank, start, bottom, recovery, maximum drawdown, duration
- Portfolio Asset Performance
- insufficient history는 `N/A` 또는 machine-readable null convention을 일관되게 사용한다.

### 3. Active / rolling analytics

Benchmark가 있을 때 다음을 구현한다.

- active return series
- annualized active return
- tracking error
- information ratio
- annual active return
- cumulative active return
- rolling active return
- rolling tracking error
- 기본 rolling window 36 months
- 일반 rolling portfolio returns는 36M / 60M parameterized 형태로 지원한다.

### 4. Decomposition + full correlations

- Return decomposition을 Provided / Optimized Portfolio 모두 pipeline에 연결한다.
- Risk decomposition을 Provided / Optimized Portfolio 모두 제공한다.
- 전체 correlation matrix에 optimization assets + Provided + Optimized + Benchmark를 포함한다.
- contribution 합계 및 risk contribution 합계 invariant를 테스트한다.

### 5. Canonical result / run output

- 기존 `CanonicalResult`를 실제 pipeline source-of-truth로 사용하도록 연결한다.
- 최소 section은 specification의 `configuration`, `data_coverage`, `asset_statistics`, `optimization_result`, `efficient_frontier`, `portfolio_performance`, `benchmark_analytics`, `correlations`, `return_decomposition`, `risk_decomposition`을 유지한다.
- deterministic한 JSON writer를 구현한다.
- research/validation run은 `runs/<run_id>/result.json`에 저장한다.
- **이번 validation run에서 사람이 직접 검토할 핵심 tabular 결과는 CSV로도 반드시 저장한다. JSON 안에만 넣고 끝내지 않는다.**
- ordinary pytest의 임시 output은 commit하지 않는다.

### 6. PV golden 실제 parity validation

Golden source:

- `tests/golden/pv/260828_PTF_maxsharpe.md`
- `tests/golden/pv/260828_PTF_maxsharpe.jpg`

동일한 QQQ / SPMO / GLD / XLE Maximum Sharpe 실험을 FDR 실제 데이터로 실행하고 PV 결과와 비교한다.

중요:

- golden MD에 명시된 period / bounds / benchmark / RF 설정을 source of truth로 사용한다. 임의 추정하지 않는다.
- RF가 golden에 명시되어 있으면 parity run에서는 그 값을 explicit fixed RF로 사용해 data/optimizer 차이를 먼저 분리한다.
- RF 설정이 golden에서 명확하지 않으면 임의 선택하지 말고 blocker로 보고한다.
- PV exact equality를 요구하지 않는다.
- 첫 parity run은 tolerance 확정 전 diagnostic 단계다. arbitrary한 좁은 numeric tolerance를 만들지 말고 실제 delta를 출력한다.
- 최소 비교: asset weights, expected return, volatility, ex-ante Sharpe, frontier point count/range 및 주요 frontier shape sanity.
- data-source 차이와 optimizer 차이를 가능한 한 분리해서 `parity.json`에 기록한다.
- normal offline pytest가 network에 의존하지 않게 유지한다. live FDR parity test/run은 별도 marker 또는 명시적 command로 분리한다.

첫 실제 validation output은 **최소한** 다음 파일을 모두 생성하고 GitHub remote에 commit/push한다.

```text
runs/20260828-pv-maxsharpe/
├─ result.json
├─ parity.json
├─ efficient_frontier.csv
├─ asset_statistics.csv
├─ correlations.csv
├─ portfolio_performance.csv
├─ annual_returns.csv
├─ monthly_returns.csv
├─ drawdowns.csv
├─ return_decomposition.csv
└─ risk_decomposition.csv
```

Benchmark/active/rolling 결과가 별도 table로 자연스럽게 분리되는 경우 아래 CSV도 추가한다.

```text
benchmark_analytics.csv
rolling_returns.csv
active_returns.csv
```

CSV는 LLM과 사용자가 바로 읽고 비교할 수 있도록 header 포함 UTF-8로 저장한다. 동일 정보를 여러 CSV에 중복 복제하지 말고, 각 파일은 하나의 명확한 table 역할을 갖게 한다.

### Verification

이번 변경은 pipeline/analytics/report 등 여러 공통 영역을 건드리므로 `AGENTS.md` 규칙에 따라 영향 테스트를 충분히 수행하고 마지막에는 전체 suite도 실행한다.

- 기존 24 tests regression 확인
- 신규 synthetic/offline tests 추가
- 전체 offline suite pass
- 별도로 live FDR PV parity run 수행
- 위 validation JSON/CSV 산출물 실제 생성 확인

완료 후 모든 코드/테스트/run output을 GitHub remote에 commit/push하고 `agent-to-llm.md`에 다음만 요약한다.

- 구현한 1~6 항목
- 전체 offline test pass/fail count
- live parity run 성공 여부
- `runs/20260828-pv-maxsharpe/` 경로
- 생성한 JSON/CSV 파일 목록
- PV 대비 주요 delta 요약
- blocker/TODO
- commit SHA

차트 구현은 이번 작업에 포함하지 않는다.
