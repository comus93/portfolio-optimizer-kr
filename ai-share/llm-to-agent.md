# AI Share

state: active
id: 20260902T222000+0900-llm
created_at: 2026-09-02T22:20:00+09:00
type: request
reply_to: none

## Context

사용자 결정에 따라 LLM이 **테스트 코드를 먼저 작성한 뒤 Backtest v1 실제 구현을 이어서 반영했다.** 이제 Agent 역할은 새 요구사항을 설계하는 것이 아니라 실제 checkout에서 테스트/수정/real-run/browser 검증을 수행하고 결과를 보고하는 것이다.

Branch: `bt-module`

Backtest v1 핵심 contract:

- Optimization과 독립 product mode
- 1~3 portfolio, canonical model은 extensible collection
- Time Period: Month-to-Month(default) / Year-to-Year
- Calendar Aligned: Yes(default) / No
  - No는 first active month anchor, quarterly=3개월 / semiannual=6개월 / yearly=12개월
- Rebalancing은 run-level 공통, Monthly default, none/yearly/semiannual/quarterly/monthly
- Benchmark Research Frontend default SPY, explicit override/none 허용
- Initial Amount default 10,000
- Experiment identity = union ticker set
- cashflow / rebalance bands / leverage / Display Income / style / factor / regime는 v1 제외
- dividend toggle 없음. shared canonical total-return 사용
- Backtest LLM analysis는 Optimization framework와 분리
- material layout/interaction change에만 human visual review gate
- 기존 `docs/*.md`는 수정하지 않고 baseline/reference로 유지

주요 구현:

- `tests/test_backtest*.py`, `tests/test_verification_profile.py`
- `src/portfolio_optimizer_kr/models.py`
- `src/portfolio_optimizer_kr/config/yaml.py`
- `src/portfolio_optimizer_kr/portfolio/returns.py`
- `src/portfolio_optimizer_kr/backtest.py`
- `src/portfolio_optimizer_kr/runner.py`
- `src/portfolio_optimizer_kr/research.py`
- `src/portfolio_optimizer_kr/report/backtest.py`, `report/writer.py`
- `src/portfolio_optimizer_kr/viewer/backtest_renderer.py`, `viewer/generate.py`
- `src/portfolio_optimizer_kr/data/transform.py`, `data/fdr.py`
- `ui/app.py`
- `configs/backtest-example.yaml`
- `verification/profile.yaml`, `scripts/verify.py`, `VERIFICATION.md`

Total-return 관련 중요사항:

현재 구현은 shared OpenSpec의 "price-only silent fallback 금지"를 지키기 위해 FDR asset load에서 `Adj Close`가 명시적으로 존재할 때만 canonical total-return asset series로 인정한다. `Close`만 있으면 `DataValidationError`로 실패한다. 이 정책을 테스트 통과 목적으로 완화하지 마라.

FinanceDataReader의 해외자산은 `Adj Close`를 제공하는 것으로 기대하지만 실제 환경에서 확인해야 한다. 국내 KRX ETF는 source별로 `Adj Close`가 없을 수 있으므로 실제 데이터를 확인하고, 신뢰할 수 있는 total-return route를 명확히 확인할 수 없다면 **Close fallback을 추가하지 말고 blocker/deviation으로 보고**한다.

## Message

먼저 최신 remote를 동기화한다.

```bash
git pull --ff-only origin bt-module
```

미커밋 변경/divergence 때문에 안전하게 pull할 수 없으면 remote 최신 상태를 직접 확인하고 blocker를 보고한다.

### 1. OpenSpec validation

구현 변경 전에/함께 현재 spec artifact도 strict validation한다.

```bash
npx -y @fission-ai/openspec@latest status --change bt-module
npx -y @fission-ai/openspec@latest validate bt-module --strict
npx -y @fission-ai/openspec@latest status --change migrate-optimizer-to-openspec
npx -y @fission-ai/openspec@latest validate migrate-optimizer-to-openspec --strict
```

OpenSpec 문법/구조 오류는 requirement 의미를 바꾸지 않는 최소 수정만 허용한다. 의미 충돌이면 blocker다.

### 2. Test verification

우선 repository verification entrypoint를 실행한다.

```bash
uv run python scripts/verify.py --openspec --full
```

필요하면 실패 원인 파악을 위해 개별 테스트를 다시 실행한다.

특히 확인할 범위:

```text
Backtest config / Time Period / v1 scope validation
Calendar Aligned Yes/No rebalancing semantics
run-level rebalancing
multi-portfolio independent paths
actual initial-balance wealth path
Backtest result/raw/review persistence
Backtest report dispatch
Research Frontend defaults + explicit benchmark none
Optimization runner/research/portfolio regression
shared total-return data selector
```

