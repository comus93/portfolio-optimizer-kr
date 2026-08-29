# Research Operation Pipeline

## 1. Purpose

이 문서는 `portfolio-optimizer-kr`의 **사용자 연구 실행 운영 파이프라인**을 정의한다.

금융 계산 공식은 `docs/specification.md`, report UI는 `docs/report-ui-specification.md`, 내부 runtime 구조는 `docs/architecture.md`를 따른다. 이 문서는 그 구성요소들을 사용자가 실제로 사용하는 하나의 end-to-end 연구 흐름으로 연결한다.

과거 문서에 Agent/Codex가 research run의 실행 주체처럼 표현된 부분이 있더라도, 일반 사용자 research run의 canonical execution path는 이 문서를 따른다.

Agent/Codex는 개발, 실제 환경 검증, browser/E2E 검증을 위한 별도 경로이며 일반 research execution engine이 아니다.

---

## 2. Canonical User Research Flow

```text
User <-> ChatGPT
        |
        | portfolio assets / provided weights / bounds /
        | objective / period / rebalance / benchmark 확정
        v
Study + Experiment YAML
        |
        | ChatGPT commits experiment and execution pointer
        v
control/execute.yaml
        |
        | GitHub Actions trigger
        v
portfolio-optimizer execute
        |
        v
runs/<run_id>/
  |- input.yaml
  |- context.yaml
  |- result.json
  |- raw/*.csv
  |- review/*.csv
  `- report.html
        |
        +--------------------+
        |                    |
        v                    v
GitHub Pages            ChatGPT analysis
user-facing report      result/review source
        |                    |
        +---------+----------+
                  v
             User discussion
                  |
                  v
           Confirmed analysis
                  |
                  v
             Repository
```

사용자가 `run 해줘`, `이 조건으로 최적화해줘` 등 명시적으로 실행을 요청했을 때 ChatGPT가 실행 포인터를 갱신한다.

실행 요청 전 연구 조건 확정 규칙은 `docs/llm-research-input-contract.md`를 따른다.

---

## 3. Existing Experiment Structure Is Canonical

새로운 run request 전용 데이터 모델을 만들지 않는다.

기존 구조를 그대로 사용한다.

```text
studies/<study-id>/
|- study.md
`- experiments/
   |- 001-base-r01.yaml
   |- 001-base-r02.yaml
   `- ...
```

Experiment YAML이 executable research input이다.

ChatGPT와 사용자가 연구 조건을 확정하면 ChatGPT가 해당 experiment YAML을 생성 또는 revision하고 GitHub에 commit한다.

실행 대상은 기존 pointer를 사용한다.

```text
control/execute.yaml
```

권장 형태:

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
request_id: 20260829T203500+0900
```

- `target`: 실행할 canonical experiment
- `request_id`: 실행 의미를 바꾸지 않는 execution trigger identity

같은 experiment를 새로운 시장 데이터로 다시 실행할 때 `target`이 같아도 `request_id`를 갱신하면 새로운 GitHub Actions run을 시작할 수 있다.

`request_id`는 optimizer input이나 `run_id`가 아니다.

---

## 4. GitHub Actions Execution Boundary

일반 research run의 실행 주체는 GitHub Actions다.

```text
ChatGPT commit
  -> control/execute.yaml changed
  -> .github/workflows/run-optimization.yml
  -> portfolio-optimizer execute
  -> runs/<run_id>/ generated
  -> generated run committed to main
```

`portfolio-optimizer execute`는 기존 `control/execute.yaml` pointer를 resolve하고 기존 runner / analysis pipeline을 호출한다.

별도 GPT 전용 optimizer path를 만들지 않는다.

GitHub Actions가 생성한 run commit은 `control/execute.yaml`을 수정하지 않으므로 자기 자신을 재귀적으로 다시 실행하지 않는다.

`workflow_dispatch`도 유지해 운영/복구 목적의 수동 실행을 허용한다.

---

## 5. Run Provenance

연구 provenance는 사용자가 수기로 작성하지 않는다.

기존 `execute_controlled_experiment()`는 이미 run 생성 시 다음 관계를 `runs/<run_id>/context.yaml`에 기록한다.

```text
Study <-> Experiment <-> Run
```

현재 최소 정보:

```yaml
run_id: <run-id>
study: studies/<study-id>/study.md
experiment: studies/<study-id>/experiments/<experiment>.yaml
```

후속 provenance 보강 단계에서 자동으로 다음을 추가한다.

