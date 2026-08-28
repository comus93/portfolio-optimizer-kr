# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 최적화 결과 페이지 또는 이에 준하는 포트폴리오 최적화 결과를 전달받은 LLM이 독립적으로 결과를 해석할 수 있도록 만든 핸드오버/참조 문서다.

LLM은 과거 데이터에서 계산된 최적 비중을 현재의 권장 비중으로 그대로 받아들이지 않는다. 분석의 목적은 다음 질문에 답하는 것이다.

> **각 자산이 포트폴리오에 어떤 한계 효용(marginal utility)을 추가하는가, 그 효용은 효율적 프론티어의 어느 구간에서 나타나는가, 그리고 그 역할은 실제로 의미 있고 견고한가?**

분석의 중심은 개별 자산 성과가 아니라 포트폴리오 수준의 효용이다. 개별 자산 성과는 주된 판정 기준이 아니라 이를 설명하는 보조 근거로 사용한다.

또한 모든 run에 동일한 checklist를 기계적으로 적용하지 않는다. **현재 Study의 연구 질문이 무엇인지 먼저 확인하고, 그 질문에 답하는 데 필요한 evidence에 분석의 무게를 둔다.**

## 예상 입력

입력은 Portfolio Visualizer 결과 페이지, 복사된 결과 텍스트, export된 표, 스크린샷 또는 이에 준하는 optimizer 결과일 수 있다. 다음 항목 중 일부 또는 전부가 포함될 수 있다.

- 최적화 설정
- 목표 함수 기준 최적 포트폴리오
- Efficient Frontier Assets
- Efficient Frontier Portfolios
- Expected Return / Volatility / Sharpe
- Correlation
- Annual / Rolling Returns
- Drawdowns
- Active Return Contribution
- Return / Risk Decomposition

일부 섹션이 없는 경우에도 가능한 범위에서 이 프레임워크를 적용한다. 필요한 근거가 없어 결론의 신뢰도가 낮아지는 부분은 명시한다.

---

## 0. Study의 연구 질문이 분석 범위를 결정한다

분석을 시작하기 전에 현재 연구가 무엇을 판정하려는지 먼저 확인한다.

예:

- 특정 후보 자산을 기존 portfolio에 추가할 가치가 있는가?
- 특정 자산의 최대 비중 제한이 결과를 왜곡하고 있는가?
- Maximum Sharpe보다 조금 높은 수익을 목표로 할 때 더 실용적인 allocation 구간이 존재하는가?
- 두 자산이 실제로 서로 다른 역할을 제공하는가, 아니면 대체 관계인가?
- 특정 allocation이 기간이나 objective가 바뀌어도 유지되는가?

LLM은 연구 질문을 한 문장으로 다시 정의한 뒤 다음을 구분한다.

```text
Primary evidence   연구 질문에 직접 답하는 근거
Supporting evidence 결과를 설명하거나 반증하는 보조 근거
Missing evidence   현재 run만으로 판단할 수 없는 부분
```

연구 질문과 직접 관계없는 metric을 모두 나열하는 방식은 피한다.

---

## 1. 결과를 해석하기 전에 실험 조건부터 확인한다

가장 먼저 설정을 읽는다.

확인 항목:

- 분석 기간
- 최적화 목적 함수
- Benchmark
- Risk-free rate
- Rebalancing frequency
- Asset universe
- 각 자산의 최소/최대 비중 제약
- 특정 자산의 짧은 히스토리 때문에 공통 분석 기간이 축소되었는지

### 제약 조건 해석 규칙

최적 비중이 최소 또는 최대 제약과 정확히 일치한다면, 그 비중은 unconstrained optimum이 아니다.

예:

- GLD 최대 비중 = 30%
- 최적화 결과 GLD 비중 = 30%

해석:

> Optimizer는 허용된 30%만큼 또는 그 이상을 원했을 수 있다. 실제 unconstrained optimum은 제약 범위 밖에 있을 수 있다.

따라서 제약 경계에 걸린 비중을 경제적으로 선호되는 정확한 비중으로 해석하지 않는다.

---

## 2. 목표 함수 기준 최적 포트폴리오는 출발점으로만 사용한다

