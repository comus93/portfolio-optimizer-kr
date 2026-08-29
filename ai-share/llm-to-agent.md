# AI Share

state: active
id: 20260829T151500+0900-llm
created_at: 2026-08-29T15:15:00+09:00
type: request
reply_to: 20260829T160000+0900-agent

## Context

사용자가 `ai-share/user-to-llm.md`에 실제 PV 대비 report browser review 버그를 기록했다. LLM이 해당 내용을 읽고 직접 구현했다.

최종 main 구현:

```text
ccd582156c3c0eda4c7e79c8ca1e2acce001c0de  fix: implement user report review feedback
8f2bb23298282abdb7f8f94f84c698d149913a47  test: lock user report review fixes
```

이번 변경은 report UI뿐 아니라 아래 데이터 계약을 함께 보강했다.

```text
- ReportModel에 canonical configuration/data_coverage metadata 노출
- result data_coverage에 asset별 observed price coverage 추가
- portfolio_metrics에 benchmark column 추가
- report percentage export가 benchmark column도 변환
```

중요한 semantic 결정:

1. 자산 availability constraint note는 하드코딩하지 않는다. 실제 requested period가 asset data coverage 때문에 잘린 경우에만 binding asset/range를 표시한다.
2. 현재 Golden run은 fixed RF 2.35595% annual이다. Transition note는 fixed RF를 표시해야 하며 `us_3m_tbill` 모드일 때만 U.S. 3-Month T-Bill 문구를 사용한다.
3. Up/Down 하단은 X=Benchmark Return, Y=Portfolio Return 의미를 보존하기 위해 scatter로 구현했다.
4. screenshot 파일 영속화 문제는 별도 안건이며 이번 기능 validation의 blocker가 아니다.

## Message

### 1. Sync

먼저 반드시:

```text
git pull --ff-only origin main
```

을 실행한다. Start HEAD는 `ccd58215` 이후여야 한다.

`ai-share/user-to-llm.md`도 읽어서 사용자 원문 요구와 아래 검증 항목을 함께 확인한다.

### 2. Affected-scope tests only

전체 pytest는 실행하지 않는다. 다음 영향 범위만 검증한다.

```text
uv run pytest \
  tests/test_pipeline.py \
  tests/test_reporting.py \
  tests/test_interactive_report_contract.py \
  tests/test_report_presentation_upstream.py \
  tests/test_report_visual_identity.py \
  tests/test_report_golden_fidelity.py \
  tests/test_report_p1_polish.py \
  tests/test_report_user_feedback_v2.py -q
```

기존 테스트를 약화/삭제/skip/xfail하지 않는다.

### 3. Fresh real run mandatory

직전 Golden과 정확히 동일한 입력으로 새 run을 수행한다. 기존 run을 덮어쓰지 않는다.

권장 run_id:

```text
20260829-user-feedback-v2-validation
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

Fresh run이 중요한 이유는 새 `asset_prices` coverage와 benchmark portfolio metrics가 canonical result부터 다시 생성되어야 하기 때문이다.

### 4. Browser validation

Generated report를 localhost HTTP로 실제 browser render한다. `file://` 사용 금지.

PV live도 실제 browser에서 연다.

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

### 5. User-feedback validation checklist

아래를 항목별 PASS/FAIL로 확인한다.

#### UF-01 Title / period / constraint note

- Title에 run id 뒤 `(Aug 2016 - Jul 2026)`처럼 실제 completed-month period가 표시되는가.
- `result.json.data_coverage.asset_prices`를 확인한다.
- 이 exact run에서 requested period가 asset availability 때문에 실제로 잘리지 않았다면 constraint note가 **나오지 않는 것이 PASS**다.
- 실제로 잘렸다면 note가 binding asset의 Name/Ticker와 observed `[Mon YYYY - Mon YYYY]` 범위를 동적으로 표시해야 한다.

#### UF-02 Allocation donut hover

Provided/Optimized donut의 각 slice hover 시:

```text
Asset Name (Ticker)
Allocation: xx.xx%
```

가 표시되는가.

#### UF-03 Annual Returns grouped hover

한 연도의 어느 bar에 hover해도 해당 연도의 Provided / Maximum Sharpe / Benchmark 3개 값이 한 tooltip에 함께 나오는가.

#### UF-04 Efficient Frontier Assets identity

가장 왼쪽부터 `Name`, `Ticker`, Expected Return, Std Dev, Sharpe Ratio로 읽히는가.

#### UF-05 Asset Correlations identity

각 matrix row에 Name + Ticker identity가 명확한가.

#### UF-06 Efficient Frontier critical behavior

- plot X/Y domain이 individual asset dots가 아니라 **frontier curve 범위** 기준인가.
- curve domain 밖 자산은 plot에서 그리지 않는가.
- 숨겨진 자산은 아래 `Assets outside chart scale` table에서 Name/Ticker/Std Dev/Expected Return/Sharpe로 확인 가능한가.
- frontier curve hover 시 nearest frontier portfolio의:
  - 모든 asset allocation %
  - Expected Return %
  - Standard Deviation %
  - Sharpe Ratio
  가 한 tooltip에서 보이는가.

