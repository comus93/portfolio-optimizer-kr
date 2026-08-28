# Architecture

## 1. Purpose

`portfolio-optimizer-kr`는 국내외 투자 자산을 동일한 mean-variance framework에서 분석하는 Python 기반 portfolio research system이다.

시스템은 다음 두 영역을 분리한다.

1. **Optimization / Analytics Runtime**
   - 재현 가능한 YAML 입력을 받아 market data, optimization, performance analytics를 계산하고 run artifact를 생성한다.
2. **Research Interaction Layer**
   - GPT와 사용자가 연구 질문, experiment, 실행 결과, 해석을 GitHub artifact로 연결해 연구를 이어갈 수 있게 한다.

Research Interaction Layer는 기존 optimizer runtime 위에 얇게 올라가며 계산 의미론을 변경하지 않는다.

---

## 2. Technology Baseline

현재 기술 구성은 다음과 같다.

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
Persistence       Repository filesystem + GitHub
Testing           pytest
Packaging         pyproject.toml / hatchling
```

실제 optimization 계산은 로컬 Python runtime에서 수행한다.

GitHub는 계산 runtime이 아니라 다음 artifact의 지속 저장소이자 GPT/Agent와 로컬 runtime 사이의 bridge다.

```text
Study
Experiment YAML
Execution pointer
Run outputs
Research interpretation
```

---

## 3. Logical Architecture

```text
                         ┌─────────────────────┐
                         │     User / GPT      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Research Artifacts  │
                         │ studies/            │
                         │ control/execute.yaml│
                         └──────────┬──────────┘
                                    │
                                    ▼
┌─────────────┐          ┌─────────────────────┐
│ Streamlit UI│─────────▶│ Execution / Runner  │◀─────────┐
└─────────────┘          └──────────┬──────────┘          │
                                    │                     │
┌─────────────┐                     │              ┌──────┴──────┐
│ Direct CLI  │─────────────────────┘              │ YAML Config │
└─────────────┘                                    └─────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ OptimizationRequest │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Analysis Pipeline  │
                         │ data / stats / opt  │
                         │ portfolio / analytics│
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Run Persistence   │
                         │ runs/<run_id>/      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │ canonical + compact review view│
                    │ result.json / research_summary│
                    └────────────────────────────────┘
```

모든 실행 surface는 최종적으로 동일한 YAML contract와 runner로 수렴한다.

```text
Streamlit ─┐
CLI run ───┼─> YAML Runner -> OptimizationRequest -> Analysis Pipeline -> Run
GPT execute┘
```

GPT 전용 financial API나 별도 optimization path를 만들지 않는다.

---

## 4. Runtime Layers

### 4.1 Input / Presentation Layer

사용자가 optimizer를 호출하는 surface다.

#### Direct CLI

기존 실행 방식:

```text
portfolio-optimizer run <config.yaml>
```

직접 YAML을 지정해 정밀하게 실행하는 개발자/Agent용 entrypoint다.

#### Streamlit UI

UI는 사용자 입력을 YAML contract로 변환한 뒤 동일 runner를 호출한다.

UI가 `OptimizationRequest`나 optimizer core를 직접 조립하는 별도 실행 경로를 만들지 않는다.

#### GPT Research Flow

GPT는 GitHub의 study와 experiment를 의미 기반으로 관리한다.

연구 실행 대상은 command argument가 아니라 다음 tracked pointer에 기록한다.

```text
control/execute.yaml
```

v0:

```yaml
target: studies/gld-cap-sensitivity/experiments/003-gld-max30-r01.yaml
```

로컬 실행 명령은 연구가 바뀌어도 동일하다.

```text
portfolio-optimizer execute
```

`execute`는 새 optimization engine이 아니라 control pointer를 해석해 기존 YAML runner를 호출하는 orchestration entrypoint다.

---

### 4.2 Configuration Layer

실행 가능한 experiment의 canonical format은 기존 YAML contract다.

```text
YAML
 ↓
load_run_config
 ↓
RunConfig
 ↓
OptimizationRequest
```

Experiment를 별도의 DB object나 중복 manifest로 관리하지 않는다.

```text
Experiment = executable YAML
```

`run_id`는 experiment identity가 아니라 persisted execution identity다.

Direct YAML은 기존처럼 explicit `run_id`를 가질 수 있다. Research experiment는 `run_id`를 생략할 수 있고, persistence boundary에서 unique run identity를 생성한다.

YAML schema와 UI contract의 세부 사항은 `docs/input-ui-contract.md`를 따른다.

---

### 4.3 Data Layer

Market data source는 v1에서 FinanceDataReader다.

개념 흐름:

```text
FDR
 ↓
asset / benchmark price series
 ↓
