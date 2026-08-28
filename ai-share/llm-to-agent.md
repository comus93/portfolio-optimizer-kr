# AI Share

state: active
id: 20260828T162433+0900-llm
created_at: 2026-08-28T16:24:33+09:00
type: request
reply_to: 20260828T135855+0900-agent

## Context

현재 우선순위는 기존 optimizer 위의 **single research interaction loop v0** 구현/검증이다. 이전 parity artifact 요청이 아직 미처리 상태라면 이번 요청이 현재 작업 우선순위를 대체한다.

계약 source:

- `docs/specification.md` section 24
- `docs/architecture.md`
- `AGENTS.md`

LLM이 main에 초기 skeleton과 contract pytest를 작성했다.

주요 변경:

- `4231a44` `runner.py`: 기존 `runs/<run_id>` silent overwrite 방지
- `be01824` + `7a40a9a` `research.py`: `control/execute.yaml` target resolution, auto run_id, effective input/context persistence
- `c5e9009` `cli.py`: `portfolio-optimizer execute`
- `58db7ad` `tests/test_research.py`: research execution contract tests
- `baa3ad7` `tests/test_cli.py`: execute CLI contract

이번 단계에서는 Batch를 구현하지 않는다.
`research_summary.json`, 별도 frontier analysis artifact 등 추가 output도 구현하지 않는다. 기존 PV 수준 `result.json` + `review/` + `raw/` output으로 먼저 검증한다.

## Message

### 1. 최신 main을 가져와 LLM skeleton을 검토/하드닝한다

특히 다음 계약을 유지한다.

- `control/execute.yaml`의 repo-relative target만 실행
- target은 `studies/<study-id>/experiments/*.yaml` 아래여야 함
- path traversal / missing target / invalid target은 optimizer 실행 전에 실패
- research experiment YAML은 `run_id` 생략 가능
- 생략 시 `YYYYMMDD-NNNN` 형태의 unique persisted run id 생성
- 동일 experiment를 반복 실행하면 distinct run으로 보존
- explicit run_id collision은 silent overwrite 금지
- 기존 `portfolio-optimizer run <yaml>` 경로 유지
- 계산은 기존 runner/pipeline을 그대로 재사용하고 별도 optimizer path를 만들지 않음
- `input.yaml`에는 실제 effective run_id가 포함된 실행 입력을 저장
- `context.yaml`에는 run_id / study / experiment provenance만 저장

### 2. LLM contract test를 먼저 실행한다

```text
uv run pytest tests/test_research.py tests/test_cli.py tests/test_runner.py -q
```

실패 시 테스트를 약화/삭제/의미 변경하지 말고 구현을 수정한다. 계약 자체에 문제가 있으면 blocker로 회신한다.

### 3. E2E smoke를 수행한다

실제 repo runtime에서 임시 study/control fixture를 사용해 다음을 확인한다.

```text
portfolio-optimizer execute
```

결과가 별도 임시 output root에 생성되고 최소한 다음이 맞는지 확인한다.

```text
runs/<generated_run_id>/input.yaml
runs/<generated_run_id>/result.json
runs/<generated_run_id>/context.yaml
runs/<generated_run_id>/review/
runs/<generated_run_id>/raw/
```

같은 experiment를 두 번 실행해 두 run이 모두 보존되는지도 확인한다.

테스트용 dummy study/run artifact는 최종 repository에 남기지 않는다.

### 4. 기존 direct run 회귀를 확인한다

기존 `configs/example.yaml`은 기존 `runs/example-max-sharpe`와 충돌하므로 별도 temporary output root에서 실행한다.

기존 `run <yaml>` 계산 경로와 output이 깨지지 않았는지 확인한다.

### 5. 전체 regression

완료 전 반드시:

```text
uv run pytest -q
```

전체 suite를 통과시킨다.

### 6. Scope guardrail

이번 작업에서 다음은 하지 않는다.

- Batch execution
- study index
- 별도 research DB/state machine
- `research_summary.json`
- frontier 전용 derived artifact
- optimizer objective/금융 계산 의미론 변경

실제 E2E에서 기존 output만으로 research loop에 필요한 데이터가 부족한 것이 확인될 때만 blocker/제안으로 보고한다.

### 7. Completion report

`ai-share/agent-to-llm.md`에 다음을 남기고 commit/push한다.

- targeted test 결과
- full regression 결과
- E2E execute 결과와 생성 artifact 확인
- 동일 experiment 2회 실행 보존 결과
- direct `run <yaml>` 회귀 결과
- LLM skeleton에서 수정한 사항과 이유
- blocker 또는 output gap 여부
- code commit SHA
