# Design

## 1. Reuse boundary

`analyze_prices()`가 완료되면 `result["_tables"]["annual_asset_returns"]`와 baseline `optimization_result.weights`가 이미 메모리에 존재한다. 이어지는 `attach_loyo_robustness()`가 `loyo_robustness` table을 생성한다.

따라서 LOYO attach가 끝나는 시점에 세 결과를 join/projection만 한다.

```text
annual_asset_returns (already computed)
+ optimization_result.weights (existing baseline)
+ loyo_robustness (already solved)
        -> asset_year_influence projection
        -> result._tables["asset_year_influence"]
        -> normal raw/review persistence
```

금지:

- annual asset return 재계산
- baseline optimization 재실행
- LOYO optimization 재실행
- browser에서 finance metric 재계산

## 2. Asset-Year Influence raw schema

Long format을 사용한다.

```text
year
ticker
asset_annual_return
baseline_weight
excluded_year_weight
delta_weight
status
```

percentage/weight 값은 raw/canonical 관례대로 decimal unit을 보존한다. Review projection은 percentage-point unit으로 변환한다.

`delta_weight = excluded_year_weight - baseline_weight`는 기존 LOYO delta를 재사용하며 새 formula path를 만들지 않는다.

## 3. User-facing Asset-Year matrix

행은 year group이고 한 year는 4개 metric row를 가진다. 열은 asset ticker다.

```text
Year | Metric                       | QQQ | SPMO | ...
2022 | 구성자산 해당년도 수익률
     | 전체기간 최적비중
     | 해당년도 제외 최적비중
     | 비중 변화
```

한 `2022 × QQQ` cell을 내부 4분할하지 않는다. HTML `rowspan`을 사용해 year label만 4개 metric row를 묶는다.

Conditional background는 presentation-only transformation이다.

- 구성자산 해당년도 수익률: 0 중심 diverging scale
- 전체기간 최적비중: low-intensity sequential scale
- 해당년도 제외 최적비중: low-intensity sequential scale
- 비중 변화: 0 중심 diverging scale, 가장 강한 emphasis

각 metric은 자체 global scale을 사용해 year 간 비교 가능성을 유지한다. Color는 보조 정보이며 numeric value를 항상 표시한다.

## 4. LOYO Summary

사용자 primary summary는 다음을 표시한다.

```text
Excluded Year
Δ Return
Δ Sharpe
Reallocation
1st Allocation Shift
2nd Allocation Shift
3rd Allocation Shift
```

Allocation Shift는 기존 per-asset delta weight를 absolute magnitude로 정렬하는 view-only ordering이며 값은 signed percentage point로 표시한다.

정상 scenario에서는 technical status/debug field를 표시하지 않는다. 실패 또는 insufficient-data scenario가 존재할 때만 Status / Reason을 조건부 추가한다.

## 5. Allocation Changes

Asset column matrix를 사용한다.

- 첫 row: Full Sample baseline optimized weights
- 이후 row: excluded year별 LOYO optimized weight와 baseline 대비 signed delta를 같은 cell에 표시

예:

```text
Baseline | 31.06%
2022     | 56.93% (+25.87%p)
```

## 6. Legacy run backfill

기존 run은 optimizer를 재실행하지 않는다. Persisted `result.json`, raw `annual_asset_returns.csv`, raw `loyo_robustness.csv`에서 동일 projection helper를 호출해 `asset_year_influence` raw/review artifact만 backfill한 뒤 report를 재생성할 수 있어야 한다.

## 7. Architecture boundary

Derived finance evidence 조합은 Python analysis/artifact layer가 소유한다. Browser는 persisted review values를 pivot/group/order/format/heatmap만 한다.
