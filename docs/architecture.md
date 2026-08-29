# Architecture

## 1. Purpose

`portfolio-optimizer-kr`는 재현 가능한 portfolio optimization / analytics runtime과 GitHub 기반 research interaction을 결합한 Python research system이다.

아키텍처는 세 책임을 분리한다.

```text
1. Analysis Runtime
   data -> stats -> optimization -> portfolio path -> analytics

2. Persistence / Presentation
   canonical result -> raw/review tables -> self-contained report.html

3. Research Interaction
   study / experiment / execution pointer / AI handoff
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

```text
User / GPT / Agent
        |
        v
YAML experiment / Streamlit / control/execute.yaml
        |
        v
Runner
        |
        v
OptimizationRequest
        |
        v
Analysis Pipeline
  |       |        |         |
 Data   Stats   Optimize   Portfolio
                    \       /
                     Analytics
                        |
                        v
                 Canonical Result
                        |
                 +------+------+ 
                 |             |
             raw/review     report model
                 |             |
                 v             v
             CSV artifacts  report.html
```

모든 실행 surface는 동일 YAML contract와 runner로 수렴한다.

```text
Direct CLI ─┐
Streamlit ──┼─> YAML Runner -> OptimizationRequest -> analyze_prices()
Research ───┘
```

별도 GPT 전용 optimizer path를 만들지 않는다.

---

## 4. Runtime Modules

```text
src/portfolio_optimizer_kr/
├─ config/        YAML parsing / validation
├─ data/          FDR loading / FX / month-end normalization
├─ stats/         expected return / covariance / volatility
├─ optimize/      CVXPY optimization / frontier
├─ portfolio/     rebalancing / historical path
├─ analytics/     performance / active / drawdown / decomposition
├─ report/        canonical JSON + raw/review persistence
├─ viewer/        presentation model + final HTML renderer
├─ models.py      canonical request/spec models
├─ pipeline.py    analysis orchestration
├─ research.py    study/control/provenance orchestration
├─ runner.py      YAML-to-run orchestration
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
      Pipeline
          |
   +------+------+-------+
   |      |      |       |
 Data   Stats  Optimize Portfolio
                   \     /
                  Analytics
                     |
                  Reporting
                     |
                   Viewer
```

Core analytics는 Study, GitHub message, browser DOM을 알지 않는다.

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
data_coverage.optimization_monthly_returns
data_coverage.benchmark_overlap
data_coverage.asset_prices
```

---

## 6. Analysis Architecture

### Optimization statistics

```text
monthly returns
 -> annual expected returns
 -> annual covariance
 -> annual volatility
 -> constrained optimization
 -> efficient frontier
```

Ex-ante optimization statistics와 realized historical statistics는 분리한다.

### Portfolio path

Provided와 Optimized portfolio는 동일 monthly asset return matrix를 이용한다.

Rebalancing policy는 portfolio layer가 담당한다.

```text
monthly
or
yearly drift + calendar-year rebalance
```

### Benchmark / active analytics

Benchmark overlap에서:

```text
monthly active return
annualized active return
tracking error
information ratio
rolling active return
rolling tracking error
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

기존 run directory를 silent overwrite하지 않는다.

---

## 8. Viewer Architecture

`report.html`은 persisted run artifact에서 만든 **self-contained static research viewer**다.

```text
run artifacts
    |
builder.py
    |
ReportModel
    |
renderer layers
    |
final_renderer.py
    |
report.html with inline JSON / SVG / JS
```

현재 renderer는 historical compatibility layer 위에 corrective presentation layer를 순차 적용한다.

```text
base renderer
 -> visual identity / presentation layers
 -> feedback_v3
 -> feedback_v4
 -> final_renderer
```

`final_renderer.py`가 public generation boundary다.

중요 원칙:

- canonical finance result는 Python runtime이 계산한다.
- browser JS는 layout, formatting, interaction만 담당한다.
- UI layer에서 finance series를 다른 convention으로 새로 계산하지 않는다.
- final renderer가 missing presentation-only derived value를 보완하더라도 canonical result의 의미를 변경하지 않는다.

향후 renderer layer가 과도하게 누적되면 기능 안정화 후 하나의 consolidated renderer로 정리할 수 있다. 현재는 regression risk를 줄이기 위해 corrective layer 방식을 유지한다.

---

## 9. Interactive Report Presentation

핵심 section:

```text
Provided / Optimized allocation
Performance Summary
Portfolio Growth
Annual Returns
Trailing Returns
Efficient Frontier Assets
Asset Correlations
Efficient Frontier
Frontier Transition
Frontier Portfolios
Annualized Active Return
Active Return Contribution
Rolling Active Return and Risk
Up vs. Down Market
Portfolio Metrics
Monthly Returns
Drawdowns / Stress / Worst Drawdowns
Portfolio Asset Performance
Portfolio / Asset Correlations
Return / Risk Decomposition
Annual Asset Returns
Rolling Returns Summary / 3Y / 5Y
```

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

Experiment identity는 **optimizer Asset Universe의 종목 집합**으로 결정한다.

```text
Asset Universe 동일 -> 같은 Experiment
종목 추가 / 삭제 / 교체 -> 새 Experiment
```

기간, Provided weights, min/max constraints, objective, target volatility, rebalancing, benchmark, risk-free convention 등 종목 집합을 바꾸지 않는 조건 변경은 같은 Experiment의 새 Run으로 관리한다.

각 Run의 실제 조건은 `runs/<run_id>/input.yaml`에 snapshot으로 보존한다. 따라서 조건 변경을 표현하기 위한 Experiment `r01/r02` revision 파일은 신규 운영 규칙에서 사용하지 않는다.

신규 운영 파일 예:

```text
001-qqq-spmo-gld.yaml
002-qqq-spmo.yaml
003-qqq-spmo-xle.yaml
```

### Execution pointer

```text
control/execute.yaml
```

현재 실행할 experiment를 가리킨다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
```

`portfolio-optimizer execute`는 새 optimizer가 아니라 pointer resolution + 기존 runner 호출 orchestration이다.

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

### Persistence

- run-id collision
- required artifact write failure
- provenance write failure

### Presentation

- canonical result missing required fields
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
Consolidated final report renderer
Additional risk/performance metrics
Additional market-data providers
```

확장 시에도 다음을 유지한다.

```text
YAML contract
single analysis pipeline
canonical result
calculation/presentation separation
reproducible run artifact
```
