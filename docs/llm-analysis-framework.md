# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 최적화 결과 페이지 또는 이에 준하는 포트폴리오 최적화 결과를 전달받은 LLM이 독립적으로 결과를 해석할 수 있도록 만든 핸드오버/참조 문서다.

LLM은 과거 데이터에서 계산된 최적 비중을 현재의 권장 비중으로 그대로 받아들이지 않는다. 분석의 목적은 다음 질문에 답하는 것이다.

> **각 자산이 포트폴리오에 어떤 한계 효용(marginal utility)을 추가하는가, 그 효용은 효율적 프론티어의 어느 구간에서 나타나는가, 그리고 그 역할은 실제로 의미 있고 견고한가?**

분석의 중심은 개별 자산 성과가 아니라 포트폴리오 수준의 효용이다. 개별 자산 성과는 주된 판정 기준이 아니라 이를 설명하는 보조 근거로 사용한다.

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

## 3. Efficient Frontier 전체를 확인한다

Efficient Frontier Portfolios 표는 결과 페이지에서 가장 정보량이 높은 출력 중 하나다.

저위험 구간부터 목표 함수 최적점 주변을 지나 고수익 구간까지 순서대로 읽으면서 각 자산의 비중 변화 궤적을 추적한다.

### Frontier에서의 자산 행동 유형

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

### 정확한 한 점보다 구간을 우선한다

17.3%, 24.6%처럼 하나의 정확한 비중에 과도한 의미를 부여하지 않는다.

인접한 포트폴리오에서도 성과와 구성의 질이 비슷하게 유지되는 안정 구간 또는 plateau를 찾는다.

좁은 수학적 최적점보다 넓은 유효 구간이 더 중요하다.

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

## 12. 최종 자산 역할 분류

모든 자산을 단순 KEEP/DROP 이분법으로 분류하지 않는다.

| 분류 | 의미 |
|---|---|
| **KEEP / Strong** | 목표 함수 최적점 주변과 인접한 프론티어 포트폴리오에서 의미 있는 비중이 지속된다. |
| **KEEP / Return Engine** | 주로 고수익 프론티어에서 Expected Return을 높이는 역할을 한다. |
| **KEEP / Diversifier** | 독립적인 움직임으로 저위험 또는 중위험 포트폴리오를 의미 있게 개선한다. |
| **WATCH** | 효용은 있으나 작거나 불안정하거나 좁은 프론티어/특정 regime에 한정된다. |
| **REDUNDANT** | 개별적으로 좋은 자산일 수 있으나 기존 자산이 같은 역할을 더 효율적으로 수행한다. |
| **DROP** | 관심 프론티어 구간에서 한계 효용이 거의 또는 전혀 없다. |

각 판정에는 반드시 Frontier에서의 행동과 이를 뒷받침하는 근거를 짧게 포함한다.

---

## 표준 분석 순서

모든 결과 검토에서 다음 순서를 사용한다.

1. **실험 조건과 제약 확인**
2. **목표 함수 기준 최적 포트폴리오를 기준점으로 확인**
3. **Efficient Frontier에서 자산 비중 변화 추적**
4. **Sharpe 희생 대비 Expected Return 증가 평가**
5. **자산 대체 관계와 포트폴리오 역할 확인**
6. **Correlation을 Return / Volatility와 함께 해석**
7. **개별 자산 지표는 보조 근거로 사용**
8. **Regime / Annual Return 행동 확인**
9. **Drawdown과 Recovery 확인**
10. **Rolling Return으로 robustness 확인**
11. **Active Return / Return-Risk Decomposition 확인**
12. **역할 기반 최종 분류**

---

## 해석 Guardrail

- 과거 Maximum Sharpe 비중을 현재의 권장 비중으로 그대로 해석하지 않는다.
- 최소/최대 비중 제약에 걸린 결과를 unconstrained optimum으로 해석하지 않는다.
- 개별 Sharpe가 낮다는 이유만으로 자산을 탈락시키지 않는다.
- Correlation이 낮다는 이유만으로 자산을 선택하지 않는다.
- 하나의 정확한 frontier point를 과대평가하지 않고 인접한 안정 구간을 우선한다.
- 최근 성과 또는 짧은 공통 분석 기간에 크게 의존하는 결과는 명시적으로 경고한다.
- 통계적으로 선택된 사실과 경제적으로 이해 가능한 포트폴리오 역할을 구분한다.

---

## 권장 LLM 응답 형식

### 1. 핵심 결론

2~4문장으로 포트폴리오 수준의 주요 발견을 먼저 제시한다.

### 2. 목표 함수 기준 포트폴리오

구성과 핵심 지표를 정리한다.

### 3. Frontier 해석

다음을 설명한다.

- 후보 자산의 비중 변화 궤적
- Sharpe-Return plateau
- 어떤 자산이 들어오고 빠지는지

### 4. 분산 효과와 중복성

Correlation을 Return / Volatility 및 대체 관계와 함께 해석한다.

### 5. Robustness

Drawdown, Recovery, Rolling Returns, Regime 의존성을 요약한다.

### 6. 최종 분류

중요 후보를 다음 중 하나로 분류한다.

`KEEP / Strong`, `KEEP / Return Engine`, `KEEP / Diversifier`, `WATCH`, `REDUNDANT`, `DROP`

각 분류의 근거를 함께 제시한다.

---

## 핵심 원칙

> **Optimization은 과거 최적 비중을 복사하기 위한 도구가 아니라 포트폴리오 구조를 발견하기 위한 도구로 사용한다. 핵심은 각 자산이 독립적이고 의미 있는 한계 효용을 추가하는지, 어떤 역할을 하는지, 그리고 그 역할이 효율적 프론티어와 시간의 변화 속에서도 유지되는지를 판단하는 것이다.**
