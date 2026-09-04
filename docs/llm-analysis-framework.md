# 포트폴리오 연구 결과 LLM 분석 프레임워크

## 목적

이 문서는 `portfolio-optimizer-kr`의 Optimization 또는 Backtest 결과를 LLM이 **사용자 의사결정 관점에서 해석**하기 위한 canonical framework다.

LLM의 주된 가치는 report의 숫자를 다시 읽어주는 것이 아니다. 현재 Run의 canonical artifact를 확인하고, 사용자의 연구 질문에 맞는 product-specific 분석 경로를 선택한 뒤 정량적 evidence를 연결하여 구조, trade-off, 취약성, 안정성, 다음 연구를 설명해야 한다.

기본 우선순위는 다음과 같다.

```text
사용자 질문
-> product_mode 확인
-> 정량적 insight
-> 구조적 해석
-> 필요한 supporting evidence
-> 부족한 evidence를 채우는 다음 실험
```

정성적 경제/regime 설명은 중요하지만 **정량 분석을 대체하지 않는다.** `주식이 많다`, `인플레이션 자산이 없다` 같은 일반론은 데이터에서 확인된 구조적 취약성을 설명하거나 다음 실험의 가설을 만들 때만 사용한다.

---

# Product Analysis Routing

분석 전에 반드시 Run의 `product_mode`를 canonical artifact에서 확인한다.

```text
product_mode: optimization
-> Optimization Analysis Branch

product_mode: backtest
-> Backtest Analysis Branch
```

`product_mode`가 없거나 지원하지 않는 값이면 결과 내용을 보고 LLM이 임의로 추론하여 분석 branch를 선택하지 않는다. Run identity/input 문제로 취급하고 product mode를 먼저 확인한다.

두 branch는 동일한 historical analytics를 일부 공유할 수 있지만 질문의 의미가 다르다.

```text
Optimization
= 주어진 Asset Universe와 constraints 안에서
  어떤 allocation이 더 효율적인가?

Backtest
= 이미 정의된 portfolio가
  해당 역사 표본에서 실제로 어떻게 행동했는가?
```

따라서 Backtest 결과만으로 `optimal allocation`, `efficient frontier`, `적정 최적 비중`을 주장하지 않는다. 반대로 Optimization에서는 historical CAGR/MDD만 보고 optimizer가 발견한 구조를 대체하지 않는다.

---

# Branch A. Optimization Analysis

Optimization의 기본 사고 순서는 다음 7단계다.

모든 단계를 사용자 답변에 동일한 길이로 출력할 필요는 없다. 내부 분석은 이 순서를 따르되, 사용자에게는 현재 Study에서 의미 있는 insight만 압축해 전달한다.

```text
1. Portfolio Diagnosis
2. Optimizer Structure
3. Asset Utility
4. Efficient Allocation Range
5. Frontier Fragility
6. Evidence Sufficiency & Robustness
7. Next Research
```

## A1. Portfolio Diagnosis

핵심 질문:

> **현재 구조는 얼마나 비효율적이고 어디가 취약한가? 최적화 후에도 어떤 취약성이 남는가?**

Provided Portfolio가 있으면 현재 포트와 Optimized Portfolio를 모두 진단한다.

### A1.1 Efficiency Gap

현재 포트가 frontier에서 얼마나 안쪽에 있는지 본다.

가능하면 두 질문에 답한다.

1. **같은 Expected Return에서 frontier는 Volatility를 얼마나 낮출 수 있었는가?**
2. **같은 Volatility에서 frontier는 Expected Return을 얼마나 높였는가?**

Interpolation은 frontier가 해당 Return 또는 Volatility를 실제로 bracket하는 범위 안에서만 사용한다. 범위 밖이면 extrapolation하지 않는다.

### A1.2 Quantitative Vulnerability

Efficiency와 Robustness는 다르다. 현재 포트가 frontier에 가까워도 구조적 취약성이 있을 수 있다.

가능하면 다음 축 중 실제로 의미 있는 문제만 선택하여 정량적으로 압축한다.

#### Risk Concentration

- 특정 자산 또는 상관 cluster가 portfolio risk를 얼마나 지배하는가?
- Allocation Weight와 Risk Contribution이 크게 다른가?
- 명목상 자산 수보다 실제 risk source가 훨씬 적은가?

#### Correlation Redundancy

Correlation matrix를 나열하지 않는다.

서로 강하게 함께 움직이는 자산을 묶어 **실질적인 독립 움직임이 얼마나 되는지** 설명한다.

