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

핵심 operating contract:

```text
docs/llm-research-input-contract.md
= 자연어 요청에서 Optimization / Backtest product intent를 확정하고
  product별 사용자 결정/default/YAML 입력을 만드는 규칙

docs/research-operation-pipeline.md
= Study / Experiment / Run을 만들고 GitHub Actions로 실행하는 운영 방식

docs/llm-analysis-framework.md
= explicit product_mode에 따라 Optimization / Backtest 결과를
  어떤 순서와 관점으로 해석할지 정의하는 단일 분석 framework
```

역할별 source of truth:

```text
연구 입력 / product intent      docs/llm-research-input-contract.md
연구 운영 흐름                  docs/research-operation-pipeline.md
결과 분석 / 해석                docs/llm-analysis-framework.md
금융 계산 의미론                docs/specification.md
시스템 구조                     docs/architecture.md
Report UI                       docs/report-ui-specification.md
개발 / 검증 운영                AGENTS.md 및 ai-share/
```

세부 규칙이 이 bootstrap 문서와 충돌하면 해당 canonical 문서를 따른다.

---

## 2. LLM의 기본 역할

정상적인 사용자 research session에서 LLM은 다음 역할을 맡는다.

```text
User
  <-> ChatGPT Research Frontend
        -> Product intent 확인
        -> Study / Experiment 확인
        -> 실행 조건 확정
        -> GitHub repository 파일 반영
        -> control/execute.yaml 실행 요청
        -> GitHub Actions
        -> Run / Result / Report
        -> product-aware ChatGPT interpretation
  <-> User discussion
        -> Confirmed insight / next research
```

중요한 경계:

- ChatGPT는 사용자와 연구 질문, product, 종목, 비중, constraints, objective, 기간 등을 대화로 정리한다.
- 실제 일반 research run의 execution engine은 **GitHub Actions**다.
- Agent/Codex는 일반 research run의 실행 주체가 아니다.
- Agent/Codex는 시스템 개발 후 실제 환경 검증, browser/E2E, targeted test 등이 필요할 때 사용하는 별도 개발 경로다.
- GPT 전용 optimizer/backtest API나 opaque request state를 만들지 않는다.
- Repository의 사람이 읽을 수 있는 YAML / result artifact가 GPT와 시스템 사이의 경계다.

---

## 3. Product Intent Gate

사용자의 실행 요청을 받았다고 바로 Experiment를 만들지 않는다.

먼저 `docs/llm-research-input-contract.md`에 따라 product intent를 확정한다.

```text
Optimization
= 주어진 Asset Universe에서 어떤 allocation이 더 효율적인가?

Backtest
= 이미 정의된 portfolio가 역사적으로 어떻게 행동했는가?
```

명확하면 바로 해당 product로 진행한다.

Optimization과 Backtest 둘 다 합리적으로 가능한 요청이면 **실행 전에 사용자에게 한 번 확인한다.** LLM이 직전 대화 주제나 비중 존재 여부만으로 하나를 임의 선택하지 않는다.

예:

```text
User: QQQ 30%, SPY 30%, GLD 30%, IEF 10%로 돌려보자.
```

이 요청만으로는 둘 다 가능하다.

```text
Backtest
= 이 비중 그대로 역사적 성과 확인

Optimization
= 이 비중을 Provided Portfolio로 두고 더 효율적인 allocation 탐색
```

따라서 어느 쪽인지 확인한 뒤 진행한다.

Product가 확정되면 Experiment YAML에 반드시 다음 둘 중 하나를 명시한다.

```yaml
product_mode: optimization
```

또는:

```yaml
product_mode: backtest
```

`product_mode` 생략 시 Optimization으로 간주하는 silent fallback은 사용하지 않는다.

---

## 4. Study / Experiment / Run 모델

### Study

```text
studies/<study-id>/study.md
```

하나의 연구 주제 또는 연속된 검증 질문을 묶는다.

### Experiment

```text
studies/<study-id>/experiments/<experiment>.yaml
```

Experiment identity의 핵심은 연구 대상 ticker set이다.

Optimization:

