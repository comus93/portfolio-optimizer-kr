# AI Share

state: active
id: 20260902T212500+0900-llm
created_at: 2026-09-02T21:25:00+09:00
type: request
reply_to: none

## Context

Backtest v1 OpenSpec의 사용자 decision gate D1-D11이 모두 확정되어 `openspec/changes/bt-module/`에 반영됐다.

주요 확정사항:

- v1 portfolio 1~3개, canonical model은 extensible collection
- Time Period: Month-to-Month(default) / Year-to-Year
- Calendar Aligned: Yes/No 모두 지원, frontend default Yes
- Calendar Aligned No: first active month anchor, quarterly=3개월 / semiannual=6개월 / yearly=12개월
- Rebalancing: run-level 공통, Monthly default, none/yearly/semiannual/quarterly/monthly 지원
- Cashflow / bands / leverage / Display Income / style / factor / regime는 v1 제외
- dividend toggle 없음, shared canonical total return
- benchmark frontend default SPY, initial balance default 10,000
- Backtest Experiment identity = union ticker set
- Backtest LLM analysis는 Optimization framework와 분리
- material layout/interaction change에만 human visual review gate

기존 `docs/*.md`는 수정하지 않고 baseline/reference로 유지한다.

## Message

최신 `bt-module`을 먼저 pull한 뒤 **구현은 시작하지 말고 OpenSpec artifact validation만 수행**해라.

먼저 다음을 실행한다.

```text
npx -y @fission-ai/openspec@latest status --change bt-module
npx -y @fission-ai/openspec@latest validate bt-module --strict
```

그리고 optimizer migration dependency도 현재 strict validation 상태를 확인한다.

```text
npx -y @fission-ai/openspec@latest status --change migrate-optimizer-to-openspec
npx -y @fission-ai/openspec@latest validate migrate-optimizer-to-openspec --strict
```

검토 범위:

1. OpenSpec schema/syntax가 유효한지
2. proposal / design / specs / tasks artifact completeness
3. `bt-module/specs/*` capability delta가 OpenSpec 규칙에 맞는지
4. D1-D11이 draft/pending/remaining decision으로 남아 있지 않은지
5. shared capability delta와 product/research/tooling capability 경계가 구조적으로 모순되지 않는지
6. 기존 requirement 의미를 임의 변경하지 않았는지

규칙:

- validation을 통과시키기 위해 requirement, 계산 의미, 사용자 결정, acceptance criterion을 변경하지 않는다.
- 단순 OpenSpec 문법/구조 오류라면 의미를 바꾸지 않는 최소 수정은 허용한다.
- 의미상 수정이 필요하거나 결정 충돌이 있으면 수정하지 말고 blocker로 회신한다.
- application/runtime 구현, dependency 변경, finance 코드 수정은 하지 않는다.

완료 후 `agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

회신 최소 내용:

- start HEAD
- bt-module status / strict validation 결과
- migrate-optimizer-to-openspec status / strict validation 결과
- validation을 위해 수정한 파일이 있으면 목록과 이유
- unresolved warning/blocker
- result commit SHA
