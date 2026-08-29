# Interactive Report Visual Acceptance Contract

이 문서는 `docs/specification.md`의 Interactive Report에 대한 browser/behavioral acceptance contract다.

목표는 Portfolio Visualizer(PV)의 pixel-perfect clone이 아니라, 동일 입력에서 사용자가 **같은 금융 의미를 읽고 비교할 수 있는 semantic parity와 충분한 presentation fidelity**를 확보하는 것이다.

---

## 1. Reference hierarchy

### Primary behavioral golden

현재 same-input PV live result:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

Current universe:

```text
QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Period: Aug 2016 - Jul 2026
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Max bounds: QQQ 50 / SPMO 50 / others 30
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100 points
```

PV live는 다음을 검증한다.

- chart type
- X/Y semantic
- axis/tick/domain behavior
- tooltip content/units
- series / marker / legend identity
- panel separation
- table composition
- interaction behavior

### Static golden

**현재 최신 full-page static golden은 PENDING USER REFRESH다.**

Report-review v4 구현 완료 후 사용자가 같은 7-asset PV 결과의 최신 screenshot을 제공하면 새 static baseline으로 고정한다.

이전 static image가 깨졌거나 asset universe가 다르면 same-input completion PASS 근거로 사용하지 않는다.

Historical files under `tests/golden/pv/`는 과거 information-structure/parity 참고용으로 유지할 수 있다.

---

## 2. Automated contract vs browser acceptance

두 검증은 서로 대체하지 않는다.

### Automated contract

최소:

- finance calculation convention
- required report fields
- missing != zero
- frontier weights sum 100%
- portfolio identity
- annual/rolling semantic X values
- rendered monetary/percentage unit contract when practical

### Browser acceptance

실제 generated `report.html`을 localhost HTTP에서 열어 직접 확인한다.

자동 테스트 PASS만으로 visual completion이라고 보고하지 않는다.

---

## 3. General chart contract

### Semantic axes

Row index를 semantic X value 대신 사용하지 않는다.

Time series:

```text
X = actual date / year
```

Efficient Frontier:

```text
X = Standard Deviation %
Y = Expected Return %
```

Frontier Transition:

```text
X = Standard Deviation %
Y = Allocation %
```

### Ticks / units

- 의미 있는 interval
- axis title
- readable density
- percentage/currency/date unit
- 과도한 overlap 없음
- 의미상 필요하지 않은 0 강제 포함 금지

### Missing value

```text
missing != zero
```

null/NaN을 0 observation으로 그리거나 표시하지 않는다.

---

## 4. Identity contract

Report 전체에서 가능한 한 다음 identity를 일관되게 사용한다.

```text
Provided Portfolio
<objective-aware optimized name, e.g. Maximum Sharpe Ratio>
<human-readable benchmark name>
```

Generic `Optimized`, `Benchmark`가 실제 portfolio identity를 대신해 여기저기 섞이지 않도록 한다.

같은 ticker는 report 전체에서 일관된 visual color identity를 유지한다.

---

## 5. Efficient Frontier

### Semantics

```text
X = Annualized Standard Deviation %
Y = Expected Annual Return %
```

표시:

- efficient frontier curve
- nearby individual assets
- Provided Portfolio
- Optimized Portfolio
- Benchmark

### Viewport

- curve raw extrema에 딱 붙이지 않는다.
- curve가 chart의 핵심이지만 nearby asset/landmark context를 충분히 보여준다.
- 극단적으로 먼 asset 때문에 curve가 지나치게 축소되지 않는다.
- final display domain 기준으로 asset visible/outside를 판정한다.
- final domain 안 asset을 outsider table로 보내면 FAIL이다.

Current 7-asset PV에서는 의미상 대략:

```text
X: 12% ~ 22.5%
Y: 11% ~ 22%
Visible: QQQ / SPMO / GLD / AIA
Outside: GDX / SLV / XLE
```

이 숫자를 hard-code하지 않고 presentation principle로 재현한다.

### Size

Desktop에서는 chart가 section 폭을 충분히 활용하고, curve/asset 위치를 한눈에 읽을 수 있는 높이를 확보한다. 260~360px의 납작한 chart로 눌리면 P1 failure다.

### Tooltip

Curve hover:

- Expected Return
- Standard Deviation
- Sharpe Ratio
- all asset allocations

Asset/landmark hover:

- identity
- Expected Return
- Std Dev
- Sharpe

### Asset table

```text
Name | Ticker | Expected Return | Std Dev | Sharpe Ratio | Min Weight | Max Weight
```

---

## 6. Frontier Transition

- stacked allocation area
- X = Std Dev
- Y = 0..100% allocation
- each frontier point weights sum 100%
- table allocation columns followed by Expected Return / Std Dev / Sharpe
- RF note must match actual run mode

---