optional FX alignment
 ↓
canonical adjusted prices
 ↓
common analysis coverage
 ↓
monthly return matrix
```

Runner가 external data loading과 warm-up loading을 담당하고, 이후 계산 계층에는 정규화된 data를 전달한다.

---

### 4.4 Domain / Analysis Pipeline

현재 source package의 주요 논리 영역은 다음과 같다.

```text
config/       YAML parsing and validation
models.py     canonical domain request/spec models
data/         market data loading and normalization
stats/        return/statistical calculations
optimize/     optimization models and solver integration
portfolio/    portfolio return/rebalancing logic
analytics/    performance/risk/benchmark analytics
pipeline.py   analysis orchestration
report/       canonical/review/raw persistence
viewer/       persisted result presentation support
runner.py     YAML-to-run orchestration
cli.py        command-line entrypoint
```

의존 방향은 외부 orchestration에서 계산 core 쪽으로 흐른다.

```text
CLI / UI / Research Control
          ↓
        Runner
          ↓
   Configuration Model
          ↓
    Analysis Pipeline
          ↓
Data -> Statistics -> Optimization
                    -> Portfolio
                    -> Analytics
          ↓
       Reporting
```

Optimizer core와 analytics는 Study, GPT interpretation, GitHub control state를 알지 않는다.

---

## 5. Research Interaction Layer

### 5.1 Study

연구의 의미 단위다.

```text
studies/<study-id>/study.md
```

`study.md` 하나에 다음 연구 상태를 함께 둔다.

```text
Research question / purpose
Hypothesis / background
Executed experiment + run references
Observed result facts
Interpretation
Conclusion
Follow-up
```

별도 `analysis.md`를 두지 않는다.

이 구조는 연구 질문과 결과 해석을 한 화면에서 볼 수 있게 하고 GPT/Agent가 연구를 복원할 때 필요한 GitHub read 횟수를 줄인다.

### 5.2 Experiment

```text
studies/<study-id>/experiments/<experiment>.yaml
```

기존 YAML 실행 contract를 그대로 사용한다.

Research experiment에서는 `run_id`를 생략할 수 있다. 동일 experiment를 여러 번 실행하면 각 실행은 별도 run identity와 output directory를 가진다.

Revision이 필요하면 파일 단위로 관리한다.

```text
003-gld-max30-r01.yaml
003-gld-max30-r02.yaml
```

Git history가 파일 변경 이력을 담당한다.

### 5.3 Execution Pointer

```text
control/execute.yaml
```

현재 실행 대상 experiment를 가리킨다.

Research Interaction v0에서는 single experiment만 지원한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
```

Batch execution은 single research loop 검증 이후 확장한다.

### 5.4 Run Context

각 research run은 계산 결과 외에 연구 provenance를 보존한다.

```text
runs/<run_id>/context.yaml
```

v0 최소 구조:

```yaml
run_id: 20260828-0007
study: studies/gld-cap-sensitivity/study.md
experiment: studies/gld-cap-sensitivity/experiments/003-gld-max30-r01.yaml
```

역할은 다음 linkage 유지다.

```text
Study <-> Experiment <-> Run
```

`context.yaml`에 계산 결과나 interpretation을 복제하지 않는다.

### 5.5 Research Summary View

Research run에는 LLM과 사람이 적은 read 횟수로 첫 분석을 시작할 수 있는 compact derived view를 둔다.

```text
runs/<run_id>/review/research_summary.json
```

`research_summary.json`은 새로운 금융 계산 계층이 아니다. `result.json`과 기존 review/raw artifact에서 이미 계산된 값을 선택·정리하고 상세 artifact 위치를 제공한다.

Canonical source of truth는 계속 `result.json`이다.

기본 연구 복원 경로는 다음과 같다.

```text
study.md
   ↓
context.yaml
   ↓
review/research_summary.json
   ↓
필요한 상세 review/raw artifact만 추가 조회
```

이 구조는 모든 CSV를 매번 읽지 않고도 연구 질문, 실행 provenance, 핵심 계산 결과를 연결하게 한다.

각 정보의 source of truth와 view는 다음처럼 분리한다.

```text
Research meaning / interpretation   study.md
Executable experiment              experiment YAML
Exact effective input              runs/<run_id>/input.yaml
Calculated canonical result        runs/<run_id>/result.json
Research provenance                runs/<run_id>/context.yaml
Compact research view              runs/<run_id>/review/research_summary.json
Human/LLM-readable detail tables   runs/<run_id>/review/
Full-precision tables              runs/<run_id>/raw/
```

---

## 6. Execution Architecture

### 6.1 YAML Execution Flow

Runtime의 목표 실행 흐름은 다음과 같다.

