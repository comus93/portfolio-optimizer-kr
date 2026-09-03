# Architecture

## 1. Purpose

`portfolio-optimizer-kr`는 재현 가능한 portfolio optimization / analytics runtime과 GitHub 기반 research interaction을 결합한 Python research system이다.

아키텍처는 세 책임을 분리한다.

```text
1. Analysis Runtime
   data -> shared statistics -> product-specific generation -> shared portfolio path -> shared analytics

2. Persistence / Presentation
   canonical result -> raw/review tables -> product composition + shared report components -> self-contained report.html

3. Research Interaction
   study / experiment / execution control / AI handoff
```

Research layer와 browser viewer는 금융 계산 의미론을 변경하지 않는다.

---

## 2. Technology Baseline

```text
Runtime           Python 3.11+
Data processing   pandas / NumPy
Market data       FinanceDataReader
Optimization      CVXPY
QP solver         OSQP
SOCP solver       CLARABEL
Configuration     YAML / PyYAML
CLI               argparse + project script
UI                Streamlit
Persistence       repository filesystem + GitHub
Viewer            self-contained HTML / SVG / JavaScript
Testing           pytest
Packaging         pyproject.toml / hatchling
```

GitHub는 optimizer runtime이 아니라 source/version/history와 LLM-Agent bridge다.

---

## 3. High-level Flow

제품별 request와 portfolio 생성 방식은 분리하지만, 생성된 target weights 이후의 simulation/evaluation/persistence와 동일 의미의 historical presentation은 공유한다.

```text
Optimization
User / GPT / Agent
        |
        v
YAML / Streamlit / control
        |
        v
Runner -> OptimizationRequest
        |
        v
market-data / shared statistics
        |
objective / constraints / solver / frontier
        |
optimized or provided target weights
        |
        +-----------------------------+
                                      v
Backtest                         shared portfolio-simulation
User / GPT / Agent                    |
        |                             v
        v                        shared portfolio-analytics
YAML / Streamlit / control             |
        |                             v
        v                        canonical result
Runner -> BacktestRequest              |
        |                       raw/review artifacts
        v                             |
market-data / shared statistics        v
        |                       product report composition
user-defined target weights            |
        +-----------------------------+
                                      v
                         shared historical report components
                                      |
                                      v
                               report.html
```

모든 실행 surface는 동일 runner/persistence 방향으로 수렴하되 product request는 억지로 하나의 schema에 합치지 않는다.

---

## 4. Runtime Modules

```text
src/portfolio_optimizer_kr/
├─ config/        YAML parsing / validation
├─ data/          FDR loading / FX / month-end normalization
├─ stats/         shared expected return / covariance / volatility / correlation
├─ optimize/      Optimization-only objective / CVXPY solver / frontier
├─ portfolio/     shared rebalancing / historical path simulation
├─ analytics/     shared performance / active / drawdown / decomposition
├─ report/        shared canonical JSON + raw/review persistence
├─ viewer/        product composition + shared historical presentation components
├─ models.py      product-specific canonical request/spec models
├─ pipeline.py    Optimization orchestration
├─ backtest.py    Backtest orchestration
├─ research.py    study/control/provenance orchestration
├─ runner.py      YAML-to-product-run orchestration
└─ cli.py         CLI entrypoint
```

의존 방향:

```text
CLI / UI / Research Control
          |
          v
        Runner
          |
          v
  Configuration / Models
          |
          v
 product orchestration
   |            |
   v            v
market-data   shared statistics
   |            |
   +------ product generation -------+
                                     |
                                     v
                          shared portfolio simulation
                                     |
                                     v
                          shared portfolio analytics
                                     |
                                     v
                             shared reporting
                                     |
                                     v
                      product composition / viewer
```

Core statistics/simulation/analytics는 Study, GitHub message, browser DOM을 알지 않는다.

### Shared capability principle

공통 backend capability와 product별 사용 policy를 구분한다.

- expected return/covariance/volatility/correlation 계산기는 shared statistics다.
- Optimization은 shared statistics를 ex-ante weight 탐색에 사용한다.
- Backtest가 현재 특정 shared statistic을 사용하지 않는 것은 허용되지만 별도 product-specific 계산기를 만들 이유가 되지 않는다.
- rebalancing engine과 portfolio path generation은 shared simulation capability다.
- Backtest의 run-level rebalancing은 UI/input policy이며 backend engine의 별도 구현을 의미하지 않는다.

