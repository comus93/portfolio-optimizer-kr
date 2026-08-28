# 세션 핸드오버 — GPT/사용자 실험 인터랙션 레이어

state: ready
created_at: 2026-08-28T14:17:00+09:00
project: `comus93/portfolio-optimizer-kr`

## 1. 이 핸드오버의 목적

다음 대화에서는 기존 optimizer v1 위에 추가할 **사용자-GPT 실험 인터랙션 레이어**를 설계한다.

목표 흐름은 다음과 같다.

> **사용자 ↔ GPT 대화 → 실험 선택/설계 → YAML 생성·관리 → 엔진 실행(배치 포함) → run 결과 저장 → GPT가 결과를 해석하고 사용자와 논의 → 해석/결론을 GitHub에 저장하고 원래 실험/run과 연결 → 후속 실험으로 이어짐**

이 주제는 별도의 새 ChatGPT 대화에서 이어간다.

기본 optimizer 설계부터 다시 시작하지 않는다. 기존 optimizer engine은 이미 존재하는 실행 backend로 본다.

---

## 2. 현재 시스템 기준선

현재 실행 경로는 개념상/부분 구현 상태로 다음과 같다.

```text
1) YAML → Optimizer Engine → result/review/raw CSV/JSON

2) Streamlit → YAML → Optimizer Engine → result/review/raw
                                      → 이후 viewer/charts
```

이미 합의한 핵심 architecture boundary:

```text
Streamlit → YAML → existing runner
CLI       → YAML → existing runner
GPT       → YAML → existing runner
```

GPT 전용 financial API나 UI 전용 실행 의미론을 따로 만들지 않는다.

**YAML contract가 공통 실행 계약이다.**

현재 v1 optimization objective는 제품 진행 관점에서 사실상 완료 상태다.

- Maximum Sharpe Ratio
- Maximum Return subject to Target Annual Volatility

둘 다 PV golden/offline/live 검증을 수행했다. Target Vol parity diagnostic artifact에 약간의 보강 작업이 남을 수 있으나 **다음 페이즈의 blocker는 아니다.**

