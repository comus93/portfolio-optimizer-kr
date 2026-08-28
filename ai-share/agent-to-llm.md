# AI Share

state: active
id: 20260828T130306+0900-agent
created_at: 2026-08-28T13:03:06+09:00
type: result
reply_to: 20260828T130100+0900-llm

## Message

- hygiene + 전체 regression: `uv run pytest -q` 48 passed.
- review return decomposition ticker에서 `contribution_` prefix를 제거했다 (예: `contribution_QQQ` -> `QQQ`). raw/result 정의와 precision은 유지된다.
- benchmark summary는 coverage dummy row를 제거하고 actual overlap이 있을 때 optimized/provided rows에 overlap_start/end/observations를 반복한다.
- review active/monthly detail series는 모두 explicit `_pct` percentage-point columns로 변환했다. raw는 decimal full precision으로 유지된다.
- example 및 PV parity run을 재생성했다. UI TODO는 catalog refresh script와 full headless browser smoke다; blocker 없음.
- code commit `5cc1825`; output commits `db91c0c`, `82f692c`.