Maximum Sharpe 실험이라면 먼저 Maximum Sharpe 포트폴리오를 확인한다.

기록할 항목:

- 선택된 자산
- 비중이 0%인 자산
- 각 자산의 비중
- Expected Return
- Standard Deviation
- Sharpe Ratio
- 가능하면 CAGR
- 가능하면 Maximum Drawdown

각 후보 자산에 대한 첫 질문은 다음과 같다.

> **이 자산이 목표 함수 기준 최적 포트폴리오에 포함되는가?**

단, 이것은 출발점일 뿐 최종 판정이 아니다. 정확한 최적점에서 비중이 0%라고 해도 효율적 프론티어의 다른 구간에서 유용할 수 있으므로 그것만으로 탈락시키지 않는다.

---

## 3. Efficient Frontier를 가장 중요한 분석 표면으로 사용한다

Efficient Frontier Portfolios는 optimizer 결과에서 가장 정보량이 높은 출력 중 하나이며, 일반적인 자산 편입 연구에서는 **가장 중요한 분석 표면**으로 취급한다.

목표는 frontier raw row를 그대로 재진술하는 것이 아니다. 전체 frontier를 사용해 **구조, 전환, 안정성, 대체 관계, 제약 효과를 가능한 많이 추출**하는 것이다.

LLM은 저위험 구간부터 목표 함수 최적점 주변을 지나 고수익 구간까지 frontier 전체를 읽는다. 다만 사용자에게 모든 raw point를 나열하지 않고, 의미가 생기는 구간과 변화 지점을 근거와 함께 설명한다.

### 3.1 Frontier의 핵심 기준점을 먼저 잡는다

가능하면 다음 landmark를 식별한다.

- Minimum Variance 또는 가장 낮은 위험의 유효 포트폴리오
- Maximum Sharpe 포트폴리오
- Maximum Return 또는 고수익 frontier 끝점
- Sharpe가 거의 유지되는 near-optimal 구간
- allocation 구조가 크게 바뀌는 전환점
- constraint가 처음 binding되기 시작하는 지점

이 landmark는 frontier를 몇 개 point로 축소하기 위한 것이 아니라, **전체 frontier를 구간별로 해석하기 위한 좌표**다.

### 3.2 Frontier의 기하와 risk-return trade-off를 읽는다

인접한 frontier 구간에서 다음을 확인한다.

- Expected Return 증가폭
- Volatility 증가폭
- Sharpe 변화
- 같은 return 증가를 얻기 위해 요구되는 추가 risk의 변화
- 작은 return 차이에 비해 allocation이 크게 변하는 지점

질문:

> **어느 구간까지는 risk를 추가하는 대가가 합리적이고, 어느 지점부터 급격히 비효율적이 되는가?**

frontier가 완만한 구간, 급격히 가팔라지는 구간, 효율 개선이 거의 없는 구간을 구분한다.

### 3.3 각 자산의 allocation trajectory를 추적한다

각 자산마다 가능하면 다음을 읽는다.

- frontier에 처음 등장하는 지점
- 의미 있는 비중을 갖기 시작하는 지점
- 비중이 가장 높은 지점
- 다시 감소하거나 퇴출되는 지점
- 목표 함수 최적점 주변에서 유지되는 비중 범위
- 넓은 구간에서 존재하는지, 좁은 corner에서만 존재하는지
- 비중 변화가 연속적인지, 갑자기 튀는지
- min/max constraint에 언제부터 붙는지

이를 통해 자산의 역할이 저위험, 중위험, 고수익 중 어느 구간에서 나타나는지 판단한다.

### 3.4 Frontier에서의 자산 행동 유형

**A. 거의 모든 프론티어에서 0%**

다른 자산 조합이 해당 자산의 역할을 대부분 지배하고 있다는 뜻이다.

1차 해석: **한계 효용이 낮음**

**B. 저위험 구간에서만 등장**

일부 분산 효과는 있지만 더 높은 수익률을 요구하면 효용이 빠르게 사라진다.

1차 해석: **약한 또는 방어형 Diversifier**

**C. 목표 함수 최적점 주변에서 지속적으로 존재**

