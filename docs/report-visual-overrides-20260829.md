# Report Visual Review Overrides — 2026-08-29

이 문서는 2026-08-29 사용자 직접 PV browser review에서 발견된 report-specific correction history를 남긴다.

**현재 normative source는 `docs/specification.md`와 `docs/visual-acceptance-contract.md`다.**

이 파일의 과거 숫자/URL이 현재 contract와 충돌하면 현재 contract를 따른다.

## Current behavioral golden

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

Current 7-asset universe:

```text
QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
```

## Corrections established by user review

### Efficient Frontier

- curve raw extrema에 딱 붙이지 않는다.
- nearby asset/portfolio context를 포함하는 dynamic display domain을 사용한다.
- extreme outsider가 curve를 압축하지 않게 한다.
- visible/outside는 final display domain 기준이다.
- Min/Max Weight columns를 유지한다.
- desktop chart는 충분한 physical height를 확보한다.

현재 same-input PV는 의미상 대략 X 12%~22.5%, Y 11%~22% 범위이며 hard-code하지 않는다.

### Annual Asset Returns

- ticker별 independent series/color/legend
- same-year grouped hover에 전체 asset identity/return 표시

### Up vs. Down Market Performance

과거 scatter interpretation은 폐기한다.

```text
conditional statistics table
+
Return vs. Benchmark paired bars
```

월별 benchmark return을 정렬하고 약 20 equal-frequency groups로 압축한다.

### Rolling Active Return and Risk

36M rolling active return은 36M total-return difference가 아니라:

```text
annualized portfolio 36M return - annualized benchmark 36M return
```

이다.

UI:

```text
Active Return = left-axis bars
Tracking Error = right-axis line
```

### Metrics

- normalized balance 1.0은 report에서 `$10,000`
- Benchmark Active Return / Tracking Error / Information Ratio는 `N/A`
- Performance Summary 필수 metrics를 축소하지 않는다.
- Asset Performance에 Annualized Return과 trailing returns를 유지한다.

### Partial calendar years

PV reference는 분석 시작/종료 때문에 calendar year가 일부 월만 포함되는 경우에도 해당 year를 제거하지 않는다.

예:

```text
2016 result period = Aug-Dec 2016
2026 result period = Jan-Jul 2026
```

우리 report도 같은 원칙으로 partial year를 숨기거나 0으로 채우지 않는다.

- Annual Returns에 실제 available completed months의 compounded return을 표시한다.
- Monthly Returns에서 unavailable months는 `N/A`로 유지한다.
- Annual Returns와 Monthly Returns 양쪽에 partial year가 어느 completed months를 기반으로 하는지 note를 표시한다.
- partial year 포함 여부 때문에 canonical historical series 자체를 잘라내지 않는다.
- Best/Worst Year가 partial year를 포함해야 하는지는 이 PV reference만으로 확정하지 않고 별도 validation 대상으로 남긴다.

## Static golden

Latest same-input full-page static golden은 report-review v4 완료 후 사용자 refresh를 기다린다.

이전 깨진 URL 또는 다른 asset-universe screenshot을 completion PASS 근거로 사용하지 않는다.
