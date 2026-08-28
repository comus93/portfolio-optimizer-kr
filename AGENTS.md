# AGENTS.md

## Source of truth

개발 전 다음 문서를 우선 확인한다.

1. `docs/specification.md`
2. `docs/visual-acceptance-contract.md`
3. `docs/architecture.md`
4. `docs/input-ui-contract.md`
5. `docs/llm-research-input-contract.md`
6. `ai-share/PROTOCOL.md`

현재 LLM 요청은 `ai-share/llm-to-agent.md`에서 확인한다.

`docs/visual-acceptance-contract.md`는 `docs/specification.md` Section 25 `Interactive Research Report`의 visual/behavioral acceptance를 구체화하는 normative contract다. 두 문서가 충돌한다고 판단되면 임의 해석하지 말고 `agent-to-llm.md`에 blocker를 남긴다.

## Role split

- LLM은 요구사항 분석, 금융 계산 정의, 테스트 시나리오와 **pytest 계약 코드**, 초기 뼈대 코드를 담당한다.
- Agent는 개발자로서 LLM이 만든 계약/테스트/초기 뼈대 코드를 기준으로 구현 보강, 의존성 정리, 실제 실행, 디버깅, UI hardening, 회귀 테스트를 담당한다.
- Agent는 테스트를 통과시키기 위해 LLM이 만든 contract test를 임의로 약화·삭제·의미 변경하지 않는다. 계약 자체에 문제가 있다고 판단하면 먼저 `agent-to-llm.md`로 blocker를 남긴다.
- YAML/UI/Viewer 작업에서도 동일 R&R을 유지한다. LLM이 YAML schema, execution boundary, viewer boundary와 테스트를 고정하고 초기 뼈대 코드를 작성하며, Agent가 실제 환경에서 end-to-end로 완성한다.
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

- 구현은 `docs/specification.md`의 계산 정의와 acceptance checks를 기준으로 검증한다.
- Interactive Report는 추가로 `docs/visual-acceptance-contract.md`의 browser-based visual/behavioral acceptance를 완료해야 한다. 자동 테스트 통과만으로 UI 완료로 판단하지 않는다.
- 핵심 수식은 synthetic fixture로 독립 검증한다.
- PV golden reference는 parity / sanity check에 사용하되, market-data 차이로 인한 수치 차이와 optimizer 로직 차이를 구분한다.
- **초기 구현 및 최초 검증에서는 전체 테스트 스위트를 실행하고 모든 테스트 결과를 확인한다.**
- **초기 검증 이후의 개발 반복 중에는 변경 영향 범위에 해당하는 테스트를 우선 실행한다.** 이는 빠른 피드백을 위한 개발 단계 규칙이다.
- 공통/core 코드 변경, 여러 모듈에 영향을 주는 변경, 또는 영향 범위가 불명확한 경우에는 개발 중에도 관련 상위 테스트 범위로 확대하고 필요하면 전체 테스트 스위트를 실행한다.
- **작업 완료로 보고하기 전에는 변경 범위와 관계없이 전체 테스트 스위트를 다시 실행해 기존 기능의 회귀(regression)가 없는지 확인한다.** 영향 범위 테스트만 통과한 상태로 완료 처리하지 않는다.
- 전체 회귀 테스트에서 실패가 발생하면 해당 실패가 이번 변경과 무관해 보이더라도 원인을 확인하고, 미해결 상태라면 완료가 아니라 blocker로 보고한다.
- solver 결과는 성공 여부뿐 아니라 weight sum, min/max, target volatility 등 constraint residual도 검증한다.

## Run outputs

- 일반 unit/integration test의 임시 출력은 repository에 저장하지 않고 `agent-to-llm.md`에 pass/fail 요약만 남긴다.
- LLM 또는 사용자가 검토해야 하는 **research / validation run의 실제 산출물은 `runs/<run_id>/` 아래에 저장하고 commit/push한다.**
- 최소 산출물은 `result.json`이다. 큰 표나 matrix가 필요하면 CSV로 분리할 수 있다.
- parity 검증을 수행한 run은 비교 결과도 같은 run 디렉터리에 machine-readable 파일로 남긴다. 예: `parity.json`.
- Interactive Report visual 검증을 수행한 run은 가능한 경우 `runs/<run_id>/validation/visual-comparison.md`와 핵심 screenshot evidence를 함께 보존한다. screenshot 저장이 도구 제약으로 불가능하면 비교 결과와 제약을 `visual-comparison.md`에 명시한다.
- run 산출물은 재현 가능한 입력/configuration과 실제 data coverage를 포함해야 한다.
- 완료 회신 시 `agent-to-llm.md`에 run 경로와 commit SHA를 남긴다.

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

Interactive Report의 same-input visual/behavioral acceptance reference는 `docs/visual-acceptance-contract.md`에 정의한다.

## AI Share

ChatGPT와 Codex 간 메시지 및 세션 handover에는 `./ai-share/PROTOCOL.md`를 따른다.

Agent 작업 결과는 `ai-share/agent-to-llm.md`에 최소한으로 정리하고 GitHub remote에 commit/push한 뒤 완료로 간주한다.
