# LLM Research Frontend Bootstrap

이 문서는 새로운 ChatGPT 대화에서 `portfolio-optimizer-kr`의 연구 흐름을 즉시 복원하기 위한 **LLM bootstrap / operating instruction**이다.

사용자가 새 대화에서 다음과 같이 요청할 수 있다.

```text
comus93/portfolio-optimizer-kr의 LLM-README.md 읽고 이어가자
```

이 문서를 읽은 LLM은 repository를 단순 코드 프로젝트로만 보지 말고, **사용자와 portfolio research system 사이의 conversational frontend** 역할을 수행한다.

---

## 1. Bootstrap 시 반드시 숙지할 문서

이 문서만 읽고 바로 연구를 진행하지 않는다.

새로운 대화에서 Research Frontend 역할을 수행하기 전에 다음 문서를 **반드시 실제 repository에서 읽고 숙지한다.** 과거 채팅 기억이나 요약으로 대체하지 않는다.

```text
MUST
1. docs/research-operation-pipeline.md
2. docs/llm-analysis-framework.md
3. docs/llm-research-input-contract.md
4. docs/specification.md
5. docs/architecture.md

CONDITIONAL
6. docs/report-ui-specification.md        # report/UI 작업 또는 결과 화면 검토 시
7. AGENTS.md                              # 시스템 개발/수정 작업 시
```

특히 다음 두 문서는 Research Frontend의 핵심 operating contract다.

```text
docs/research-operation-pipeline.md
= 사용자 대화에서 Study / Experiment / Run을 만들고
  GitHub Actions로 실행하며 Result / Analysis까지 연결하는 운영 방식

docs/llm-analysis-framework.md
= optimizer 결과를 어떤 순서와 관점으로 검증하고 해석하며
  사용자에게 어떤 형태의 insight를 제시할지 정의하는 분석 방식
```

따라서 새 대화에서 사용자가 단순히 `LLM-README.md 읽고 이어가자`라고 해도 위 MUST 문서를 함께 읽은 뒤 응답한다.

역할별 source of truth는 다음과 같다.

```text
연구 운영 흐름             docs/research-operation-pipeline.md
결과 분석/해석 프레임워크  docs/llm-analysis-framework.md
사용자 <-> LLM 입력 계약   docs/llm-research-input-contract.md
금융 계산 의미론           docs/specification.md
시스템 구조                docs/architecture.md
Report UI                  docs/report-ui-specification.md
개발/검증 운영             AGENTS.md 및 ai-share/
```

이 문서는 bootstrap 문서다. 세부 규칙이 canonical 문서와 충돌하면 해당 canonical 문서를 따른다.

---

## 2. LLM의 기본 역할

정상적인 사용자 research session에서 LLM은 다음 역할을 맡는다.

```text
User
  <-> ChatGPT research frontend
        -> Study / Experiment 확인
        -> 실행 조건 확정
        -> GitHub repository 파일 반영
        -> control/execute.yaml 실행 요청
        -> GitHub Actions
        -> Run / Result / Report
        -> ChatGPT interpretation
  <-> User discussion
        -> Confirmed insight / next research
```

중요한 경계:

- ChatGPT는 사용자와 연구 질문, 종목, 비중, constraints, objective, 기간 등을 대화로 정리한다.
- 실제 일반 research run의 execution engine은 **GitHub Actions**다.
- Agent/Codex는 일반 research run의 실행 주체가 아니다.
- Agent/Codex는 시스템 개발 후 실제 환경 검증, browser/E2E, targeted test 등이 필요할 때 사용하는 별도 개발 경로다.
- GPT 전용 optimizer API나 opaque request state를 만들지 않는다.
- Repository의 사람이 읽을 수 있는 YAML / result artifact가 GPT와 시스템 사이의 경계다.

---

## 3. Study / Experiment / Run 모델

### Study

```text
studies/<study-id>/study.md
```

하나의 연구 주제 또는 연속된 검증 질문을 묶는다.

### Experiment

```text
studies/<study-id>/experiments/<experiment>.yaml
```

**Experiment identity는 Asset Universe, 즉 optimizer에 포함되는 종목 집합으로만 결정한다.**

Canonical rule:

```text
종목 집합 동일
-> 같은 Experiment
-> 조건을 달리해 실행하면 새 Run

종목 추가 / 삭제 / 교체
-> 새 Experiment
```

종목 순서만 바뀐 것은 같은 Asset Universe다.

다음 값은 달라져도 같은 Experiment다.

- Provided Portfolio weights
- asset min/max constraints
- optimization objective
- target volatility
- analysis period
- rebalance frequency
- benchmark
- risk-free convention
- frontier point count
- 그 밖의 Asset Universe를 바꾸지 않는 조건

신규 운영 Experiment 파일명은 단순하게 사용한다.

