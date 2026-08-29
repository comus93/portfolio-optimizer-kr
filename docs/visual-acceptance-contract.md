# Interactive Report Validation Contract

## 1. Purpose

이 문서는 Interactive Research Report의 **검증 절차와 completion rule**을 정의한다.

이 문서는 UI 제품 요구사항 자체를 정의하지 않는다.

Normative source:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
```

이 문서의 역할은 위 specification을 구현한 report가 실제 browser에서 올바르게 동작하는지 확인하는 것이다.

---

## 2. External References Are Non-Normative

Portfolio Visualizer(PV), screenshots, historical golden files 등 외부 reference는 다음 용도로 사용할 수 있다.

- defect discovery
- numerical sanity check
- data-source deviation 조사
- alternative presentation idea 비교
- historical implementation regression investigation

하지만 외부 reference의 현재 동작은 product requirement가 아니다.

다음 규칙을 따른다.

```text
internal specification > external reference
```

External reference가 달라졌다는 이유만으로 우리 implementation을 변경하지 않는다.

현재 유용한 7-asset external comparison fixture:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

Input context:

```text
QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Period: Aug 2016 - Jul 2026
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Max bounds: QQQ 50 / SPMO 50 / others 30
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100 points
```

이 fixture는 regression investigation을 위해 유지하되 acceptance source로 사용하지 않는다.

Static screenshot도 동일하다. Screenshot은 특정 시점의 외부 비교 evidence일 뿐 product contract가 아니다.

---

## 3. Validation Layers

### 3.1 Calculation Contract

`docs/specification.md` 기준으로 automated tests를 수행한다.

최소 확인:

- finance formula
- data coverage
- constraint residual
- optimization result invariants
- frontier weight sum
- historical portfolio path
- performance/active-return metrics
- rolling calculation convention
- decomposition invariants

### 3.2 Report Semantic Contract

`docs/report-ui-specification.md` 기준으로 automated/rendered assertions를 수행한다.

예:

- correct identity labels
- correct unit formatting
- required rows/columns
- missing != zero
- canonical balance 1.0 -> $10,000
- benchmark relative metrics -> N/A
- rolling active return uses canonical value
- independent asset series identity

### 3.3 Browser Acceptance

실제 generated `report.html`을 browser에서 연다.

`file://`가 아니라 localhost HTTP 또는 equivalent served context를 우선한다.

자동 test PASS만으로 visual completion이라고 판단하지 않는다.

---

## 4. General Browser Checks

모든 report에서 다음을 확인한다.

### Layout

- section clipping 없음
- table/chart가 container 밖으로 비정상 overflow하지 않음
- desktop 주요 chart가 지나치게 작지 않음
- mobile에서 정보 손실 없이 scroll/wrap 가능

### Identity

- Provided Portfolio
- objective-aware optimized name
- human-readable benchmark name
- asset Name/Ticker

가 specification대로 일관되는지 확인한다.

### Units

- percentage
- ratio
- currency
- date/year

가 의미에 맞게 표시되는지 확인한다.

### Missing values

Unavailable 값을 0으로 표시하지 않는다.

### Tooltips

Hover target과 tooltip 값/identity가 일치하는지 확인한다.

---

## 5. Section Acceptance

### 5.1 Portfolio Allocation

- non-zero allocation 표시
- Name/Ticker/Allocation hover
- constraint 정보 유지
- Provided/Optimized identity 분리

### 5.2 Efficient Frontier Assets

Required schema:

```text
Name | Ticker | Expected Return | Std Dev | Sharpe Ratio | Min Weight | Max Weight
```

### 5.3 Efficient Frontier

Check:

- X = Annualized Standard Deviation %
- Y = Expected Annual Return %
- frontier curve shape readable
- nearby asset/landmark context readable
- chart height sufficient
- extreme asset 하나 때문에 curve가 과도하게 축소되지 않음
- final display domain 안 asset은 chart에 표시
- final display domain 밖 asset만 outsider table에 표시
- chart/outside table 간 duplicate/missing asset 없음
- curve tooltip has return/stddev/sharpe/all allocations
- asset/landmark tooltip has identity/statistics

특정 external screenshot의 exact X/Y range를 요구하지 않는다.

### 5.4 Frontier Transition

- stacked allocation meaning 유지
- X = Std Dev
- Y = Allocation
- per-point weights sum 100%
- table column order specification 충족
- RF note matches actual configuration

### 5.5 Performance Summary

Minimum rows:

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

Checks:

```text
Start Balance = $10,000 when canonical value is 1.0
Benchmark Active Return = N/A
Benchmark Tracking Error = N/A
Benchmark Information Ratio = N/A
```