강한 신호다. 하나의 정확한 최적점에서만 큰 비중이 나오는 것보다 인접한 여러 프론티어 포트폴리오에서 의미 있는 비중을 유지하는 것이 더 신뢰할 수 있다.

1차 해석: **구조적인 포트폴리오 기여 자산**

**D. 주로 고수익 구간에서 등장**

Risk-adjusted return을 최대로 만드는 자산은 아니지만 Expected Return을 높이는 데 기여한다.

1차 해석: **Return Engine**

**E. 매우 좁은 구간에서만 급격히 등장하거나 사라짐**

추정치나 covariance의 작은 변화에 allocation이 민감할 가능성이 있다.

1차 해석: **불안정한 corner allocation**

### 3.5 정확한 한 점보다 plateau와 안정 구간을 우선한다

17.3%, 24.6%처럼 하나의 정확한 비중에 과도한 의미를 부여하지 않는다.

인접한 portfolio에서도 risk-return 효율과 구성의 질이 비슷하게 유지되는 안정 구간 또는 plateau를 찾는다.

특히 Maximum Sharpe 근처에서는 다음을 함께 본다.

- Sharpe가 거의 동일하게 유지되는 범위
- Expected Return 범위
- Volatility 범위
- 각 자산의 비중 범위
- portfolio 구성의 변화량

좁은 수학적 최적점보다 넓은 유효 구간이 더 중요하다.

### 3.6 자산 간 대체 관계를 frontier 전체에서 추적한다

후보 자산의 비중이 증가할 때 어떤 기존 자산의 비중이 감소하는지 확인한다.

단일 point에서의 before/after보다 frontier 여러 구간에서 같은 대체 패턴이 반복되는지 확인한다.

예:

- 후보 자산 증가와 함께 QQQ가 반복적으로 감소한다 → 성장/고베타 역할의 대체 가능성
- 후보 자산 증가와 함께 금 또는 채권성 자산이 감소한다 → 방어/분산 역할의 대체 가능성
- 후보가 증가해도 기존 핵심 자산 비중이 크게 줄지 않는다 → 새로운 독립 역할 가능성

핵심 질문:

> **이 후보 자산은 누구를 밀어내며, 그 교체가 portfolio에 무엇을 새로 가져오는가?**

### 3.7 Frontier의 집중도와 구성 다양성 변화를 본다

저위험에서 고수익으로 이동하면서 다음을 확인한다.

- 활성 자산 수가 줄어드는가
- 한두 자산에 allocation이 몰리는가
- 특정 후보가 추가되면서 기존 concentration이 완화되는가
- 반대로 후보가 기존 portfolio를 더 집중시키는가

높은 Expected Return이 단순히 한 자산 집중의 결과인지, 여러 독립 수익엔진의 조합인지 구분한다.

### 3.8 작은 성과 차이에 큰 allocation 변화가 있는지 본다

두 인접 frontier point의 Expected Return / Volatility / Sharpe 차이는 매우 작은데 자산 비중이 크게 뒤집힌다면 해당 exact allocation은 신뢰하기 어렵다.

이 경우 다음처럼 해석한다.

> Portfolio 효율은 비교적 평평하지만 optimizer allocation은 불안정하다. 따라서 정확한 비중보다 두 구성을 모두 포함하는 넓은 allocation range 또는 역할 수준의 결론이 더 신뢰할 만하다.

### 3.9 Raw frontier는 evidence source이지 최종 설명 형식이 아니다

가능한 많은 해석을 얻기 위해 frontier 전체 데이터를 사용한다.

하지만 최종 분석에서는 100개 point를 그대로 나열하기보다 다음을 빠짐없이 추출한다.

```text
landmarks
risk-return 구간
Sharpe-Return plateau
asset entry / exit / peak / persistent range
constraint binding events
allocation transition events
asset substitution patterns
concentration changes
unstable corner regions
대표적인 근거 point
```

즉 **정보를 줄이는 것이 아니라 raw point를 구조적 evidence로 변환한다.**

---

## 4. Sharpe 희생 대비 Expected Return 증가를 비교한다

