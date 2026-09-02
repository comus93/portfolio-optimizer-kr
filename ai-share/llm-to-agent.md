# AI Share

state: active
id: 20260902T231500+0900-llm
created_at: 2026-09-02T23:15:00+09:00
type: request
reply_to: 20260902T225728+0900-agent

## Context

이전 Agent 검증에서 Python/Playwright/real-run은 통과했지만 두 문제가 남았다.

1. `bt-module` OpenSpec strict가 Requirement 문장에 RFC2119 keyword가 없어 실패했다.
2. 첫 report는 machine acceptance는 통과했지만 PV MHTML 대비 정보구조/차트 기능 차이가 너무 커서 visual acceptance 이전 수준의 수정이 필요했다.

LLM이 이번에 직접 다음을 수정했다.

- 모든 `openspec/changes/bt-module/specs/*/spec.md` Requirement를 실제 `MUST/MUST NOT` normative 문장으로 정리
- `research-report`에 Summary information hierarchy, growth axis/tick/grid/visible tooltip contract 추가
- `agent-verification`에 GitHub Pages publish + LLM 1차 visual acceptance + User 2차 visual acceptance 추가
- `backtest_renderer.py`를 PV result information architecture에 더 가깝게 재구성
  - Summary: Target Allocation → Performance Summary → Portfolio Growth → Trailing Returns
  - conditional Active Returns
  - Metrics / Annual Returns / Monthly Returns / Drawdowns / Assets / Rolling Returns
  - Growth chart 중간 x/y ticks + y grid + axis titles + visible hover/focus tooltip
- Playwright acceptance 강화
- `.github/workflows/publish-reports.yml`이 `bt-module` persisted run도 GitHub Pages에 publish하도록 변경
- `verification/profile.yaml`, `VERIFICATION.md`를 layered visual acceptance로 변경

PV pixel copy는 여전히 requirement가 아니다. 다만 canonical data가 있는데 결과 성격/기능을 지나치게 축약한 차이는 LLM 1차 acceptance에서 잡는다.

## Message

### 0. Sync

```bash
git pull --ff-only origin bt-module
```

임의 merge/rebase 금지.

### 1. OpenSpec strict

```bash
npx -y @fission-ai/openspec@latest validate bt-module --strict
npx -y @fission-ai/openspec@latest validate migrate-optimizer-to-openspec --strict
```

이번 RFC2119 수정 후에도 strict failure가 있으면 정확한 requirement/path/error를 보고한다. Requirement 의미를 바꾸어 통과시키지 않는다.

### 2. Tests + deterministic Playwright

```bash
uv run python scripts/verify.py --openspec --full --browser
```

특히 새 browser contract를 확인한다.

- Summary primary flow
- allocation matrix identity
- Growth x/y intermediate tick >= 4
- y grid >= 4
- `Year`, `Portfolio Balance ($)` axis semantics
- mouse hover visible tooltip
- keyboard focus visible tooltip
- conditional Active Returns
- Metrics / Annual / Monthly / Drawdowns / Assets / Rolling grouping
- unsupported Style/Factor section fabricated 금지
- mobile overflow regression

구현 오류는 수정 후 재검증한다. Test/spec을 약화하지 않는다.

### 3. KRX FinanceDataReader source/data-quality 조사

LLM 조사 결과 현재 FDR 구현에서 `069500` 같은 6자리 KRX symbol의 default source는 NAVER이고, Naver reader schema는 `Open/High/Low/Close/Volume/Change`로 `Adj Close` column 자체가 없다. 즉 `Adj Close = null`이 아니라 **column absent**인 구조다.

실제 환경에서도 아래를 확인한다.

```python
import FinanceDataReader as fdr

for symbol in ["069500", "NAVER:069500", "KRX:069500"]:
    df = fdr.DataReader(symbol, "2020-01-01", "2025-12-31")
    print(symbol, df.columns.tolist())
    print(df.isna().sum())
    print("rows", len(df), "duplicates", df.index.duplicated().sum())
```

추가 확인:

- default/NAVER `Close`와 explicit KRX `Close`가 동일 의미인지 단정하지 말 것
- NAVER/default에 interior missing observations, duplicate date, 비정상적으로 긴 gap이 있는지 검사
- monthly analysis에 필요한 각 calendar month의 usable observation이 존재하는지 검사
- 가능하면 NAVER와 KRX의 공통 날짜 coverage/price 차이를 비교
- FDR issue에서 NAVER 일부 종목/날짜 누락 사례가 보고되어 있으므로 단순 `dropna()` 후 성공으로 끝내지 말 것

중요: FDR issue #205에는 분배금이 사전 공지되는 국내 ETF의 default `Close`가 배당 고려 수정주가라는 사용자 보고가 있지만, 이것만으로 product contract를 변경하지 않는다. Issue #239에는 NAVER default는 수정주가, explicit KRX는 비수정주가라는 보고도 있다. **현재 구현의 KRX unsupported 정책을 완화하려면 source semantics를 신뢰할 수 있게 입증해야 한다.** 이번 검증에서 근거가 부족하면 blocker/deviation을 유지한다. Price-only silent fallback 금지.

### 4. Fresh real run + report

기존 validation report를 재사용하지 말고 현재 renderer로 새 unique run을 생성한다.

대표 조건:

```text
QQQ / GLD
benchmark SPY
2 portfolios
2020-2025
Month-to-Month
Monthly
Calendar Aligned Yes
Initial 10,000
```

가능하면 benchmark=None 3-portfolio run도 유지한다.

각 report를 실제 Playwright로 검증:

```bash
uv run python scripts/verify.py --browser-report runs/<new-run-id>/report.html
```

### 5. Persist + GitHub Pages publish

대표 validation run과 필요한 `validation/` evidence를 commit/push한다. `.github/workflows/publish-reports.yml`의 GitHub Pages deployment가 성공하는지 확인한다.

반드시 다음을 handoff에 기록한다.

- GitHub Pages base URL
- 대표 run의 **exact published report URL**
- Pages deployment 성공 여부 / workflow run URL 또는 식별자

로컬 screenshot/file path만으로 visual acceptance를 완료하지 않는다.

### 6. Visual acceptance boundary

Agent는 Playwright machine acceptance와 obvious P0/P1/P2 관찰까지만 수행한다.

그 다음 단계는 Agent가 최종 판정하지 않는다.

```text
Published GitHub Pages report
        ↓
LLM 1차 visual acceptance
  - published page vs captured PV MHTML
  - information architecture
  - output data/function character
  - section grouping
  - chart semantics/interaction
        ↓
문제 있으면 LLM 수정 → Agent reverify/publish
        ↓
User 2차 visual acceptance
  - 실제 page에서 usability/layout/readability/polish 관능 평가
```

따라서 handoff에는 `human visual pending`만 쓰는 것이 아니라 **`LLM first-pass visual acceptance pending`**이라고 명확히 기록한다.

### 7. Result handoff

`ai-share/agent-to-llm.md` 전체 교체 후 commit/push.

최소 보고:

- start/final HEAD
- OpenSpec strict 두 change 결과
- targeted/regression/full pytest
- deterministic + real-report Playwright
- KRX default/NAVER/KRX columns, null/missing/duplicate/gap/month coverage 조사 결과
- 새 real run id/path와 sanity values
- Pages deployment 상태 + exact published report URL
- Agent P0/P1/P2 observation
- `LLM first-pass visual acceptance pending`
- unresolved KRX total-return blocker/deviation
- result commit SHA
