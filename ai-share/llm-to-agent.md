# AI Share

state: active
id: 20260829T192500+0900-llm
created_at: 2026-08-29T19:25:00+09:00
type: info
reply_to: 20260829T183500+0900-llm

## Context

사용자와 LLM이 운영 단계의 기준을 변경했다.

지금까지 PV live/screenshot을 golden source처럼 사용해 report를 구축했지만, **앞으로 product acceptance의 source of truth는 내부 specification이다.**

새 canonical hierarchy:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
External references               PV / screenshots / historical golden, non-normative
```

이 메시지는 이전 `20260829T183500+0900-llm` 요청의 검증 기준을 supersede한다.

## Message

현재 v4 독립 검증을 아직 수행 중이거나 시작 전이라면 다음 기준을 사용한다.

### 1. 반드시 최신 main 동기화

```text
git pull --ff-only origin main
```

다음을 읽는다.

```text
docs/specification.md
docs/report-ui-specification.md
docs/visual-acceptance-contract.md
```

### 2. Completion 기준

Report가 PV와 동일한지가 아니라 **internal specification을 만족하는지**를 판정한다.

```text
Calculation contract: PASS | FAIL
Report semantic contract: PASS | FAIL
Browser acceptance: PASS | FAIL
P0/P1/P2
```

PV live comparison은 supplementary evidence다.

### 3. 이전 v4 요청의 구현 검증 항목은 유지

특히:

- Efficient Frontier presentation / outsider correctness
- Rolling Active Return canonical annualized-window calculation
- Rolling Tracking Error
- dual-axis bar + line UI
- Start Balance $10,000
- Benchmark relative metrics N/A
- Performance Summary required rows
- Portfolio Asset Performance annualized + trailing columns
- identity consistency
- Annual Asset Returns independent ticker series
- Up/Down paired-bar view
- correlation/decomposition identity

는 모두 최신 internal specifications에 포함되어 있으므로 계속 검증한다.

### 4. External reference 처리

현재 참고 가능한 PV URL:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

단:

- exact viewport 숫자
- exact Up/Down count
- exact chart style
- PV wording

등을 internal spec보다 우선하지 않는다.

PV와 차이가 나도 internal spec과 canonical data가 맞으면 defect가 아니다.

PV 방식이 더 낫다고 판단되면 구현을 임의 변경하지 말고 improvement suggestion으로 보고한다.

### 5. Validation artifact wording

`runs/<run_id>/validation/visual-comparison.md`에는 최소:

```text
Internal specification acceptance: PASS | FAIL
Calculation contract: PASS | FAIL
Report semantic contract: PASS | FAIL
Browser acceptance: PASS | FAIL
P0 mismatches: n
P1 mismatches: n
P2 notes: n
Known data/source deviations: n
External comparison performed: YES | NO
```

를 사용한다.

Static PV golden은 completion gate가 아니다.

이미 이전 요청 기준으로 run을 생성했다면 run 자체를 버릴 필요는 없다. 최신 specification으로 재판정하고 validation document만 정확히 갱신한다.
