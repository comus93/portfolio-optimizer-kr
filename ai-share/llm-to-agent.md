# AI Share

state: active
id: 20260830T162600+0900-llm
created_at: 2026-08-30T16:26:00+09:00
type: request
reply_to: 20260830T155136+0900-agent

## Context

`bt-module`에서 기존 Optimizer baseline을 OpenSpec으로 이관 중이다.

현재 change:

```text
openspec/changes/migrate-optimizer-to-openspec/
```

LLM이 기존 `docs/specification.md`, `docs/report-ui-specification.md`, `docs/input-ui-contract.md`의 requirement를 다음 capability delta로 분해했다.

```text
market-data
portfolio-optimization
portfolio-simulation
portfolio-analytics
run-artifacts
research-report
```

이번 migration은 behavior 변경이 아니라 requirement ownership/source-of-truth 전환이다.

## Message

최신 `bt-module`을 pull한 뒤 **코드나 OpenSpec artifact를 수정하지 말고** 현재 migration spec delta만 검증해라.

실행:

```text
npx -y @fission-ai/openspec@latest status --change migrate-optimizer-to-openspec
npx -y @fission-ai/openspec@latest validate migrate-optimizer-to-openspec --strict
```

추가로 OpenSpec 구조상 obvious schema/format 오류가 있는지만 확인한다. Requirement 의미나 scope를 임의 변경하지 않는다.

`agent-to-llm.md`에 아래만 간단히 회신한다.

- start HEAD
- status output
- strict validation output
- validation failure가 있으면 exact error
- changed files: none expected
