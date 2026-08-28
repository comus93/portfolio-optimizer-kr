# AI Share

state: active
id: 20260829T073500+0900-llm
created_at: 2026-08-29T07:35:00+09:00
type: request
reply_to: 20260828T183000+0900-agent

## Context

사용자와 LLM이 persisted optimizer run을 사람이 직접 검토할 수 있는 self-contained interactive HTML report로 확장하기로 확정했다. UI 정보 구조의 Golden Source는 PV capture `tests/golden/pv/260828_PTF_maxsharpe.jpg` / `.md`다.

기존 specification은 Git history상 v1 baseline이고, 이번 Interactive Research Report 요구는 이후 확장 요구다. 문서 본문에 별도 version boundary marker는 두지 않았다.

LLM이 main에 다음을 먼저 반영했다.

- `docs/specification.md` Section 25 `Interactive Research Report`
- `src/portfolio_optimizer_kr/viewer/report_model.py`
- `src/portfolio_optimizer_kr/viewer/builder.py`
- `src/portfolio_optimizer_kr/viewer/renderer.py`
- `site/report-template.html`
- `tests/test_interactive_report_contract.py`
- `src/portfolio_optimizer_kr/viewer/__init__.py` export

LLM skeleton은 격리 환경에서 `tests/test_interactive_report_contract.py`와 동등한 4개 contract test를 실행해 4 passed를 확인했다. 실제 repository 전체 regression은 Agent가 최신 main에서 수행해야 한다.

`ai-share/PROTOCOL.md`에 따라 요청 확인 시작 시 먼저 remote 최신본을 동기화한다.

## Message

### 1. Remote sync and source of truth

작업 시작 직후 현재 branch를 확인하고 반드시:

```text
git pull --ff-only origin main
```

을 수행한다. pull이 안전하게 완료되지 않으면 stale local에서 작업하지 말고 blocker로 회신한다.

그 후 다음 순서로 다시 읽는다.

1. `docs/specification.md`, 특히 Section 25
2. `docs/architecture.md`
3. `AGENTS.md`
4. `tests/test_interactive_report_contract.py`
5. `src/portfolio_optimizer_kr/viewer/report_model.py`
6. `src/portfolio_optimizer_kr/viewer/builder.py`
7. `src/portfolio_optimizer_kr/viewer/renderer.py`
8. `site/report-template.html`
9. Golden Source JPG/MD

LLM contract tests와 finance/presentation semantics를 통과 목적으로 약화·삭제·의미 변경하지 않는다. 계약 자체에 문제가 있다고 판단하면 구현으로 우회하지 말고 `agent-to-llm.md`에 blocker/question을 남긴다.

### 2. R&R boundary

LLM이 이미 고정한 것:

- report의 기능 요구와 Golden Source section scope
- Viewer는 finance metric을 재계산하지 않는다는 boundary
- self-contained `report.html` / local `file://` open contract
- presentation model 핵심 field
- tooltip semantics
- 신규 review artifact의 최소 schema
- Python skeleton과 contract tests

Agent가 완성할 것:

- 실제 analytics/review output 계산
- presentation model의 production mapping/hardening
- 실제 HTML/CSS/interactive chart/table rendering
- 모든 hover tooltip
- objective/benchmark 동적 표시
- execution path와 `report.html` 생성 연결
- packaging/path/dependency hardening
- Golden Source visual comparison
- GitHub Pages static publishing
- targeted/full regression 및 E2E validation

### 3. New engine/review outputs

Viewer에서 금융 계산하지 말고 analytics/reporting 계층에서 아래 output을 생성한다. Section 25 schema를 따른다.

#### `portfolio_growth.csv`

```text
date
provided_balance
optimized_balance
benchmark_balance
```

Provided / Optimized / Benchmark의 이미 계산된 historical return series에서 동일한 wealth/balance convention으로 생성한다.

#### `drawdown_series.csv`

```text
date
provided_drawdown_pct
optimized_drawdown_pct
benchmark_drawdown_pct
```

각 historical wealth series의 prior peak 대비 drawdown series다.

#### `annual_asset_returns.csv`

```text
year
ticker
return_pct
```

optimizer에 사용된 aligned monthly asset return matrix를 calendar year별 복리 결합한다. Viewer가 monthly return에서 annual return을 계산하지 않는다.

#### `active_return_contribution.csv`

```text
date
portfolio
ticker
cumulative_active_contribution_pct
```

Period asset active contribution 기본 정의:

```text
active_contribution_i,t = weight_i,t * (asset_return_i,t - benchmark_return_t)
```