```text
optimizer Asset Universe 동일
-> 같은 Experiment

Asset Universe 추가 / 삭제 / 교체
-> 새 Experiment
```

Backtest:

```text
비교 portfolio 전체의 union ticker set 동일
-> 같은 Experiment

union ticker set 추가 / 삭제 / 교체
-> 새 Experiment
```

다음 조건이 바뀌어도 ticker set이 같으면 같은 Experiment의 새 Run으로 취급한다.

- Provided Portfolio weights 또는 Backtest portfolio weights/membership
- asset min/max constraints
- optimization objective / target volatility
- analysis/time period
- rebalancing
- benchmark
- risk-free convention
- Backtest initial balance / Calendar Aligned
- frontier point count

신규 운영 Experiment 파일명은 단순하게 사용한다.

```text
<experiment-number>-<short-name>.yaml
```

### Run

Run은 특정 Experiment를 **특정 조건으로 실제 실행한 instance**다.

```text
runs/<run_id>/
```

실제 실행 당시 조건은:

```text
runs/<run_id>/input.yaml
```

에 snapshot으로 보존한다.

과거 실행 조건을 복원할 때 현재 Experiment YAML만 보고 추측하지 않는다. 해당 Run의 `input.yaml`을 읽는다.

---

## 5. Product별 입력 경계

세부 규칙은 `docs/llm-research-input-contract.md`를 따른다.

### Optimization

대표 입력:

```text
product_mode: optimization
Asset Universe
Provided Portfolio if applicable
min/max bounds
Optimization objective
target volatility if applicable
analysis period/default
benchmark/default
rebalancing/default
risk-free/default
```

### Backtest

대표 입력:

```text
product_mode: backtest
Asset Universe
portfolio target weights
Time Period/default
initial balance/default
benchmark/default or explicit none
rebalancing/default
Calendar Aligned/default
risk-free/default
```

Backtest에서 optimizer objective/min-max/target-volatility를 요구하지 않는다.

사용자가 이미 말한 조건은 다시 묻지 않는다.

---

## 6. 실행 요청 방식

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

사용자가 `분석해`, `돌려줘`, `백테스트해줘`, `최적화해줘`, `다시 실행해`처럼 명시적으로 실행을 요청했고 필수 사용자 decision이 해소되면:

1. product intent를 확정한다.
2. 적절한 Study / Experiment를 찾거나 생성한다.
3. `product_mode`와 실행 조건을 Experiment YAML에 명시적으로 반영한다.
4. 입력을 sanity-check한다.
5. `control/execute.yaml`의 target을 해당 Experiment로 지정한다.
6. `run: true`로 변경해 commit한다.
7. GitHub Actions 실행 결과를 확인한다.

실행 의도를 이미 밝혔다면 `진행할까?` 같은 redundant approval을 다시 묻지 않는다.

Action은 성공한 요청을 consume하면 `run: false`로 되돌린다.

---

## 7. GitHub Actions 이후 LLM이 해야 할 일

Action status가 성공이라는 것만으로 연구가 완료됐다고 판단하지 않는다.

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

### Analysis routing

결과를 해석할 때 자연어 요청을 다시 보고 product를 추측하지 않는다.

`context.yaml` / `input.yaml`의 explicit `product_mode`를 기준으로 `docs/llm-analysis-framework.md`에서 branch를 선택한다.

```text
product_mode: optimization
-> Optimization Analysis Branch

product_mode: backtest
-> Backtest Analysis Branch
```

`product_mode`가 없으면 결과 내용을 보고 임의 선택하지 않는다. Run identity/input 문제로 취급한다.

Optimization은 Efficient Frontier / optimizer structure / allocation range를 해석한다.

Backtest는 historical realized comparison을 해석하며 기본 흐름은 다음과 같다.

```text
Effective Data Coverage
-> Return / Risk
-> Drawdown / Recovery
-> Annual / Rolling Consistency
-> Benchmark-relative Behavior
-> Correlation Structure
-> Contribution / Diversification Evidence
-> Evidence Limitation / Next Research
```

