# Architecture

## 1. Purpose

`portfolio-optimizer-kr`는 계산 엔진과 연구 관리 인터랙션을 분리한다.

계산 엔진의 책임은 재현 가능한 portfolio optimization과 analytics를 수행하는 것이다. 연구 관리 레이어의 책임은 사용자가 GPT와 자연어로 연구를 이어가면서 어떤 실험을 실행할지 선택하고, 실행 결과와 당시 해석을 지속 가능한 GitHub artifact로 연결하는 것이다.

핵심 원칙은 다음과 같다.

> Research interaction은 기존 YAML runner 위에 얇게 올라가며 optimizer core의 계산 의미론을 변경하지 않는다.

개발 시 LLM과 Agent의 역할 분담은 `AGENTS.md`를 source of truth로 따른다.

## 2. System Boundary

전체 실행 경계는 다음과 같다.

```text
User ↔ GPT
       │
       ▼
   GitHub Study
       │
       ├─ experiment YAML
       └─ control/execute.yaml
                 │
                 ▼
       Control-aware Executor
                 │
                 ▼
          Existing YAML Runner
                 │
                 ▼
          OptimizationRequest
                 │
                 ▼
            Optimizer Core
                 │
                 ▼
             Run Outputs
                 │
                 ├─ canonical result
                 ├─ review/raw tables
                 └─ context.yaml
                 │
                 ▼
User ↔ GPT updates study.md with findings / conclusion / follow-up
```

Streamlit과 direct CLI도 같은 YAML runner를 사용한다.

```text
Streamlit ─┐
CLI YAML ──┼─> YAML Runner -> Optimizer Core -> Runs
GPT flow ──┘
```

GPT 전용 optimization API나 별도 계산 경로를 만들지 않는다.

## 3. Sources of Truth

각 artifact의 책임을 명확히 분리한다.

### Experiment YAML

재현 가능한 실행 입력의 source of truth다.

```text
studies/<study-id>/experiments/<experiment>.yaml
```

Experiment는 별도의 registry object가 아니라 실행 가능한 기존 YAML contract 자체다.

### Canonical Result

계산 결과의 source of truth는 다음이다.

```text
runs/<run_id>/result.json
```

`review/`는 사람/GPT가 읽기 쉬운 표현이고 `raw/`는 full-precision machine-oriented data다.

### Study Document

연구 의미와 해석의 source of truth는 다음이다.

```text
studies/<study-id>/study.md
```

`study.md`는 별도 analysis/report 파일로 분리하지 않는다. 한 문서 안에 최소한 다음 내용을 함께 관리한다.

- 연구 질문과 목적
- 필요한 배경/가설
- 실행한 experiment와 run 연결
- 계산 결과에서 확인한 사실
- GPT + 사용자 해석
- 합의된 결론
- follow-up 질문 또는 다음 experiment

이 구조는 사람이 한눈에 연구 상태를 파악하게 하고 GPT/Agent의 GitHub read 횟수를 줄인다.

### Execution Pointer

현재 사용자가 실행하려는 target의 source of truth는 다음이다.

```text
control/execute.yaml
```

v0 schema는 single experiment 실행만 지원한다.

```yaml
target: studies/gld-cap-sensitivity/experiments/003-gld-max30-r01.yaml
```

연구를 전환할 때 command-line argument를 계속 바꾸지 않는다. GPT 또는 사용자가 `control/execute.yaml`의 target을 변경하고 로컬에서는 동일한 command를 실행한다.

```text
portfolio-optimizer execute
```

Batch execution은 single-study research loop가 검증된 뒤 별도 확장한다.

### Run Context

연구 관리 레이어와 계산 결과를 연결하는 provenance artifact는 다음이다.

```text
runs/<run_id>/context.yaml
```

최소 형태:

```yaml
run_id: 20260828-0007
study: studies/gld-cap-sensitivity/study.md
experiment: studies/gld-cap-sensitivity/experiments/003-gld-max30-r01.yaml
```

`context.yaml`에는 분석 내용이나 계산 결과를 복제하지 않는다.

역할은 오직 다음 연결을 유지하는 것이다.

```text
Study <-> Experiment <-> Run
```

분석과 결론은 `study.md`, exact executed input은 `runs/<run_id>/input.yaml`, 계산 결과는 `result.json`이 담당한다.

## 4. Repository Layout

Research Interaction v0의 최소 구조는 다음과 같다.

```text
studies/
└─ <study-id>/
   ├─ study.md
   └─ experiments/
      ├─ 001-base-r01.yaml
      ├─ 002-...-r01.yaml
      └─ ...

control/
└─ execute.yaml

runs/
└─ <run_id>/
   ├─ input.yaml
   ├─ result.json
   ├─ context.yaml
   ├─ review/
   └─ raw/
```

초기 버전에서는 별도 study registry DB, state machine, report version subsystem을 만들지 않는다. Git history가 변경 이력을 담당한다.

Experiment revision은 필요할 때 새 YAML 파일로 관리한다.

```text
003-gld-max30-r01.yaml
003-gld-max30-r02.yaml
```

## 5. Component Responsibilities

### GPT / Research Front-end

GPT는 repository path를 사용자에게 직접 관리시키는 UI가 아니라 의미 기반 research front-end 역할을 한다.

책임:

