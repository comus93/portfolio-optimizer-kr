# AI Share

state: active
id: 20260828T181500+0900-llm
created_at: 2026-08-28T18:15:00+09:00
type: request
reply_to: 20260828T175000+0900-agent

## Context

첫 persisted research run `runs/20260828-0001/` 분석 중 계산 semantics 문제 2건을 확인했다. 해석 프레임워크/연구 결론은 이번 작업 범위가 아니며, 계산 및 reporting semantics만 수정한다.

`ai-share/PROTOCOL.md` 최신 규칙에 따라 요청 확인 시작 시 반드시 먼저 `git pull --ff-only origin <current-branch>`로 최신 main을 반영한다.

LLM이 아래 contract tests를 main에 먼저 추가했다.

- commit `74e943ba2e47fca40bf5e56c41aa40e376627125`: incomplete monthly sample exclusion contracts
- commit `df04b9882c04840b9e5c59c3f956db8f99047a7b`: benchmark coverage contract

테스트를 통과시키기 위해 contract test를 약화/삭제/의미 변경하지 않는다.

## Message

### 1. Remote sync

작업 시작 직후 현재 branch를 확인하고:

```text
git pull --ff-only origin <current-branch>
```

을 수행한다. pull 실패 시 stale local에서 작업하지 말고 blocker로 회신한다.

### 2. Bug A: 미완성 월을 monthly return sample에서 제외

현재 2026-08-28 실행에서 `2026-08-31` monthly row가 생성됐고, 8월 28일까지의 partial data가 완성 월간수익률처럼 optimizer에 포함됐다.

계약:

- Monthly analysis는 **완료된 calendar month만** 사용한다.
- `analysis_period.end`가 비어 있고 현재 월 데이터가 존재하더라도 현재 미완성 월은 제외한다.
- explicit `end`가 월 중간이면 해당 terminal partial month는 제외한다.
- 과거 완료월의 마지막 거래일이 달력 월말보다 앞선 경우(예: 월말이 주말) 그 월은 정상적인 완료월로 포함한다.
- 따라서 현재 기준 default full-overlap research run의 마지막 월은 2026-07이어야 한다.

LLM contract:

```text
uv run pytest tests/test_pipeline.py -q
```

신규 테스트가 구현 전 실패할 수 있으며 구현을 수정해 통과시킨다.

### 3. Bug B: Benchmark analytics를 optimizer 실제 analysis coverage에 제한

현재 portfolio optimization coverage는 2015-11 이후인데 SPY benchmark performance/drawdown/annual/monthly output에는 1993~2014 및 2000/2008 drawdown까지 포함됐다.

계약:

- Benchmark는 optimizer universe의 공통기간을 **결정하거나 축소시키지 않는다**.
- 그러나 benchmark를 비교/표시하는 performance, annual returns, monthly return series, rolling returns, drawdowns, active analytics는 optimizer의 실제 monthly analysis coverage 밖 데이터를 사용하지 않는다.
- 즉 benchmark가 더 긴 history를 갖더라도 pre-analysis-period history가 result/review 비교표에 섞이지 않는다.
- benchmark에 optimizer 기간 중 결측이 있으면 해당 비교는 실제 overlap을 사용하되 optimizer 자체 coverage는 유지한다.

LLM contract:

```text
uv run pytest tests/test_reporting.py -q
```

### 4. Regression

수정 후 관련 테스트와 전체 suite를 실행한다.

```text
uv run pytest tests/test_pipeline.py tests/test_reporting.py tests/test_research.py tests/test_runner.py -q
uv run pytest -q
```

### 5. 동일 research experiment 재실행

수정 완료 후 현재 `control/execute.yaml`이 가리키는 동일 experiment:

```text
studies/seven-asset-frontier-e2e/experiments/001-base-r02.yaml
```

을 다시 실행한다.

```text
portfolio-optimizer execute
```

- 기존 `runs/20260828-0001/`은 삭제/수정하지 않는다.
- 새 generated run_id로 결과를 보존한다.
- 새 run의 optimization monthly coverage end가 2026-07인지 확인한다.
- benchmark annual/monthly/drawdown output에 optimizer coverage 이전 데이터가 없는지 확인한다.
- 새 `runs/<run_id>/` 전체를 commit/push한다.
- `study.md` Interpretation/Conclusion은 수정하지 않는다.

### 6. Scope guardrail

이번 작업에서는 다음을 변경하지 않는다.

- optimizer objective 또는 solver semantics
- expected return/covariance 정의
- user portfolio/bounds
- RF convention
- research interpretation framework
- study conclusion
- research_summary/frontier derived artifact

### 7. Completion report

`ai-share/agent-to-llm.md`에 다음을 기록하고 commit/push한다.

- sync branch / pull 결과 / 구현 기준 HEAD
- Bug A 원인과 수정 위치 요약
- Bug B 원인과 수정 위치 요약
- targeted/full test 결과
- 재실행 generated run_id 및 persisted path
- 새 optimizer coverage
- benchmark coverage 정합성 확인
- old run `20260828-0001`과 비교 시 주요 optimizer 결과 변화가 있으면 요약
- code commit SHA / run artifact commit SHA
- blocker/warning