---

## 5. Data Architecture

v1 market-data source는 FDR다.

```text
FDR asset / benchmark prices
        |
optional USD/KRW conversion
        |
common price alignment
        |
calendar month-end prices
        |
completed monthly simple returns
        |
requested analysis-period rows
```

첫 요청 월 return 생성을 위해 직전 month-end price는 warm-up으로 로드할 수 있다.

Pipeline 이후 계층에는 정규화된 return matrix와 effective RF가 전달된다.

Data coverage는 run artifact에 남긴다.

```text
data_coverage.optimization_monthly_returns or backtest_monthly_returns
data_coverage.benchmark_overlap
data_coverage.asset_prices
```

---

## 6. Analysis Architecture

### Shared statistics

```text
monthly returns
 -> expected returns
 -> covariance
 -> volatility
 -> correlation
```

위 계산 capability는 product-neutral이다. Optimization은 이를 ex-ante objective/solver 입력으로 사용할 수 있고, Historical Analytics는 covariance/correlation을 realized evaluation이나 decomposition에 사용할 수 있다.

### Optimization-only generation

```text
shared statistics
 -> objective / constraints
 -> constrained optimization
 -> optimized weights
 -> efficient frontier
```

Optimization 전용 경계는 수학 계산기 자체가 아니라 **weight를 찾기 위한 search policy와 결과**다.

### Portfolio path

Provided, Optimized, Backtest user-defined portfolio는 모두 동일 monthly asset return matrix와 shared portfolio path engine을 이용한다.

Rebalancing policy는 portfolio layer가 담당한다. Product UI가 하나의 rebalancing setting을 여러 portfolio에 공통 적용할 수 있지만, 실제 계산 엔진은 공유한다.

```text
none / monthly / quarterly / semiannual / yearly
calendar aligned or first-active-month anchored
canonical drift between rebalance events
```

동일 target weights와 동일 market-data/simulation setting이면 weight의 출처와 관계없이 동일 return/weight path를 만들어야 한다.

### Shared historical analytics

```text
CAGR / annualized return / volatility
Sharpe / Sortino
trailing / annual / monthly / rolling returns
drawdown series / episodes
asset performance
correlation / return-risk decomposition
benchmark-relative active return / tracking error / information ratio
active contribution / rolling active-risk / conditional benchmark analytics
```

동일 historical evaluation 의미를 product별 orchestration에서 복제 구현하지 않는다. Product orchestration은 portfolio identity와 applicable input을 shared analytics에 전달하고 결과를 canonical domain/artifact로 조립한다.

### Benchmark / active analytics

Benchmark overlap에서:

```text
monthly active return
annualized active return
tracking error
information ratio
rolling active return
rolling tracking error
conditional benchmark-relative analytics
```

을 계산한다.

36M Rolling Active Return은 **각 leg의 36M total return을 annualize한 뒤 차감**한다.

```text
portfolio 36M CAGR - benchmark 36M CAGR
```

Rolling Tracking Error는 같은 36M monthly active-return sample standard deviation을 annualize한다.

이 계산은 `analytics/`가 source of truth이며 browser viewer가 재계산하지 않는다.

---

## 7. Persistence Architecture

실행 instance identity는 `run_id`다.

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ context.yaml        # research execution only
├─ raw/
│  └─ *.csv
├─ review/
│  └─ *.csv
├─ report.html
└─ validation/
   └─ visual-comparison.md
```

Source of truth 분리:

```text
Executable input              input.yaml
Canonical calculation         result.json
Full precision tables         raw/
Human/LLM-readable tables     review/
Research provenance           context.yaml
Interactive presentation      report.html
Validation evidence           validation/
```

공통 historical analytics는 product report가 재계산하지 않도록 canonical result 또는 raw/review artifact에 필요한 identity와 series를 loss 없이 보존한다.

기존 run directory를 silent overwrite하지 않는다.

---

## 8. Viewer Architecture

`report.html`은 persisted run artifact에서 만든 **self-contained static research viewer**다.

개념 구조:

```text
run artifacts
    |