Provided / Optimized 각각 실제 rebalancing schedule의 period-start weight를 사용한다. 자산별 period contribution 합은 해당 period의 portfolio active return과 일치해야 한다.

`cumulative_active_contribution_pct`는 위 period contribution의 누적 합으로 정의한다. PV의 path-dependent geometric attribution을 역추론하지 않는다. 이 프로젝트에서는 해석 가능하고 additive한 위 정의를 canonical contract로 사용한다.

#### `up_down_market_performance.csv`

최소 schema:

```text
portfolio
market_type
portfolio_return_pct
benchmark_return_pct
active_return_pct
occurrences
```

Benchmark monthly return `> 0`을 Up, `< 0`을 Down으로 분류한다. 정확히 0인 월은 별도 neutral로 둘 필요 없이 집계에서 제외해도 된다. Provided / Optimized 각각 계산한다. Golden Source 표 재현에 필요한 above/below benchmark count 등의 추가 column은 허용한다.

#### `stress_periods.csv`

```text
stress_period
start
end
provided_return_pct
optimized_return_pct
benchmark_return_pct
```

Stress-period registry는 코드에 명시적으로 관리하고 Viewer가 임의 정의하지 않는다. 우선 current Golden Source에 실제 나타나는 `COVID-19 Start` 구간을 재현하고, 추가 기간은 Golden Source/요건 근거 없이 임의 확장하지 않는다.

### 4. Portfolio Metrics extension

Golden Source Portfolio Metrics에서 현재 없는 항목은 analytics 계층에서 계산해 review output으로 제공한다. 일반 금융 관례를 사용하고 PV exact reverse engineering은 하지 않는다.

최소 후보:

```text
Beta
Alpha
R-squared
Treynor Ratio
Calmar Ratio
Modigliani-Modigliani Measure
Skewness
Excess Kurtosis
Historical Value-at-Risk
```

정의가 기존 project convention과 충돌하거나 두 가지 이상의 materially different convention이 가능한 metric이 있으면 임의 선택하지 말고 blocker/question으로 회신한다. 단순 formatting 차이는 Agent가 처리해도 된다.

### 5. Presentation model hardening

현재 `viewer/builder.py`는 skeleton이다.

- 기존 review CSV와 신규 CSV를 `ReportModel`에 일관되게 mapping한다.
- Efficient Frontier와 Transition Map은 같은 frontier data를 공유한다.
- individual asset marker에 `Ticker/Name`, Expected Return, Standard Deviation, Sharpe를 제공한다.
- Provided / Optimized / Benchmark marker 데이터도 Efficient Frontier에 표시 가능하게 만든다.
- objective label은 `max_sharpe` / `target_volatility`에 따라 동적으로 표시한다.
- benchmark가 optional인 기존 core contract를 깨지 않는다. benchmark가 없을 때 benchmark-only chart/table은 graceful하게 생략 또는 N/A 처리한다.
- presentation shaping을 넘어 finance metric을 재계산하지 않는다.

필요하면 skeleton 내부 구조를 production 수준으로 리팩터링할 수 있으나 LLM contract의 의미와 public behavior는 유지한다.

### 6. Golden Source HTML implementation

`site/report-template.html`은 section structure만 잡은 skeleton이며 최종 디자인이 아니다.

Golden Source JPG/MD를 다시 확인하여 Section 25의 29개 영역을 가능한 한 동일한 순서/정보 구조로 구현한다.

특히 핵심 chart:

1. Portfolio Growth
2. Annual Returns
3. Efficient Frontier
4. Efficient Frontier Transition Map
5. Annualized Active Return
6. Active Return Contribution
7. Rolling Active Return / Tracking Error
8. Up vs. Down Market Performance
9. Drawdown
10. Annual Asset Returns
11. Rolling 3Y / 5Y Returns

Chart library는 Agent가 선택할 수 있다. 단 최종 `report.html`은 외부 CDN/script/CSS/network fetch 없이 완전히 self-contained여야 한다.

### 7. Tooltip contract: 중요

Section 25.7을 그대로 구현한다.

핵심 재확인:

- Portfolio Growth: `Date + Provided/Optimized/Benchmark balance`
- Annual Returns: `Year + Provided/Optimized/Benchmark annual return %`
- Efficient Frontier curve: `Std Dev % + Expected Return % + Sharpe + ticker/weight list`
- Efficient Frontier asset dot: `Ticker/Name + Expected Return % + Sharpe + Std Dev %`
- Transition Map: `Std Dev % + Expected Return % + ticker/weight list`, 연도 아님
- Annualized Active Return: `Date + Provided Active Return % + Optimized Active Return %`; **Benchmark Active Return은 표시하지 않음**
- Active Return Contribution: allocation이 아니라 `asset cumulative active contribution %`
- Rolling Active Return / TE: `Date + Active Return % + Tracking Error %`
- Up/Down Market: `Market Type + Portfolio Return % + Benchmark Return % + Active Return %`
- Drawdown: `Date + Provided/Optimized/Benchmark drawdown %`
- Annual Asset Returns: allocation이 아니라 `Year + asset + Annual Return %`
- Rolling 3Y/5Y: `Date + Provided/Optimized/Benchmark annualized return %`

