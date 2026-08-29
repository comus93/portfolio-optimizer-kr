# Report Visual Review Overrides — 2026-08-29

이 문서는 `docs/visual-acceptance-contract.md` 중 2026-08-29 사용자 직접 PV browser review로 더 정확한 reference가 확보된 항목을 우선 적용한다.

충돌하는 경우 이 문서가 우선한다.

## 1. Efficient Frontier viewport

Efficient Frontier의 chart domain은 individual asset 전체 범위가 아니라 **efficient frontier curve를 중심**으로 결정한다.

단, raw curve min/max에 딱 맞추지 않는다.

- curve span에 비례한 padding과 최소 absolute padding을 함께 적용한다.
- padding을 적용한 뒤 readable tick interval 기준으로 domain을 바깥 방향으로 snap한다.
- 따라서 좁은 curve에서도 충분한 주변 context를 보여야 한다.
- asset의 visible / outside 판정은 raw curve min/max가 아니라 **최종 snapped display domain**을 기준으로 한다.
- final display domain 안의 asset을 `Assets outside chart scale`로 보내면 FAIL이다.
- final display domain 밖의 asset만 plot에서 생략하고 아래 table에 Name / Ticker / Std Dev / Expected Return / Sharpe Ratio를 표시한다.

Reference PV screenshot에서는 curve보다 왼쪽/아래쪽으로 충분한 여백을 두며 X축이 10%부터 시작한다. 숫자 자체를 hard-code하지 않고 같은 presentation principle을 따른다.

## 2. Efficient Frontier Assets table

Specification 필수 schema를 유지한다.

```text
Name
Ticker
Expected Return
Std Dev
Sharpe Ratio
Min Weight
Max Weight
```

사용자 feedback을 반영하면서 기존 Min/Max Weight를 떨어뜨리면 regression이다.

## 3. Annual Asset Returns

- 각 ticker는 독립적인 chart series/bar identity와 고유 color를 가져야 한다.
- 단일 generic `return_pct` series로 합치지 않는다.
- year hover는 같은 연도의 전체 asset Name / Ticker / Annual Return %를 한 tooltip에 표시한다.
- report 전체에서 동일 ticker color identity를 유지한다.

## 4. Up vs. Down Market Performance

`docs/visual-acceptance-contract.md` Section 7의 하단 **scatter 요구는 폐기한다.**

사용자 제공 PV live screenshot을 기준으로 각 Provided / Optimized block은 다음 구조다.

```text
conditional monthly statistics table
+
Return vs. Benchmark paired bar chart
```

Return vs. Benchmark chart:

- monthly observations를 Benchmark Return 기준 오름차순으로 정렬한다.
- PV presentation처럼 약 20개 equal-frequency groups로 압축한다.
- Golden run은 120 monthly observations이므로 20 groups × 6 months/group가 된다.
- 각 group은 평균 Portfolio Return과 평균 Benchmark Return을 나란한 두 bar로 표시한다.
- X tick은 해당 group의 평균 Benchmark Return %다.
- Y축은 Return %다.
- hover는 같은 group의 Portfolio Return %와 Benchmark Return %를 함께 표시한다.

이 grouped bar는 연구용 presentation layer다. 원본 월별 데이터와 Up/Down 통계 계산은 canonical monthly series를 계속 사용한다.

## 5. Up / Down occurrence parity

PV와 local FDR source가 한 달의 benchmark return 부호에서 다를 수 있으므로 `85/35` 같은 count를 UI에서 hard-code하지 않는다.

- local report count는 canonical local benchmark monthly return의 `> 0` / `< 0` classification에서 계산한다.
- PV와 count가 다르면 어떤 month가 분류 차이를 만드는지 조사하여 data-source / adjusted-price difference인지 logic defect인지 구분한다.
- data-source 차이라면 intentional deviation으로 기록한다.
- logic defect라면 P0/P1 severity를 판정하고 수정한다.
