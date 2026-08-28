# Agent Session Handover — GPT/User Experiment Interaction Layer

state: ready
created_at: 2026-08-28T14:20:00+09:00
project: `comus93/portfolio-optimizer-kr`

## 1. 이 문서의 목적

다음 Codex/Agent 대화창에서 현재 프로젝트의 구현 맥락을 바로 이어가기 위한 인수인계 문서다.

다음 페이즈의 핵심은 기존 optimizer 엔진을 다시 만드는 것이 아니라, 그 앞뒤에 **사용자 ↔ GPT 기반의 실험 선택/생성/배치 실행/결과 해석/연구기억 저장 레이어**를 추가하는 것이다.

새 Agent는 처음부터 optimizer 구조를 다시 설계하지 말고, 현재 v1 엔진을 실행 백엔드로 간주한다.

---

## 2. 현재 엔진 상태

현재 v1에서 제품 진행에 필요한 주요 기능은 사실상 닫힌 상태다.

주요 objective:

- Maximum Sharpe Ratio
- Maximum Return subject to Target Annual Volatility

공통 실행 흐름:

```text
YAML
  ↓
Optimizer Engine
  ↓
result.json
review/*.csv
raw/*.csv
```

현재 실행 인터페이스 방향:

```text
CLI       → YAML → existing runner
Streamlit → YAML → existing runner
GPT       → YAML → existing runner
```

중요 원칙:

> GPT 전용 계산 API나 UI 전용 별도 계산 규칙을 만들지 않는다.
> 모든 front-end는 동일한 YAML contract와 existing runner로 수렴한다.

