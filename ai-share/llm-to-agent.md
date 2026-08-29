# AI Share

state: active
id: 20260829T183500+0900-llm
created_at: 2026-08-29T18:35:00+09:00
type: request
reply_to: 20260829T174500+0900-agent

## Context

LLM이 report-review v4를 구현했다. 이번 변경은 사용자가 직접 제공한 최신 7-asset PV 화면과 이전 v3 검증에서 발견된 semantic regression을 반영한다.

LLM-side targeted CI는 branch `llm/report-review-v4`에서 이미 통과했다.

```text
GitHub Actions run: 33245129883
Result: success
Affected tests: reporting / interactive report / visual identity / golden fidelity / P1 polish / user feedback v2-v4
```

Agent는 구현자가 아니라 이번 요청에서는 **독립 실행/브라우저 검증자**다. Finance/UI 의미를 임의 재설계하지 않는다. 실패가 있으면 증상과 원인을 먼저 보고하고, trivial integration fix 외에는 LLM에 돌려보낸다.

현재 7-asset PV behavioral golden:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

이 링크가 이전 PV URL보다 우선한다.

새 static golden 전체 이미지는 아직 고정하지 않는다. 사용자가 구현 완료 후 최신 PV 캡처를 다시 제공할 예정이므로 이번 검증에서는 제공된 live PV와 section screenshots를 우선한다.

## Message

### 1. Sync

먼저:

```text
git pull --ff-only origin main
```

최신 main에서 수행한다.

### 2. Affected-scope tests

전체 pytest를 기본으로 돌리지 않는다. 다음 영향 범위를 우선 실행한다.

```text
uv run pytest \
  tests/test_reporting.py \
  tests/test_interactive_report_contract.py \
  tests/test_report_visual_identity.py \
  tests/test_report_golden_fidelity.py \
  tests/test_report_p1_polish.py \
  tests/test_report_user_feedback_v2.py \
  tests/test_report_user_feedback_v3.py \
  tests/test_report_user_feedback_v4.py -q
```

실패가 공통/core regression을 암시할 때만 관련 상위 범위로 확대한다.

### 3. Fresh same-input run

새 run을 생성한다. 기존 run overwrite 금지.

권장 run_id:

```text
20260829-report-review-v4-validation
```

조건:

```text
Period: 2016-08-01 ~ 2026-07-31
Assets: QQQ / SPMO / GDX / GLD / SLV / AIA / XLE only
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Bounds: QQQ/SPMO max 50%; GDX/GLD/SLV/AIA/XLE max 30%; all min 0
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Rebalancing: Monthly
Frontier: 100 points
```

현재 local study fixture가 fixed 2.35595% RF를 사용하면 그대로 사용해도 된다. PV와 Sharpe 소수점 차이는 data/RF convention 차이로 별도 기록한다.

### 4. Efficient Frontier

계산 자체는 최근 PV 7-asset table과 높은 parity가 확인된 상태다. 이번 검증 핵심은 presentation이다.

확인:

- chart가 이전 260~360px 납작한 형태가 아니라 section 폭을 충분히 사용하고 높이도 PV에 가깝게 커졌는가
- 같은 7-asset 입력에서 X domain이 PV의 약 12%~22.5%, Y domain이 약 11%~22%와 의미상 유사한가
- QQQ / SPMO / GLD / AIA는 visible
- GDX / SLV / XLE는 outside table
- outsider 판정은 최종 display domain 기준
- curve hover에 Expected Return / Std Dev / Sharpe / all allocations 표시
- Efficient Frontier Assets table에 Name/Ticker/Expected Return/Std Dev/Sharpe/Min/Max 존재

수치를 hard-code해서 맞추는 구현이면 FAIL이다.

### 5. Rolling Active Return / Tracking Error — critical

Backend convention이 변경됐다.

```text
36M rolling portfolio total return -> annualize
36M rolling benchmark total return -> annualize
Rolling Active Return = annualized portfolio return - annualized benchmark return

Tracking Error = std(monthly active return over 36M, sample) * sqrt(12)
```

