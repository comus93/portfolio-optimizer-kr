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
        | ChatGPT commits experiment and updates execution pointer
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

사용자가 `run 해줘`, `이 조건으로 최적화해줘` 등 명시적으로 실행을 요청했을 때 ChatGPT가 실행할 Experiment를 GitHub에 저장하고 `control/execute.yaml`이 해당 파일을 가리키도록 갱신한다.

실행 요청 전 연구 조건 확정 규칙은 `docs/llm-research-input-contract.md`를 따른다.

---

## 3. Experiment Files Are the Research Interface

새로운 run-request 전용 ID나 별도 orchestration 데이터 모델을 만들지 않는다.

기존 구조를 그대로 사용한다.

```text
studies/<study-id>/
|- study.md
`- experiments/
   |- 001-base-r01.yaml
   |- 001-base-r02.yaml
   |- 002-add-gld-r01.yaml
   `- ...
```

Experiment YAML이 사람이 읽고 다시 사용할 수 있는 executable research input이다.

ChatGPT는 사용자와의 대화에서 과거 실험을 찾아 재사용할 수 있다.

예:

```text
User: QQQ랑 SPMO를 사용한 실험 있었어? 그거 가져와.
ChatGPT: repository에서 해당 Study/Experiment를 찾고 기존 조건과 결과를 설명한다.
User: 여기서 종목 하나를 바꿔서 다시 실험해줘.
ChatGPT: 기존 Experiment를 기반으로 새 Experiment 파일을 만든 뒤 실행한다.
```

이 흐름에서 GPT와 runtime 사이에 별도의 opaque request identity는 두지 않는다. GitHub에 저장된 Study/Experiment 파일이 공유 경계다.

### Experiment와 Revision 규칙

파일명 revision을 기존 방식으로 사용한다.

```text
<experiment-number>-<short-name>-r##.yaml
```

의미는 다음과 같다.

- **같은 연구 질문/실험의 수정**: 같은 experiment number를 유지하고 `r##`를 증가시킨다.
- **자산 universe, 핵심 가설, 주요 조건을 바꾸어 별개 비교 실험을 수행**: 새 experiment number와 `r01`을 만든다.
- 과거 Experiment 파일은 삭제하거나 덮어쓰지 않고 그대로 보존한다.

예:

```text
001-qqq-spmo-r01.yaml
001-qqq-spmo-r02.yaml       # 같은 실험의 수정
002-qqq-gld-r01.yaml        # 자산 변경으로 파생된 별개 실험
```

`r##`는 실행 횟수가 아니라 **실험 정의의 revision**이다.

### Execution Pointer

실행 대상은 기존 pointer를 사용한다.

```text
control/execute.yaml
```

형식은 단순하게 유지한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
```

새로운 Experiment를 실행할 때 ChatGPT가 `target`을 그 파일로 변경한다. 이 Git commit이 GitHub Actions 실행의 자연스러운 trigger가 된다.

동일 Experiment 파일을 변경 없이 그대로 재실행해야 하는 운영/복구 상황은 `workflow_dispatch`를 사용한다. 이를 위해 Experiment 모델에 별도의 `request_id`를 추가하지 않는다.

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

`workflow_dispatch`는 같은 Experiment의 명시적 재실행, 복구, 운영 점검용으로 유지한다.

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

이 관계 자체가 provenance의 중심이다. Experiment 파일명과 Git history가 사람이 이해할 수 있는 revision history를 제공하므로 별도 execution request ID는 도입하지 않는다.

후속 provenance 보강 단계에서는 시스템이 자동으로 다음 정도만 추가할 수 있다.

```yaml
source_commit: <execution-source commit sha>
executed_at: <timestamp>
```

필요하다면 experiment 파일의 blob/commit SHA를 추가할 수 있지만, 사용자나 GPT가 이를 일상적으로 다루는 인터페이스로 만들지는 않는다.

목표는 `run_id`에서 Study와 Experiment 파일로 거슬러 올라갈 수 있고, Experiment 파일에서는 Git history를 통해 revision 변화를 확인할 수 있게 하는 것이다.

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

- 연구 질문
- Asset universe
- Provided Portfolio weights
- Min/max constraints
- Optimization objective
- Target volatility if required
- Analysis period 또는 project default 적용
- Rebalancing
- Benchmark
- 기존 Experiment를 재사용할지, 새 Experiment로 파생할지

### System이 자동으로 결정/수행하는 것

- `control/execute.yaml`을 통한 실행 plumbing
- `run_id` (`YYYYMMDD-####` existing convention)
- GitHub Actions environment/setup
- Run artifact generation
- Run artifact commit
- Pages deployment
- Run provenance capture
- Result artifact locations

Experiment 파일명과 revision은 ChatGPT가 기존 repository convention을 보고 자연스럽게 선택하며, 사용자가 별도의 시스템 ID를 관리할 필요는 없다.

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
Run analysis      = 한 Experiment 실행 결과의 해석
Study conclusion  = 여러 Run/Analysis를 종합한 연구 결론
```

새 insight가 다음 실험을 요구하면 ChatGPT는 기존 Experiment를 참고해 새로운 Experiment 파일을 생성한다. 이렇게 research loop는 별도 API state가 아니라 repository의 Study/Experiment/Run 파일 관계로 이어진다.

---

## 10. Operational Principle

Canonical user research execution은 다음 한 줄로 요약한다.

```text
User <-> ChatGPT -> Study/Experiment files -> GitHub Actions -> Run/Result -> GitHub Pages + ChatGPT Interpretation -> User -> Confirmed Analysis -> Repo
```

GPT와 시스템의 통합은 repository 파일을 공유하는 수준으로 유지한다. 중간 과정에서 opaque request state나 과도한 tight coupling을 만들지 않는다.