필요하면 correlation clustering, PCA, effective independent bets 같은 정량 분석을 후속 기능 또는 실험으로 제안할 수 있다.

#### Drawdown Co-failure

평균 correlation이 낮아도 stress 구간에서는 함께 무너질 수 있다.

가능하면 다음을 본다.

- 주요 drawdown에서 어떤 자산/cluster가 동시에 하락했는가
- worst-N months의 동시 하락 정도
- stress-period conditional correlation
- portfolio drawdown에 크게 기여한 자산/cluster

핵심 질문은 `평균적으로 분산되는가?`가 아니라 **`나쁜 시기에 실제로 분산되는가?`**다.

#### Return Dependence

- 역사적 수익의 대부분이 특정 자산/cluster에서 발생했는가?
- Allocation 대비 Return Contribution이 과도하게 집중되는가?

숫자는 표 전체를 반복하지 말고 취약성의 크기를 이해시키는 핵심 1~3개만 사용한다.

### A1.3 Optimized Portfolio도 다시 진단한다

Optimizer는 **주어진 Asset Universe 안에서** 효율적인 조합을 찾을 뿐, 결과 자체가 구조적으로 robust하다고 보장하지 않는다.

따라서 최적화 후에도 확인한다.

- Risk Concentration이 더 커졌는가?
- 높은 상관의 자산들이 큰 비중을 동시에 차지하는가?
- 안정성이 특정 diversifier 하나에 과도하게 의존하는가?
- drawdown protection이 특정 역사 구간에만 의존하는가?

> **Efficient within universe ≠ Structurally robust**

---

## A2. Optimizer Structure

핵심 질문:

> **Optimizer는 어떤 포트폴리오 구조를 발견했는가?**

Maximum Sharpe의 정확한 비중부터 설명하지 않는다.

먼저 여러 후보 중 실제 frontier를 반복적으로 만드는 **핵심 엔진 조합**을 찾는다.

그 다음 exact weight, frontier trajectory, constraint, correlation 등을 근거로 붙인다.

### Constraint Pressure

최적 비중이 min/max에 붙으면 그 비중을 `적정 비중`으로 해석하지 않는다.

```text
Role inference         = 강할 수 있음
Exact weight inference = 약함
```

한 점의 boundary touch보다 near-efficient 구간에서 계속 상한/하한에 붙는 **persistent pressure**를 더 중요하게 본다.

---

## A3. Asset Utility

핵심 질문:

> **이 자산은 왜 필요한가? 그리고 그 필요성은 얼마나 큰가?**

주요 자산은 `Role -> Utility Magnitude` 순으로 해석한다.

### A3.1 Role: 왜 필요한가?

예:

- Return Engine
- Return Enhancer
- Diversifier
- Low-risk Stabilizer
- Substitute
- Not Selected in Current Model

Role은 standalone Sharpe만으로 정하지 않는다. Frontier trajectory와 portfolio interaction을 우선한다.

### A3.2 Utility Magnitude: 얼마나 필요한가?

단순 `선택됨 / 0%`가 아니라 portfolio 효용의 **크기**를 본다.

#### 수익 기여

- Allocation 대비 Return Contribution
- 자산을 제거했을 때 동일 Volatility에서 Expected Return이 얼마나 감소하는가
- 높은 Return target으로 갈수록 비중이 지속적으로 증가하는가

#### 안정성 기여

- 자산을 제거했을 때 동일 Expected Return에서 Volatility가 얼마나 증가하는가
- Risk Contribution 대비 allocation이 효율적인가
- 낮은 risk budget으로 갈수록 비중이 증가하는가
- drawdown / downside / recovery에서 실제 보호 효과가 관찰되는가

#### Breadth of Utility

- 넓은 risk/return 영역에서 지속적으로 필요한가
- 특정 사용자 목표에서만 필요한가
- 아주 좁은 frontier 구간 또는 작은 비중에서만 필요한가

필요성 강도는 다음처럼 해석할 수 있다.

- **Structural**: 넓은 risk/return 영역에서 반복적으로 필요
- **Target-dependent**: 특정 목표에서만 필요
- **Marginal**: 아주 좁은 영역 또는 작은 비중에서만 필요
- **Not Selected in Current Model**: 현재 조건에서 frontier 효용이 확인되지 않음

`REDUNDANT`는 단순 0%가 아니라 **다른 자산이 같은 역할을 더 효율적으로 대체한다는 evidence가 있을 때만** 사용한다.

### A3.3 Diversifier Dependency는 correlation보다 ablation을 우선한다

