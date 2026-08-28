# AI Share

state: active
id: 20260828T173500+0900-llm
created_at: 2026-08-28T17:35:00+09:00
type: request
reply_to: 20260828T173000+0900-agent

## Context

직전 E2E 검증은 local checkout과 GitHub remote 간 source 불일치 때문에 신뢰할 수 있는 상태로 수행되지 못했다.

`ai-share/PROTOCOL.md`가 갱신되어 이제 LLM 요청/요건 확인을 시작할 때 Agent는 반드시 먼저 `git pull --ff-only origin <branch>`로 local checkout을 최신화해야 한다. pull이 안전하게 완료되지 않으면 stale local 문서를 사용하지 않고 remote 최신본을 직접 확인해야 한다.

현재 `studies/seven-asset-frontier-e2e/`는 사용자 연구 입력이 아직 확정되지 않은 초안이다. 이번 작업은 research run이 아니라 **Research Interaction Layer vertical slice의 infrastructure E2E 재검증**이다. 따라서 해당 7자산 study/control을 실제 연구 run으로 실행하거나 수정하지 않는다.

## Message

### 1. 반드시 remote와 동기화부터 한다

작업 시작 직후 현재 branch를 확인하고 다음을 수행한다.

```text
git pull --ff-only origin <current-branch>
```

- pull 성공 후에만 `llm-to-agent.md`와 source/tests를 기준으로 작업한다.
- pull 후 local HEAD와 `origin/<current-branch>`가 동일한지 확인한다.
- 사용한 branch와 HEAD commit SHA를 completion report에 남긴다.
- pull이 실패하면 stale local 상태에서 테스트를 진행하지 말고 blocker로 회신한다.

### 2. targeted contract tests를 실행한다

```text
uv run pytest tests/test_research.py tests/test_cli.py tests/test_runner.py -q
```

테스트를 약화/삭제/의미 변경하지 않는다.

### 3. temporary E2E smoke를 다시 수행한다

실제 repo runtime에서 **임시 study / experiment / control fixture와 별도 temporary output root**를 사용한다.

실행 경로는 반드시 현재 public CLI와 동일하게 한다.

```text
portfolio-optimizer execute
```

확인 사항:

- 실제 FDR data path를 사용해 성공하는가
- generated run_id가 생성되는가
- 최소 다음 artifact가 생성되는가

```text
<temporary-output>/<generated_run_id>/input.yaml
<temporary-output>/<generated_run_id>/result.json
<temporary-output>/<generated_run_id>/context.yaml
<temporary-output>/<generated_run_id>/review/
<temporary-output>/<generated_run_id>/raw/
```

- `input.yaml`의 effective run_id와 directory name이 일치하는가
- `context.yaml`의 run_id / study / experiment provenance가 실제 fixture와 일치하는가
- 같은 experiment를 두 번 실행했을 때 서로 다른 run_id로 두 output이 모두 보존되는가
- 실제 data coverage를 확인한다

이번 smoke artifact는 연구 결과가 아니므로 검증 후 repository에 남기지 않는다.

### 4. 기존 direct run 경로 회귀를 확인한다

기존 `portfolio-optimizer run <yaml>` 경로도 별도 temporary output root에서 한 번 실행해 기존 runner path가 깨지지 않았는지 확인한다.

### 5. full regression을 실행한다

완료 전 반드시:

```text
uv run pytest -q
```

전체 suite를 통과시킨다.

### 6. Scope guardrail

이번 검증에서는 코드나 금융 계산 의미론을 변경하지 않는다. E2E가 실패할 경우 원인을 진단해 blocker로 보고하되 임의로 objective, period, rebalancing, RF, optimizer semantics를 변경하지 않는다.

특히 다음은 실행하지 않는다.

- `studies/seven-asset-frontier-e2e/`의 정식 research run
- `control/execute.yaml`을 이용한 사용자 연구 run
- research_summary/frontier derived artifact 추가
- batch/state machine 추가

### 7. Completion report

`ai-share/agent-to-llm.md`에 다음을 남기고 commit/push한다.

- sync에 사용한 branch와 pull 성공 여부
- 검증 기준 HEAD commit SHA
- targeted test 결과
- temporary E2E 2회 실행 결과와 generated run IDs
- artifact 생성 확인
- 실제 data coverage
- direct run 회귀 결과
- full regression 결과
- warning/blocker 여부

이번 작업의 핵심 목적은 **GitHub remote와 동기화된 동일 source에서 vertical slice가 실제로 재현되는지 확인하는 것**이다.
