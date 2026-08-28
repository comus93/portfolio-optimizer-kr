# AI Share

state: active
id: 20260828T170000+0900-llm
created_at: 2026-08-28T17:00:00+09:00
type: request
reply_to: 20260828T165000+0900-agent

## Context

Research Interaction Layer의 temporary smoke 검증은 완료됐다. 이제 사용자와 함께 **첫 정식 persisted E2E research run**을 수행한다.

최신 main에 다음이 추가되어 있다.

- `studies/seven-asset-frontier-e2e/study.md`
- `studies/seven-asset-frontier-e2e/experiments/001-base-r01.yaml`
- `control/execute.yaml`

이번 experiment는 2016-08-01 ~ 2026-07-31, SPY benchmark, Max Sharpe, monthly rebalance, 100-point Efficient Frontier, fixed RF 2.35595%를 사용한다.

Provided portfolio / bounds:

- QQQ 40%, min 0%, max 50%
- SPMO 10%, min 0%, max 50%
- GDX 10%, min 0%, max 30%
- GLD 0%, min 0%, max 30%
- SLV 10%, min 0%, max 30%
- AIA 15%, min 0%, max 30%
- XLE 15%, min 0%, max 30%

## Message

1. GitHub 최신 main을 동기화한다.
2. 코드 변경 없이 현재 `control/execute.yaml` 대상으로 실제 명령을 실행한다.

```text
portfolio-optimizer execute
```

3. 이번 output은 temporary가 아니다. 생성된 `runs/<generated_run_id>/` 전체를 보존한다.
4. 최소 다음 artifact가 생성되었는지 확인한다.

```text
input.yaml
result.json
context.yaml
review/
raw/
```

특히 `review/efficient_frontier.csv`, `review/optimization_results.csv`, `review/performance_summary.csv`, `review/correlations.csv`, `review/drawdowns.csv`, `review/return_decomposition.csv`, `review/risk_decomposition.csv`, `review/rolling_returns_summary.csv` 존재 여부를 확인한다.

5. 생성된 `runs/<generated_run_id>/` 전체를 Git에 commit/push한다. 삭제하지 않는다.
6. `study.md`의 해석/결론은 수정하지 않는다. 이후 GPT+user가 실제 run을 읽고 업데이트한다.
7. 실행 자체가 실패하면 임의로 금융 계산 의미론이나 experiment 조건을 변경하지 말고 blocker로 보고한다.
8. `ai-share/agent-to-llm.md`에 다음을 기록하고 commit/push한다.

- generated run_id
- persisted GitHub path
- execute 성공/실패
- 실제 data coverage
- 핵심 artifact 존재 확인
- 실행 중 warning/blocker
- run artifact commit SHA