특정 diversifier가 중요해 보인다면 가능하면 **그 자산이 없을 때 portfolio가 얼마나 악화되는지** 확인한다.

Leave-one-out / ablation에서 본다.

- 동일 Expected Return에서 Δ Volatility
- 동일 Volatility에서 Δ Expected Return
- Δ Max Sharpe
- drawdown / recovery 변화
- risk concentration 변화

이런 정량 evidence가 있을 때 `single-diversifier dependency` 같은 강한 구조적 표현을 사용한다.

---

## A4. Efficient Allocation Range

핵심 질문:

> **사용자의 목표 Risk / Return에서는 이 자산을 어느 정도 비중으로 가져가는 것이 역사적으로 효율적이었는가?**

Max Sharpe 한 점보다 **사용자의 실제 목표 구간에서 반복적으로 선택되는 비중 범위**를 우선한다.

### A4.1 Risk Budget 기준

사용자가 감수할 수 있는 Volatility 구간이 있다면 그 frontier 구간에서 본다.

- 주요 자산의 비중 범위
- 어떤 자산이 등장/퇴출하는가
- 추가 Return을 얻기 위해 무엇을 줄이는가
- Risk Concentration이 어떻게 변하는가

### A4.2 Return Target 기준

사용자가 Expected Return 목표를 제시하면 해당 Return을 만들기 위한:

- Minimum Volatility
- Allocation Range
- 구조 변화

를 같은 방식으로 본다.

### A4.3 Frontier를 메뉴판으로 사용한다

Efficient Frontier는 추상적인 곡선이 아니라 **Risk를 더 감수하거나 Return을 더 요구할 때 어떤 자산을 늘리고 무엇을 포기해야 했는지 보여주는 메뉴판**으로 해석한다.

### A4.4 현재 Run만으로 부족하면 목표 조건의 추가 Run을 제안한다

현재 frontier만으로 대략적인 범위는 읽을 수 있지만 사용자의 실제 목표에 대해 더 직접적인 evidence가 필요할 수 있다.

예:

```text
Maximum Return @ Vol 12%
Maximum Return @ Vol 13%
Maximum Return @ Vol 14%
```

또는:

```text
Minimum Volatility @ Expected Return 12%
Minimum Volatility @ Expected Return 14%
Minimum Volatility @ Expected Return 16%
```

목적은 sensitivity run을 많이 만드는 것이 아니라 **사용자의 목표 안에서 efficient allocation range를 더 정확히 식별하는 것**이다.

이 단계에서 얻은 비중 범위는 미래 적정 비중이 아니라 **현재 역사 표본에서의 efficient range**다.

---

## A5. Frontier Fragility

핵심 질문:

> **이 비중과 구조는 안정적인가, 아니면 칼날 위의 optimum인가?**

Risk 또는 Return 목표를 조금만 바꿨는데 allocation이 크게 바뀐다면 exact optimal weight는 불안정하다.

반대로 넓은 목표 구간에서 특정 자산의 비중과 역할이 유지되면 해당 역할과 allocation range에 대한 신뢰는 높아진다.

### A5.1 인접 Efficient Portfolio를 비교한다

작은 Risk/Return 변화에서 확인한다.

- 주요 자산 비중이 얼마나 움직이는가
- 자산이 갑자기 등장/퇴출하는가
- cluster 간 자금이 크게 이동하는가
- Sharpe/Expected Return 개선은 작은데 allocation 변화는 큰가

필요하면 다음을 보조지표로 사용할 수 있다.

```text
Allocation Distance = 0.5 × Σ |weight_A - weight_B|
```

절대 threshold를 기계적으로 적용하지 않는다. 핵심은 **작은 risk/return 변화 대비 allocation 변화가 큰지**다.

### A5.2 Role Confidence와 Weight Confidence를 분리한다

| 구분 | 의미 |
|---|---|
| **Role Confidence** | 어떤 portfolio 역할을 하는지 얼마나 명확한가 |
| **Weight Confidence** | exact weight 또는 efficient range를 얼마나 신뢰할 수 있는가 |

Weight Confidence는 다음 경우 낮춘다.

- min/max constraint binding
- Frontier Fragility가 큼
- near-efficient 구간에서 비중이 크게 흔들림
- 기간/objective 변경 시 exact weight가 크게 변함
- material threshold 근처에서만 존재

Role은 안정적이지만 Weight Confidence가 낮은 것은 정상이다.

---

## A6. Evidence Sufficiency & Robustness

핵심 질문:

> **현재 evidence로 이 결론에 충분히 답할 수 있는가? 그리고 이 결과를 얼마나 믿을 수 있는가?**

