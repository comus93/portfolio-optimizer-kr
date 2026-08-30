# AI Share

state: active
id: 20260830T154500+0900-llm
created_at: 2026-08-30T15:45:00+09:00
type: request
reply_to: none

## Context

`bt-module` branch에서 Phase 1 OpenSpec 도입을 시작했다.

LLM이 추가/변경한 핵심:

```text
openspec/config.yaml
openspec/changes/bt-module/.openspec.yaml
openspec/changes/bt-module/proposal.md
openspec/specs/.gitkeep
openspec/changes/archive/.gitkeep
AGENTS.md
README.md
```

OpenSpec은 change scope/status를 관리하고, 아직 이관되지 않은 기존 상세 contract는 `docs/`를 baseline으로 유지한다. 현재 active change는 `bt-module`이다.

## Message

`bt-module` 최신 remote를 pull한 뒤 OpenSpec의 Codex integration을 실제 repo checkout에 초기화하고 구조를 검증해라.

1. Node >= 20.19 확인.
2. OpenSpec CLI가 없으면 global install 대신 `npx -y @fission-ai/openspec@latest`를 사용한다.
3. 기존 OpenSpec-managed legacy files가 있는지 먼저 확인한다. 있으면 삭제/이동하지 말고 blocker로 보고한다.
4. 아래와 동등한 방식으로 Codex core skills를 repo에 생성한다.

```text
npx -y @fission-ai/openspec@latest init --tools codex --profile core --no-animation
```

5. 생성된 OpenSpec skill 파일은 commit 대상이다.
6. 아래를 실행해 결과를 확인한다.

```text
openspec status --change bt-module
openspec validate bt-module --strict
```

`openspec`가 PATH에 없으면 같은 `npx -y @fission-ai/openspec@latest` prefix를 사용한다.

현재 Phase 1에서는 Backtest spec/design/tasks를 임의 작성하지 않는다. `proposal.md` 이후 단계는 LLM/사용자와 기획 후 진행한다.

결과를 `agent-to-llm.md`에 간단히 남긴다.

- start HEAD
- OpenSpec version
- generated files
- status output
- validation output
- blocker 여부
- result commit SHA
