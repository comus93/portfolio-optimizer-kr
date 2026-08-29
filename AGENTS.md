# AGENTS.md

## Source of truth

개발 전 다음 문서를 우선 확인한다.

1. `docs/specification.md`
2. `docs/visual-acceptance-contract.md`
3. `docs/architecture.md`
4. `docs/input-ui-contract.md`
5. `docs/llm-research-input-contract.md`
6. `ai-share/PROTOCOL.md`

현재 LLM 요청은 `ai-share/llm-to-agent.md`에서 확인한다.

`docs/specification.md`는 금융 계산과 결과 계약의 canonical source다. `docs/visual-acceptance-contract.md`는 Interactive Report의 browser/behavior acceptance를 구체화한다. 충돌이 의심되면 임의 해석하지 말고 `agent-to-llm.md`에 blocker를 남긴다.

---

## Development workflow mode

이 repository는 LLM과 Codex Agent의 역할을 고정하지 않는다. 작업마다 사용자가 선택하거나 LLM이 명시한 workflow mode를 따른다.

### LLM sandbox development

```text
LLM = 설계 + sandbox 구현 + targeted test/CLI 1차 검증
Agent = 독립 real-environment / E2E / browser 검증
```

### LLM implementation

```text
LLM = 설계 + GitHub 구현
Agent = 실제 checkout에서 targeted test / CLI / browser 검증
```

필요하면 LLM이 GitHub-side CI로 구현 후 1차 실행 검증을 추가할 수 있다.

### LLM design

```text
LLM = 요구사항 + 계산 정의 + 테스트/수용조건 + 리뷰
Agent = 구현 + 실제 실행 검증
```

`AGENTS.md`는 어느 mode가 항상 우월하다고 규정하지 않는다. **현재 `ai-share/llm-to-agent.md`의 요청이 해당 작업의 역할 분담을 결정한다.**

Agent는 자신이 독립 검증자 역할로 요청받았을 때 구현 범위를 임의 확대하지 않는다. 반대로 개발자로 요청받았을 때는 요구사항과 테스트 계약 범위 안에서 구현을 책임진다.

---

## Development principles

- v1 market data source는 FinanceDataReader(FDR)다.
- 일반적인 금융 분석 관례를 우선하고 PV는 numerical/behavioral golden reference로 사용한다.
- PV와 수치가 다르면 market-data 차이와 calculation defect를 구분한다.
- 데이터 정규화, 통계, optimization, portfolio path, analytics, reporting, viewer 책임을 분리한다.
- 동일 입력과 설정에서 deterministic result를 만든다.
- 계산 함수는 가능한 한 side-effect 없이 테스트 가능하게 유지한다.
- 실제 반복 요구가 없는 범용 abstraction/framework를 선제적으로 만들지 않는다.
- browser presentation layer는 canonical finance result를 재계산하지 않는다.
- 비밀값, token, 개인 환경 설정은 commit하지 않는다.

금융 계산 정의나 canonical result 의미를 바꿔야 하면 현재 요청에 명시되어 있지 않은 한 Agent가 임의 변경하지 않는다.

---

## Testing discipline

### Calculation

- 핵심 수식은 synthetic fixture로 독립 검증한다.
- solver status뿐 아니라 weight sum, min/max, long-only, target-volatility residual과 finite result를 확인한다.
- PV parity test에서는 source-data deviation과 optimizer defect를 구분한다.

### Scope

개발 반복에서는 **changed/affected scope 테스트를 우선**한다.

Full regression은 자동 의무가 아니다. 다음 경우에 범위를 확대한다.

- 사용자 또는 LLM이 명시적으로 요청
- 공통/core 코드 변경으로 영향 범위가 넓음
- 영향 범위가 불명확함
- targeted failure가 cross-module regression 가능성을 드러냄
- release/completion gate에서 필요하다고 현재 작업 요청이 정의함

작은 viewer/presentation 수정마다 관성적으로 전체 pytest를 실행하지 않는다.

테스트를 통과시키기 위해 기존 contract test를 임의로 약화·삭제·skip·xfail하지 않는다. Contract가 잘못됐다고 판단되면 evidence와 함께 blocker를 남긴다.

### Interactive Report

자동 pytest만으로 UI 완료라고 판단하지 않는다.

필요한 작업에서는:

```text
generate report
-> localhost HTTP browser render
-> current PV live reference open
-> section-by-section semantic/visual comparison
-> P0/P1/deviation 기록
```

을 수행한다.

특히 table/metric은 문자열 marker 존재뿐 아니라 실제 rendered unit/value를 확인한다.

---

## Run outputs

일반 unit test 임시 출력은 repository에 저장하지 않는다.

사용자/LLM이 검토해야 하는 research 또는 validation run은:

```text
runs/<run_id>/
```

아래에 저장하고 commit/push한다.

최소 source of truth는 `result.json`이며 필요에 따라:

```text
input.yaml
context.yaml
raw/*.csv
review/*.csv
report.html
validation/visual-comparison.md
```

를 함께 둔다.

Run은 재현 가능한 effective input과 실제 data coverage를 포함해야 한다. 기존 run directory를 silent overwrite하지 않는다.

Interactive Report validation screenshot은 가능하면 보존하되 tool/browser 제약으로 저장할 수 없다면 blocker로 취급하지 않고 `visual-comparison.md`에 사실과 직접 비교 결과를 기록한다.

---

## Golden / PV reference

Current Interactive Report behavioral golden의 source of truth는 `docs/visual-acceptance-contract.md`다.

Historical reference는 `tests/golden/pv/`에 유지할 수 있지만 **asset universe나 input 조건이 현재 validation fixture와 다르면 same-input PASS 근거로 사용하지 않는다.**

Static Golden은 최신 동일-input screenshot이 있을 때만 completion evidence로 사용한다. 깨진 URL이나 다른-universe 이미지를 PASS로 간주하지 않는다.

---

## AI Share

ChatGPT와 Codex 간 메시지 및 세션 handover에는 `./ai-share/PROTOCOL.md`를 따른다.

### Inbound to Agent

요청 확인 전에 GitHub remote를 source of truth로 동기화한다.

```text
git pull --ff-only origin <branch>
```

안전하게 pull할 수 없으면 remote의 최신 `ai-share/llm-to-agent.md`를 직접 확인하고 local sync blocker를 알린다.

### Outbound from Agent

Agent 결과는 `ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한 뒤 전달 완료로 간주한다.

최소 결과:

- start HEAD
- changed files
- test/run/browser evidence
- P0/P1/deviation or blocker
- run path / user-facing Pages URL when applicable
- result commit SHA

과거 메시지는 Git history에 맡기고 ai-share 파일에 append하지 않는다.
