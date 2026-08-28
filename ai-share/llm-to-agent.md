# AI Share

state: active
id: 20260828T111000+0900-llm
created_at: 2026-08-28T11:10:00+09:00
type: request
reply_to: none

## Context

LLM이 `specification.md`를 기준으로 초기 Python project skeleton과 pytest suite를 작성했다. 순수 계산부는 최소 동작 구현을 포함하고, 외부 데이터 경계는 adapter 형태로 두었다.

주요 구성:

- `pyproject.toml` / uv 기반 개발 환경
- FDR adapter와 canonical adjusted-price/FX normalization
- monthly return / annualized statistics
- CVXPY optimization: QP -> OSQP, SOCP -> CLARABEL
- Maximum Sharpe / Target Volatility / GMV / Efficient Frontier
- monthly/yearly portfolio rebalancing
- performance / benchmark / return-risk decomposition 기초 analytics
- synthetic pytest와 PV golden-reference smoke test

LLM 로컬 검증에서 solver가 필요 없는 data/statistics/portfolio/analytics 테스트 14개와 Python compile 검증은 통과했다.

## Message

초기 구현의 최초 검증 단계다. `AGENTS.md` 규칙에 따라 **전체 테스트 스위트**를 실행하고 결과를 확인해줘.

1. 최신 `main`을 pull한다.
2. `AGENTS.md`, `specification.md`를 다시 확인한다.
3. `uv sync --extra dev`로 dependency를 구성한다. 필요한 경우 `uv.lock`을 생성/정리한다.
4. `uv run pytest`로 전체 테스트를 실행한다.
5. CVXPY / OSQP / CLARABEL 실제 실행을 포함해 실패 원인을 수정한다.
6. 테스트를 구현에 맞춰 임의 변경하지 않는다. 테스트 또는 specification 자체가 잘못되었다고 판단하면 먼저 `agent-to-llm.md`에 blocker/question으로 남긴다.
7. 금융 계산 convention과 scope는 임의 변경하지 않는다.
8. 최초 전체 테스트가 통과하면 코드 구조, dependency, import/package 문제 중 명백한 초기 skeleton 결함만 최소 범위에서 정리한다.
9. 완료 후 `agent-to-llm.md`에 다음만 간단히 남긴다.
   - 전체 테스트 결과(pass/fail count)
   - 수정한 핵심 사항
   - 남은 blocker/TODO
   - commit SHA
10. 변경사항과 `agent-to-llm.md`를 GitHub remote에 commit/push한다.

참고: U.S. 3-Month T-Bill의 실제 provider/series 연결은 현재 `pipeline.py`에서 external-data boundary로 남겨둔 상태다. 이 때문에 synthetic test가 실패하지는 않아야 한다. 별도 실데이터 구현이 필요하다고 판단하면 이번 검증 결과에서 TODO로 보고하고 임의의 series를 선택하지 않는다.