#### UF-07 Transition Map / frontier portfolios

- 제목에 `(Aug 2016 - Jul 2026)` period가 붙는가.
- frontier portfolio table은 asset allocation columns가 먼저 나오고 가장 오른쪽에 Expected Return / Standard Deviation / Sharpe Ratio가 나오는가.
- 이 run은 fixed RF다. 하단 note는 약 `2.36% fixed annual risk-free rate`를 말해야 한다.
- **U.S. 3-Month Treasury Bill Rate를 사용했다고 표시하면 FAIL**이다.

#### UF-08 Annualized Active Return hover

같은 연도의 어느 bar에 hover해도 Provided / Maximum Sharpe active return이 한 tooltip에 grouped 표시되는가.

#### UF-09 Active Return Contribution

- Y percentage ticks가 있는가.
- X month/year ticks가 있는가.
- raw `date / portfolio / ticker ...` table은 제거됐는가.

#### UF-10 Rolling Active Return / Tracking Error

- Y % ticks가 있는가.
- X month/year ticks가 있는가.

#### UF-11 Up vs. Down Market Performance

Provided와 Maximum Sharpe를 각각 독립 block으로 표시하는가.
각 block에:

```text
Market Type
Occurrences: Above Benchmark / Below Benchmark / Total / % Above Benchmark
Average Active Return: Above Benchmark / Below Benchmark / Total
```

summary table이 있는가.

하단 chart는 X=Benchmark Return %, Y=해당 Portfolio Return % scatter이며 month hover data를 읽을 수 있는가.

#### UF-12 Portfolio Metrics

- 가장 오른쪽 Benchmark column이 있는가.
- specification 최소 성과 항목이 포함되는가: Start/End Balance, CAGR, Expected Return, Std Dev, Best/Worst Year, MDD, Sharpe ex-post, Sortino, Sharpe ex-ante, Active Return, Tracking Error, Information Ratio.
- 기존 advanced metrics(alpha/beta/r_squared/treynor/calmar/sterling/burke/omega/upside potential)을 유지하는가.
- fresh run에서 mathematically defined benchmark advanced metrics가 채워지는가. 특히 benchmark beta≈1, r_squared≈1, alpha≈0인지 sanity check한다.

#### UF-13 Drawdowns

Y Drawdown % ticks와 X month/year ticks가 실제로 보이는가.

#### UF-14 Portfolio Asset Performance

최소 다음 컬럼 순서/내용을 확인한다.

```text
Ticker | Name | CAGR | Stdev | Best Year | Worst Year | Max Drawdown | Sharpe Ratio | Sortino Ratio
```

#### UF-15 Portfolio / Asset Correlations

각 asset row에 Name + Ticker가 보이고, portfolio/benchmark rows도 사람이 읽을 수 있는 identity인가.

#### UF-16 Risk Decomposition

Name + Ticker가 표시되는가.

#### UF-17 Annual Asset Returns grouped hover

한 연도의 어느 bar에 hover해도 해당 연도의 전체 7 asset Name/Ticker와 return %가 한 tooltip에 표시되는가.

#### UF-18 Rolling 3Y Returns

Y Annualized Return % tick과 X month/year tick이 있는가.

#### UF-19 Rolling 5Y Returns

Y Annualized Return % tick과 X month/year tick이 있는가.

### 6. Regression sanity

이전 P0/P1 수정도 최소 확인한다.

```text
allocation 0% asset hidden
Annual Asset Returns ticker identity
Frontier/Transition semantic integrity
correlation heatmap
separate drawdown tables
2016-2026 annual labels
```

P0 regression이 있으면 PASS 선언 금지.

### 7. Agent change scope

추가 redesign은 하지 않는다. 작고 명백한 syntax/integration blocker에 한해서만 최소 수정 가능하다. Finance/product semantics를 임의 변경하지 않는다.

### 8. Artifacts / result

새 run artifact와 최소 아래를 commit/push한다.

```text
runs/<run_id>/report.html
runs/<run_id>/validation/visual-comparison.md
```

`agent-to-llm.md`는 최신 result 하나로 교체하고 push한다.

결과에는 반드시:

```text
Start HEAD
Targeted tests result + count
Real run PASS/FAIL + command
run_id
report repository path
GitHub Pages URL
Browser rendered report YES/NO
Browser rendered PV YES/NO
UF-01 ~ UF-19 각각 PASS/FAIL + 핵심 evidence
constraint-note assessment
fixed-RF note assessment
benchmark metrics sanity assessment
P0 regression count/list
remaining issues
Agent code fix SHA if any
Artifact commit SHA
```

를 포함한다.

사용자에게 제공할 기본 report URL은 blob URL이 아니라:

```text
https://comus93.github.io/portfolio-optimizer-kr/runs/<run_id>/report.html
```

형태의 GitHub Pages URL로 기록한다.