Maximum Sharpe 지점에서 시작해 더 높은 Expected Return을 가진 프론티어 포트폴리오 쪽으로 이동하며 비교한다.

확인 항목:

- Expected Return 증가폭
- Volatility 증가폭
- Sharpe 하락폭
- 구성 자산 변화

핵심 질문:

> **Risk-adjusted efficiency를 얼마나 포기하고 Expected Return을 얼마나 추가로 얻는가?**

Sharpe가 조금만 낮아지면서 Expected Return이 의미 있게 높아지는 구간은 정확한 Maximum Sharpe 한 점보다 실제 운용에서 더 매력적인 후보가 될 수 있다.

반대로 작은 추가 수익을 위해 Volatility가 크게 증가하거나 Sharpe가 급격히 하락한다면 비효율적인 구간이다.

숫자상 최고 Sharpe 한 점이 아니라 **Sharpe-Return plateau**를 찾는다.

---

## 5. 자산 대체 관계를 추적한다: 누가 들어오고 누가 빠지는가

후보 자산의 비중이 증가할 때 어떤 기존 자산의 비중이 감소하는지 확인한다.

이 변화는 후보 자산의 실제 포트폴리오 역할을 드러내는 경우가 많다.

예:

- 고베타 성장 자산이 QQQ를 대체한다: 기존 성장 엔진의 고수익 버전일 가능성
- 한 지역 주식이 다른 지역 주식을 대체한다: 지역 노출 측면에서 중복 가능성
- 후보 자산이 계속 0%이고 기존 두 자산이 유지된다: 기존 자산들이 후보의 유용한 특성을 더 효율적으로 제공하고 있을 가능성

항상 다음 질문을 한다.

> **이 후보 자산은 어떤 기존 자산을 대체하며, 기존 포트폴리오에 실제로 무엇을 새로 추가하는가?**

개별적으로 좋은 자산이어도 포트폴리오에서는 중복 자산일 수 있다.

---

## 6. Correlation은 Return과 Volatility를 함께 본다

Correlation은 진단 근거이지 단독 선택 기준이 아니다.

다음과 같이 단순 해석하지 않는다.

> 낮은 Correlation = 좋은 포트폴리오 자산

반드시 함께 확인한다.

- 주요 포트폴리오 자산과의 Correlation
- Expected Return
- Standard Deviation
- 개별 Sharpe / Sortino
- Efficient Frontier 포함 여부

Correlation이 낮아도 Volatility가 너무 높거나 Expected Return이 낮다면 선택되지 않을 수 있다.

반대로 Correlation이 더 높더라도 Return efficiency가 충분히 강하면 유용할 수 있다.

핵심 질문:

> **이 자산이 주는 분산 효과를 얻기 위해 포기하는 수익과 추가되는 변동성이 감당할 만한가?**

---

## 7. 개별 자산 지표는 판정이 아니라 설명에 사용한다

구성 자산별로 다음을 확인한다.

- Expected Return
- CAGR
- Standard Deviation
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown

이 지표들은 optimizer가 왜 특정 자산을 선택하거나 배제했는지 설명하는 데 사용한다.

포트폴리오 수준의 결과보다 우선하지 않는다.

개별 Sharpe가 낮은 자산도 Correlation 구조 덕분에 포트폴리오를 개선할 수 있다. 반대로 개별 Sharpe가 매우 높은 자산도 기존 자산과 역할이 중복되면 선택되지 않을 수 있다.

우선순위:

> **포트폴리오 한계 효용 > 개별 자산 성과**

---

## 8. Regime별 행동을 확인한다

Annual Returns, Monthly Returns, Stress Periods, Up/Down Market Statistics를 이용해 자산이 어떤 환경에서 수익과 손실을 냈는지 확인한다.

질문:

- 주식 급락 시 방어 역할을 했는가?
- 인플레이션, 원자재, Growth, Value 등 특정 regime에서 주로 작동했는가?
- 전체 효용이 특정 한 해의 비정상적으로 좋은 성과에 크게 의존하는가?
- 관측된 움직임에 경제적으로 설명 가능한 역할이 있는가?

이 단계는 optimizer가 발견한 관계가 단순한 통계적 우연인지, 이해 가능한 경제적 역할을 가진 것인지 확인하는 과정이다.

