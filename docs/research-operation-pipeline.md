# Research Operation Pipeline

## 1. Purpose

이 문서는 `portfolio-optimizer-kr`의 **사용자 연구 실행 운영 파이프라인**을 정의한다.

금융 계산 공식은 `docs/specification.md`, report UI는 `docs/report-ui-specification.md`, 내부 runtime 구조는 `docs/architecture.md`를 따른다. 이 문서는 그 구성요소들을 사용자가 실제로 사용하는 하나의 end-to-end 연구 흐름으로 연결한다.

일반 사용자 research run의 canonical execution path는 이 문서를 따른다.

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
        | ChatGPT persists experiment/run conditions
        v
control/execute.yaml
  target: <experiment>
  run: true
        |
        | GitHub push
        v
GitHub Actions
        |
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

사용자가 `run 해줘`, `이 조건으로 최적화해줘`, `분석해` 등 명시적으로 실행을 요청했을 때 ChatGPT가 해당 Asset Universe의 Experiment를 찾거나 새로 만들고, 실행 조건을 반영한 뒤 `control/execute.yaml`의 `target`을 맞추고 `run: true`로 저장한다.

실행 요청 전 연구 조건 확정 규칙은 `docs/llm-research-input-contract.md`를 따른다.

---

## 3. Experiment Identity Rule

Experiment의 identity는 **Asset Universe, 즉 optimizer에 포함되는 종목 집합**으로만 결정한다.

Canonical rule은 두 줄이다.

```text
종목 집합이 동일하다 -> 같은 Experiment, 새 Run
종목이 추가/삭제/교체된다 -> 새 Experiment
```

종목 순서만 달라지는 것은 같은 집합으로 본다.

### 같은 Experiment에서 바뀔 수 있는 조건

다음 값이 달라져도 Asset Universe가 같으면 **새 Experiment를 만들지 않는다.** 실행할 때마다 새 Run으로 남긴다.

- Provided Portfolio weights
- Min/max constraints
- Optimization objective
- Target volatility
- Analysis period
- Rebalancing
- Benchmark
- Risk-free convention
- Frontier point count
- 그 밖의 종목 집합을 바꾸지 않는 실행 조건

각 Run의 정확한 effective condition은 `runs/<run_id>/input.yaml`에 snapshot으로 보존한다.

따라서 Experiment 파일을 조건 변경마다 `r01`, `r02` 식으로 복제하지 않는다.

### 새 Experiment가 되는 경우

Optimizer Asset Universe에서 ticker 하나라도 추가, 삭제 또는 교체되면 별개의 Experiment다.

예:

```text
Experiment 001: QQQ / SPMO / GLD
Experiment 002: QQQ / SPMO
Experiment 003: QQQ / SPMO / XLE
```

반면 아래는 모두 Experiment 001의 서로 다른 Run이다.

```text
Run A: Maximum Sharpe / monthly / QQQ max 50% / 2016-2026
Run B: Target Vol 15% / annual / QQQ max 40% / 2020-2026
Run C: Maximum Sharpe / monthly / benchmark SPY / latest common period
```

### Experiment filename

신규 운영 Experiment는 단순한 파일명을 사용한다.

```text
<experiment-number>-<short-name>.yaml
```

예:

```text
001-qqq-spmo-gld.yaml
002-qqq-spmo.yaml
003-qqq-spmo-xle.yaml
```

Experiment 번호는 Study 안에서 사람이 구분하기 위한 순번이다. 별도의 opaque system ID가 아니다.

개발 과정에서 생성된 과거 `r01/r02` 형식 파일은 이 신규 운영 규칙의 기준으로 삼지 않는다. 정식 운영 전 정리할 수 있다.

---

## 4. Experiment Files Are the Research Interface

새로운 run-request 전용 ID나 별도 orchestration 데이터 모델을 만들지 않는다.

기존 구조를 사용한다.

```text
studies/<study-id>/
|- study.md
`- experiments/
   |- 001-qqq-spmo-gld.yaml
   |- 002-qqq-spmo.yaml
   `- ...
```

Experiment YAML은 사람이 읽고 다시 사용할 수 있는 executable research input이다.

ChatGPT는 사용자와의 대화에서 과거 실험을 찾아 재사용할 수 있다.

예:

```text
User: QQQ랑 SPMO를 사용한 실험 있었어? 그거 가져와.
ChatGPT: repository에서 해당 Study/Experiment와 연결된 Run/Result를 찾는다.

User: 조건을 바꿔서 다시 돌려줘.
ChatGPT: Asset Universe가 같으므로 같은 Experiment의 조건을 갱신하고 새 Run을 실행한다.

User: SPMO를 GLD로 바꿔서 돌려줘.
ChatGPT: Asset Universe가 달라졌으므로 새 Experiment를 만든 뒤 실행한다.
```

이 흐름에서 GPT와 runtime 사이에 별도의 opaque request identity는 두지 않는다. GitHub에 저장된 Study/Experiment/Run 파일이 공유 경계다.

### Execution Control

실행 대상과 실행 의도는 `control/execute.yaml` 하나로 표현한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
run: false
```

필드 의미:

```text
target     현재 실행 대상으로 선택된 Experiment
run: false 저장/대기 상태. 실행하지 않음
run: true  현재 target을 한 번 실행하라는 명시적 요청
```

`control/execute.yaml`은 Experiment identity나 Run identity를 만들지 않는다. 사람이 읽을 수 있는 작은 execution console이다.

Experiment YAML을 수정하는 것만으로는 optimizer가 실행되지 않는다. 사용자가 실행을 명시했을 때 ChatGPT가 필요한 Experiment 변경을 먼저 저장하고 마지막으로 `control/execute.yaml`을 `run: true`로 갱신한다.

---

## 5. GitHub Actions Execution Boundary

일반 research run의 실행 주체는 GitHub Actions다.

Canonical trigger는 `control/execute.yaml`의 변경이다.

```text
Experiment YAML 수정/저장
  -> 실행 안 함

