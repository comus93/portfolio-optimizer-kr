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
        | ChatGPT persists the experiment/run conditions
        | and commits explicit run intent
        v
GitHub push (`run:` commit)
        |
        | GitHub Actions
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

사용자가 `run 해줘`, `이 조건으로 최적화해줘` 등 명시적으로 실행을 요청했을 때 ChatGPT가 해당 Asset Universe의 Experiment를 찾거나 새로 만들고, 실행 조건을 반영한 뒤 `run:` 커밋으로 실행 의도를 명시한다.

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

### Execution Pointer

실행 대상은 기존 pointer를 사용한다.

```text
control/execute.yaml
```

형식은 단순하게 유지한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
```

`control/execute.yaml`은 현재 실행할 Experiment를 가리키는 pointer일 뿐 Experiment identity나 Run identity를 만들지 않는다.

---

## 5. GitHub Actions Execution Boundary

일반 research run의 실행 주체는 GitHub Actions다.

파일 저장과 실행 의도는 분리한다.

```text
Experiment YAML 일반 commit
  -> 연구 정의만 저장
  -> optimizer 실행 안 함

Experiment YAML 또는 control pointer 변경
+ head commit message가 `run:`으로 시작
  -> GitHub Actions 실행
  -> portfolio-optimizer execute
  -> runs/<run_id>/ 생성
```

Canonical 실행 commit 예:

```text
run: QQQ SPMO GLD target-vol-15
```

`.github/workflows/run-optimization.yml`은 `main`의 다음 경로 변경을 감시한다.

```text
studies/**/experiments/*.yaml
studies/**/experiments/*.yml
control/execute.yaml
```

Push 이벤트가 발생해도 마지막 commit message가 `run:`으로 시작하지 않으면 execution job은 수행하지 않는다.

따라서 같은 Experiment에서 조건만 바꾸는 경우:

```text
Experiment YAML 수정
-> `run:` commit
-> 새 Run
```

새 Asset Universe인 경우:

```text
새 Experiment 파일 저장
-> control/execute.yaml을 새 Experiment로 변경
-> 마지막 변경을 `run:` commit
-> 새 Run
```

이 구조에서 파일은 사람이 읽을 수 있는 연구 인터페이스이고, commit message는 해당 변경을 실제로 실행하겠다는 가벼운 command signal이다. 별도의 request ID나 GPT 전용 API는 사용하지 않는다.

`workflow_dispatch`는 사람이 GitHub UI/CLI에서 명시적으로 재실행하거나 복구/운영 점검할 때 사용할 수 있는 보조 경로로 유지한다. ChatGPT의 canonical 실행 경로는 `run:` commit이다.

`portfolio-optimizer execute`는 `control/execute.yaml` pointer를 resolve하고 기존 runner / analysis pipeline을 호출한다. 별도 GPT 전용 optimizer path를 만들지 않는다.

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

### System이 자동으로 결정/수행하는 것

- Experiment/Run persistence plumbing
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
User <-> ChatGPT -> Study/Experiment -> `run:` commit -> GitHub Actions -> Run/Result -> GitHub Pages + ChatGPT Interpretation -> User -> Confirmed Analysis -> Repo
```

GPT와 시스템의 통합은 repository 파일을 공유하는 수준으로 유지한다. 중간 과정에서 opaque request state나 과도한 tight coupling을 만들지 않는다.