현재 Run에서 관찰된 사실과 더 강한 결론에 필요한 evidence를 구분한다.

### A6.1 Supporting Evidence는 이유를 설명하거나 반증할 때만 사용한다

#### Correlation + Return + Volatility

낮은 correlation 자체를 좋은 자산의 증거로 사용하지 않는다. 낮은 상관을 얻기 위해 얼마의 낮은 return 또는 높은 volatility를 감수하는지 함께 본다.

#### Return / Risk Contribution

Allocation Weight와 Contribution의 불균형을 통해 Return Dependence 또는 Risk Concentration을 찾는다.

#### Drawdown / Recovery

MDD 깊이뿐 아니라 recovery/underwater 기간과 동시 하락 여부를 본다.

#### Rolling Return

Rolling 3Y/5Y Low 등으로 full-period 결과가 특정 시기에 과도하게 의존하는지 본다.

#### Regime / Annual Return

정량 구조를 설명하기 위한 보조 evidence다. 데이터로 확인되지 않은 경제적 라벨을 먼저 붙이지 않는다.

### A6.2 Missing Engine은 정량 취약점 뒤에만 제안한다

순서는 반드시 다음과 같다.

```text
정량적 취약성 발견
-> 구조적 문제 정의
-> 가능한 경제적 원인/대체 엔진 가설
-> 새 Asset Universe 실험
-> 실제 개선 여부 검증
```

### A6.3 Robustness 확인

필요하면 다음을 비교한다.

- 기간 변경
- objective 변경
- target risk / target return 변경
- constraint sensitivity
- 후보 포함/제외 ablation

역할은 반복되지만 정확한 비중만 흔들리면:

> `robust role / uncertain exact weight`

로 해석한다.

---

## A7. Next Research

핵심 질문:

> **다음에 어떤 실험을 하면 사용자 의사결정에 가장 많은 정보를 추가할 수 있는가?**

좋은 후속 실험은 다음 네 요소를 가진다.

```text
Uncertainty : 무엇을 아직 모르는가
Manipulation: 무엇만 바꾸는가
Observation : 어떤 결과를 볼 것인가
Decision    : 어떤 결과면 현재 해석이 강화/약화되는가
```

대표 유형:

1. Target-risk runs
2. Target-return runs
3. Constraint sensitivity
4. Leave-one-out / ablation
5. Universe expansion
6. Period / objective robustness

실험을 많이 제안하지 않는다. **사용자 의사결정을 가장 크게 바꿀 수 있는 불확실성부터 1~3개**만 우선한다.

---

# Branch B. Backtest Analysis

Backtest의 목적은 이미 정의된 portfolio의 **historical realized behavior**를 비교하고 해석하는 것이다.

Backtest에서 높은 CAGR이나 Sharpe를 확인했다고 해서 그 portfolio가 `최적`이라고 표현하지 않는다. 결과는 해당 데이터 coverage, rebalancing, benchmark, portfolio definition 아래에서 관찰된 역사적 결과다.

기본 사고 순서는 다음 8단계다.

```text
1. Effective Data Coverage
2. Return / Risk
3. Drawdown / Recovery
4. Annual / Rolling Consistency
5. Benchmark-relative Behavior
6. Correlation Structure
7. Contribution / Diversification Evidence
8. Evidence Limitation / Next Research
```

모든 단계를 사용자 답변에 동일한 길이로 출력할 필요는 없다. 사용자의 질문과 실제 evidence에 의미 있는 단계만 압축해서 보여준다.

---

## B1. Effective Data Coverage

핵심 질문:

> **우리가 실제로 어떤 역사 구간을 비교하고 있으며, 이 기간이 결론을 왜곡할 수 있는가?**

Backtest 결과를 비교하기 전에 requested period와 실제 effective period를 확인한다.

확인할 항목:

- requested Time Period
- effective common period
- 시작/종료 시점
- observation 수
- 특정 asset 또는 benchmark가 공통기간을 제한했는가
- portfolio 간 비교가 동일 coverage 위에서 이루어지는가

사용자가 기간을 지정하지 않았으면 full common effective period가 적용됐는지 확인한다.

짧은 history asset 때문에 기간이 크게 줄었다면 performance 숫자보다 먼저 밝힌다.

예:

> 이 결과는 2004년 이후 전체 시장 역사가 아니라 GLD 데이터가 존재하는 공통기간부터의 비교다. 따라서 2000년 닷컴 버블 전체를 포함한 결론으로 확대하면 안 된다.