Diversifier는 모든 regime에서 높은 수익을 낼 필요가 없다. 다른 자산과 다르게 움직이는 것 자체가 가치일 수 있다.

---

## 9. Drawdown의 깊이와 회복 시간을 함께 본다

확인 항목:

- Maximum Drawdown
- Worst Drawdowns
- Recovery Time
- Underwater Period
- Stress-period loss

MDD가 같다고 해서 동일한 위험으로 취급하지 않는다.

20% 하락 후 6개월 만에 회복하는 포트폴리오와 20% 하락 후 3년 동안 원금을 회복하지 못하는 포트폴리오는 실질적으로 다르다.

항상 다음 두 요소를 구분한다.

> **Drawdown Depth**와 **Drawdown Duration**

---

## 10. Rolling Return으로 기간 의존성을 확인한다

전체 기간 평균은 시작일과 종료일 선택에 대한 의존성을 숨길 수 있다.

가능하면 다음을 확인한다.

- Rolling 1-year Returns
- Rolling 3-year Returns
- Rolling 5-year Returns
- Average / High / Low

특히 Rolling 3-year 및 5-year의 Low 값을 중요하게 본다.

질문:

- 최적화 포트폴리오가 서로 다른 하위 기간에서도 받아들일 만한 결과를 유지하는가?
- 좋은 전체 기간 성과가 최근 특정 regime에 크게 의존하는가?
- 후보 자산의 기여가 지속적인가, 특정 좁은 기간에서만 나타나는가?

전체 기간 성과가 좋아도 Rolling Low가 약하다면 robustness 경고를 남긴다.

---

## 11. Contribution과 Decomposition으로 숨은 비용을 확인한다

가능한 경우 다음을 확인한다.

### Active Return Contribution

최근 기여도와 전체 기간 기여도를 비교한다.

1년 또는 3년 기여도는 강하지만 장기 기여도가 약하다면 최근 regime 의존 가능성이 있다.

### Return Decomposition

포트폴리오 이익 중 각 자산이 얼마나 기여했는지 확인한다.

### Risk Decomposition

포트폴리오 전체 변동성 중 각 자산이 얼마나 차지했는지 확인한다.

Allocation Weight, Return Contribution, Risk Contribution을 함께 비교한다.

예:

- 작은 비중 + 큰 Risk Contribution + 약한 Return Contribution: 비효율적
- 작은 비중 + 제한적인 Risk Contribution + 의미 있는 Return Contribution: 효율적

핵심 질문:

> **이 자산은 포트폴리오의 위험을 얼마나 소비했고, 그 대가로 얼마나 많은 수익을 제공했는가?**

---

## 12. 한계 효용은 portfolio의 변화량으로 평가한다

후보 자산의 standalone 성과보다 **후보가 portfolio에 들어왔을 때 무엇이 달라졌는지**를 본다.

가능한 경우 기준 portfolio와 후보를 허용한 portfolio 사이에서 다음 변화량을 비교한다.

```text
Δ Expected Return
Δ CAGR
Δ Volatility
Δ Sharpe
Δ Sortino
Δ Maximum Drawdown
Δ Drawdown Duration / Recovery
Δ Active Return
Δ Tracking Error / Information Ratio
Δ Risk Contribution structure
Δ Return Contribution structure
Δ Concentration / diversification structure
```

모든 항목이 개선될 필요는 없다. 연구 질문에 따라 어떤 trade-off를 얻었는지가 중요하다.

예:

- Return은 거의 동일하지만 Volatility와 MDD가 낮아짐 → Diversifier 가치
- Risk는 비슷하지만 Expected Return이 높아짐 → Return Engine 가치
- Sharpe가 약간 낮아지지만 Expected Return이 의미 있게 상승하고 frontier plateau가 넓음 → 실용적인 return-seeking allocation 가능성
- standalone 성과는 좋지만 portfolio 변화가 거의 없음 → Redundant 가능성

한계 효용을 판단할 때 단일 metric 개선보다 **여러 portfolio-level 변화가 같은 경제적 이야기를 지지하는지**를 본다.

---