Backtest 결과만으로 optimal allocation을 주장하지 않는다.

---

## 8. 결과 해석 후 연구를 끝내지 않는다

기본 research loop:

```text
Experiment
 -> Run
 -> Result
 -> ChatGPT Initial Interpretation
 -> ChatGPT <-> User discussion
 -> Confirmed insight
 -> Next Run or New Experiment
```

사용자와의 토론에서 처음 해석이 수정될 수 있다.

초기 GPT 분석을 곧바로 최종 연구 결론으로 취급하지 않는다.

Ticker set이 그대로인 후속 검증이면 같은 Experiment의 새 Run이고, ticker set이 바뀌면 새 Experiment다.

`analysis.md` persistence가 repository에 구현되어 있는 경우 확정된 분석을 해당 Run과 연결해 보존한다. 아직 구현되어 있지 않다면 임의의 별도 저장 규칙을 만들지 않는다.

---

## 9. 검색 / 복원 원칙

새 대화에서는 과거 채팅 기억보다 repository를 기준으로 연구 맥락을 복원한다.

사용자가:

```text
QQQ, SPMO 들어간 실험
지난번 금 넣어서 돌린 것
target vol 바꿨던 run
QQQ 30 / SPY 30 / GLD 30 / IEF 10 백테스트
```

처럼 말하면 repository에서 다음 순서로 찾는다.

```text
Study / Experiment
-> context.yaml로 연결된 Run
-> Run input
-> Result / review tables
-> persisted analysis가 있으면 함께 확인
```

Experiment 이름만으로 실행 조건이나 product를 추정하지 않는다.

---

## 10. 금융 결과를 다룰 때의 중요한 규칙

금융 계산 의미론은 반드시 `docs/specification.md`를 따른다.

분석은 반드시 `docs/llm-analysis-framework.md`의 해당 product branch를 따른다.

특히 외부 시스템인 Portfolio Visualizer(PV)와 다른 결과가 나왔을 때:

- PV와 다르다는 이유만으로 자동으로 defect라고 판단하지 않는다.
- PV 동작을 자동으로 내부 specification에 복제하지 않는다.
- 숫자 차이, 특히 Expected Return / volatility / performance 차이는 민감하게 조사한다.
- 데이터 source, total-return treatment, 기간 alignment, RF convention 등을 확인한다.
- 의미 있는 차이는 사용자와 검토한 뒤 specification 변경 여부를 결정한다.

Optimization의 Expected Return과 Backtest의 historical CAGR/realized return은 같은 개념처럼 섞지 않는다.

---

## 11. Research 요청과 System Development 요청을 구분한다

사용자가 포트폴리오 구성, 조건 변경, 실행, 결과 비교를 요청하면 **Research Frontend mode**로 동작한다.

사용자가 다음을 요청하면 **System Development mode**다.

```text
계산 로직 수정
report UI 수정
workflow 수정
새 metric 구현
bug fix
테스트 추가
Research Frontend contract 수정
```

System Development mode에서는:

1. `AGENTS.md`를 먼저 확인한다.
2. 관련 architecture / specification / OpenSpec을 읽는다.
3. 금융 의미론 변경과 단순 구현 변경을 구분한다.
4. 개발 검증이 필요하면 현재 project workflow에 따라 Agent/Codex를 executor / evidence producer로 사용할 수 있다.

Agent의 PASS/FAIL 문구 자체를 검증 근거로 대체하지 않는다. 실제 test/run/artifact를 확인한다.

---

## 12. Canonical 한 줄 요약

```text
User request
-> Product Intent Gate
-> explicit product_mode + Study/Experiment
-> control/execute.yaml(run:true)
-> GitHub Actions
-> Run artifacts
-> product_mode-based Analysis Branch
-> User discussion
-> Confirmed insight / next research
```

핵심은 두 가지다.

> **모호한 자연어 요청에서 Optimization/Backtest를 임의 선택하지 않는다.**

> **Product가 결정된 이후에는 그 identity를 `product_mode`로 YAML, Run, Analysis까지 명시적으로 전달하며 다시 추론하지 않는다.**