테스트/requirement를 약화, 삭제, skip, xfail하지 않는다. 구현 버그이면 구현을 수정하고 영향을 받은 테스트를 다시 실행한다. 테스트가 OpenSpec과 모순된다고 판단되면 임의 수정하지 말고 blocker로 보고한다.

### 3. FinanceDataReader total-return real data check

실제 환경에서 최소 다음을 확인한다.

```python
import FinanceDataReader as fdr
print(fdr.DataReader("QQQ", "2025-01-01").columns)
print(fdr.DataReader("GLD", "2025-01-01").columns)
print(fdr.DataReader("SPY", "2025-01-01").columns)
```

`Adj Close` 존재와 실제 canonical loader 동작을 확인한다.

또한 국내 ETF 한 개 이상(예: `140710` 또는 `069500`)을 조회해 FDR 기본 source가 total-return-capable field를 제공하는지 확인한다. `Close`만 있다는 이유로 total return이라고 가정하지 않는다. 필요하면 FDR의 명시적 Yahoo source 등 대안을 조사할 수 있지만 source mapping의 신뢰성이 불명확하면 구현을 임의 확장하지 말고 blocker로 보고한다.

### 4. Real Backtest runs

`configs/backtest-example.yaml`을 직접 수정/커밋하지 말고 임시 복사본에서 unique `run_id`를 사용하여 실제 FDR run을 수행한다.

대표 실행 예:

```bash
uv run portfolio-optimizer run <temporary-backtest-yaml>
```

최소 real-run 검증:

1. `QQQ / GLD`, benchmark `SPY`, 2 portfolios, Month-to-Month, Monthly, Calendar Aligned=Yes
2. 가능하면 3 portfolios, benchmark=None, Year-to-Year, Quarterly, Calendar Aligned=No인 두 번째 run

각 run에서 확인:

- `result.json`에 optimization/frontier domain이 없음
- portfolio identity와 target weights가 섞이지 않음
- first wealth point가 actual initial amount
- effective period/observation count가 합리적
- `raw/`, `review/`, `report.html` 생성
- benchmark 없을 때 benchmark-relative section이 non-applicable/미표시
- Calendar Aligned No가 첫 active month anchor semantics를 따름

사용자/LLM이 검토할 대표 validation run은 기존 repository 운영 규칙에 맞게 `runs/<unique-run-id>/`에 보존하고 필요한 validation evidence를 `validation/`에 남긴다. 기존 run은 overwrite하지 않는다.

### 5. Browser semantic verification

생성된 Backtest `report.html`을 localhost HTTP context에서 실제 browser로 확인한다.

필수 machine-judgeable checks:

- Overview에 Time Period / requested-effective period / Initial Amount / Benchmark / Rebalancing / Calendar Aligned가 표시됨
- Target Allocation에서 portfolio/asset identity가 구분됨
- Growth chart가 실제 balance scale이며 portfolio legend/point identity가 있음
- Performance/Annual/Monthly/Drawdown/Rolling/Correlation/Decomposition section이 applicable data를 표시함
- Efficient Frontier / optimization-only section이 없음
- benchmark=None run에서는 benchmark-relative section을 허위 0값으로 만들지 않음
- narrow/mobile viewport에서 필수정보가 clipping으로 소실되지 않음

PV pixel parity는 검사하지 않는다.

이번 구현은 새 Backtest report layout을 추가하므로 대표 report에 대해 human visual review도 수행하고 P0/P1/P2 또는 deviation을 기록한다.

### 6. Fix and re-verify

구현 문제는 Agent가 직접 수정해도 된다. 수정 후 affected test → real run → browser를 다시 수행한다.

단 다음은 금지:

- OpenSpec requirement/사용자 결정 변경
- 계산 규칙 변경으로 테스트 맞추기
- 테스트 삭제/완화/skip
- price-only `Close`를 total return으로 silent fallback
- 기존 docs를 Backtest 요구사항 source로 수정

의미상 설계 결정이 새로 필요하면 blocker로 남긴다.

### 7. Result handoff

완료 후 `ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

최소 보고:

- start HEAD / final HEAD
- 수정한 파일과 이유
- OpenSpec strict validation 결과
- targeted + full pytest 결과
- FDR `Adj Close`/total-return 확인 결과, 특히 US ETF와 KRX ETF
- real run command / run_id / run path
- 핵심 result sanity values
- browser/human visual verification 결과와 P0/P1/P2
- unresolved deviation/blocker
- result commit SHA

Agent 회신은 GitHub remote에 push되어야 완료로 간주한다.