현재 run output 구조:

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ review/*.csv
├─ raw/*.csv
└─ golden validation용 optional parity diagnostics
```

`review/`는 사람/GPT가 읽기 쉬운 percentage-oriented output이고, `raw/`는 계산 full precision을 보존한다.

---

## 3. 새로 원하는 사용자 인터랙션 모델

사용자는 YAML 파일 목록을 직접 보고 파일명을 선택하고 싶어하지 않는다.

**GPT가 의미 기반 연구 front-end가 되어야 한다.**

예시:

```text
사용자: 예전에 하던 실험 이어서 하자.

GPT가 GitHub 연구 상태를 읽고 대략 다음처럼 제시:

1. 8/28 GLD cap sensitivity
   - 어떤 실험을 했는지
   - 당시 사용자 + GPT가 어떤 결론을 냈는지
   - 어떤 follow-up을 남겼는지

2. QQQ / target-volatility study
   - 어떤 실험을 했는지
   - 당시 해석
   - 다음 후보 작업

사용자: 1번

GPT:
- 해당 experiment 또는 follow-up batch를 선택
- GitHub의 실행 pointer를 갱신
- 사용자는 YAML 파일명을 몰라도 엔진이 선택된 실험을 실행할 수 있음
```

즉 **실험 탐색과 선택도 GPT의 책임**이다.

사용자는 repository path가 아니라 실험의 의미와 과거 맥락을 기준으로 선택한다.

---

## 4. GitHub의 역할

GitHub는 다음 사이의 지속 가능한 연구 기억/상태 bridge로 사용한다.

```text
User ↔ GPT ↔ GitHub ↔ Optimizer
                ↑         ↓
                └─ results / interpretation
```

GitHub가 계산 runtime 자체일 필요는 없다.

실제 계산 실행은 기존 runner/runtime 환경에서 수행한다.

GitHub에는 연구 문맥을 복원할 수 있는 지속 artifact를 저장한다.

예상 역할:

```text
Specification / code
Experiment definitions
Batch definitions
Execution selection pointer
Run outputs
GPT + 사용자 해석 / 결론
Experiment → Run → Interpretation → Follow-up 연결
```

---

## 5. 지금까지 논의한 핵심 연구 객체

개념 모델:

```text
Study
  │
  ├─ Experiment YAML
  │      │
  │      ▼
  │     Run
  │      │
  │      ▼
  └── Interpretation / Report
          │
          ▼
      Follow-up Experiment or Batch
```

### Study
관련 실험 여러 개를 묶는 연구 주제/질문.

예:

```text
GLD allocation cap sensitivity
KODEX 운송 편입 연구
QQQ concentration study
```

### Experiment
재현 가능하게 실행할 수 있는 구체적인 optimizer YAML.

### Batch
하나의 비교 질문을 검증하기 위해 함께 실행하는 여러 experiment의 묶음.

사용자는 **batch experiment 지원에 명시적으로 동의**했다.

### Run
실제로 한 번 수행된 실행 instance와 그 결과물.

하나의 experiment가 시간에 따라 여러 run을 가질 수 있다.

### Interpretation / Report
단순 AI summary보다 넓은 개념으로 본다.

다음을 함께 담는다.

```text
계산 결과의 사실
GPT 해석
사용자의 이해 / 반응 / 판단
합의된 결론
follow-up 질문 또는 다음 실험
```

이게 중요한 이유는 나중에 GPT가 단순히:

> 이런 run이 있었다

라고 말하는 수준이 아니라,

> 그 당시 사용자와 LLM은 이 결과를 이렇게 해석했고, 이런 follow-up을 남겼다

까지 복원해야 하기 때문이다.

---

## 6. Experiment ↔ Run ↔ Interpretation 연결은 필수

사용자가 명시적으로 원하는 연결:

```text
experiment set
   ↓
run
   ↓
interpretation
```

이 연결은 future GPT recall/navigation에 사용된다.

Run에는 어떤 exact experiment/revision으로 생성됐는지 식별 가능한 source metadata가 있어야 한다.

현재 `runs/<run_id>/input.yaml` 복사본이 이미 좋은 reproducibility anchor다.

추가로 lightweight metadata를 둘 수 있다.

예:

```yaml
study_id: gld-cap-sensitivity
experiment: studies/gld-cap-sensitivity/experiments/004-gld-max30-r02.yaml
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

정확한 schema는 **아직 확정하지 않았다.** 새 대화에서 논의한다.

---

## 7. 실행 pointer 아이디어

이전 대화에서, 사용자가 의미 기반으로 실험을 선택하면 GPT가 GitHub의 작은 control file 하나를 변경하는 방식을 제안했다.

`.env`보다는 tracked YAML pointer가 더 적합하다는 방향이었다.

이유:
- `.env`는 secrets/local environment 의미가 강함
- 보통 gitignore 대상
- batch나 metadata 표현에도 부적합

후보:

```text
control/execute.yaml
```

단일 실행 예:

```yaml
mode: single
study_id: korean-transport
experiment: studies/korean-transport/experiments/003-add-140710-r01.yaml
```

Batch 실행 예:

```yaml
mode: batch
study_id: gld-cap-sensitivity
batch: studies/gld-cap-sensitivity/batches/round-02.yaml
```

그러면 runtime command는 단순하게:

```text
portfolio-optimizer execute
```

만 실행하고 pointer를 읽는다.

이건 아직 **설계 아이디어이지 구현 contract는 아니다.**

새 대화에서 이 구조를 검토/수정한 뒤 구현한다.

---

## 8. Batch experiment 방향

사용자는 batch experiment에 명시적으로 찬성했다.

원하는 흐름:

```text
GPT/사용자 논의
   ↓
GPT가 여러 YAML 실험 설계
   ↓
하나의 연구 질문 아래 batch로 묶음
   ↓
engine이 선택된/전체 batch member 실행
   ↓
비교 결과
   ↓
GPT가 batch를 함께 해석
```

개념 예:

```yaml
batch_id: round-02
question: >
  GLD 25~35% stable plateau 내부를 세분화해 적정 allocation range를 확인한다.
experiments:
  - ...27.5...
  - ...30.0...
  - ...32.5...
```

이 exact schema는 아직 확정하지 않았다.

새 대화에서 중요한 설계 질문 중 하나:

> 비교 aggregation을 engine이 얼마나 만들어야 하고, GPT가 기존 run output을 읽어 얼마나 비교해야 하는가?

초기 버전은 작고 실용적으로 유지한다.

---

## 9. Revision 관리 철학

사용자는 무거운 versioning subsystem을 원하지 않는다.

Experiment YAML revision은 파일명으로 구분하는 정도면 충분하다.

예:

```text
004-gld-max30-r01.yaml
004-gld-max30-r02.yaml
```

실제 필요가 생기기 전에는 semantic version DB 같은 복잡한 시스템을 만들지 않는다.

Git 자체가 이미 history를 제공한다.

이전 대화에서 사용자 수정사항:

> **Interpretation/Report 파일을 immutable로 강제하거나, 수정할 때마다 새 report 파일을 만들도록 강제하지 않는다.**

이런 경직된 규칙은 사용자가 원하지 않는다.

Report/Interpretation은 실전적으로 필요에 따라:

```text
수정
보강
교체
추가
```

가능하게 둔다.

Traceability는 유지하되 연구 기록을 관료적인 절차로 만들지 않는다.

---

## 10. 논의된 repository 구조 후보

아직 확정 아님:

```text
studies/
└─ <study-id>/
   ├─ study.md                 # optional human/GPT context
   ├─ index.yaml               # optional navigation index
   ├─ experiments/
   │  ├─ 001-base-r01.yaml
   │  ├─ 002-...yaml
   │  └─ ...
   ├─ batches/
   │  ├─ round-01.yaml
   │  └─ ...
   └─ reports/                 # GPT + 사용자 해석/history
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

이 구조를 final architecture로 간주하지 않는다.

새 대화에서 더 단순하고 실용적인 구조가 나오면 변경한다.

---

## 11. GPT recall/navigation 요구사항

Repository 구조는 나중에 이런 대화를 가능하게 해야 한다.

```text
사용자: 운송 관련 실험 다시 보자.

GPT:
- 관련 study 탐색
- 수행한 experiment 요약
- linked run 확인
- 당시 GPT/사용자 해석 복원
- 남아 있던 follow-up 설명
- 어떤 줄기를 이어갈지 사용자에게 제시

사용자: 1번

GPT:
- 해당 follow-up YAML 또는 batch를 선택/생성
- 실행 선택 pointer 갱신
```

GPT가 매번 repository의 모든 raw CSV를 전부 훑어야 하는 구조는 피한다.

따라서 lightweight navigation/index 전략은 가치가 있을 수 있다.

다만 `draft → ready → executed → reviewed` 같은 복잡한 state machine을 미리 만들지는 않는다.

이전 선호는 **mutable execution status를 experiment YAML 자체에 넣지 않는 방향**이었다.

---

## 12. 세 가지 front-end, 하나의 backend

최종적으로 세 가지 사용자 surface가 공존한다.

| Interface | 주 용도 |
|---|---|
| YAML / CLI | 개발자·Agent의 정밀 실행 |
| Streamlit | GUI 검색/선택/설정/실행/조회 |
| ChatGPT ↔ GitHub | 자연어 실험 설계, 기억, 선택, 비교, 해석 |

셋 다 최종적으로 같은 YAML/run contract로 수렴해야 한다.

개념적으로:

```text
             ChatGPT
                │
Streamlit ──── YAML ──── CLI
                │
                ▼
             Engine
                │
                ▼
              Runs
```

---

## 13. 유지해야 할 설계 원칙

1. **형식보다 실전성 우선**
   - 연구관리 framework를 과도하게 만들지 않는다.

2. **GPT가 의미 기반 실험 선택을 담당**
   - 사용자가 YAML 파일명/path를 기억할 필요가 없어야 한다.

3. **재현 가능한 실행은 YAML 기반 유지**
   - GPT 대화 자체가 계산 source of truth가 되어서는 안 된다.

4. **Run은 계산된 사실**
   - GPT/사용자 해석과 계산 결과는 구분 가능해야 한다.

5. **Interpretation은 지속 가능한 연구 기억**
   - metric뿐 아니라 당시 사용자와 GPT가 내린 결론도 저장한다.

6. **Batch는 실용적으로 중요한 first-class 개념이지만 v1은 작게**

7. **Report는 수정 가능하고 유연하게**
   - 불필요한 immutability rule 금지.

8. **Experiment revision은 초기에는 파일명 수준이면 충분**

9. **GitHub가 durable bridge**
   - 새 GPT 대화에서도 study, run, 결론, next step을 복원할 수 있어야 한다.

10. **완료된 optimizer-engine 문제를 다시 열지 않는다**
   - 새 interaction layer 구현 중 실제 gap이 발견될 때만 재검토한다.

---

## 14. 새 대화에서 가장 먼저 논의할 것

Codex/Agent 구현 요청 전에 최소 contract부터 정한다.

```text
Study
Experiment
Batch
Run linkage metadata
Interpretation/Report linkage
Execution pointer
Navigation/index
```

가장 중요한 end-to-end 시나리오를 먼저 설계한다.

```text
1. 사용자와 GPT가 portfolio hypothesis를 논의한다.
2. GPT가 관련 experiment YAML 3개와 batch 1개를 만든다.
3. 나중에 사용자가 “그 실험 이어가자”고 말한다.
4. GPT가 study를 찾아 과거 실험/결론을 요약한다.
5. 사용자가 대화로 “1번”을 선택한다.
6. GPT가 execution pointer를 변경한다.
7. Engine이 batch를 실행한다.
8. GPT가 review output을 읽어 run들을 비교한다.
9. GPT와 사용자가 결과 의미를 논의한다.
10. 결론 + follow-up을 repository에 기록하고 study/run과 연결한다.
11. 이후 다른 GPT session에서도 사용자가 파일을 직접 전달하지 않고 이 전체 chain을 복원한다.
```

이 시나리오가 깔끔하게 동작하면 metadata model도 충분하다고 볼 수 있다.

---

## 15. 이 핸드오버 외의 현재 남은 작업

Target Volatility golden parity diagnostic artifact를 조금 더 풍부하게 만드는 non-blocking 후속 요청이 있다.

이건 validation polish이며, **다음 interaction-layer 설계의 blocker가 아니다.**

새 대화에서 이 작업 때문에 메인 다음 페이즈가 흐트러지지 않게 한다.

---

## 16. 이 페이즈에서의 사용자 작업 스타일

사용자는 LLM이 단순히 요청을 다시 말하는 역할이 아니라 **연구 PM/분석가** 역할을 하길 원한다.

기대 행동:

- 구체적인 다음 실험 구조를 제안
- 약한 설계에는 반론/수정 제안
- 단순하고 robust한 workflow 선호
- 설계 합의 후 repository artifact 직접 생성
- LLM이 contract/test를 먼저 정의하고 Codex Agent가 구현/hardening
- GPT ↔ Agent 사이의 수동 복사/붙여넣기 최소화

새 대화에서의 즉시 과제는 **구현보다 interaction contract 설계 논의**다.