## 13. Cross-experiment robustness를 확인한다

하나의 run에서 좋은 결과가 나왔다고 연구 결론을 확정하지 않는다.

같은 Study 안에 기간, objective, constraint 또는 후보 구성이 다른 experiment가 존재한다면 다음을 비교한다.

- 후보 자산의 포함/제외 방향이 유지되는가
- 자산의 역할 분류가 유지되는가
- frontier에서 등장하는 위험 구간이 비슷한가
- 안정적인 allocation range가 겹치는가
- max/min constraint가 바뀌어도 같은 방향의 수요가 나타나는가
- 기간을 바꿨을 때 결과가 완전히 뒤집히는가
- Maximum Sharpe와 Target Volatility 등 objective가 달라도 경제적 역할이 유지되는가

정확한 optimal weight가 달라지는 것 자체는 실패가 아니다.

더 중요한 질문은 다음이다.

> **조건이 조금 바뀌어도 이 자산의 portfolio role과 marginal utility의 방향이 유지되는가?**

여러 experiment에서 역할은 유지되지만 정확한 비중만 흔들린다면 `robust role / uncertain exact weight`로 해석할 수 있다.

반대로 단일 기간 또는 단일 constraint에서만 강하게 선택된다면 robustness 경고를 남긴다.

---

## 14. 최종 자산 역할 분류

모든 자산을 단순 KEEP/DROP 이분법으로 분류하지 않는다.

| 분류 | 의미 |
|---|---|
| **KEEP / Strong** | 목표 함수 최적점 주변과 인접한 프론티어 포트폴리오에서 의미 있는 비중이 지속된다. |
| **KEEP / Return Engine** | 주로 고수익 프론티어에서 Expected Return을 높이는 역할을 한다. |
| **KEEP / Diversifier** | 독립적인 움직임으로 저위험 또는 중위험 포트폴리오를 의미 있게 개선한다. |
| **WATCH** | 효용은 있으나 작거나 불안정하거나 좁은 프론티어/특정 regime에 한정된다. |
| **REDUNDANT** | 개별적으로 좋은 자산일 수 있으나 기존 자산이 같은 역할을 더 효율적으로 수행한다. |
| **DROP** | 관심 프론티어 구간에서 한계 효용이 거의 또는 전혀 없다. |

각 판정에는 반드시 Frontier에서의 행동과 이를 뒷받침하는 근거를 포함한다.

---

## 15. 결론은 Uncertainty와 Next Experiment까지 연결한다

분석은 KEEP/WATCH/DROP 판정으로 끝내지 않는다.

최종적으로 다음 네 가지를 구분한다.

```text
Current Conclusion
Evidence
Uncertainty
Next Experiment
```

예:

```text
Current Conclusion
GLD는 현재 portfolio에서 강한 diversifier 역할을 보인다.

Evidence
Max Sharpe 주변의 넓은 frontier 구간에서 의미 있는 비중을 유지하고,
portfolio volatility와 drawdown을 낮추는 방향으로 기여한다.

Uncertainty
GLD가 30% max constraint에 반복적으로 붙어 있어 적정 allocation 상단을 판단할 수 없다.

Next Experiment
GLD max weight를 40%, 50%로 완화해 frontier와 plateau가 어떻게 이동하는지 확인한다.
```

다음 experiment는 단순히 더 많은 run을 만드는 것이 아니라 **현재 결론을 가장 크게 흔들 수 있는 불확실성을 줄이는 방향**으로 설계한다.

---

## 표준 분석 순서

모든 결과 검토에서 다음 순서를 기본으로 사용하되 Study 질문에 따라 깊이를 조절한다.

1. **Study의 연구 질문과 판정 대상 확인**
2. **실험 조건과 제약 확인**
3. **목표 함수 기준 최적 포트폴리오를 기준점으로 확인**
4. **Efficient Frontier 전체의 구조와 landmark 확인**
5. **각 자산의 frontier trajectory와 안정 구간 추적**
6. **Sharpe 희생 대비 Expected Return 증가 평가**
7. **자산 대체 관계, constraint event, concentration 변화 확인**
8. **Correlation을 Return / Volatility와 함께 해석**
9. **portfolio-level marginal utility 변화량 평가**
10. **개별 자산 지표는 보조 근거로 사용**
11. **Regime / Annual Return 행동 확인**
12. **Drawdown과 Recovery 확인**
13. **Rolling Return으로 기간 robustness 확인**
14. **Active Return / Return-Risk Decomposition 확인**
15. **가능하면 cross-experiment robustness 확인**
16. **역할 기반 현재 결론 도출**
17. **Uncertainty와 Next Experiment 정의**