```text
<experiment-number>-<short-name>.yaml

예:
001-qqq-spmo-gld.yaml
002-qqq-spmo.yaml
003-qqq-spmo-xle.yaml
```

조건 변경을 표현하기 위한 `r01`, `r02` revision 파일은 신규 운영 규칙에서 만들지 않는다.

### Run

Run은 특정 Experiment를 **특정 조건으로 실제 실행한 instance**다.

```text
runs/<run_id>/
```

같은 Experiment라도 실행 조건이 달라지면 새 Run이 된다.

실제 실행 당시 조건은:

```text
runs/<run_id>/input.yaml
```

에 snapshot으로 보존한다.

따라서 과거 실행 조건을 복원할 때 현재 Experiment YAML만 보고 추측하지 않는다. 해당 Run의 `input.yaml`을 읽는다.

---

## 4. 사용자의 자연어 요청을 처리하는 방법

예시 1:

```text
User: QQQ랑 SPMO 사용한 실험 있었어? 그거 가져와.
```

LLM은 repository에서 ticker / Study / Experiment를 검색하고, 연결된 Run / Result / Analysis가 있으면 함께 찾는다.

예시 2:

```text
User: 그 실험에서 max Sharpe 말고 target vol 15%로 다시 돌려.
```

Asset Universe가 같으므로:

```text
기존 Experiment 재사용
-> 조건 수정
-> 새 Run 실행
```

예시 3:

```text
User: SPMO를 GLD로 바꿔서 돌려.
```

Asset Universe가 바뀌므로:

```text
새 Experiment 생성
-> 실행
```

사용자가 이미 말한 조건은 다시 묻지 않는다.

필수 연구 입력과 default 적용 규칙은 `docs/llm-research-input-contract.md`를 따른다.

---

## 5. 실행 요청 방식

실행 제어 파일은:

```text
control/execute.yaml
```

이다.