Coverage 차이가 portfolio 간 공정한 비교를 깨뜨리면 그 상태에서 승패를 해석하지 않는다.

---

## B2. Return / Risk

핵심 질문:

> **이 역사 표본에서 각 portfolio는 얼마의 수익을 위해 얼마의 위험을 감수했는가?**

사용자 질문에 필요한 범위에서 다음을 함께 본다.

- CAGR / Full-period return
- Annualized Return
- Standard Deviation / Volatility
- Sharpe
- Sortino
- Best / Worst Year 또는 period
- Maximum Drawdown은 B3에서 더 깊게 해석

한 지표로 승자를 정하지 않는다.

예를 들어 Portfolio A의 CAGR이 더 높지만 volatility와 MDD도 훨씬 높다면 `더 좋았다`보다 **더 높은 risk를 감수해 더 높은 return을 얻은 trade-off**로 설명한다.

반대로 CAGR이 비슷하면서 volatility, downside risk, MDD가 의미 있게 낮다면 risk-adjusted historical behavior의 개선 evidence로 볼 수 있다.

### CAGR과 Annualized Return을 구분한다

CAGR과 arithmetic annualized return을 같은 값처럼 사용하지 않는다.

- CAGR은 실제 복리 성장 경험을 설명할 때 우선한다.
- arithmetic annualized return은 사용된 calculation/report 의미론에 맞춰 별도로 해석한다.
- benchmark active return이 arithmetic mean 기반이면 CAGR 차이와 동일한 값으로 설명하지 않는다.

### Initial Balance는 비율 지표와 분리한다

End Balance는 사용자가 입력한 initial balance를 반영한 wealth outcome이다.

비율 성과와 절대 wealth를 혼동하지 않고 필요할 때만 함께 설명한다.

---

## B3. Drawdown / Recovery

핵심 질문:

> **나쁜 시기에 얼마나 깊게 손실이 났고, 얼마나 오래 물려 있었으며, 회복 특성은 어땠는가?**

평균 수익률만으로 Backtest를 평가하지 않는다.

가능하면 다음을 본다.

- Maximum Drawdown depth
- drawdown start / bottom / recovery
- underwater duration
- 주요 drawdown episode의 순위와 반복성
- 동일 stress period에서 portfolio 간 손실 차이
- benchmark 대비 방어 효과

CAGR이 비슷한 두 portfolio라면 drawdown depth와 duration 차이가 핵심 의사결정 evidence가 될 수 있다.

한 번의 큰 crisis에서만 방어됐는지, 여러 drawdown에서 반복적으로 방어됐는지도 구분한다.

`MDD가 낮다`를 곧바로 미래 방어력 보장으로 표현하지 않는다.

---

## B4. Annual / Rolling Consistency

핵심 질문:

> **Full-period 성과가 시간 전반에서 반복됐는가, 아니면 특정 좋은 구간에 크게 의존하는가?**

가능한 artifact를 사용해 시간 분산을 확인한다.

- Annual Returns
- Monthly Returns
- Trailing Returns
- Rolling 3Y / 5Y Returns
- rolling volatility가 있으면 함께 확인
- 특정 decade / sub-period 성과

Full-period CAGR이 높아도 rolling 3Y/5Y에서 자주 열세라면 `일관된 우위`라고 표현하지 않는다.

반대로 여러 시작점과 rolling window에서 비슷한 risk/return 특성이 반복되면 historical consistency에 대한 confidence를 높일 수 있다.

최근 1Y/3Y가 강하다는 이유만으로 장기 구조를 대표한다고 보지 않는다. 반대로 오래된 장기 평균이 최근 구조 변화를 가리는지도 필요하면 분리해서 본다.

---

## B5. Benchmark-relative Behavior

핵심 질문:

> **Benchmark가 존재할 때, portfolio의 절대성과와 별개로 상대 성과는 어떤 형태였는가?**

이 단계는 benchmark가 실제 Run에 존재할 때만 적용한다.

가능하면 다음을 본다.

- Active Return
- Tracking Error
- Information Ratio
- Rolling Active Return
- Up / Down Market Performance
- Active Return Contribution

Benchmark가 없으면 값을 0으로 채우거나 가상의 benchmark를 추가하지 않는다.

### 상대수익의 크기뿐 아니라 형태를 본다

예:

- 상승장에서 덜 오르고 하락장에서 훨씬 덜 빠지는가
- 상승/하락장에서 모두 benchmark를 이겼는가
- 장기 outperformance가 특정 몇 년에 집중됐는가
- Tracking Error 대비 active return이 충분했는가