---

## 해석 Guardrail

- 과거 Maximum Sharpe 비중을 현재의 권장 비중으로 그대로 해석하지 않는다.
- 최소/최대 비중 제약에 걸린 결과를 unconstrained optimum으로 해석하지 않는다.
- 개별 Sharpe가 낮다는 이유만으로 자산을 탈락시키지 않는다.
- Correlation이 낮다는 이유만으로 자산을 선택하지 않는다.
- 하나의 정확한 frontier point를 과대평가하지 않고 인접한 안정 구간을 우선한다.
- Frontier raw row를 모두 나열하는 것을 깊은 분석으로 착각하지 않는다.
- 작은 risk-return 차이에 allocation이 크게 바뀌면 exact weight의 신뢰도를 낮춘다.
- 최근 성과 또는 짧은 공통 분석 기간에 크게 의존하는 결과는 명시적으로 경고한다.
- 통계적으로 선택된 사실과 경제적으로 이해 가능한 포트폴리오 역할을 구분한다.
- 하나의 run에서 얻은 결론과 여러 experiment에서 반복 확인된 결론의 신뢰도를 구분한다.

---

## 권장 LLM 응답 형식

### 1. 핵심 결론

2~4문장으로 현재 Study 질문에 대한 portfolio-level 발견을 먼저 제시한다.

### 2. 실험 조건과 목표 함수 기준 포트폴리오

중요한 constraint, data coverage와 목표 함수 기준 구성을 정리한다.

### 3. Frontier 심층 해석

가능한 범위에서 다음을 설명한다.

- 핵심 landmark와 frontier 구간
- 후보 자산의 진입 / 퇴출 / peak / persistent allocation range
- Sharpe-Return plateau
- allocation이 크게 바뀌는 transition point
- constraint binding point
- 어떤 자산이 들어오고 빠지는지
- concentration 변화
- 불안정한 corner allocation 여부

raw frontier 전체를 반복하지 않고, 의미 있는 구조와 대표 근거 point를 충분히 제시한다.

### 4. Portfolio Marginal Utility

후보 또는 최적화 결과가 기준 portfolio 대비 Return, Risk, Drawdown, Sharpe, Contribution 구조를 어떻게 바꾸는지 설명한다.

### 5. 분산 효과와 중복성

Correlation을 Return / Volatility 및 대체 관계와 함께 해석한다.

### 6. Robustness

Drawdown, Recovery, Rolling Returns, Regime 의존성과 가능하면 cross-experiment 일관성을 요약한다.

### 7. 최종 역할 분류

중요 후보를 다음 중 하나로 분류한다.

`KEEP / Strong`, `KEEP / Return Engine`, `KEEP / Diversifier`, `WATCH`, `REDUNDANT`, `DROP`

각 분류의 근거를 함께 제시한다.

### 8. 남은 불확실성과 다음 실험

현재 결론을 가장 크게 흔들 수 있는 불확실성을 명시하고, 이를 검증할 다음 experiment를 제안한다.

---

## 핵심 원칙

> **Optimization은 과거 최적 비중을 복사하기 위한 도구가 아니라 포트폴리오 구조를 발견하기 위한 도구로 사용한다. 핵심은 각 자산이 독립적이고 의미 있는 한계 효용을 추가하는지, 어떤 역할을 하는지, 그리고 그 역할이 효율적 프론티어와 시간·조건의 변화 속에서도 유지되는지를 판단하는 것이다. Efficient Frontier는 이 구조를 발견하기 위한 가장 중요한 분석 표면이며, 목표는 raw point를 줄이는 것이 아니라 그 안의 구조적 의미를 최대한 추출하는 것이다.**