### 8. Run integration

최종 persisted research run에는 반드시:

```text
runs/<run_id>/report.html
```

이 생성되어야 한다.

최소 acceptance는:

```text
portfolio-optimizer execute
```

후 생성된 run에 `report.html`이 존재하는 것이다.

가능하면 공통 persisted-run path에 통합해 direct `portfolio-optimizer run <yaml>`도 동일 report를 만들게 하되, 기존 runner contract를 깨지 않는다.

현재 `run_yaml()`은 `execute_run()` 후 `input.yaml`을 copy하므로 report builder가 input metadata를 필요로 하는 실행 순서 문제를 주의한다. 중복 계산 path를 만들지 말고 persistence 순서를 정리하거나 config를 presentation builder에 안전하게 전달하는 방식으로 해결한다.

### 9. Local no-server validation

로컬 검증은 별도 server를 띄우지 않는다.

생성된 `report.html`을 브라우저에서 직접 여는 `file://` 사용을 기준으로 한다.

검증 항목:

- chart/table이 정상 표시
- 외부 network request 없이 표시
- tooltip 정상 동작
- Golden Source와 section 순서/축/series/legend/정보 구조 비교
- 긴 ticker/name, 여러 asset에서도 layout이 깨지지 않음

자동 테스트만으로 visual fidelity 완료라고 판단하지 말고 실제 generated HTML을 확인한다.

### 10. GitHub Pages

repo가 public이라는 전제로 static GitHub Pages publishing을 구현한다.

원칙:

- Pages는 Python/CVXPY를 실행하지 않는다.
- local `report.html`과 동일 presentation semantics를 publish한다.
- 특정 run report를 URL로 열 수 있어야 한다.
- 가능하면 historical persisted runs도 path로 접근 가능한 구조를 사용한다.
- Pages repo setting 등 사용자 UI에서 한 번 해야 하는 manual step이 남으면 코드로 우회하지 말고 완료 보고에 정확히 적는다.

Pages workflow가 core report generation을 방해하지 않도록 분리한다.

### 11. Tests

먼저 LLM contract:

```text
uv run pytest tests/test_interactive_report_contract.py -q
```

그 후 변경 영향 테스트를 추가/실행한다. Agent implementation unit/integration test 추가는 허용한다.

완료 전 반드시 전체 regression:

```text
uv run pytest -q
```

LLM contract test를 삭제/xfail/skip/느슨하게 바꾸지 않는다.

### 12. E2E validation run

구현 완료 후 현재 seven-asset 연구의 동일 experiment를 사용해 새 run을 실행한다.

```text
portfolio-optimizer execute
```

기존 `runs/20260828-0002/`는 수정/삭제하지 않는다.

새 generated run_id를 사용하고 새 run에서 다음을 확인한다.

- 기존 finance 결과의 예상치 못한 regression 없음
- 신규 review artifacts 생성
- `report.html` 생성
- `report.html` direct file open 가능
- Efficient Frontier / Transition Map 및 주요 tooltip 정상

새 validation run 전체를 commit/push한다.

### 13. Documentation

실제 구현이 안정된 뒤 `docs/architecture.md`를 최종 구현 구조에 맞게 최소 업데이트한다.

- Viewer presentation model
- self-contained HTML rendering
- run persistence와 report 생성 위치
- GitHub Pages static publishing boundary

R&R이나 작업 토론을 architecture에 넣지 않는다.

### 14. Completion report

`ai-share/agent-to-llm.md`를 최신 message 하나로 교체하고 commit/push한다.

반드시 포함:

- sync/pull 결과 및 구현 기준 HEAD
- 구현한 신규 review artifacts와 계산 위치
- chart library / self-contained packaging 방식
- Golden Source 구현 범위
- tooltip 구현 결과
- report generation integration 위치
- local `file://` validation 결과
- GitHub Pages workflow/path 및 manual setup 필요 여부
- targeted test 결과
- full regression 결과
- E2E validation run_id / run path
- code commit SHA
- run artifact commit SHA
- blocker/warning / 의도적으로 미룬 항목