Benchmark 대비 우위가 있어도 그 원인이 portfolio의 구조적 diversifier인지, 단순히 특정 return engine의 초과성과인지 B6/B7 evidence와 함께 확인한다.

---

## B6. Correlation Structure

핵심 질문:

> **portfolio 안의 자산들은 실제로 얼마나 독립적으로 움직였고, 어떤 자산들이 사실상 같은 risk source를 공유했는가?**

Correlation matrix를 그대로 읽어주지 않는다.

우선 다음 구조를 찾는다.

- 높은 상관의 asset cluster
- 낮거나 음의 상관을 가진 후보
- 명목상 여러 자산이지만 실제 움직임이 중복되는 부분
- benchmark와 portfolio/asset의 관계

### Correlation은 역할의 후보 evidence다

낮은 correlation만으로 `좋은 diversifier`라고 결론 내리지 않는다.

다음 단계의 evidence가 필요하다.

- 실제 allocation에서 의미 있는 비중을 가졌는가
- return contribution은 어떤가
- portfolio volatility 또는 drawdown을 실제로 줄였는가
- stress period에서도 diversification이 유지됐는가

### Stress correlation을 별도로 의식한다

Full-period 평균 correlation이 낮아도 crisis에서 함께 무너질 수 있다.

가능한 경우:

- 주요 drawdown 구간
- worst months
- 특정 stress period

에서 co-movement가 달라졌는지 확인한다.

현재 artifact가 stress conditional correlation을 직접 제공하지 않으면 평균 correlation만으로 stress diversification을 단정하지 않고 evidence gap으로 남긴다.

---

## B7. Contribution / Diversification Evidence

핵심 질문:

> **각 자산은 portfolio의 역사적 결과에 실제로 무엇을 기여했고, diversification 효과는 숫자로 확인되는가?**

가능하면 다음을 함께 본다.

- target allocation
- Return Contribution
- Risk Contribution
- asset standalone performance
- correlation
- drawdown / recovery evidence
- benchmark-relative contribution

### Return Contribution

Allocation보다 훨씬 큰 return contribution을 만든 자산은 return engine일 가능성이 있다.

반대로 작은 수익 기여만 했더라도 volatility 또는 drawdown 감소에 의미 있게 기여했다면 stabilizer/diversifier 역할일 수 있다.

Rebalanced portfolio의 contribution은 해당 Backtest의 실제 rebalancing path와 계산 의미론 아래에서 생성된 attribution이다. 이를 단순 buy-and-hold standalone return과 같은 의미로 설명하지 않는다.

### Risk Contribution

명목 비중이 작아도 portfolio risk를 크게 지배할 수 있다. Allocation Weight와 Risk Contribution의 차이를 통해 hidden concentration을 찾는다.

### Diversification 판정

`상관이 낮다` 하나로 끝내지 않는다.

가능하면 다음 evidence가 함께 있을 때 더 강한 표현을 사용한다.

```text
낮거나 보완적인 correlation
+ 실제 portfolio allocation
+ volatility / downside / drawdown 개선
+ return contribution 또는 opportunity cost 확인
```

예를 들어 금이 주식과 낮은 상관을 보였더라도 실제 drawdown 방어 또는 portfolio volatility 감소 evidence가 없다면 `필수 diversifier`라고 단정하지 않는다.

Backtest 하나만으로 특정 자산의 marginal utility를 강하게 주장하기 어렵다면 해당 자산을 제거하거나 비중을 바꾼 follow-up Backtest를 제안한다.

---

## B8. Evidence Limitation / Next Research

핵심 질문:

> **현재 Backtest로 무엇까지 말할 수 있고, 어떤 결론에는 추가 실험이 필요한가?**

Backtest는 historical realized evidence다. 미래 optimal allocation의 증거가 아니다.

현재 결론의 주요 limitation을 필요한 만큼만 밝힌다.

예:

- 짧은 common period
- 특정 crisis 또는 bull market 의존
- 한 가지 rebalancing frequency만 사용
- 하나의 benchmark만 사용
- asset universe가 좁음
- 특정 diversifier의 효과가 correlation만으로 추정됨
- 최근/과거 regime의 성과 차이가 큼

후속 연구는 evidence gap에 직접 답해야 한다.

대표 유형:

1. **Period robustness**
   - 다른 시작/종료 시점
   - crisis 포함/제외
   - sub-period 비교

2. **Rebalancing robustness**
   - Monthly / Quarterly / Annual / No Rebalancing 비교
   - 필요하면 Calendar Aligned 조건 비교

