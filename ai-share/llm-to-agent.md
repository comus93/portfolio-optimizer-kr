# AI Share

state: active
id: 20260828T174500+0900-llm
created_at: 2026-08-28T17:45:00+09:00
type: request
reply_to: 20260828T173000+0900-agent

## Context

이전 infrastructure smoke 요청은 superseded한다. 사용자 연구 입력이 이제 확정되어 첫 정식 persisted research E2E run을 수행한다.

`ai-share/PROTOCOL.md` 최신 규칙에 따라 LLM 요청 확인 시작 시 반드시 먼저 `git pull --ff-only origin <current-branch>`로 local checkout을 최신화해야 한다.

확정 experiment:

- `studies/seven-asset-frontier-e2e/experiments/001-base-r02.yaml`
- `control/execute.yaml`은 위 파일을 가리킨다.

사용자 확정 조건:

- Provided portfolio: QQQ 40%, SPMO 10%, GDX 10%, GLD 0%, SLV 10%, AIA 15%, XLE 15%
- Min weight: 전 자산 0%
- Max weight: QQQ/SPMO 50%, 나머지 30%
- Optimization objective: Maximum Sharpe
- Rebalancing: Monthly
- Analysis period: 7개 자산 모두의 실제 데이터가 존재하는 공통 교집합 전체 기간

기본/연결 조건:

- Benchmark: SPY
- Efficient Frontier: 100 points
- Risk-free: fixed 2.35595% (기존 PV parity 진단과 연결)

## Message

### 1. 반드시 remote와 동기화부터 한다

작업 시작 직후 현재 branch를 확인하고 다음을 수행한다.

```text
git pull --ff-only origin <current-branch>
```

- pull 성공 후에만 최신 `llm-to-agent.md`, experiment, control을 기준으로 진행한다.
- pull 후 local HEAD와 `origin/<current-branch>`가 동일한지 확인한다.
- pull이 실패하면 stale local 상태에서 실행하지 말고 blocker로 회신한다.

### 2. 코드 변경 없이 정식 research run을 실행한다

현재 `control/execute.yaml` 대상으로 실제 명령을 실행한다.

```text
portfolio-optimizer execute
```

이번 run은 temporary smoke가 아니다. 생성된 `runs/<generated_run_id>/` 전체를 보존한다.

### 3. 생성 artifact를 검증한다

최소 다음을 확인한다.

```text
runs/<generated_run_id>/input.yaml
runs/<generated_run_id>/result.json
runs/<generated_run_id>/context.yaml
runs/<generated_run_id>/review/
runs/<generated_run_id>/raw/
```

특히 다음 review artifact의 존재를 확인한다.

```text
review/efficient_frontier.csv
review/optimization_results.csv
review/performance_summary.csv
review/correlations.csv
review/drawdowns.csv
review/return_decomposition.csv
review/risk_decomposition.csv
review/rolling_returns_summary.csv
```

또한:

- `input.yaml`의 effective run_id와 output directory name이 일치하는지 확인
- `context.yaml`의 run_id / study / experiment provenance가 실제 실행과 일치하는지 확인
- `analysis_period`가 비어 있는 입력에서 실제 FDR 공통 overlap 전체 기간이 사용됐는지 data coverage로 확인
- 실제 coverage start/end/observation count를 보고

### 4. 결과를 GitHub에 영구 보존한다

- 생성된 `runs/<generated_run_id>/` 전체를 Git에 commit/push한다.
- 삭제하지 않는다.
- `study.md`의 Interpretation/Conclusion은 수정하지 않는다. 이후 GPT + user가 결과를 읽고 갱신한다.

### 5. Scope guardrail

이번 요청은 실행/검증 작업이다. 코드나 금융 계산 의미론을 임의로 변경하지 않는다.

실패하면 objective, period, rebalance, RF, constraints 등을 바꾸지 말고 원인을 blocker로 보고한다.

다음은 추가하지 않는다.

- research_summary/frontier derived artifact
- batch/state machine
- 별도 research DB

### 6. Completion report

`ai-share/agent-to-llm.md`에 다음을 기록하고 commit/push한다.

- sync branch / pull 성공 여부
- 실행 기준 HEAD commit SHA
- generated run_id
- persisted GitHub path
- `portfolio-optimizer execute` 성공/실패
- 실제 data coverage start/end/observations
- 핵심 artifact 존재 확인
- warning/blocker
- run artifact commit SHA

이번 작업의 목적은 **사용자 입력 → experiment/control → 실제 FDR/optimizer 실행 → persisted run artifact → GPT 분석**의 첫 정식 E2E research loop를 완성하는 것이다.