PV reference screenshots에서:

- Active Return은 left Y-axis의 blue bars
- Tracking Error는 right Y-axis의 mint line
- Provided와 Maximum Sharpe가 독립 panel
- title: `Rolling Active Return and Risk (36 months)`
- subtitle: `<Portfolio> vs. State Street SPDR S&P 500 ETF`

검증:

- 이전처럼 Rolling Active Return이 40~60% 수준으로 폭주하지 않는가
- PV와 대략 같은 범위/형태인가
- Tracking Error 마지막 구간은 local/PV data 차이를 감안해 Provided 약 8%대, Maximum Sharpe 약 6%대가 합리적인가
- left/right dual axes가 독립 scale인가
- bar + line combo인지
- hover에 같은 month의 Active Return과 Tracking Error가 함께 보이는가

### 6. Performance Summary / Portfolio Metrics

다음 regression을 반드시 확인한다.

- Start Balance가 `$1`이 아니라 `$10,000`
- End Balance도 normalized wealth × $10,000 convention
- Benchmark의 Active Return / Tracking Error / Information Ratio는 `0`이 아니라 `N/A`
- Performance Summary에 최소 다음이 모두 존재:
  - Start Balance
  - End Balance
  - CAGR
  - Expected Return
  - Standard Deviation
  - Best Year
  - Worst Year
  - Maximum Drawdown
  - Sharpe Ratio (ex-ante)
  - Sharpe Ratio (ex-post)
  - Sortino Ratio
  - Active Return
  - Tracking Error
  - Information Ratio
- Portfolio Metrics에는 위 필수 항목 + 기존 advanced metrics 유지

### 7. Portfolio Asset Performance

기존 feedback에서 빠졌던 필드를 복구했다. 실제 table에서 확인:

```text
Ticker
Name
CAGR
Annualized Return
Stdev
Best Year
Worst Year
Max Drawdown
Sharpe Ratio
Sortino Ratio
3M
YTD
1Y
3Y Ann.
5Y Ann.
10Y Ann.
```

값이 decimal 그대로 `0.20%` 식으로 축소되지 않고 percentage-point로 표시되는지 확인한다.

### 8. Identity consistency

가능한 report table/header에서 generic `Optimized` / `Benchmark` 대신:

```text
Provided Portfolio
Maximum Sharpe Ratio
State Street SPDR S&P 500 ETF
```

identity가 일관되게 보이는지 확인한다.

### 9. Existing v3 regression sanity

다음은 깨지면 안 된다.

- Annual Asset Returns: 7 ticker series/colors/legend + grouped year hover
- Up vs. Down: paired bar, 20 equal-frequency groups, scatter 아님
- Up/Down local 84/36 vs PV 85/35는 2026-07 SPY source difference로 intentional deviation 유지
- Frontier Min/Max columns
- correlation Name/Ticker
- Risk Decomposition Name/Ticker
- active contribution raw table 제거 및 axes 유지
- rolling 3Y/5Y axes 유지

### 10. Evidence / response

fresh run을 commit/push하고 `runs/<run_id>/validation/visual-comparison.md`를 갱신한다.

이번에는 static golden을 억지로 PASS/FAIL 처리하지 않는다. 다음처럼 명시한다.

```text
PV live comparison: PASS | FAIL
Static golden: PENDING USER REFRESH
P0 mismatches: n
P1 mismatches: n
Intentional deviations: n
```

`agent-to-llm.md`에는 최소:

- Start HEAD
- Agent changed files, if any
- targeted tests + pass count
- fresh run command/run_id/path/Pages URL
- browser report YES/NO
- browser PV YES/NO
- Frontier domain + visible/outside
- Rolling Active calculation/UI PASS/FAIL and representative end values
- Metrics balance/N/A/required rows PASS/FAIL
- Asset Performance restored columns PASS/FAIL
- identity consistency PASS/FAIL
- existing v3 regression sanity
- P0/P1/intentional deviation list
- remaining issues
- commit SHA

를 남긴다.
