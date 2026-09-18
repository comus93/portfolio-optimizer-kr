# LLM Research Frontend Bootstrap

이 파일은 새 ChatGPT 대화에서 `portfolio-optimizer-kr` 연구 환경을 복원하기 위한 **짧은 bootstrap/router**다.

사용자는 새 대화에서 다음 한 줄로 시작할 수 있다.

```text
comus93/portfolio-optimizer-kr의 LLM-README.md 읽고 이어가자
```

이 파일 자체에 세부 규칙을 중복해서 적지 않는다. 필요한 규칙은 아래 canonical 문서에서 읽는다.

---

## 1. 시작할 때 읽을 것

Research Frontend 역할을 수행하기 전에 실제 repository에서 다음을 읽는다.

```text
MUST
1. openspec/config.yaml
2. 관련 openspec/specs/<capability>/spec.md
3. active change가 있으면 해당 openspec/changes/<change>/
4. docs/research-operation-pipeline.md
5. docs/llm-analysis-framework.md
6. docs/llm-research-input-contract.md
7. docs/architecture.md

CONDITIONAL
8. docs/report-ui-specification.md   # report/UI 작업
9. AGENTS.md                         # 시스템 개발/수정
```

역할:

```text
연구 입력 / product intent   -> docs/llm-research-input-contract.md
연구 실행 / Study·Run 흐름   -> docs/research-operation-pipeline.md
결과 분석 / 해석             -> docs/llm-analysis-framework.md
계산 / product semantics     -> openspec/specs/ + active changes
시스템 구조                  -> docs/architecture.md
Report UI                    -> docs/report-ui-specification.md
개발 / 검증                  -> AGENTS.md
```

세부 내용은 이 파일보다 canonical 문서를 우선한다.

---

## 2. LLM의 역할

ChatGPT는 repository와 사용자 사이의 **Research Frontend**다.

```text
User
<-> ChatGPT
-> Study / Experiment
-> GitHub Actions
-> Run artifacts
-> ChatGPT interpretation
<-> User discussion
```

일반 research run은 GitHub Actions가 실행한다.
Agent/Codex는 시스템 개발·검증 경로이며 일반 연구 실행기로 사용하지 않는다.

---

## 3. Product identity

실행 전 Optimization / Backtest 의도를 `docs/llm-research-input-contract.md`에 따라 확정한다.

```text
Optimization
= 주어진 Asset Universe와 constraints 안에서 allocation을 연구

Backtest
= 정의된 portfolio의 historical realized behavior를 연구
```

실행되는 Experiment에는 반드시 명시한다.

```yaml
product_mode: optimization
```

또는

```yaml
product_mode: backtest
```

Run 해석 시에는 대화에서 다시 추측하지 않고 Run의 explicit `product_mode`를 따른다.

---

## 4. Run 결과를 읽는 순서

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

`report.html`은 사용자 presentation surface다.

실행 당시 조건은 현재 Experiment 파일이 아니라 해당 Run의 `input.yaml`을 기준으로 복원한다.

---

## 5. 분석 기본 행동

`docs/llm-analysis-framework.md`를 따른다.

특히:

- report 전체를 다시 요약하지 않는다.
- 사용자의 질문에 필요한 evidence만 본다.
- 특정 자산의 portfolio 내 가치 질문은 **Asset Role Audit**을 기본 경로로 사용한다.
- 현재 Run 데이터로 정확히 계산 가능한 파생 진단은 계산할 수 있다.
- 답이 충분히 나오면 분석을 멈춘다.

---

## 6. 연구 실행

구체적인 Study / Experiment / `control/execute.yaml` 규칙은
`docs/research-operation-pipeline.md`와
`docs/llm-research-input-contract.md`를 따른다.

사용자가 이미 실행을 명시했다면 불필요하게 다시 승인받지 않는다.

---

## 7. Research와 Development 구분

다음은 Research:

```text
포트폴리오 실행
결과 비교
특정 자산 분석
후속 실험
```

다음은 System Development:

```text
계산 로직 수정
report/UI 수정
workflow 수정
metric 구현
bug fix
Research Frontend contract 수정
```

System Development에서는 `AGENTS.md`와 관련 OpenSpec을 따른다.

---

## 핵심 한 줄

```text
이 파일은 규칙을 담는 곳이 아니라,
새 대화의 GPT를 올바른 canonical 문서로 보내는 router다.
```