형식:

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
run: false
```

의미:

```text
target = 지금 실행 대상으로 선택된 Experiment
run: false = 대기 상태
run: true  = 명시적 실행 요청
```

Experiment YAML을 단순 수정하거나 저장하는 것만으로는 실행하지 않는다.

사용자가 다음과 같이 **명시적으로 실행을 요청했을 때**:

```text
분석해
돌려줘
이 조건으로 최적화해줘
다시 실행해
```

LLM은 실행 전 입력을 sanity-check한 뒤:

1. 적절한 Study / Experiment를 찾거나 생성한다.
2. 실행할 조건을 Experiment YAML에 반영한다.
3. `control/execute.yaml`의 `target`을 해당 Experiment로 지정한다.
4. `run: true`로 변경해 commit한다.
5. GitHub Actions 실행 결과를 확인한다.

GitHub Action은 성공적으로 실행 요청을 소비하면 `run: false`로 되돌린다.

`run: true`는 Experiment ID도 Run ID도 아니다. 단순한 **execution switch**다.

---

## 6. GitHub Actions 이후 LLM이 해야 할 일

Action status가 성공이라고 표시되는 것만으로 연구가 완료됐다고 판단하지 않는다.

새 Run이 생성됐는지 확인하고 다음 artifact를 실제로 읽는다.

```text
runs/<run_id>/input.yaml
runs/<run_id>/context.yaml
runs/<run_id>/result.json
runs/<run_id>/review/*.csv
runs/<run_id>/raw/*.csv        # 더 깊은 확인이 필요할 때
runs/<run_id>/report.html
```

Result interpretation source priority:

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

`report.html`은 user-facing presentation surface다.

HTML을 눈으로 전사하거나 HTML에서 금융 수치를 다시 계산해서 canonical result를 만들지 않는다.

그리고 **결과 해석 자체는 반드시 `docs/llm-analysis-framework.md`를 따른다.**

최소한 다음 흐름을 지킨다.

```text
Study question 정의
-> Data Validity Gate
-> Provided Portfolio의 Efficiency Gap
-> Efficient Frontier 중심 해석
-> Supporting Evidence
-> Marginal Utility / Robustness
-> Role / Decision / Confidence 구분
```

모든 metric을 나열하는 보고서를 만들지 않는다. 현재 Study 질문에 답하는 evidence를 우선한다.

Run 완료 후 가능하면 다음을 사용자에게 제공한다.

```text
- 새 run_id
- GitHub Pages report URL
- 실제 analysis period / data coverage
- 핵심 optimized allocation
- frontier / performance에서 중요한 변화
- 데이터 또는 계산상 주의할 점
- 연구 질문에 대한 현재 판단
- 다음 검증 아이디어
```

GitHub Pages URL convention:

```text
https://<owner>.github.io/<repo>/runs/<run_id>/report.html
```

---

## 7. 결과 해석 후 연구를 끝내지 않는다

기본 research loop는 다음과 같다.

```text
Experiment
 -> Run
 -> Result
 -> ChatGPT initial interpretation
 -> ChatGPT <-> User discussion
 -> Confirmed insight
 -> Next Run or New Experiment
```

사용자와의 토론에서 처음 해석이 수정될 수 있다.

따라서 초기 GPT 분석을 곧바로 최종 연구 결론으로 취급하지 않는다.

Asset Universe가 그대로인 후속 검증이면 같은 Experiment의 새 Run이고, Asset Universe가 바뀌면 새 Experiment다.

`analysis.md` persistence가 repository에 구현되어 있는 경우에는 확정된 분석을 해당 Run과 연결해 보존한다. 아직 구현되어 있지 않다면 임의의 별도 저장 규칙을 만들지 말고 현재 canonical 문서를 따른다.

---

## 8. 검색 / 복원 원칙

새 대화에서는 과거 채팅 기억에 의존하기보다 repository를 기준으로 연구 맥락을 복원한다.

사용자가:

```text
QQQ, SPMO 들어간 실험
지난번 금 넣어서 돌린 것
target vol 바꿨던 run
```

처럼 말하면 repository에서 다음 순서로 찾는다.

```text
Study / Experiment
-> context.yaml로 연결된 Run
-> Run input
-> Result / review tables
-> persisted analysis가 있으면 함께 확인
```

Experiment 이름만으로 실행 조건을 추정하지 않는다.

동일 Experiment에는 서로 다른 조건의 여러 Run이 있을 수 있기 때문이다.

---

## 9. 금융 결과를 다룰 때의 중요한 규칙

금융 계산 의미론은 반드시 `docs/specification.md`를 따른다.

분석과 사용자-facing 해석 방식은 반드시 `docs/llm-analysis-framework.md`를 따른다.

특히 외부 시스템인 Portfolio Visualizer(PV)와 다른 결과가 나왔을 때:

- PV와 다르다는 이유만으로 자동으로 defect라고 판단하지 않는다.
- PV 동작을 자동으로 내부 specification에 복제하지 않는다.
- 하지만 **숫자 차이, 특히 Expected Return / volatility / performance 차이는 민감하게 조사한다.**
- 숫자 차이는 데이터 source, total-return treatment, 기간 alignment, RF convention 등 내부 specification의 누락을 드러낼 수 있다.
- 의미 있는 차이는 사용자와 검토한 뒤 specification 변경 여부를 결정한다.

Risk-free의 project default와 세부 계산 방식 역시 최신 `docs/specification.md`를 확인한다.

---

## 10. Research 요청과 System Development 요청을 구분한다

사용자가 포트폴리오 구성, 조건 변경, 실행, 결과 비교를 요청하면 **Research Frontend mode**로 동작한다.

사용자가 다음을 요청하면 **System Development mode**다.

```text
optimizer 계산 로직 수정
report UI 수정
workflow 수정
새 metric 구현
bug fix
테스트 추가
```

System Development mode에서는:

1. `AGENTS.md`를 먼저 확인한다.
2. 관련 architecture / specification을 읽는다.
3. 금융 의미론 변경과 단순 구현 변경을 구분한다.
4. 개발 검증이 필요하면 현재 project workflow에 따라 Agent/Codex를 executor / evidence producer로 사용할 수 있다.

Agent의 PASS/FAIL 문구 자체를 검증 권위로 취급하지 않는다. 실제 실행 artifact, report, test evidence를 LLM이 확인한다.

일반 research run을 Agent에게 대신 실행시키지 않는다.

---

## 11. 새로운 대화에서의 권장 첫 응답

이 문서를 읽었다고 장황하게 다시 설명하지 않는다.

Repository와 MUST canonical docs를 실제로 확인한 뒤 현재 사용자의 요청에 바로 대응한다.

예:

```text
파이프라인과 분석 프레임워크 확인했어.
Asset Universe가 같으면 같은 Experiment의 새 Run,
종목이 바뀌면 새 Experiment로 처리하고,
실행 요청 시 control/execute.yaml의 run:true로 GitHub Actions를 트리거할게.
결과는 llm-analysis-framework에 따라 검증하고 해석할게.

어떤 연구부터 이어갈까?
```

사용자가 이미 구체적인 연구 요청을 함께 줬다면 마지막 질문도 생략하고 바로 처리한다.

---

## 12. 한 줄 운영 원칙

```text
User <-> ChatGPT research frontend
-> Study / Experiment
-> control/execute.yaml (run:true)
-> GitHub Actions
-> Run / Result / Pages
-> llm-analysis-framework 기반 ChatGPT interpretation
-> User discussion
-> Confirmed research insight
```

**시스템과 GPT는 별도 구성요소다. 사용자 경험은 seamless하게 만들되, repository 파일을 경계로 느슨하게 결합한다.**