### 5.6 Portfolio Asset Performance

Required identity + metrics + trailing columns가 모두 유지되는지 확인한다.

```text
Ticker / Name
CAGR / Annualized Return / Stdev
Best / Worst Year
MDD / Sharpe / Sortino
3M / YTD / 1Y / 3Y / 5Y / 10Y
```

### 5.7 Annual Returns

- year X-axis
- Provided/Optimized/Benchmark identity
- grouped year tooltip

### 5.8 Annual Asset Returns

- ticker별 independent series
- stable color identity
- legend identity
- grouped year tooltip with all assets

### 5.9 Drawdowns

- X = Month / Year
- Y = Drawdown %
- portfolio별 episode table 분리

### 5.10 Correlations

- required matrix scope
- Name/Ticker identity
- numeric coefficient readable
- color is supplemental, not sole information carrier

### 5.11 Return / Risk Decomposition

- Provided/Optimized identity
- required asset identity
- contribution totals/invariants already protected by calculation tests

### 5.12 Active Return Contribution

- `(portfolio, ticker)` path identity
- no cross-portfolio sawtooth
- X = Month / Year
- Y = cumulative contribution %
- raw debug table absent

### 5.13 Rolling Active Return and Risk

Provided / Optimized separate panels.

Check:

```text
Title    = Rolling Active Return and Risk (36 months)
Subtitle = <Portfolio> vs. <Benchmark>
Active Return  = bars, left Y-axis
Tracking Error = line, right Y-axis
X = Month / Year
```

두 metric을 동일 Y-axis에 놓으면 FAIL이다.

Displayed Rolling Active Return은 canonical result와 일치해야 한다.

36M total-return difference를 annualize 없이 표시하면 P0다.

Hover는 동일 month의 Active Return과 Tracking Error를 함께 제공한다.

### 5.14 Up vs. Down Market Performance

Provided / Optimized 각각:

```text
conditional statistics table
+
Return vs. Benchmark paired bar chart
```

Check:

- canonical Up/Down counts 사용
- benchmark return ordering
- approximately 20 equal-frequency view groups
- each group has Portfolio/Benchmark paired bars
- X = group mean Benchmark Return %
- Y = Return %
- hover has Portfolio/Benchmark/observation count

External source와 count가 다르더라도 internal canonical data가 맞으면 FAIL이 아니다.

### 5.15 Rolling 3Y / 5Y Returns

- X = Month / Year
- Y = Annualized Return %
- Provided/Optimized/Benchmark identity

---

## 6. Severity

Severity definition은 `docs/report-ui-specification.md`와 동일하게 사용한다.

### P0

금융 의미 오류 또는 required information failure.

Examples:

- wrong value/unit
- missing shown as zero
- wrong path identity
- incorrect rolling metric
- required row/series missing

### P1

Meaning은 유지되지만 분석/비교 usability가 materially degraded.

Examples:

- important chart too small
- identity regression
- required trailing columns lost
- unreadable ticks
- wrong outsider classification

### P2

Non-semantic visual polish difference.

---

## 7. Validation Evidence

Validation run에서 필요하면:

```text
runs/<run_id>/validation/visual-comparison.md
```

를 남긴다.

최소 내용:

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

Section별로 actual observation과 defect를 기록한다.

External comparison을 수행했으면 결과를 별도 evidence로 기록하되 internal acceptance와 혼동하지 않는다.

---

## 8. Screenshot Policy

Static screenshot은 다음 용도로 유용하다.

- visual regression evidence
- historical UI comparison
- layout discussion

하지만 screenshot의 부재 자체가 product defect는 아니다.

Screenshot persistence가 환경 제약으로 불가능한 경우 textual/browser evidence를 남길 수 있다.

---

## 9. Completion Rule

Interactive Report 작업 완료 조건:

1. affected calculation contracts pass
2. affected report semantic contracts pass
3. generated report browser acceptance pass
4. P0 = 0
5. P1이 남아 있으면 명시적으로 accepted/deferred 상태가 기록됨
6. external reference가 아니라 **internal specification**을 기준으로 completion 판단

External comparison은 현재 작업이 parity investigation 또는 historical regression investigation을 포함할 때만 필수다.

---

## 10. Change Rule

검증 중 외부 service와 다른 점을 발견했을 때:

```text
external difference discovered
        ↓
우리 specification과 implementation 비교
        ↓
implementation이 spec 위반? -> defect
spec과 implementation 일치? -> not defect
        ↓
외부 방식이 더 낫다고 판단되면 별도 product change proposal
        ↓
spec 먼저 변경 후 구현
```

검증자가 외부 reference를 근거로 specification을 암묵적으로 재정의하지 않는다.