report model / artifact adapter
    |
product report composition
    |------------------------------|
    |                              |
product-specific sections   shared historical report components
    |                              |
    +--------------+---------------+
                   |
                   v
               report.html
```

Optimizer와 Backtest의 top-level report composition은 달라도 된다. 그러나 동일 canonical 의미의 historical section은 shared component를 재사용한다.

예:

```text
Shared historical report components
├─ Performance Summary
├─ Portfolio Growth
├─ Trailing / Annual / Monthly Returns
├─ Drawdowns
├─ Portfolio Asset Performance
├─ Correlations
├─ Return / Risk Decomposition
├─ Annual Asset Returns
├─ Rolling Returns
└─ applicable benchmark-relative views
```

Optimization-only Efficient Frontier/constraints/optimized allocation과 Backtest-only overview/portfolio comparison 같은 section 선택과 순서는 product composition이 담당한다.

현재 legacy Optimizer renderer는 historical compatibility layer 위에 corrective presentation layer를 순차 적용하고 있다.

```text
base renderer
 -> visual identity / presentation layers
 -> feedback_v3
 -> feedback_v4
 -> final_renderer
```

기능 안정화 과정에서 shared historical component를 추출하여 Optimizer와 Backtest가 동일 구현을 소비하도록 정리한다. 동일 의미의 section을 별도 renderer에 계속 복제하는 것은 target architecture가 아니다.

중요 원칙:

- canonical finance result는 Python runtime의 shared statistics/simulation/analytics가 계산한다.
- raw/review artifact는 shared calculation 결과를 presentation에 필요한 형태로 보존한다.
- browser JS는 layout, formatting, interaction만 담당한다.
- UI layer에서 finance metric/series를 다른 convention으로 새로 계산하지 않는다.
- chart coordinate transform, axis domain, tooltip selection, display ordering, presentation-only binning은 viewer 책임일 수 있다.
- 동일 historical section의 calculation뿐 아니라 renderer/report component도 가능한 한 공유하며 product layer는 composition을 담당한다.

---

## 9. Interactive Report Presentation

공통 historical section 후보:

```text
Performance Summary
Portfolio Growth
Annual Returns
Trailing Returns
Annualized Active Return
Active Return Contribution
Rolling Active Return and Risk
Up vs. Down Market
Portfolio Metrics
Monthly Returns
Drawdowns / Worst Drawdowns
Portfolio Asset Performance
Portfolio / Asset Correlations
Return / Risk Decomposition
Annual Asset Returns
Rolling Returns Summary / 3Y / 5Y
```

Optimization 전용 section:

```text
Efficient Frontier Assets
Efficient Frontier
Frontier Transition
Frontier Portfolios
Optimization constraints / optimized allocation
```

Backtest 전용 composition에는 Time Period, initial balance, named portfolio collection, Calendar Aligned와 target allocation comparison 등이 포함될 수 있다.

Rolling Active Return and Risk는 dual-axis combo chart다.

```text
left Y-axis  = Rolling Active Return, bars
right Y-axis = Rolling Tracking Error, line
```

Efficient Frontier는 curve 중심 viewport를 사용하지만 nearby assets와 portfolio landmarks가 연구 맥락을 제공할 수 있도록 충분한 display context를 확보한다. 최종 display domain 밖 asset만 outsider table로 분리한다.

Visual acceptance의 normative source는 `docs/visual-acceptance-contract.md`다.

---

## 10. Research Interaction Layer

사용자 연구의 운영 규칙은 `docs/research-operation-pipeline.md`를 따른다.

### Study

```text
studies/<study-id>/study.md
```

연구 질문, 관측 사실, 해석, 결론, follow-up을 한 파일에 유지한다.

### Experiment

```text
studies/<study-id>/experiments/*.yaml
```

Experiment 자체가 executable YAML이다. 별도 DB manifest를 만들지 않는다.

Experiment identity는 product가 정의하는 asset/ticker universe 규칙을 따른다. Optimization과 Backtest의 구체 identity policy는 각 product spec에 둔다.

각 Run의 실제 조건은 `runs/<run_id>/input.yaml`에 snapshot으로 보존한다. 따라서 같은 Experiment에서 조건이 달라져도 실행 시점의 effective input을 복원할 수 있다.

### Execution control

```text
control/execute.yaml
```

현재 실행할 Experiment와 실행 의도를 함께 표현한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
run: false
```

의미는 다음과 같다.

```text
target     현재 선택된 Experiment
run: false 저장/대기 상태
run: true  현재 target을 한 번 실행하라는 요청
```

일반 research execution에서는 `control/execute.yaml`의 main push가 GitHub Actions trigger다. Action은 `run: true`일 때만 `portfolio-optimizer execute`를 호출하고, 성공한 요청은 최신 요청을 덮어쓰지 않는 조건에서 `run: false`로 consume한다.

`portfolio-optimizer execute`는 새 optimizer/backtester가 아니라 target resolution + 기존 runner 호출 orchestration이다.

### Provenance

Research run은:

```text
Study <-> Experiment <-> Run
```

link를 `runs/<run_id>/context.yaml`에 보존한다.

Run의 `input.yaml`은 같은 Experiment에서 실행 조건이 달라졌더라도 해당 시점의 effective input을 복원할 수 있는 source다.

---

## 11. Development / Verification Architecture

개발 역할은 고정하지 않는다. `AGENTS.md`와 현재 `ai-share/llm-to-agent.md`가 작업별 workflow mode를 정한다.

지원 workflow:

```text
LLM sandbox development
LLM implementation
LLM design / Codex implementation
```

공통 검증 층:

```text
1. calculation/unit contract
2. affected-scope regression tests
3. real CLI run when needed
4. browser/E2E validation when needed
5. PV live / golden comparison for report work
```

Shared capability를 변경하면 해당 capability를 소비하는 제품의 affected-scope regression을 포함한다. 예를 들어 shared simulation/analytics/report component 변경은 Optimization과 Backtest 중 실제 영향을 받는 양쪽을 검증한다.

LLM sandbox가 network/resource 제약으로 repo checkout을 수행할 수 없는 경우 GitHub-side implementation + targeted CI를 1차 검증으로 사용할 수 있다. Agent real-environment validation은 별도 독립 검증으로 유지한다.

---

## 12. AI Share Boundary

```text
ai-share/PROTOCOL.md
ai-share/llm-to-agent.md
ai-share/agent-to-llm.md
ai-share/llm-to-llm.md
ai-share/agent-to-agent.md
```

AI Share는 project history 저장소가 아니라 최신 handoff/message transport다.

```text
Inbound  = GitHub remote latest
Outbound = commit + push 완료 후 전달 완료
History  = Git history
```

Project rules를 PROTOCOL에 중복하지 않는다. Project-specific source of truth는 `docs/`와 `AGENTS.md`다.

---

## 13. Failure Boundaries

### Input/control

- invalid YAML
- missing experiment target
- path traversal
- invalid asset / unsupported currency
- missing required price series

### Data

- insufficient completed monthly observations
- missing FX for mixed KRW/USD
- empty common coverage

### Optimization

- infeasible constraints
- solver failure
- invalid residual / non-finite result

### Shared simulation / analytics

- 동일 input에서 product별 historical path divergence
- 동일 metric의 product별 계산 convention divergence
- portfolio/asset identity loss
- benchmark-relative calculation mismatch

### Persistence

- run-id collision
- required artifact write failure
- provenance write failure

### Presentation

- canonical result missing required fields
- shared historical section을 product별로 다르게 해석
- semantic X/Y mismatch
- missing treated as zero
- wrong monetary/percentage unit
- wrong portfolio identity

Presentation failure는 canonical finance calculation과 분리해 진단한다.

---

## 14. Current Behavioral Golden

Current same-input PV reference:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

Universe:

```text
QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
```

Current static golden은 report-review v4 완료 후 사용자 제공 최신 PV screenshot으로 다시 고정할 예정이다.

---

## 15. Extension Boundary

후속 후보:

```text
Batch experiment execution
Cross-run comparison aggregation
Study navigation/search
Remote execution / notification
Consolidated shared historical report components
Additional risk/performance metrics
Additional market-data providers
```

확장 시에도 다음을 유지한다.

```text
product-specific request / generation policy
shared market data and statistics
shared portfolio simulation
shared historical analytics
shared run artifacts
shared historical report components
product-specific report composition
reproducible run artifact
```
