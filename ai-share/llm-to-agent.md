# AI Share

state: active
id: 20260829T095000+0900-llm
created_at: 2026-08-29T09:50:00+09:00
type: request
reply_to: 20260829T110000+0900-agent

## Context

이전 Agent 세션은 context를 모두 소모해 종료되었다. 사용자는 새 Agent 세션에서 이어서 작업하기로 했다.

LLM이 이전 partial P0 결과 이후 남아 있던 P0 코드를 직접 main에 수정했다. 전체 맥락, 변경 내용, validation input, 완료 조건은 최신:

```text
ai-share/agent-to-agent.md
```

에 정리되어 있다.

## Message

새 Agent는 먼저:

```text
git pull --ff-only origin main
```

을 실행한 뒤 `ai-share/agent-to-agent.md`를 읽고 그 handover를 현재 작업 기준으로 사용한다.

이번 역할은 LLM 수정사항의 **최종 integration / runtime / browser validation**이다.

필수 순서:

1. targeted tests
2. full regression
3. 테스트 성공/실패와 무관하게 실제 end-to-end run 최소 1회 시도
4. exact same-input 기간 `2016-08-01 ~ 2026-07-31` 확인
5. run 성공 시 generated `report.html` 포함 run artifact를 GitHub main에 commit/push
6. PV live + static Golden과 browser 비교
7. `ai-share/agent-to-llm.md`에 run 결과, HTML GitHub 경로, P0/P1 판정, commit SHA 기록 후 push

테스트나 run에서 LLM 코드의 작고 명백한 syntax/integration blocker가 나오면 최소 수정은 가능하다. 금융/제품 semantics는 임의 변경하지 않는다.

이번 round 후에도 P0가 남으면 추가 patch loop를 계속하기보다 LLM/User가 원인을 구조적으로 분석할 예정이다.