```text
config.yaml
   ↓
load_run_config()
   ↓
RunConfig / OptimizationRequest
   ↓
resolve run_id
(explicit or generated)
   ↓
runner.execute_run()
   ↓
FDR data loading
   ↓
pipeline.analyze_prices()
   ↓
report.write_analysis_run()
   ↓
runs/<run_id>/
   ├─ input.yaml
   ├─ result.json
   ├─ review/
   │  └─ research_summary.json
   └─ raw/
```

Persisted `input.yaml`은 source YAML의 단순 복사본이 아니라 실제 실행에 사용된 effective configuration을 재현할 수 있어야 한다. 자동 생성된 `run_id`도 포함한다.

기존 run directory를 silent overwrite하지 않는다.

### 6.2 Research Control Flow

Research Interaction v0는 동일 실행 경로 앞에 target resolution과 뒤에 provenance persistence를 추가한다.

```text
control/execute.yaml
        ↓
resolve target experiment
        ↓
studies/.../experiment.yaml
        ↓
existing YAML execution path
        ↓
runs/<run_id>/
        ├─ result.json
        ├─ review/research_summary.json
        └─ ...
        ↓
write context.yaml
```

즉 새 기능의 핵심 경계는 다음이다.

```text
Control-aware Executor
      = target resolution + research provenance persistence
```

금융 계산, data loading, solver, analytics를 다시 구현하지 않는다.

---

## 7. Persistence Architecture

Repository 안의 persistent artifact는 세 범주다.

### Definition

```text
studies/<study-id>/study.md
studies/<study-id>/experiments/*.yaml
control/execute.yaml
```

### Execution Result

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ context.yaml
├─ review/
│  ├─ research_summary.json
│  └─ *.csv
└─ raw/
   └─ *.csv
```

`run_id`는 실행 시점의 persisted instance identity다. Experiment file identity와 분리한다.

### System Documents

```text
docs/specification.md
docs/architecture.md
docs/input-ui-contract.md
AGENTS.md
ai-share/
```

GitHub는 이 파일들의 durable history와 GPT/Agent 간 접근 지점을 제공한다.

로컬 runtime은 GitHub API를 통해 optimization을 수행하지 않는다. 계산은 checkout된 repository와 Python runtime에서 수행한다.

---

## 8. Repository Structure

Research Interaction v0가 추가된 목표 구조:

```text
portfolio-optimizer-kr/
├─ control/
│  └─ execute.yaml
├─ studies/
│  └─ <study-id>/
│     ├─ study.md
│     └─ experiments/
│        └─ *.yaml
├─ runs/
│  └─ <run_id>/
│     ├─ input.yaml
│     ├─ result.json
│     ├─ context.yaml
│     ├─ review/
│     │  ├─ research_summary.json
│     │  └─ *.csv
│     └─ raw/
│        └─ *.csv
├─ src/portfolio_optimizer_kr/
│  ├─ analytics/
│  ├─ config/
│  ├─ data/
│  ├─ optimize/
│  ├─ portfolio/
│  ├─ report/
│  ├─ stats/
│  ├─ viewer/
│  ├─ cli.py
│  ├─ models.py
│  ├─ pipeline.py
│  └─ runner.py
├─ ui/
│  └─ app.py
├─ tests/
└─ docs/
   ├─ specification.md
   ├─ architecture.md
   └─ input-ui-contract.md
```

Research artifact와 executable source code를 분리한다.

---

## 9. Failure Boundaries

### Control resolution failure

다음은 optimizer core 호출 전에 실패한다.

```text
control/execute.yaml missing
invalid YAML
missing target
nonexistent target
non-experiment target
path traversal outside repository
```

### Experiment validation failure

Target resolution 후에는 기존 YAML validation contract를 사용한다.

Research layer가 invalid experiment를 보정해서 실행하지 않는다.

### Calculation failure

Market data, solver, analytics failure는 기존 runtime error boundary를 유지한다.

### Persistence failure

다음 경우 persisted research run 완료로 취급하지 않는다.

```text
run_id collision
required run artifact write failure
context.yaml write failure
research_summary.json write failure
```

기존 run directory를 덮어써서 이전 연구 결과를 훼손하지 않는다.

---

## 10. Extension Boundary

Research Interaction v0의 목표는 single experiment research loop다.

후속 확장 후보:

```text
Batch experiment execution
Study navigation index
Run comparison aggregation
Remote execution / notification
Study search optimization
```

이 확장들은 Research Interaction / orchestration layer에서 해결한다.

기본 원칙은 다음과 같다.

```text
YAML contract 유지
Existing runner 재사용
Optimizer core 계산 의미론 유지
Run canonical result 유지
```
