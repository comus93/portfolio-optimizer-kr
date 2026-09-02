# AI Share

state: active
id: 20260902T224200+0900-llm
created_at: 2026-09-02T22:42:00+09:00
type: request
reply_to: none

## Context

Backtest v1 구현과 테스트가 `bt-module`에 반영되어 있다. 이번 요청의 Agent 역할은 요구사항 재설계가 아니라 **실제 checkout에서 dependency setup → test → real run → Playwright browser verification → evidence/reporting → 필요 시 구현 수정/재검증**이다.

사용자 환경 참고:

- Codex Full CDP Access는 이미 활성화되어 있다.
- 그러나 canonical automated browser acceptance는 repository-local **Playwright Chromium**이다.
- CDP는 추가 진단용으로 사용할 수 있으며 Playwright를 대체하지 않는다.

새 browser verification 구성:

```text
package.json
playwright.config.mjs
scripts/prepare_browser_fixture.py
verification/browser/backtest-report.spec.mjs
verification/profile.yaml
scripts/verify.py
VERIFICATION.md
```

Playwright는 localhost HTTP server에서 report를 검사한다. `file://` 검증이나 PV pixel-diff는 사용하지 않는다.

## Message

### 0. Sync

```bash
git pull --ff-only origin bt-module
```

pull이 안전하지 않으면 임의 merge/rebase하지 말고 blocker를 보고한다.

### 1. One-time Playwright setup

Node/npm 상태를 확인하고 repository root에서 실행한다.

```bash
node --version
npm --version
npm install
npx playwright install chromium
```

- `npm install`로 정상 생성된 `package-lock.json`은 dependency lockfile로 commit/push한다.
- 설치/Chromium download를 위해 network permission이 필요하면 사용자 승인을 받아 진행한다.
- 테스트 통과를 위해 Playwright dependency/version 또는 browser check를 임의 제거하지 않는다.

### 2. OpenSpec + Python tests + deterministic browser fixture

```bash
uv run python scripts/verify.py --openspec --full --browser
```

이 명령은 다음을 수행해야 한다.

```text
OpenSpec strict validation
→ targeted Backtest tests
→ affected Optimization regression
→ full pytest
→ deterministic Backtest fixture 생성
→ Playwright semantic/responsive acceptance
```

Playwright fixture는 benchmark 있음/없음 두 report를 검사한다.

Browser checks:

- Overview: Time Period Mode / Requested Period / Effective Period / Initial Amount / Benchmark / Rebalancing / Calendar Aligned / Return Semantics
- Target Allocation: portfolio / ticker / target weight identity
- Growth chart: portfolio / date / actual balance semantics
- Performance / Annual / Monthly / Drawdown / Rolling / Correlation / Decomposition 존재
- Optimization-only `Efficient Frontier`, `Optimized Portfolio` 없음
- benchmark=None이면 benchmark-relative section 없음
- 390px viewport에서 document-level horizontal clipping 없음
- 넓은 table/chart는 자체 horizontal scroll 가능

PASS 시에도 desktop/mobile screenshot이 Playwright test output에 생성된다. 실패 시 trace/screenshot도 남는다.

### 3. FinanceDataReader total-return real-data check

현재 contract는 canonical total return이며 price-only silent fallback은 금지다.

최소 확인:

```python
import FinanceDataReader as fdr
print(fdr.DataReader("QQQ", "2025-01-01").columns)
print(fdr.DataReader("GLD", "2025-01-01").columns)
print(fdr.DataReader("SPY", "2025-01-01").columns)
print(fdr.DataReader("069500", "2025-01-01").columns)
```

- US ETF에서 `Adj Close`와 canonical loader 동작 확인
- KRX ETF에서 total-return-capable field/source 확인
- KRX에서 신뢰할 수 있는 total-return route를 확인하지 못하면 `Close` fallback을 추가하지 말고 blocker/deviation으로 보고

### 4. Real Backtest run

`configs/backtest-example.yaml`을 직접 변경/커밋하지 말고 임시 복사본과 unique run_id를 사용한다.

최소 대표 run:

```text
QQQ / GLD
benchmark SPY
2 portfolios
Month-to-Month
Monthly rebalance
Calendar Aligned Yes
Initial Amount 10,000
```

가능하면 추가 run:

```text
3 portfolios
benchmark None
Year-to-Year
Quarterly
Calendar Aligned No
```

확인:

- `result.json`에 optimization/frontier domain 없음
- portfolio identity/target weights 독립
- actual initial balance 반영
- period/observation count 정상
- `raw/`, `review/`, `report.html` 생성
- benchmark None이면 benchmark-relative artifact/UI가 허위 생성되지 않음
- Calendar Aligned No가 first-active-month anchor 의미를 따름

대표 validation run은 기존 overwrite 금지 원칙을 지켜 보존한다.

### 5. Playwright verification against the real report

실제 run의 report를 아래 entrypoint로 검사한다.

```bash
uv run python scripts/verify.py --browser-report runs/<run-id>/report.html
```

또는 동등하게 `BACKTEST_REPORT_PATH`를 지정해 `npx playwright test`를 실행할 수 있다.

Playwright output:

```text
playwright-report/
test-results/playwright/
```

대표 validation evidence를 영구 보존할 필요가 있으면 필요한 desktop/mobile screenshot과 요약을 `runs/<run-id>/validation/`에 복사해 commit한다.

### 6. Visual review boundary

Agent는 screenshot을 보고 명백한 clipping, overlap, unreadable label, broken layout 등의 P0/P1/P2 관찰을 기록할 수 있다.

하지만 **human visual acceptance의 최종 PASS는 Agent가 대신 선언하지 않는다.** Agent는 screenshot/evidence와 관찰사항을 준비한다. 사용자가 최종 visual gate를 판단한다.

Full CDP Access는 Playwright 실패 원인 추적, DOM/console/network 조사에 자유롭게 사용해도 된다.

### 7. Fix and re-verify

구현 버그는 직접 수정하고 affected 단계부터 다시 실행한다.

금지:

- OpenSpec requirement/사용자 결정 변경
- finance 계산 규칙을 테스트에 맞춰 임의 변경
- 테스트 삭제/완화/skip/xfail
- price-only `Close`를 total return으로 silent fallback
- 기존 `docs/*.md`를 Backtest normative source로 변경
- Playwright check를 통과시키기 위해 검사 자체를 약화

새로운 제품/finance 의사결정이 필요하면 blocker로 남긴다.

### 8. Result handoff

완료 후 `ai-share/agent-to-llm.md`를 최신 result 하나로 교체하고 commit/push한다.

최소 보고:

- start HEAD / final HEAD
- Node/npm/Playwright setup 결과와 `package-lock.json` commit 여부
- OpenSpec strict validation
- targeted / affected regression / full pytest
- deterministic Playwright 결과
- FDR US/KRX total-return 확인
- real run command / run_id / path / 핵심 sanity values
- real-report Playwright 결과
- desktop/mobile screenshot evidence 위치
- visual P0/P1/P2 관찰사항, human gate는 pending으로 표시
- unresolved blocker/deviation
- result commit SHA

remote push까지 완료되어야 handoff 완료로 간주한다.
