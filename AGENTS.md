# AGENTS.md

## OpenSpec / Source of truth

이 repository는 OpenSpec으로 **변경 요구사항과 진행 상태**를 관리한다.

```text
openspec/specs/                 현재 capability requirements
openspec/changes/<change>/      진행 중 change의 proposal/spec/design/tasks
openspec/changes/archive/       완료된 change history
```

기존 capability 중 아직 OpenSpec으로 이관되지 않은 상세 contract는 기존 `docs/` 문서가 baseline이다. 해당 capability를 변경할 때 OpenSpec delta를 작성하고, 완료 후 archive/sync를 통해 `openspec/specs/`로 점진적으로 옮긴다.

개발 전 우선 확인 순서:

1. `openspec/config.yaml`
2. 현재 작업의 `openspec/changes/<change>/`
3. 관련 `openspec/specs/`
4. 아직 이관되지 않은 관련 `docs/` contract
5. `ai-share/PROTOCOL.md`

현재 LLM 요청은 `ai-share/llm-to-agent.md`에서 확인한다.

Normative responsibility:

```text
Change scope / status           OpenSpec
Finance / calculation semantics docs/specification.md (until migrated)
Report UI / interaction         docs/report-ui-specification.md (until migrated)
Architecture / responsibility   docs/architecture.md
Validation procedure            docs/visual-acceptance-contract.md
```

Active OpenSpec delta가 존재하면 그 change 범위에서는 delta가 기존 baseline에 대한 명시적 변경 계약이다. 외부 서비스, PV 결과, screenshot, historical golden은 non-normative reference다.

요구사항 충돌이나 해석이 materially 달라질 수 있으면 임의로 정답을 바꾸지 말고 evidence와 함께 blocker를 남긴다.

---

## Development workflow mode

이 repository는 LLM과 Codex Agent의 역할을 고정하지 않는다. 작업마다 사용자 또는 현재 `ai-share/llm-to-agent.md`가 workflow mode를 정한다.

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

### LLM design

```text
LLM = 요구사항 + 계산 정의 + 테스트/수용조건 + 리뷰
Agent = 구현 + 실제 실행 검증
```

OpenSpec planning artifact가 필요한 change에서는 proposal/spec/design/tasks가 구현의 입력 계약이다. Agent는 구현을 고칠 수 있지만 requirement, Acceptance Criteria, 계산 규칙, 검증 기준을 임의 변경하지 않는다.

---

## Development principles

- v1 market data source는 FinanceDataReader(FDR)다.
- 계산/리포트 behavior 변경은 관련 OpenSpec delta를 먼저 정의한다.
- 아직 OpenSpec으로 이관되지 않은 baseline semantics는 기존 `docs/` contract를 따른다.
- external reference와 다르다는 이유만으로 requirement를 변경하지 않는다.
- external reference에서 더 나은 convention/UX를 발견하면 product change proposal로 다룬다.
- data, stats, optimization, portfolio path, analytics, reporting, viewer 책임을 분리한다.
- 동일 입력과 설정에서 deterministic result를 만든다.
- browser presentation layer는 canonical finance result를 재계산하지 않는다.
- 실제 반복 요구가 없는 범용 abstraction/framework를 선제적으로 만들지 않는다.
- 비밀값, token, 개인 환경 설정은 commit하지 않는다.

---

## Testing discipline

### Calculation

- 핵심 수식은 synthetic fixture로 독립 검증한다.
- solver status뿐 아니라 weight sum, min/max, long-only, target-volatility residual과 finite result를 확인한다.
- external numerical comparison은 sanity/data-source investigation 용도이며 internal contract를 대체하지 않는다.

### Scope

개발 반복에서는 changed/affected scope 테스트를 우선한다.

Full regression은 다음 경우에 확대한다.

- 사용자 또는 LLM이 명시적으로 요청
- 공통/core 코드 변경으로 영향 범위가 넓음
- 영향 범위가 불명확함
- targeted failure가 cross-module regression 가능성을 드러냄
- release/completion gate에 필요

테스트를 통과시키기 위해 contract test를 임의로 약화·삭제·skip·xfail하지 않는다. Contract가 잘못됐다고 판단되면 blocker로 보고한다.

### Interactive Report

필요한 작업에서는:

```text
generate report
-> localhost HTTP browser render
-> internal UI specification verification
-> P0/P1/P2 기록
```

을 수행한다.

External reference comparison은 parity investigation 또는 현재 change가 요구하는 경우에만 추가한다.

---

## Run outputs

일반 unit test 임시 출력은 repository에 저장하지 않는다.

사용자/LLM이 검토해야 하는 research 또는 validation run은:

```text
runs/<run_id>/
```

아래에 저장한다.

최소 source of truth는 `result.json`이며 필요에 따라:

```text
input.yaml
context.yaml
raw/*.csv
review/*.csv
report.html
validation/*
```

를 함께 둔다. 기존 run directory를 silent overwrite하지 않는다.

---

## External References

Historical PV/golden data는 다음 목적으로 사용한다.

- numerical sanity
- data-source deviation investigation
- historical regression investigation
- UX idea comparison

Asset universe나 input 조건이 다르면 same-input numerical comparison 근거로 사용하지 않는다. PV 또는 다른 외부 서비스가 변경돼도 internal requirement가 자동 변경되는 것은 아니다.

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
- run path / user-facing URL when applicable
- result commit SHA

과거 메시지는 Git history에 맡기고 ai-share 파일에 append하지 않는다.
