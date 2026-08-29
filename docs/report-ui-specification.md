# Interactive Research Report UI Specification

## 1. Purpose and Authority

이 문서는 `portfolio-optimizer-kr`의 self-contained HTML research report에 대한 **canonical UI/interaction specification**이다.

이 문서의 목적은 특정 외부 서비스의 화면을 복제하는 것이 아니라, 사용자가 optimization과 historical analytics의 의미를 일관되게 읽고 비교할 수 있는 자체 report contract를 고정하는 것이다.

Normative hierarchy:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
External references               PV live / screenshots / historical golden
```

외부 reference와 이 문서가 다르면 **이 문서가 우선**한다. 외부 reference는 defect discovery, sanity check, data-source deviation 조사에 사용할 수 있지만 product requirement를 자동 변경하지 않는다.

---

## 2. General Report Contract

Report는 `runs/<run_id>/result.json` 및 persisted review/raw artifact에서 생성된 presentation model을 사용한다.

Browser는 금융 계산을 다시 수행하지 않는다. Browser layer가 허용되는 계산은 다음과 같은 presentation-only transform에 한정한다.

- 단위 변환 및 formatting
- chart coordinate transform
- tooltip용 nearest-point 선택
- table ordering/filtering
- display-domain 계산
- chart용 binning처럼 canonical raw observation의 의미를 바꾸지 않는 view transform

Canonical finance value와 화면 value가 다르면 canonical result가 source of truth다.

### 2.1 Identity

Report 전체에서 portfolio identity를 다음처럼 사용한다.

```text
Provided Portfolio
<objective-aware optimized portfolio name>
<human-readable benchmark name>
```

예:

```text
Provided Portfolio
Maximum Sharpe Ratio
State Street SPDR S&P 500 ETF
```

Generic `Optimized`, `Benchmark`는 내부 key로 사용할 수 있지만 사용자-facing primary label로 사용하지 않는다.

Asset identity는 가능한 경우:

```text
Name + Ticker
```

를 함께 제공한다.

### 2.2 Units

- return / volatility / drawdown / allocation / active metrics: `%`
- ratio metrics: unitless decimal
- balance: currency
- date/time: actual observation date 또는 calendar year/month

Normalized wealth convention:

```text
canonical 1.0 = report $10,000
```

`null`, `NaN`, unavailable value는 `N/A`로 표시한다.

```text
missing != zero
```

### 2.3 Table behavior

- numeric columns는 동일 precision convention을 유지한다.
- identity column은 왼쪽 정렬한다.
- numeric column은 비교하기 쉽게 정렬한다.
- 기존 정보를 보강하기 위해 column을 추가할 때 기존 required column을 제거하지 않는다.
- raw/debug table은 사용자-facing report에 노출하지 않는다.

### 2.4 Chart behavior

- semantic X value를 사용한다. row index를 실제 date/year/volatility 대신 쓰지 않는다.
- meaningful tick interval과 axis title을 제공한다.
- percentage/date/currency unit이 명확해야 한다.
- hover tooltip은 해당 mark를 해석하는 데 필요한 핵심 값을 한 번에 제공한다.
- 동일 ticker는 report 전체에서 가능한 한 동일 color identity를 유지한다.
- desktop에서 핵심 chart는 section 폭을 충분히 활용한다.
- mobile에서는 horizontal overflow 또는 readable stacking을 허용하되 정보 손실은 없어야 한다.

---

## 3. Report Header

Title은 최소 다음 정보를 포함한다.

```text
Portfolio Optimization · <run_id> (<Mon YYYY> - <Mon YYYY>)
```

기간은 실제 report에 사용된 completed monthly observations의 시작/끝을 사용한다.

Requested period가 asset availability 때문에 실제로 줄어든 경우에만 limiting asset과 effective period를 note로 표시한다.

Fixed risk-free run과 historical T-Bill run의 설명 문구를 혼용하지 않는다.

---

## 4. Portfolio Allocation Sections

Provided Portfolio와 Optimized Portfolio는 각각:

- allocation visualization
- asset identity
- allocation %
- min/max constraint

를 제공한다.

0% allocation은 primary allocation visualization에서 숨길 수 있다.

Allocation hover는 최소:

```text
Asset Name (Ticker)
Allocation %
```

를 표시한다.

---

## 5. Efficient Frontier Assets

Required table:

```text
Name
Ticker
Expected Return
Standard Deviation
Sharpe Ratio
Min Weight
Max Weight
```

Expected Return / Standard Deviation / Sharpe는 optimization statistics 기반 ex-ante value다.

---

## 6. Efficient Frontier Chart

### 6.1 Semantics

```text
X = Annualized Standard Deviation %
Y = Expected Annual Return %
```

표시 대상:

- Efficient Frontier curve
- display domain 안의 individual assets
- Provided Portfolio
- Optimized Portfolio
- Benchmark

### 6.2 Viewport

Viewport 목적은 **frontier shape를 읽기 쉽게 유지하면서 nearby asset/landmark의 상대 위치를 제공하는 것**이다.

규칙:

1. curve raw extrema에 chart domain을 딱 붙이지 않는다.
2. curve span에 비례한 context padding을 제공한다.
3. nearby asset/landmark가 curve 해석에 유용하면 domain 후보에 포함한다.
4. 극단적으로 먼 asset 하나 때문에 curve가 chart에서 과도하게 작아지지 않도록 한다.
5. 최종 domain은 readable nice tick boundary로 확장한다.
6. `visible/outside` 판정은 **최종 display domain** 기준이다.
7. final domain 안의 asset을 outsider table로 보내면 defect다.
8. 특정 종목 또는 특정 퍼센트 범위를 hard-code하지 않는다.

### 6.3 Size

Desktop에서 Efficient Frontier는 주요 분석 chart로 취급한다.

- section 폭을 실질적으로 사용해야 한다.
- curve와 individual asset 위치를 한눈에 읽을 수 있는 충분한 vertical height를 확보한다.
- generic chart default 때문에 납작하게 눌려서는 안 된다.

### 6.4 Tooltip

Curve hover:

```text
Expected Return
Standard Deviation
Sharpe Ratio
all asset allocations
```

Asset hover:

```text
Name / Ticker
Expected Return
Standard Deviation
Sharpe Ratio
```

Portfolio/benchmark landmark hover도 동일한 statistics를 제공하며 allocation data가 있으면 weights를 함께 제공한다.

### 6.5 Outside-scale assets

Final display domain 밖 asset이 있는 경우 chart 아래에 별도 table을 제공한다.

```text
Name
Ticker
Std Dev
Expected Return
Sharpe Ratio
```

Chart와 outsider table 사이에서 asset이 중복되거나 누락되면 defect다.

---

## 7. Efficient Frontier Transition Map

Semantics:

```text
X = Annualized Standard Deviation %
Y = Asset Allocation %
```

Frontier를 따라 각 asset allocation이 어떻게 바뀌는지 stacked allocation area로 표시한다.

Requirements:

- 각 point allocation 합 = 100%
- 같은 ticker color identity 유지
- X축은 frontier volatility
- title에 effective period 표시
- hover는 point statistics + asset allocations 제공

Transition table column order:

```text
Point
<asset allocation columns...>
Expected Return
Standard Deviation
Sharpe Ratio
```

Ex-ante/RF note는 실제 run risk-free mode와 일치해야 한다.

---

## 8. Performance Summary

Provided / Optimized / Benchmark 비교 table의 최소 rows:

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

Balance display:

```text
canonical 1.0 -> $10,000
```

Benchmark 자체의 benchmark-relative metrics:

```text
Active Return       N/A
Tracking Error      N/A
Information Ratio   N/A
```

`0`으로 표시하지 않는다.

Advanced metrics는 calculation contract가 존재하는 항목만 추가한다.

---

## 9. Trailing Returns

Portfolio-level trailing table은 최소:

```text
3M
YTD
1Y
3Y annualized
5Y annualized
10Y annualized
Full Period CAGR
3Y Annualized Volatility
5Y Annualized Volatility
```

Observation이 부족하면 `N/A`.

---

## 10. Annual Returns

Chart/table identity:

```text
Provided Portfolio
Optimized Portfolio
Benchmark
```

한 year의 어느 bar/mark에 hover하더라도 같은 year의 세 series 값을 하나의 tooltip에서 비교할 수 있어야 한다.

X축은 calendar year다.

---

## 11. Monthly Returns

Portfolio별 monthly calendar table:

```text
Year
Jan ... Dec
YTD
```

Portfolio identity를 명시한다.

Unavailable month는 0%로 채우지 않는다.

---

## 12. Drawdowns

Provided / Optimized / Benchmark별 독립적으로 표시한다.

Chart:

```text
X = Month / Year
Y = Drawdown %
```

Episode table minimum:

```text
Rank
Start
Bottom
Recovery
Maximum Drawdown
Duration
```

Portfolio별 drawdown episode를 한 table에 의미 없이 섞지 않는다.

---

## 13. Portfolio Asset Performance

Required columns:

```text
Ticker
Name
CAGR
Annualized Return
Standard Deviation
Best Year
Worst Year
Maximum Drawdown
Sharpe Ratio
Sortino Ratio
3M
YTD
1Y
3Y annualized
5Y annualized
10Y annualized
```

Identity 또는 새 metric을 추가하면서 기존 required trailing column을 제거하면 regression이다.

---

## 14. Correlations

### Asset Correlations

Optimization universe monthly return correlation matrix.

### Portfolio / Asset Correlations

다음을 함께 포함한다.

```text
Optimization Assets
Provided Portfolio
Optimized Portfolio
Benchmark
```

UI row identity는 asset의 경우 `Name + Ticker`, portfolio/benchmark는 human-readable identity를 사용한다.

Heatmap은 numeric coefficient를 읽을 수 있어야 하고 color는 보조 의미다.

---

## 15. Return Decomposition

Provided / Optimized를 구분해 asset별 realized contribution을 표시한다.

Asset identity는 최소 Ticker, 가능하면 Name + Ticker를 제공한다.

Contribution unit/convention은 `docs/specification.md`를 따른다.

---

## 16. Risk Decomposition

Provided / Optimized ex-ante component risk contribution을 표시한다.

Required identity:

```text
Name
Ticker
Provided Risk Contribution
Optimized Risk Contribution
```

각 portfolio의 contribution 합이 100%가 되는 canonical result를 표현한다.

---

## 17. Annual Asset Returns

- 각 ticker는 independent series다.
- 동일 ticker color identity를 유지한다.
- legend에 ticker identity를 제공한다.
- X축은 calendar year다.
- 한 year의 어느 asset mark에 hover해도 같은 year의 모든 asset `Name / Ticker / Return`을 grouped tooltip으로 제공한다.

Generic single `return_pct` series로 asset identity를 잃으면 defect다.

---

## 18. Active Return Analytics

### 18.1 Annualized Active Return

Provided / Optimized series를 구분한다.

Year hover는 같은 year의 비교 값을 함께 제공한다.

### 18.2 Active Return Contribution

Provided / Optimized는 별도 panel 또는 명확히 분리된 series group으로 표시한다.

```text
X = Month / Year
Y = Cumulative Active Contribution %
```

Path identity는 `(portfolio, ticker)`다. Portfolio boundary를 넘어서 한 ticker path를 이어 붙여 sawtooth artifact를 만들면 defect다.

Raw debug table은 표시하지 않는다.

---

## 19. Rolling Active Return and Risk

Provided와 Optimized 각각 독립 panel.

```text
Title    = Rolling Active Return and Risk (36 months)
Subtitle = <Portfolio> vs. <Benchmark>
```

Presentation:

```text
Active Return  = bars, left Y-axis
Tracking Error = line, right Y-axis
X              = Month / Year
```

두 series는 scale 의미가 다르므로 동일 Y-axis를 공유하지 않는다.

Calculation convention은 `docs/specification.md`가 canonical source다.

Hover는 같은 month의:

```text
Active Return
Tracking Error
```

를 함께 제공한다.

---

## 20. Up vs. Down Market Performance

Provided / Optimized 각각 하나의 block:

```text
conditional statistics table
+
Return vs. Benchmark paired bar chart
```

Statistics minimum:

```text
Market Type
Above Benchmark count
Below Benchmark count
Total
% Above Benchmark
Average Active Return Above
Average Active Return Below
Average Active Return Total
```

Chart view transform:

1. monthly observations를 Benchmark Return 오름차순으로 정렬
2. 약 20 equal-frequency groups로 압축
3. 각 group에서 Portfolio Return 평균과 Benchmark Return 평균 계산
4. 두 값을 paired bars로 표시

X축:

```text
group mean Benchmark Return %
```

Y축:

```text
Return %
```

Hover:

```text
Portfolio Return
Benchmark Return
Observation count
```

Canonical Up/Down count를 외부 reference 숫자에 맞추기 위해 hard-code하지 않는다.

---

## 21. Rolling Returns

기본 chart:

```text
Rolling 3 Year Annualized Return
Rolling 5 Year Annualized Return
```

Axes:

```text
X = Month / Year
Y = Annualized Return %
```

Provided / Optimized / Benchmark identity를 유지한다.

---

## 22. Responsive Layout

Desktop:

- analytical chart는 card width를 적극적으로 사용한다.
- wide correlation/frontier table은 horizontal scroll 허용 가능.
- 핵심 chart는 지나치게 낮은 fixed height를 사용하지 않는다.

Mobile:

- chart/table 의미 보존이 pixel parity보다 우선이다.
- table horizontal scroll 허용.
- legend는 wrap 가능.
- tooltip은 viewport 밖으로 잘리지 않도록 positioning한다.

---

## 23. Accessibility / Readability

- color 하나만으로 series 의미를 전달하지 않는다. legend/label/tooltip identity를 함께 제공한다.
- percentage, ratio, currency 단위를 명시한다.
- chart text가 겹치면 per-point permanent label을 줄이고 hover를 우선한다.
- 필요한 정보가 clipping되어 읽을 수 없는 상태는 defect다.

---

## 24. UI Regression Severity

### P0

금융 의미가 틀리거나 필수 정보를 읽을 수 없는 상태.

예:

- 잘못된 unit 또는 10,000배 balance 오류
- missing을 0으로 표시
- 서로 다른 portfolio path를 한 series로 연결
- Rolling Active Return의 잘못된 calculation value를 표시
- required table/series 누락

### P1

금융 의미는 유지되지만 분석/비교가 현저히 어려워진 상태.

예:

- 핵심 chart가 지나치게 작음
- identity가 generic label로 퇴행
- required trailing metric이 보이지 않음
- unreadable tick/label density
- nearby asset이 잘못 outsider로 분류됨

### P2

정보 의미에는 영향이 없는 visual polish 차이.

---

## 25. Change Rule

운영 단계에서 report UI를 변경할 때 기준은 다음이다.

1. 이 문서의 product semantics를 먼저 변경할지 결정한다.
2. product semantics 변경이면 문서와 tests를 함께 갱신한다.
3. 외부 서비스가 달라졌다는 이유만으로 구현을 변경하지 않는다.
4. 새로운 외부 reference가 더 좋은 UX 아이디어를 제공하면 별도 개선 제안으로 검토한다.
5. 구현 완료 판정은 `docs/visual-acceptance-contract.md`의 validation procedure를 따른다.