```yaml
source_commit: <execution-request commit sha>
experiment_revision: <experiment blob/commit identity>
request_id: <control execution request identity>
executed_at: <UTC/KST timestamp>
```

목표는 임의의 `run_id`만 보더라도 어떤 Study의 어떤 Experiment revision이 어떤 GitHub request에서 실행됐는지 역추적 가능하게 하는 것이다.

---

## 6. Run Result Source of Truth

하나의 persisted run은 다음 의미를 가진다.

```text
runs/<run_id>/input.yaml       executable effective input
runs/<run_id>/context.yaml     provenance/linkage
runs/<run_id>/result.json      canonical calculation result
runs/<run_id>/raw/*.csv        full-precision machine/audit data
runs/<run_id>/review/*.csv     ChatGPT/user-readable analysis data
runs/<run_id>/report.html      interactive user presentation
```

ChatGPT의 optimization interpretation은 `report.html` 화면을 재계산하거나 눈으로 전사해서 만들지 않는다.

기본 source는:

1. `result.json`
2. `review/*.csv`
3. 필요한 경우 `raw/*.csv`

이다.

`report.html`은 사용자가 결과를 직접 탐색하기 위한 presentation surface다.

---

## 7. GitHub Pages Publication

Research run이 성공해 `runs/<run_id>/`가 main에 저장되면 Pages publication을 이어서 수행한다.

기존 workflow:

```text
.github/workflows/publish-reports.yml
```

을 재사용한다.

Canonical user-facing URL 형식:

```text
https://<owner>.github.io/<repo>/runs/<run_id>/report.html
```

`run-optimization.yml`은 run artifact commit 후 `publish-reports.yml`을 dispatch한다.

GitHub Actions의 기본 `GITHUB_TOKEN`으로 생성한 push는 다른 push-triggered workflow를 자동 연쇄 실행하지 않을 수 있으므로, Pages publish는 명시적 workflow dispatch로 연결한다.

ChatGPT는 run 완료 후 사용자에게 이 Pages URL을 안내한다.

---

## 8. User Decisions vs System Decisions

### User + ChatGPT가 결정하는 것

- Asset universe
- Provided Portfolio weights
- Min/max constraints
- Optimization objective
- Target volatility if required
- Analysis period 또는 project default 적용
- Rebalancing
- Benchmark
- 명시적 override가 필요한 연구 조건

### System이 자동으로 결정/수행하는 것

- Experiment file persistence convention
- Execution request plumbing
- `run_id` (`YYYYMMDD-####` existing convention)
- GitHub Actions environment/setup
- Run artifact generation
- Run artifact commit
- Pages deployment
- Provenance capture
- Result artifact locations

현재 Phase 1 실행 파이프라인을 위해 사용자가 추가로 정해야 하는 필수 infrastructure option은 없다.

---

## 9. Run -> Result -> Analysis Linkage

최종 연구 lifecycle은 계산 결과에서 끝나지 않는다.

```text
Study
  -> Experiment
  -> Run
  -> Result
  -> ChatGPT Initial Interpretation
  -> ChatGPT <-> User Discussion
  -> Confirmed Analysis / Insight
  -> Next Experiment (optional)
```

Run과 Result는 같은 `runs/<run_id>/` identity를 공유한다.

후속 Phase에서 `analysis.md`를 같은 run directory에 추가해 run-result-analysis를 물리적으로도 묶는다.

예정 구조:

```text
runs/<run_id>/
|- input.yaml
|- context.yaml
|- result.json
|- review/
|- raw/
|- report.html
`- analysis.md
```

`analysis.md`는 전체 채팅 transcript 저장소가 아니다. 계산 사실, ChatGPT의 초기 해석, 사용자의 challenge/feedback, 최종 합의된 insight와 다음 실험을 구조화해 보존한다.

개별 run analysis와 여러 run을 종합하는 Study conclusion은 분리한다.

```text
Run analysis      = 한 experiment 실행 결과의 해석
Study conclusion  = 여러 run/analysis를 종합한 연구 결론
```

이 analysis persistence는 GitHub Actions execution backbone이 안정화된 다음 단계에서 구현한다.

---

## 10. Operational Principle

Canonical user research execution은 다음 한 줄로 요약한다.

```text
User <-> ChatGPT -> Experiment -> GitHub Actions -> Run/Result -> GitHub Pages + ChatGPT Interpretation -> User -> Confirmed Analysis -> Repo
```

중간 과정에서 사용자가 config/result 파일을 수동으로 복사하거나 Agent/Codex에 실행 명령을 전달하는 것을 정상 운영 경로로 삼지 않는다.