3. **Allocation sensitivity**
   - 핵심 자산 비중을 단계적으로 변경
   - 동일 asset union이면 같은 Experiment의 새 Run으로 비교

4. **Ablation / substitution**
   - 특정 자산 제거
   - 유사 역할 자산으로 교체

5. **Benchmark sensitivity**
   - 연구 질문상 benchmark 자체가 중요한 경우에만 변경

실험을 많이 제안하지 않는다. **현재 해석을 가장 크게 강화하거나 뒤집을 수 있는 1~3개**를 우선한다.

---

# 전 Branch 공통 Guardrail

아래 규칙은 별도의 분석 단계가 아니라 Optimization과 Backtest 모든 단계에 적용되는 품질 규칙이다.

## Run Identity / Data Validity

분석 전에 현재 Run을 canonical artifact에서 확인한다.

공통 확인:

- run_id
- product_mode
- asset universe
- benchmark
- risk-free convention
- 실제 effective period
- rebalancing

Optimization이면 추가 확인:

- provided portfolio
- objective
- constraints
- target volatility if applicable

Backtest이면 추가 확인:

- portfolio collection과 target weights
- initial balance
- Time Period mode / requested period
- Calendar Aligned

Repository 기반 시스템에서는 source priority를 따른다.

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

`report.html`은 presentation surface다. HTML을 눈으로 전사하거나 다시 계산해서 canonical result를 만들지 않는다.

다른 Run의 분석문이나 과거 대화 숫자를 현재 Run과 자동으로 섞지 않는다.

Data 문제는:

- **Blocking**: 계산 또는 핵심 비교 자체가 바뀔 수 있음
- **Reporting**: 일부 비교/report만 오염됨

으로 구분하고 영향을 받는 결론의 범위를 명시한다.

## In-sample / Ex-post Discipline

같은 역사 표본에서 추정하거나 관찰한 결과를 미래 성과처럼 표현하지 않는다.

좋은 표현:

- `이 역사 표본에서는 더 효율적이었다`
- `이 역사 표본에서는 CAGR과 MDD가 이랬다`
- `현재 추정치에서는 optimizer 수요가 강했다`
- `동일 역사 구간에서 drawdown이 더 얕았다`

피해야 할 표현:

- `앞으로 수익률을 3%p 높일 수 있다`
- `MDD를 줄여준다`
- `적정 비중은 20%다`

Expected Return, arithmetic Annualized Return, CAGR, Active Return은 계산 의미가 다르면 서로 같은 숫자처럼 섞지 않는다.

## Fact / Interpretation / Decision Separation

- **Observation / Fact**: artifact에서 직접 확인되는 사실
- **Interpretation**: 그 사실이 portfolio 구조에서 의미하는 것
- **Decision / Hypothesis**: 다음 연구 또는 후보 판단

경제적 원인 데이터가 없는 상태에서 특정 시기의 성과 원인을 설명한다면 `관측 사실`과 `원인 가설`을 분리한다.

## Numerical Materiality

별도 기준이 없으면 1% 미만 weight는 Optimization 사용자 서술에서 numerical dust로 보고 `사실상 퇴출`로 취급할 수 있다.

Study 특성상 작은 비중도 중요한 경우에는 기준을 명시적으로 바꾼다.

Backtest에서는 target allocation이 사용자가 직접 정의한 값이므로 작은 비중을 자동으로 무의미하다고 제거하지 않는다.

---

# Narrative Compression 규칙

## 1. Report를 다시 읽어주지 않는다

```text
report.html = 정확한 표, 차트, 전체 숫자 확인
LLM text    = 구조, trade-off, 취약성, 역할, 안정성, 다음 실험
```

## 2. 숫자는 insight를 위해서만 사용한다

숫자는 가능하면 다음 질문 중 하나에 답해야 한다.

- 무엇과 비교해 다른가?
- 얼마나 큰 차이인가?
- 어떤 Risk / Return 위치인가?
- 그래서 무엇을 의미하는가?

맥락 없는 숫자는 삭제 후보로 본다.

## 3. 자산은 사람이 읽을 수 있게 쓴다

첫 등장 시 `자산명/성격 (Ticker)`를 기본으로 한다.

예:

- 금 현물 (GLD)
- 나스닥100 성장주 (QQQ)
- 미국 중장기국채 (IEF)

## 4. Product-specific language를 지킨다

Optimization:

- efficient / frontier / optimized / constraint / expected return

Backtest:

- historical / realized / observed / drawdown / rolling / benchmark-relative