- 기존 study 탐색과 과거 결론 복원
- 사용자와 연구 질문/가설 논의
- experiment YAML 생성 또는 revision
- 실행할 experiment 선택
- `control/execute.yaml` target 갱신
- run output 해석
- 사용자와 합의한 결과를 `study.md`에 반영
- 필요한 follow-up experiment 제안/생성

### Control-aware Executor

`portfolio-optimizer execute`의 책임:

1. `control/execute.yaml`을 읽는다.
2. target experiment YAML path를 검증한다.
3. existing YAML runner에 해당 YAML을 전달한다.
4. 생성된 run과 study/experiment를 연결하는 `context.yaml`을 저장한다.

이 계층은 orchestration 역할만 하며 금융 계산을 수행하지 않는다.

### Existing YAML Runner

기존 contract를 유지한다.

책임:

- YAML parsing / validation
- market data와 필요한 warm-up/FX data loading
- `OptimizationRequest` 생성
- optimizer core 호출
- persisted run 생성
- exact input을 `runs/<run_id>/input.yaml`에 보존

### Optimizer Core

연구 관리 개념을 알지 않는다.

Optimizer Core에는 다음 개념이 들어가지 않는다.

```text
Study
control/execute.yaml
study.md
GPT interpretation
follow-up
```

Core는 `OptimizationRequest`를 받아 계산 결과를 반환한다.

### Viewer / Streamlit

Viewer는 기존 run output만으로 동작할 수 있어야 한다. 연구 관리 metadata가 없어도 과거 run을 표시할 수 있어야 한다.

Streamlit에서 실행하는 경우에도 YAML을 생성하고 existing runner를 호출한다. Streamlit이 별도 optimization path를 만들지 않는다.

## 6. Development R&R

구체적인 LLM/Agent 역할 분담과 테스트 규율의 source of truth는 `AGENTS.md`다. Research Interaction Layer도 동일한 R&R을 그대로 적용한다.

이 레이어에서의 적용 방식은 다음과 같다.

```text
User + LLM
  ↓
interaction requirement / schema / acceptance scenario 확정
  ↓
LLM
  - control/execute.yaml contract
  - context.yaml contract
  - single research loop contract test
  - 필요한 최소 skeleton
  ↓
Agent
  - repository 실제 구조에 맞춘 구현 보강
  - dependency / CLI wiring
  - end-to-end 실행 및 디버깅
  - regression test
```

Agent는 구현 편의를 위해 LLM이 확정한 schema나 contract test를 임의로 약화하거나 다른 실행 의미론을 만들지 않는다. 계약에 문제가 있으면 `ai-share/agent-to-llm.md`로 blocker를 제기한다.

LLM 역시 optimizer core 구현 세부를 불필요하게 선점하지 않는다. 계약과 최소 skeleton을 넘은 실제 환경 hardening은 Agent 책임으로 둔다.

## 7. Single Research Loop v0

첫 번째 구현 목표는 하나의 연구가 끝까지 한 바퀴 도는 것이다.

```text
1. User + GPT가 연구 질문을 정의한다.
2. GPT가 studies/<study-id>/study.md를 생성 또는 갱신한다.
3. GPT가 실행 가능한 experiment YAML을 생성한다.
4. GPT가 control/execute.yaml의 target을 해당 experiment로 설정한다.
5. 사용자가 로컬에서 `portfolio-optimizer execute`를 실행한다.
6. Executor가 existing YAML runner를 호출한다.
7. run output과 context.yaml이 생성된다.
8. GPT가 study.md와 linked run output을 읽고 결과를 해석한다.
9. User + GPT가 결론과 후속 질문을 논의한다.
10. GPT가 study.md에 findings / conclusion / follow-up을 반영한다.
11. 후속 experiment가 필요하면 3번부터 반복한다.
```

이 루프가 안정적으로 동작하는 것이 Batch보다 우선한다.

## 8. Dependency Direction

의존 방향은 다음을 유지한다.

```text
Research Interaction
        ↓
Control-aware Executor
        ↓
Existing YAML Runner
        ↓
OptimizationRequest
        ↓
Optimizer Core
```

반대 방향 의존을 만들지 않는다.

특히 Optimizer Core가 study file이나 GitHub 상태를 읽지 않는다.

## 9. Failure Boundaries

### Invalid control target

`control/execute.yaml`이 없거나 target이 존재하지 않거나 실행 가능한 YAML이 아니면 optimizer core 호출 전에 명시적으로 실패한다.

### Invalid experiment YAML

기존 YAML validation error를 그대로 사용한다. Research layer가 계산 contract를 우회하지 않는다.

### Run persistence failure

계산이 성공했더라도 required run artifacts 저장에 실패하면 완료된 research run으로 취급하지 않는다.

### Study update failure

계산된 run 자체는 유효할 수 있다. 다만 `study.md`에 해석/결론을 아직 반영하지 못한 상태는 research loop가 끝난 것으로 간주하지 않는다. 별도 복잡한 status machine은 만들지 않는다.

## 10. Deferred Extensions

다음은 v0 single research loop가 검증된 후 필요에 따라 확장한다.

- Batch experiment execution
- study navigation index
- richer run aggregation/comparison artifact
- automatic notification / remote execution
- study search optimization

Batch를 추가할 때도 existing YAML runner와 optimizer core contract는 유지하고 orchestration layer만 확장하는 것을 기본 원칙으로 한다.
