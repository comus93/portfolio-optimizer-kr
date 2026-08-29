# AGENTS.md

## Source of truth

개발 전 다음 문서를 우선 확인한다.

1. `docs/specification.md`
2. `docs/report-ui-specification.md`
3. `docs/architecture.md`
4. `docs/visual-acceptance-contract.md`
5. `docs/input-ui-contract.md`
6. `docs/llm-research-input-contract.md`
7. `ai-share/PROTOCOL.md`

현재 LLM 요청은 `ai-share/llm-to-agent.md`에서 확인한다.

Normative responsibility:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
```

External services, PV results, screenshots, historical golden files are **non-normative references**. They may reveal defects or alternative ideas but do not override the internal specification.

문서 간 충돌이 의심되면 임의 해석하지 말고 evidence와 함께 `agent-to-llm.md`에 blocker를 남긴다.

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

Agent는 독립 검증자로 요청받았을 때 구현 범위를 임의 확대하지 않는다. 개발자로 요청받았을 때는 requirement와 contract 범위 안에서 구현을 책임진다.

---

## Development principles

- v1 market data source는 FinanceDataReader(FDR)다.
- calculation behavior는 `docs/specification.md`를 따른다.
- report behavior는 `docs/report-ui-specification.md`를 따른다.
- external reference와 다르다는 이유만으로 implementation을 변경하지 않는다.
- external reference에서 더 나은 convention/UX를 발견하면 먼저 product change proposal로 취급한다.
- 데이터 정규화, 통계, optimization, portfolio path, analytics, reporting, viewer 책임을 분리한다.
- 동일 입력과 설정에서 deterministic result를 만든다.
- 계산 함수는 가능한 한 side-effect 없이 테스트 가능하게 유지한다.
- 실제 반복 요구가 없는 범용 abstraction/framework를 선제적으로 만들지 않는다.
- browser presentation layer는 canonical finance result를 재계산하지 않는다.
- 비밀값, token, 개인 환경 설정은 commit하지 않는다.

Finance semantic 또는 canonical result meaning을 변경해야 하면 specification을 먼저 갱신한다.

UI semantic 또는 required interaction을 변경해야 하면 `docs/report-ui-specification.md`를 먼저 갱신한다.

---

## Testing discipline

### Calculation

- 핵심 수식은 synthetic fixture로 독립 검증한다.
- solver status뿐 아니라 weight sum, min/max, long-only, target-volatility residual과 finite result를 확인한다.
- external numerical comparison은 sanity/data-source investigation 용도이며 internal contract를 대체하지 않는다.

### Scope

개발 반복에서는 changed/affected scope 테스트를 우선한다.

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
-> internal UI specification section-by-section verification
-> P0/P1/P2 기록
```

을 수행한다.

External reference comparison은 parity investigation 또는 현재 작업 요청에 명시된 경우에만 추가한다.

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

Interactive Report validation screenshot은 가능하면 보존하되 tool/browser 제약으로 저장할 수 없다면 blocker로 취급하지 않고 validation artifact에 사실과 직접 browser observation을 기록한다.

---

## External References

Historical PV/golden data는 다음 목적으로만 사용한다.

- numerical sanity
- data-source deviation investigation
- historical regression investigation
- UX idea comparison

Asset universe나 input 조건이 다르면 same-input numerical comparison 근거로 사용하지 않는다.

PV 또는 다른 외부 서비스가 변경돼도 우리 specification이 자동으로 변경되는 것은 아니다.

Current useful external comparison fixture는 `docs/visual-acceptance-contract.md`에서 관리한다.

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
- P0/P1/P2/deviation or blocker
- run path / user-facing Pages URL when applicable
- result commit SHA

과거 메시지는 Git history에 맡기고 ai-share 파일에 append하지 않는다.