현재 run output 기본 구조:

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ review/*.csv
├─ raw/*.csv
└─ optional parity diagnostics
```

`review/`는 사용자/GPT 해석용 가독성 레이어이고, `raw/`는 full precision 계산 결과를 보존한다.

Max Sharpe 및 Target Volatility는 PV Golden을 이용한 offline/live 검증까지 수행했다.

Target Volatility parity artifact를 조금 더 풍부하게 남기는 후속 polish 요청이 있었지만, 이는 **다음 페이즈의 blocker가 아니다**.

---

## 3. 다음 페이즈의 사용자 요구

사용자는 YAML 파일명을 직접 찾아 선택하고 싶어 하지 않는다.

GPT가 실험의 의미와 이력을 이해하고 사용자가 자연어로 선택하도록 중개해야 한다.

예시:

```text
User: 예전에 하던 금 비중 실험 이어서 하자.

GPT:
1. 8/28 GLD cap sensitivity
   - 당시 무엇을 실험했는지
   - 어떤 run이 있었는지
   - 사용자와 GPT가 어떤 결론을 냈는지
   - follow-up이 무엇이었는지

2. QQQ / target-vol study
   - 당시 실험 및 해석
   - 남은 후속 실험

User: 1번

GPT:
- 관련 experiment 또는 batch 선택
- 실행 pointer 갱신
- 사용자는 YAML 파일명을 몰라도 됨
```

즉 **실험 discovery와 selection도 GPT의 책임**이다.

---

## 4. 목표 연구 루프

최종적으로 아래 루프를 지원하는 것이 목표다.

```text
사용자 ↔ GPT
        ↓
실험 아이디어 / 가설
        ↓
Experiment YAML 생성
        ↓
필요 시 여러 Experiment를 Batch로 구성
        ↓
GPT가 실행 대상을 선택
        ↓
Engine 실행
        ↓
Run output 저장
        ↓
GPT가 review/result 읽고 해석
        ↓
사용자와 결과 논의
        ↓
GPT 해석 + 사용자 판단 + 합의 결론 저장
        ↓
Follow-up Experiment / Batch
```

GitHub는 이 연구 흐름의 durable memory / handoff bus 역할을 한다.

---

## 5. 개념 객체

현재 논의된 핵심 객체는 다음과 같다.

### Study

여러 관련 실험을 묶는 연구 주제.

예:

```text
GLD allocation cap sensitivity
KODEX 운송 편입 연구
QQQ concentration study
```

### Experiment

실제로 실행 가능한 하나의 optimizer YAML.

### Batch

하나의 비교 질문을 위해 여러 Experiment를 묶은 실행 단위.

사용자는 **Batch experiment 지원에 명시적으로 동의했다.**

### Run

특정 Experiment가 실제로 실행된 1회 execution instance.

하나의 Experiment가 향후 최신 데이터로 다시 실행되어 여러 Run을 가질 수 있다.

### Interpretation / Report

단순 AI 요약이 아니다.

최소 다음 맥락을 보존하는 것이 목표다.

```text
계산 결과 사실
GPT 해석
사용자의 이해/반응/판단
합의된 결론
follow-up 질문 / 다음 실험
```

사용자가 나중에 원하는 UX는 다음과 같다.

> “어떤 실험이 있었고, 당시 사용자와 LLM이 결과를 어떻게 이해했고, 어떤 follow-up이 남았는지”

GPT가 GitHub만 보고 복원할 수 있어야 한다.

---

## 6. Experiment → Run → Interpretation 연결

이 linkage는 핵심 요건이다.

```text
Experiment
   ↓
Run
   ↓
Interpretation
   ↓
Follow-up
```

현재 `runs/<run_id>/input.yaml`이 exact input copy를 보존하므로 재현성 anchor로 이미 유용하다.

추가로 run metadata에 source experiment를 명시하는 방향이 논의됐다.

예시 후보:

```yaml
study_id: gld-cap-sensitivity
experiment: studies/gld-cap-sensitivity/experiments/004-gld-max30-r02.yaml
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

정확한 schema는 아직 확정하지 않았다.

새 대화에서 LLM/User가 최소 contract를 확정한 뒤 구현한다.

---

## 7. 실행 Pointer 아이디어

사용자가 semantic choice를 하면 GPT가 GitHub의 작은 control file을 수정하고, runtime은 그 파일만 보고 실행하는 방식이 논의됐다.

`.env`보다 Git에 추적되는 YAML이 적합하다고 판단했다.

후보:

```text
control/execute.yaml
```

single 예시:

```yaml
mode: single
study_id: korean-transport
experiment: studies/korean-transport/experiments/003-add-140710-r01.yaml
```

batch 예시:

```yaml
mode: batch
study_id: gld-cap-sensitivity
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

runtime command는 단순하게 유지할 수 있다.

```text
portfolio-optimizer execute
```

이 방식은 아직 design candidate이며 구현 contract는 아니다.

---

## 8. Batch 처리 방향

Batch는 단순 파일 리스트 이상의 최소 의미를 가져도 된다.

예:

```yaml
batch_id: round-02
question: >
  GLD 25~35% stable plateau 내부를 세분화하여
  적정 allocation range를 확인한다.
experiments:
  - ...27.5...
  - ...30.0...
  - ...32.5...
```

다만 schema를 과도하게 키우지 않는다.

새 대화에서 결정할 핵심 질문:

- engine이 batch comparison까지 어느 정도 자동 집계할 것인가
- GPT가 개별 run output을 읽어 comparison을 만들 것인가
- 둘 사이의 최소 practical boundary는 무엇인가

초기 버전은 작고 명확해야 한다.

---

## 9. Revision 원칙

Experiment YAML 수정 이력은 무거운 versioning system을 만들지 않는다.

초기에는 파일명 정도면 충분하다.

```text
004-gld-max30-r01.yaml
004-gld-max30-r02.yaml
```

Git 자체가 history를 제공한다.

중요한 사용자 결정:

> Report/Interpretation은 immutable 강제하지 않는다.

즉 필요하면 수정/보완/덮어쓰기/새 파일 추가 모두 가능하다.

연구 메모 관리 때문에 별도의 bureaucratic workflow를 만들지 않는다.

---

## 10. 후보 repo 구조

아래는 논의된 방향일 뿐 final spec은 아니다.

```text
studies/
└─ <study-id>/
   ├─ study.md
   ├─ index.yaml
   ├─ experiments/
   │  ├─ 001-base-r01.yaml
   │  ├─ 002-...yaml
   │  └─ ...
   ├─ batches/
   │  ├─ round-01.yaml
   │  └─ ...
   └─ reports/
      └─ ...

control/
└─ execute.yaml

runs/
└─ <run_id>/
   ├─ input.yaml
   ├─ result.json
   ├─ review/
   └─ raw/
```

새 대화에서 더 단순하고 robust한 구조가 나오면 바꿔도 된다.

---

## 11. Navigation / Recall 요구

GPT가 매번 repository의 모든 raw CSV를 뒤져야 하는 구조는 피한다.

향후 다음 질의가 가능해야 한다.

```text
User: 운송 관련 실험 다시 보자.

GPT:
- 관련 Study 탐색
- 수행된 Experiment 요약
- linked Run 확인
- 이전 사용자/GPT 해석 복원
- 남은 follow-up 제시
- 사용자가 선택하면 해당 Experiment/Batch 선택
```

그래서 `study.md`, `index.yaml` 같은 lightweight navigation layer가 유용할 수 있다.

하지만 다음과 같은 무거운 상태 machine은 당장 만들지 않는다.

```text
draft → ready → executed → reviewed
```

실제 필요가 생길 때 추가한다.

---

## 12. Agent가 다음 페이즈에서 맡을 역할

새 Agent는 LLM/User가 contract를 확정한 뒤 다음을 담당한다.

- repo/version/dependency에 맞는 실제 구현
- YAML / Batch / Execute pointer loader 구현
- CLI 실행 경로 연결
- Experiment ↔ Run metadata 연결
- 필요한 index/report persistence helper 구현
- Streamlit/CLI가 같은 contract를 쓰도록 유지
- 테스트 실행 및 regression 확인
- path/serialization edge case hardening

반대로 Agent가 임의로 확정하면 안 되는 것:

- Study/Batch/Report의 product semantics
- 사용자와 GPT의 interaction UX
- 어떤 metadata가 canonical source of truth인지
- report의 인간/AI 해석 형식
- 과도한 workflow/status system 추가

이 부분은 먼저 LLM/User가 논의해 정한다.

---

## 13. 개발 역할 분담 원칙

현재 프로젝트에서 이미 합의된 패턴:

```text
LLM/User
  ↓
요건 정의
금융/제품 의미 정의
테스트 contract / 최소 skeleton
  ↓
Agent
  ↓
실제 구현
의존성/경로/CLI/UI hardening
테스트 실행
디버깅
회귀 검증
```

Agent는 LLM이 만든 contract test를 단순히 통과시키기 위해 의미를 약화/삭제하지 않는다.

개발 중 affected tests를 빠르게 돌리는 것은 가능하지만, 완료 전에는 **전체 regression suite를 다시 실행**한다.

---

## 14. 다음 대화에서 먼저 확정해야 할 것

구현 전 최소한 아래 contract를 확정한다.

```text
Study
Experiment
Batch
Run linkage metadata
Interpretation/Report linkage
Execution pointer
Navigation/index
```

가장 먼저 end-to-end로 검토할 대표 scenario:

```text
1. 사용자와 GPT가 포트폴리오 가설 논의
2. GPT가 관련 Experiment YAML 3개 생성
3. GPT가 이를 Batch로 묶음
4. 나중에 사용자가 “그 실험 이어가자”라고 함
5. GPT가 Study/이전 결론/follow-up을 찾아 요약
6. 사용자가 1번 선택
7. GPT가 실행 pointer 변경
8. Engine이 Batch 실행
9. GPT가 review output 읽고 비교
10. 사용자와 해석 논의
11. 결론 + 사용자 판단 + follow-up을 GitHub에 저장
12. 다음 GPT/Agent session이 이 체인을 다시 복원
```

이 scenario가 깔끔하게 되면 첫 버전 metadata 설계는 충분할 가능성이 높다.

---

## 15. 현재 비차단 pending 사항

Target Volatility Golden parity artifact를 향후 debugging용으로 조금 더 풍부하게 만드는 LLM→Agent 요청이 남아 있을 수 있다.

이 작업은 validation polish이며, 새로운 interaction layer 설계/개발의 blocker가 아니다.

새 Agent는 새로운 대화에서 사용자가 다음 페이즈를 우선하면 그 흐름을 따라간다.

---

## 16. 새 Agent 대화 시작 시 권장 행동

1. 이 파일을 먼저 읽는다.
2. `ai-share/llm-to-llm.md`도 함께 읽어 product/interaction 맥락을 확인한다.
3. 현재 `AGENTS.md`, `specification.md` 및 관련 최신 docs를 다시 읽는다.
4. 사용자/LLM이 다음 페이즈 contract를 확정하기 전에는 큰 구현을 선행하지 않는다.
5. 구현 요청이 오면 existing YAML runner와 run writer를 재사용하고 별도 parallel execution semantics를 만들지 않는다.

핵심은 **기존 optimizer를 재작성하는 것이 아니라, 그 위에 실험 연구 workflow를 얹는 것**이다.