Backtest에 `optimizer가 선택했다`, `frontier`, `optimal weight` 같은 표현을 가져오지 않는다.

---

# 사용자 답변의 기본 Narrative

## Optimization

일반적인 답변은 다음 순서가 자연스럽다.

1. **Executive Thesis**
2. **Portfolio Diagnosis**
3. **Optimizer Structure**
4. **주요 Asset Utility와 Allocation Range**
5. **Fragility / Confidence**
6. **다음 Research**

Data Validity에 특별한 문제가 없으면 긴 validity 설명으로 시작하지 않는다. 짧게 확인하고 바로 insight로 이동한다.

## Backtest

일반적인 답변은 다음 순서가 자연스럽다.

1. **Executive Thesis**
2. **실제 비교기간 / Coverage 주의점**
3. **Return / Risk trade-off**
4. **Drawdown / 시간 일관성**
5. **Benchmark / Correlation / Contribution에서 중요한 evidence**
6. **현재 결론의 한계와 다음 Research**

Coverage가 결과 해석을 크게 제한하지 않으면 첫 문단을 긴 data-validity 보고서로 만들지 않는다.

---

# 최종 Self-Check

## Common

- [ ] `product_mode`를 canonical artifact에서 확인했는가?
- [ ] 다른 product의 분석 언어를 섞지 않았는가?
- [ ] result/review/raw source priority를 지켰는가?
- [ ] report 숫자를 반복하기보다 새로운 insight를 추가했는가?
- [ ] Observation / Interpretation / Decision을 구분했는가?
- [ ] 역사 표본의 결과를 미래 성과처럼 표현하지 않았는가?
- [ ] 남은 불확실성을 정보가치 높은 다음 실험으로 연결했는가?

## Optimization

- [ ] 현재 포트의 Efficiency와 Vulnerability를 구분했는가?
- [ ] Optimized Portfolio 자체의 구조적 취약성도 확인했는가?
- [ ] Risk Concentration / Correlation Redundancy / Drawdown Co-failure / Return Dependence 중 실제로 중요한 것을 정량적으로 압축했는가?
- [ ] Optimizer가 발견한 core structure를 exact weight보다 먼저 설명했는가?
- [ ] 주요 자산에 대해 `왜 필요한가 / 얼마나 필요한가`를 설명했는가?
- [ ] 사용자 목표 Risk / Return에서 efficient allocation range를 해석했는가?
- [ ] Frontier Fragility를 확인했는가?
- [ ] exact optimum보다 stable allocation range와 core structure를 우선했는가?
- [ ] diversifier importance를 correlation만이 아니라 가능하면 ablation으로 확인했는가?
- [ ] binding constraint를 적정 비중으로 오해하지 않았는가?

## Backtest

- [ ] requested/effective data coverage와 limiting asset을 확인했는가?
- [ ] CAGR과 volatility/downside를 함께 비교했는가?
- [ ] CAGR과 arithmetic annualized return을 같은 값처럼 사용하지 않았는가?
- [ ] MDD뿐 아니라 drawdown duration/recovery를 확인했는가?
- [ ] annual/rolling evidence로 full-period 결과의 시간 일관성을 확인했는가?
- [ ] benchmark가 있을 때만 active/relative metric을 사용했는가?
- [ ] correlation matrix를 나열하지 않고 redundancy/independence 구조를 설명했는가?
- [ ] 낮은 correlation만으로 diversifier라고 단정하지 않았는가?
- [ ] allocation / return contribution / risk contribution / drawdown evidence를 함께 봤는가?
- [ ] Backtest 결과를 optimal allocation의 증거로 표현하지 않았는가?
- [ ] 현재 evidence gap에 직접 답하는 후속 Backtest를 제안했는가?

---

# 핵심 원칙

> **먼저 `product_mode`를 확인하고 분석 branch를 결정한다. Optimization은 `Portfolio Diagnosis -> Optimizer Structure -> Asset Utility -> Efficient Allocation Range -> Frontier Fragility -> Evidence Sufficiency & Robustness -> Next Research` 순서로 사고한다. Backtest는 `Effective Data Coverage -> Return / Risk -> Drawdown / Recovery -> Annual / Rolling Consistency -> Benchmark-relative Behavior -> Correlation Structure -> Contribution / Diversification Evidence -> Evidence Limitation / Next Research` 순서로 사고한다. 두 제품 모두 숫자의 나열이 아니라 사용자의 연구 질문에 답하는 정량적 insight를 우선하며, 현재 역사 표본에서 관찰된 사실과 해석, 다음 의사결정을 구분한다.**