## 7. Annual / Asset Returns

### Annual Returns

한 year hover에서:

- Provided
- Optimized
- Benchmark

annual return을 함께 표시한다.

### Annual Asset Returns

- ticker별 independent series/color
- generic single return series로 합치지 않는다.
- legend에 asset identity
- year hover에서 전체 asset Name/Ticker/return을 함께 표시

---

## 8. Active Return Contribution

Provided와 Optimized는 별도 panel/series group이다.

Ticker path key:

```text
(portfolio, ticker), ordered by date
```

Cross-portfolio sawtooth artifact는 P0다.

Raw debug table을 UI에 남기지 않는다.

---

## 9. Rolling Active Return and Risk

Provided / Optimized 각각 독립 panel.

```text
Title: Rolling Active Return and Risk (36 months)
Subtitle: <Portfolio> vs. <Benchmark>
```

Presentation:

```text
Active Return   = blue bars, left Y-axis
Tracking Error  = mint line, right Y-axis
```

두 scale을 하나의 Y축에 얹으면 FAIL이다.

Rolling Active Return 계산 convention은 `docs/specification.md`를 따른다.

```text
36M portfolio annualized return - 36M benchmark annualized return
```

36M total-return difference를 annualize 없이 표시하면 P0 semantic failure다.

Hover는 동일 month의 Active Return과 Tracking Error를 함께 표시한다.

---

## 10. Up vs. Down Market Performance

Provided와 Optimized 각각:

```text
conditional statistics table
+
Return vs. Benchmark paired bar chart
```

Scatter requirement는 폐기됐다.

Paired bar presentation:

- benchmark monthly return 오름차순 정렬
- 약 20 equal-frequency groups
- 120 observations이면 20 groups x 6 months
- each group: Portfolio / Benchmark mean-return bars
- X tick = mean Benchmark Return
- Y = Return %
- hover = Portfolio / Benchmark values + observation count

PV/local source가 benchmark sign에서 다르면 count를 hard-code하지 않는다. Exact divergent month와 source-data deviation을 기록한다.

Known current deviation: local FDR SPY 2026-07 sign difference로 84/36 vs PV 85/35가 발생할 수 있다.

---

## 11. Tables / Metrics

### Performance Summary minimum

```text
Start Balance
End Balance
CAGR
Expected Return
Standard Deviation
Best Year
Worst Year
Maximum Drawdown
Sharpe Ratio (ex-ante)
Sharpe Ratio (ex-post)
Sortino Ratio
Active Return
Tracking Error
Information Ratio
```

Normalized balance convention:

```text
1.0 -> $10,000
```

Benchmark Active Return / Tracking Error / Information Ratio는 `N/A`, not `0`.

### Portfolio Asset Performance

최소:

```text
Ticker / Name
CAGR / Annualized Return / Stdev
Best / Worst Year
MDD / Sharpe / Sortino
3M / YTD / 1Y / 3Y / 5Y / 10Y
```

Identity 추가 과정에서 기존 trailing columns를 제거하면 regression이다.

### Correlation / Decomposition

Asset identity는 Name + Ticker를 제공한다.

---

## 12. Other time-series charts

Drawdown / rolling 3Y / rolling 5Y / active contribution은:

- readable date ticks
- percentage Y ticks
- correct title/unit
- panel identity

를 제공한다.

---

## 13. Mandatory validation loop

Report UI 변경은 필요 범위에서:

```text
implement
-> affected automated tests
-> fresh same-input run
-> generated report browser open
-> current PV live open
-> section comparison
-> fix P0/P1
-> final validation artifact
```

Agent가 독립 검증자로 요청된 작업에서는 LLM implementation을 임의 redesign하지 않고 evidence를 우선 보고한다.

---

## 14. Validation evidence

`runs/<run_id>/validation/visual-comparison.md` 최소:

```text
PV live comparison: PASS | FAIL
Static golden: PASS | FAIL | PENDING USER REFRESH

P0 mismatches: n
P1 mismatches: n
Intentional deviations: n

Efficient Frontier
- domain
- visible/outside
- tooltip

Rolling Active Return and Risk
- calculation range
- left/right axes
- bars/line

Metrics
- balance unit
- benchmark N/A
- required rows

Remaining differences
- ...
```

Screenshot persistence가 도구 제약으로 불가능한 것 자체는 blocker가 아니다. 직접 비교 evidence를 문서에 남긴다.

---

## 15. Completion rule

Interactive Report 작업 완료는 현재 작업 scope에 대해:

1. affected automated contracts pass
2. same-input generated report browser acceptance pass
3. current PV live comparison과 intentional deviations가 durable artifact로 기록
4. static golden이 필요한 completion gate라면 최신 same-input image가 확보됨

을 만족해야 한다.

P0 semantic mismatch가 하나라도 남으면 완료가 아니다.