control/execute.yaml 변경
  -> GitHub Actions 시작
  -> run: false 이면 no-op
  -> run: true 이면 target Experiment 실행
```

`.github/workflows/run-optimization.yml`은 `main`의 다음 경로만 실행 trigger로 감시한다.

```text
control/execute.yaml
```

실제 실행 흐름:

```text
User가 실행 요청
-> ChatGPT가 Experiment 조건 저장
-> ChatGPT가 control/execute.yaml의 target 확인/변경 + run: true
-> GitHub Actions
-> portfolio-optimizer execute
-> runs/<run_id>/ 생성 및 main 저장
-> GitHub Pages publish
-> 실행 요청 consume
-> run: false
```

Action은 성공적으로 실행한 요청을 자동으로 `run: false`로 되돌린다.

단, 실행 중 `control/execute.yaml`이 새로운 요청으로 변경됐다면 이전 Action이 최신 요청을 덮어쓰지 않는다. Action은 자신이 시작할 때 읽었던 control 내용이 여전히 최신일 때만 `run: false`로 reset한다. reset 직전에 remote가 다시 변경되면 reset push를 포기하고 새로운 요청을 보존한다.

이 구조에서 역할은 다음처럼 분리된다.

```text
Experiment YAML       무엇을 계산할 것인가
control/execute.yaml  무엇을 지금 실행할 것인가
runs/<run_id>/        무엇이 실제로 실행되었는가
```

커밋 메시지에 별도 실행 명령을 숨기지 않으며 `request_id` 같은 별도 execution identity도 만들지 않는다.

`workflow_dispatch`는 사람의 수동 복구/운영 점검을 위한 보조 force-execution 경로로 유지한다. ChatGPT의 canonical 실행 경로는 `control/execute.yaml`의 `run: true`다.

`portfolio-optimizer execute`는 `control/execute.yaml`의 target을 resolve하고 기존 runner / analysis pipeline을 호출한다. 별도 GPT 전용 optimizer path를 만들지 않는다.

---

## 6. Run Provenance

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

후속 provenance 보강 단계에서는 시스템이 자동으로 다음 정도를 추가할 수 있다.

```yaml
source_commit: <execution-source commit sha>
executed_at: <timestamp>
```

필요하다면 experiment 파일의 blob/commit SHA를 추가할 수 있지만, 사용자나 GPT가 이를 일상적으로 다루는 인터페이스로 만들지는 않는다.

목표는 `run_id`에서 Study와 Experiment로 거슬러 올라갈 수 있고, Run의 `input.yaml`에서 그 실행 당시의 정확한 조건을 복원할 수 있게 하는 것이다.

---

## 7. Run Result Source of Truth

하나의 persisted run은 다음 의미를 가진다.

```text
runs/<run_id>/input.yaml       executable effective input snapshot
runs/<run_id>/context.yaml     Study/Experiment/Run provenance
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

## 8. GitHub Pages Publication

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

ChatGPT는 run 완료 후 사용자에게 이 Pages URL을 안내한다.

---

## 9. User Decisions vs System Decisions

### User + ChatGPT가 결정하는 것

- 연구 질문
- Asset universe
- Provided Portfolio weights
- Min/max constraints
- Optimization objective
- Target volatility if required
- Analysis period 또는 project default 적용
- Rebalancing
- Benchmark
- 기존 Asset Universe를 재사용할지, 종목 변경으로 새 Experiment를 만들지
- 실제 실행 여부

### System이 자동으로 결정/수행하는 것

- `control/execute.yaml` push를 통한 execution trigger
- `run: true` execution gate
- 성공한 요청의 안전한 `run: false` reset
- `run_id` (`YYYYMMDD-####` existing convention)
- GitHub Actions environment/setup
- Run artifact generation
- Run artifact commit
- Pages deployment
- Run provenance capture
- Result artifact locations

사용자는 별도의 system ID나 execution request ID를 관리하지 않는다.

---

## 10. Run -> Result -> Analysis Linkage

최종 연구 lifecycle은 계산 결과에서 끝나지 않는다.

```text
Study
  -> Experiment (Asset Universe)
  -> Run (specific execution conditions)
  -> Result
  -> ChatGPT Initial Interpretation
  -> ChatGPT <-> User Discussion
  -> Confirmed Analysis / Insight
  -> Next Run or New Experiment
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
Run analysis      = 특정 조건으로 실행한 한 Run의 해석
Study conclusion  = 여러 Run/Experiment 분석을 종합한 연구 결론
```

새 insight가 다음 검증을 요구할 때:

```text
Asset Universe 동일 -> 같은 Experiment의 새 Run
Asset Universe 변경 -> 새 Experiment
```

규칙을 그대로 적용한다.

---

## 11. Operational Principle

Canonical user research execution은 다음 한 줄로 요약한다.

```text
User <-> ChatGPT -> Study/Experiment -> control/execute.yaml(run:true) -> GitHub Actions -> Run/Result -> GitHub Pages + ChatGPT Interpretation -> User -> Confirmed Analysis -> Repo
```

GPT와 시스템의 통합은 repository 파일을 공유하는 수준으로 유지한다. 중간 과정에서 opaque request state나 과도한 tight coupling을 만들지 않는다.
