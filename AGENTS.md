# AGENTS.md

## Source of truth

개발 전 다음 문서를 우선 확인한다.

1. `specification.md`
2. `ai-share/PROTOCOL.md`

현재 LLM 요청은 `ai-share/llm-to-agent.md`에서 확인한다.

## Role split

- LLM은 요구사항 분석, 금융 계산 정의, 테스트 시나리오, 초기 뼈대 코드를 담당한다.
- Agent는 개발자로서 구현 보강, 의존성 정리, 실제 실행, 디버깅, 테스트를 담당한다.
- 금융 계산 정의나 scope를 바꿔야 하면 임의로 변경하지 말고 `agent-to-llm.md`로 질문 또는 blocker를 남긴다.

## Development principles

- v1의 market data source는 FinanceDataReader(FDR)다.
- 계산 로직은 일반적인 금융 분석 관례를 우선하며 Portfolio Visualizer(PV)는 참고 및 golden reference로 사용한다.
- PV와 100% 동일한 결과를 목표로 하지 않는다. 동일 입력과 설정에서 일관되고 재현 가능한 결과를 만드는 것이 우선이다.
- 데이터 정규화, 통계 계산, optimization, analytics의 책임이 코드에서 구분되어야 한다.
- 동일 입력과 설정은 동일 결과를 만들어야 한다.
- 계산 함수는 가능한 한 side effect 없이 테스트 가능하게 유지한다.
- 실제 반복 요구가 없는 추상화 계층이나 범용 framework를 선제적으로 만들지 않는다.
- 비밀값이나 개인 환경 설정은 repository에 commit하지 않는다.

## Testing discipline

- 구현은 `specification.md`의 계산 정의와 acceptance checks를 기준으로 검증한다.
- 핵심 수식은 synthetic fixture로 독립 검증한다.
- PV golden reference는 parity / sanity check에 사용하되, market-data 차이로 인한 수치 차이와 optimizer 로직 차이를 구분한다.
- 신규 core 구현 또는 공통 계산 변경 시 전체 관련 테스트를 실행한다.
- solver 결과는 성공 여부뿐 아니라 weight sum, min/max, target volatility 등 constraint residual도 검증한다.

## Golden reference

PV reference는 다음 위치를 사용한다.

```text
tests/golden/pv/
```

현재 기준 reference:

```text
260828_PTF_maxsharpe.md
260828_PTF_maxsharpe.jpg
```

## AI Share

ChatGPT와 Codex 간 메시지 및 세션 handover에는 `./ai-share/PROTOCOL.md`를 따른다.

Agent 작업 결과는 `ai-share/agent-to-llm.md`에 최소한으로 정리하고 GitHub remote에 commit/push한 뒤 완료로 간주한다.
