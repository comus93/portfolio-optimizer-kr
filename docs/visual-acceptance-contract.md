# Interactive Report Visual Acceptance Contract

이 문서는 `docs/specification.md` Section 25 `Interactive Research Report`의 visual/behavioral acceptance를 구체화한다.

목표는 Portfolio Visualizer(PV)를 pixel-perfect clone하는 것이 아니라, 동일 조건에서 사용자가 chart/table을 **같은 의미로 읽을 수 있도록** semantic parity와 충분한 presentation fidelity를 확보하는 것이다.

## 1. Reference hierarchy

### Primary static reference

동일한 입력 조건으로 PV에서 생성한 고정 visual baseline:

```text
https://github.com/comus93/llm_share/blob/main/projects/portfoliovisualizer/optimizations/2026-08-29-maxsharpegolden.png
```

이 이미지는 layout, section composition, chart type, axis/tick presentation, table structure, legend/marker 배치를 검증하는 immutable visual reference다.

### Primary behavioral reference

동일 조건의 PV live result:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg
```

Agent가 접근 가능한 경우 반드시 직접 열어 generated `report.html`과 비교한다.

Live PV는 다음을 검증하는 behavioral golden이다.

- hover selection behavior
- tooltip content and units
- semantic X/Y values
- tick density and formatting
- axis domain behavior
- series/marker/legend identity
- chart-specific panel separation

기존 repository golden:

```text
tests/golden/pv/260828_PTF_maxsharpe.jpg
tests/golden/pv/260828_PTF_maxsharpe.md
```

은 정보 구조와 finance/parity sanity reference로 계속 유지한다.

## 2. Automated contract vs visual acceptance

자동 pytest contract와 실제 browser visual acceptance는 서로 대체하지 않는다.

### Automated contract

자동 테스트는 최소한 다음을 잠근다.

- Efficient Frontier presentation point는 `volatility_pct`를 X 의미로 가진다.
- Efficient Frontier point는 `expected_return_pct`, `sharpe_ratio`, `weights_pct`를 가진다.
- frontier weight 합은 fully-invested portfolio에서 100%다.
- Provided / Optimized / Benchmark / asset marker를 표현할 landmark contract가 존재한다.
- Annualized Active Return은 월별 중복 point가 아니라 `year` 단위 point다.
- Annualized Active Return에는 benchmark active-return field가 없다.
- Active Return Contribution의 Provided와 Optimized series는 presentation model 단계에서 분리된다.
- Rolling Active Return / Tracking Error의 Provided와 Optimized series는 presentation model 단계에서 분리된다.
- missing value는 실제 0 수익률/0 metric과 같은 의미로 취급하지 않는다.
- objective-aware optimized portfolio label을 유지한다.

### Visual acceptance

실제 chart type, axis/tick, layout, tooltip interaction, sawtooth/cross-series artifact 등은 browser rendering을 직접 확인해야 한다.

자동 테스트가 통과했다는 이유만으로 visual acceptance 완료라고 판단하지 않는다.

## 3. Chart axis and scale contract

모든 chart는 row index가 아니라 실제 semantic X value를 사용한다.

### Time series

- X축은 실제 date/year다.
- 기간에 맞는 readable tick을 표시한다.
- raw row number를 X축으로 사용하지 않는다.

### Efficient Frontier

```text
X = Standard Deviation %
Y = Expected Return %
```

- X spacing은 실제 volatility 값에 비례해야 한다.
- frontier curve와 individual assets, Provided Portfolio, Optimized Portfolio, Benchmark marker를 동일 risk/return coordinate space에 표시한다.
- Max Sharpe/Tangency landmark는 objective에 맞게 식별 가능해야 한다.

### Efficient Frontier Transition Map

```text
X = Standard Deviation %
Y = Allocation 0..100%
```

- row index나 year를 X로 사용하지 않는다.
- Golden/PV와 같은 의미의 stacked allocation area로 표현한다.
- 각 point의 asset allocations 합은 100%다.

### Axis ticks

Golden과 숫자 tick을 무조건 hard-code해서 같게 만들 필요는 없다.

다만 동일 데이터 범위에서는 PV와 유사하게 읽을 수 있는 합리적인 tick density를 사용하고 다음을 만족해야 한다.

- 의미 있는 interval
- axis title
- percentage/currency unit formatting
- 실제 date/year/category label
- 과도한 label overlap 없음

0이 chart 의미상 필요하지 않은 경우 단순 generic renderer 편의를 위해 axis domain에 0을 강제로 포함하지 않는다.

## 4. Missing value contract

```text
missing != zero
```

null/NaN/missing observation을 `0`으로 coercion해서 line/bar/marker를 생성하지 않는다.

missing point는 chart 성격에 따라 gap 또는 omitted point로 표현한다.

## 5. Active Return Contribution contract

Provided Portfolio와 Optimized Portfolio는 반드시 별도 panel/series group으로 렌더링한다.

하나의 ticker path가 portfolio identity를 넘어서 연결되어서는 안 된다.

각 path는 다음 key 안에서만 연결한다.

```text
(portfolio, ticker), ordered by date
```

현재 발견된 defect처럼 같은 date마다 Provided와 Optimized observation을 번갈아 연결해 톱니바퀴/sawtooth 형태를 만드는 것은 P0 failure다.

Acceptance:

- Provided contribution chart와 Optimized contribution chart가 분리되어 있다.
- cross-portfolio line segment가 없다.
- PV live result에 존재하지 않는 alternating sawtooth artifact가 없다.
- tooltip은 allocation이 아니라 asset cumulative active-return contribution을 표시한다.

## 6. Annualized and rolling active-return contract

### Annualized Active Return

X축/presentation point는 calendar year다.

```text
Year
Provided Portfolio Active Return %
Optimized Portfolio Active Return %
```

동일 annual value를 각 month에 반복해 monthly staircase series로 만들지 않는다.

Benchmark Active Return은 표시하지 않는다.

### Rolling Active Return / Tracking Error

Provided와 Optimized를 별도 chart/panel로 렌더링한다.

각 panel에는 동일 portfolio identity의:

- Active Return
- Tracking Error

만 존재한다.

서로 다른 portfolio의 observation을 하나의 path로 연결하지 않는다.

## 7. Up vs Down Market contract

Golden/PV와 같은 의미로 Provided와 Optimized 각각 다음을 제공한다.

```text
conditional monthly statistics table
+
Portfolio Return vs Benchmark Return scatter
```

단순 annualized bar chart로 대체하지 않는다.

통계에는 가능한 경우 다음을 포함한다.

- Above Benchmark count
- Below Benchmark count
- Total
- % Above Benchmark
- Average Active Return when above
- Average Active Return when below
- Overall Average Active Return

## 8. Presentation fidelity requirements

다음은 visual acceptance 대상이다.

- Provided/Optimized allocation table + allocation pie
- 0% allocation asset는 상단 allocation summary에서 숨김
- table별 explicit human-readable column schema
- internal snake_case field name UI 노출 금지
- percent/balance/correlation/Sharpe 등 unit-aware display formatting
- Portfolio Growth는 normalized canonical wealth를 presentation에서 `Growth of $10,000` convention으로 표시 가능
- Efficient Frontier asset table은 focused schema 사용
- correlation은 intended matrix scope별 heatmap 제공
- Worst Drawdowns는 Provided / Optimized / Benchmark별 별도 table
- Portfolio Assets와 Portfolio Asset Performance는 목적이 다른 별도 projector/table로 구성
- Annual Returns chart와 detailed Annual Returns table을 구분
- Monthly Returns detailed table은 portfolio return/balance, benchmark, 필요한 asset columns를 Golden 의미에 맞게 구성
- 같은 ticker는 report 전체에서 일관된 visual identity/color를 사용

Golden의 부가 기능 전체를 무조건 복제하지 않는다. 연구 목적과 직접 관련 없는 metric은 intentional deviation으로 기록할 수 있다.

## 9. Mandatory Agent self-review loop

구현 완료 전 Agent는 다음 loop를 수행한다.

```text
implement
-> generate report
-> open generated report in browser
-> open PV live result
-> compare section by section
-> fix discovered P0/P1 defects
-> regenerate report
-> final comparison
-> completion report
```

한 번 구현하고 자동 테스트만 실행한 뒤 visual completion으로 보고하지 않는다.

핵심 비교 대상:

1. Portfolio Growth
2. Annual Returns
3. Efficient Frontier
4. Efficient Frontier Transition Map
5. Annualized Active Return
6. Active Return Contribution
7. Rolling Active Return / Tracking Error
8. Up vs Down Market Performance
9. Drawdown
10. Annual Asset Returns
11. Rolling 3Y / 5Y Returns

각 chart에서 최소 다음을 비교한다.

- chart type
- X semantic
- Y semantic
- X ticks
- Y ticks/domain
- unit formatting
- series count and identity
- panel separation
- legend
- marker
- tooltip
- missing-value behavior
- title/subtitle/window label

P0 semantic mismatch가 하나라도 남으면 완료로 보고하지 않는다.

## 10. Validation evidence

Validation run에는 가능한 한 다음 evidence를 저장한다.

```text
runs/<validation-run>/validation/
├─ visual-comparison.md
├─ report-full.png
├─ pv-frontier.png
├─ report-frontier.png
├─ pv-transition.png
├─ report-transition.png
├─ pv-active-contribution.png
└─ report-active-contribution.png
```

Browser/tool 제약으로 screenshot 저장이 불가능하면 그 사실을 명시하고, 최소 `visual-comparison.md`에 직접 비교한 결과와 남은 차이를 기록한다.

`visual-comparison.md` 최소 형식:

```text
PV live comparison: PASS | FAIL
Static golden comparison: PASS | FAIL

P0 mismatches: <count>
P1 mismatches: <count>
Intentional deviations: <count>

Efficient Frontier
- X/Y semantics: PASS | FAIL
- ticks/units: PASS | FAIL
- landmarks: PASS | FAIL
- tooltip: PASS | FAIL

Transition Map
- stacked area: PASS | FAIL
- X = Std Dev: PASS | FAIL
- allocations sum 100%: PASS | FAIL

Active Return Contribution
- portfolio panels separated: PASS | FAIL
- cross-portfolio path: NONE | FOUND
- sawtooth artifact: NONE | FOUND
- tooltip: PASS | FAIL

Remaining differences
- ...
```

## 11. Completion rule

Interactive report 작업 완료는 다음 세 조건을 모두 만족해야 한다.

1. automated contract/regression tests pass
2. same-input generated report browser rendering passes visual acceptance
3. PV live/static Golden comparison 결과와 intentional deviations가 durable artifact로 기록됨
