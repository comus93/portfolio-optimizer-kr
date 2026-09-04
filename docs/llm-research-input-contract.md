# LLM ↔ User Research Input Contract

## 목적

이 문서는 LLM이 사용자와 포트폴리오 연구를 시작할 때 **어떤 product를 사용할지, 무엇을 물어보고, 무엇을 default로 처리하며, 어떤 값을 실행 YAML에 반드시 기록할지** 정의한다.

핵심 원칙:

> **사용자의 투자/연구 의사결정은 사용자에게 확인한다. Canonical default가 있는 값은 불필요한 선택 질문으로 만들지 않는다. Optimization과 Backtest 중 어느 product를 사용할지 모호하면 실행 전에 반드시 사용자에게 확인한다.**

이 문서는 금융 계산 공식을 정의하는 문서가 아니라 Research Frontend의 사용자 응대와 실행 입력 생성 계약이다.

---

# 1. Product Intent Gate

Research Frontend는 세부 입력을 정리하기 전에 먼저 현재 요청의 product intent를 결정한다.

```text
Optimization
= 주어진 Asset Universe에서 어떤 allocation이 더 효율적인가?

Backtest
= 이미 정의된 portfolio가 역사적으로 어떻게 행동했는가?
```

## 1.1 명확한 Optimization 요청

다음과 같이 optimization 목적이 명확하면 추가 product 확인 없이 Optimization으로 진행한다.

예:

```text
최적 비중 찾아줘
Max Sharpe로 돌려줘
변동성 12% 안에서 최대수익 조합 찾아줘
각 종목을 0~40% 범위로 제한해서 최적화해줘
Efficient Frontier 보고 싶어
```

## 1.2 명확한 Backtest 요청

다음과 같이 이미 정해진 portfolio의 historical behavior를 보려는 의도가 명확하면 추가 product 확인 없이 Backtest로 진행한다.

예:

```text
이 비중 그대로 과거 성과 봐줘
백테스트 돌려줘
월 리밸런싱으로 CAGR/MDD 봐줘
2008년 위기 때 얼마나 빠졌는지 보자
이 두 포트의 과거 성과를 비교해줘
```

## 1.3 Product intent가 모호하면 반드시 질문한다

Optimization과 Backtest 둘 다 합리적으로 가능한 요청이면 LLM이 context만으로 하나를 임의 선택하지 않는다.

대표 예:

```text
QQQ 30%, SPY 30%, GLD 30%, IEF 10%로 돌려보자.
```

이 경우 비중이 주어졌다는 사실만으로 Backtest라고 단정하지 않는다. Optimization에서도 Provided Portfolio로 같은 비중을 사용할 수 있기 때문이다.

사용자에게 한 번만 자연스럽게 묻는다.

> 이 비중 그대로 과거 성과를 보는 Backtest로 할까, 아니면 이 비중을 현재 포트로 두고 더 나은 비중을 찾는 Optimization으로 할까?

Product 선택은 연구 질문 자체를 바꾸므로 canonical default로 대신하지 않는다.

## 1.4 금지되는 heuristic

다음 규칙을 product classifier처럼 사용하지 않는다.

```text
비중이 있다      -> Backtest
비중이 없다      -> Optimization
'돌려줘'라고 함 -> Backtest
자산이 여러 개다 -> Optimization
```

이런 단서는 보조 evidence일 뿐 product intent를 확정하지 못한다.

## 1.5 product_mode는 실행 YAML에서 mandatory다

Product intent가 정해지면 모든 canonical Experiment/Run input에는 다음 둘 중 하나를 반드시 명시한다.

```yaml
product_mode: optimization
```

또는:

```yaml
product_mode: backtest
```

`product_mode` 생략 시 Optimization으로 암묵 fallback하지 않는다.

Research Frontend는 product를 추론한 뒤 이 값을 생략해서는 안 된다.

---

# 2. Common Conversation Protocol

## Step 1. 이미 받은 정보를 먼저 추출한다

사용자가 이미 말한 값은 다시 묻지 않는다.

공통으로 복원할 수 있는 정보:

```text
Product intent
Asset Universe
Portfolio weights 또는 Provided Portfolio weights
Analysis / Time Period
Rebalancing
Benchmark override
Risk-free override
```

Product별 추가 입력은 해당 branch에서 확인한다.

## Step 2. 기계적으로 검증 가능한 것은 LLM이 먼저 검증한다

예:

```text
- ticker가 명확한가
- 같은 자산이 중복됐는가
- portfolio weight 합이 100%인가
- target-volatility 방식인데 허용 변동성이 빠졌는가
- Optimization min/max constraint가 서로 모순되지 않는가
```

기계적으로 판단 가능한 것을 사용자에게 되묻지 않는다.

## Step 3. 사용자 결정과 default를 구분한다

사용자의 의사결정에 직접 영향을 주는 값은 필요한 경우 질문한다.

Project default가 있고 연구 의미를 대신 결정하지 않는 값은 자동 적용하고 필요한 경우 짧게 고지한다.

## Step 4. 남은 질문만 한 번에 묻는다

질문의 수를 채우지 않는다.

이미 결정된 값이나 canonical default를 다시 선택하게 하지 않는다.

## Step 5. 실행 의도가 이미 있으면 다시 승인받지 않는다

다음 표현은 실행 의도로 본다.

```text
분석해
돌려줘
백테스트해줘
최적화해줘
실행해
다시 돌려
```

Product intent와 필수 사용자 decision이 모두 해소되면 짧게 조건을 정리한 뒤 `진행할까?`를 다시 묻지 않고 실행한다.

---

# 3. Optimization Input Contract

Optimization의 연구 질문은 **주어진 Asset Universe와 constraints 안에서 어떤 allocation이 더 효율적인가**이다.

## 3.1 User Research Decisions

다음은 결과와 해석을 직접 바꾸므로 사용자 결정으로 취급한다.

- Asset Universe
- Provided Portfolio가 연구에 필요한 경우 현재 비중
- 각 자산의 최소/최대 허용 비중
- Optimization Goal
- Target Volatility, 해당 objective에서 필요한 경우
- 특정 기간 자체가 연구 질문일 때의 Analysis Period
- 사용자가 default benchmark를 변경하려는 경우의 비교대상

이미 대화에서 결정된 값은 다시 묻지 않는다.

### 비중 제한

비중 제한이 아직 정해지지 않았다면 실행 전에 사용자에게 확인한다.

> 각 자산 비중을 어디까지 허용할까? 0%까지 빠져도 되는지, 최대 몇 %까지 허용할지 정해줘. 모두 같은 상한을 써도 되고 자산별로 달라도 돼.

사용자가 `제약 없이` 또는 `비중 제한 없음`이라고 하면 0~100% 허용으로 해석할 수 있다.

LLM이 자산 성격을 근거로 임의의 제한을 확정하지 않는다.

### Optimization Goal

사용자-facing 표현은 의미를 먼저 보여준다.

```text
변동성 대비 기대수익이 좋은 조합
= Maximum Sharpe

허용한 변동성 안에서 기대수익이 가장 높은 조합
= Maximum Return at Target Volatility
```

두 번째를 선택하면 허용 연간 변동성을 반드시 확인한다.

## 3.2 Optimization Canonical Defaults

사용자가 별도 지정하지 않으면:

```text
Benchmark             = S&P 500 (SPY)
Analysis Period       = 모든 optimization asset의 공통 유효기간 전체
Portfolio Rebalancing = Monthly
Risk-free             = U.S. 3-Month T-Bill convention
Return Frequency      = Monthly
```

Default가 있다는 이유로 별도 승인 질문을 만들지 않는다.

## 3.3 Optimization YAML meaning

Optimization Experiment에는 최소한 product identity와 실제 연구 조건을 명시한다.

예:

```yaml
product_mode: optimization
assets:
  - symbol: QQQ
    provided_weight_pct: 30
    min_weight_pct: 0
    max_weight_pct: 50
optimization:
  objective: max_sharpe
benchmark:
  symbol: SPY
portfolio:
  rebalancing_period: monthly
```

Provided Portfolio는 optimizer constraint가 아니라 비교 baseline이다.

---

# 4. Backtest Input Contract

Backtest의 연구 질문은 **이미 정의된 portfolio가 역사적으로 어떻게 행동했는가**이다.

Backtest에서는 Optimization objective, min/max constraint, target volatility를 질문하거나 입력으로 요구하지 않는다.

## 4.1 User Research Decisions

다음은 필요하면 사용자에게 확인한다.

- 어떤 asset을 사용할지
- 각 portfolio의 target weights
- 여러 portfolio를 비교할 경우 각각의 구성
- 특정 기간 자체가 연구 질문일 때의 Time Period
- 사용자가 default benchmark를 변경하거나 benchmark 없음으로 지정하는 경우
- rebalancing 차이 자체가 연구 질문인 경우의 Rebalancing
- Calendar Aligned 차이 자체가 연구 질문인 경우의 설정

Portfolio별 weight 합은 100%를 mechanical validation한다.

## 4.2 Backtest Canonical Defaults

사용자가 지정하지 않으면 Research Frontend는 다음 값을 적용한다.

```text
Benchmark         = S&P 500 (SPY)
Initial Balance   = 10,000
Time Period       = Month-to-Month
Analysis Period   = full common effective period
Calendar Aligned  = Yes
Rebalancing       = Monthly
Portfolio Name    = Portfolio 1, Portfolio 2, Portfolio 3
Risk-free         = U.S. 3-Month T-Bill convention
```

Core Backtest에서 benchmark는 optional이며 사용자가 명시적으로 `benchmark 없음`을 선택할 수 있다.

기간 미지정은 미확정 상태가 아니다. full common effective period를 사용하고 실행 후 실제 coverage를 보고한다.

Backtest v1에서 run-level rebalancing 하나를 모든 비교 portfolio에 동일하게 적용한다.

## 4.3 Backtest YAML meaning

예:

```yaml
product_mode: backtest
assets:
  - symbol: QQQ
  - symbol: SPY
  - symbol: GLD
portfolios:
  - name: Portfolio 1
    weights_pct:
      QQQ: 40
      SPY: 30
      GLD: 30
benchmark:
  symbol: SPY
initial_balance: 10000
time_period:
  mode: month_to_month
rebalancing:
  period: monthly
  calendar_aligned: true
```

Optimization-only field를 Backtest 입력에 섞지 않는다.

---

# 5. Benchmark / Period / Risk-free Common Rules

## 5.1 Benchmark

Research Frontend의 default benchmark는 SPY다.

사용자가 다른 비교대상을 명시하면 override한다.

Backtest에서는 명시적인 `benchmark 없음`도 허용한다.

Research Frontend가 생성하거나 갱신하는 Experiment YAML에는 default를 사용하더라도 benchmark를 명시적으로 기록한다.

## 5.2 Period

사용자가 특정 기간을 지정하면 그대로 사용한다.

지정하지 않으면 해당 product의 canonical full common effective period를 적용한다.

실행 후 실제 시작일, 종료일, observation 수와 limiting asset이 의미 있으면 보고한다.

## 5.3 Risk-free

사용자가 별도 convention을 요구하지 않으면 canonical default를 적용한다.

외부 시스템 parity 연구에서는 convention 차이를 결과에서 명시한다.

---

# 6. 질문 표현 규칙

내부 YAML field를 그대로 사용자에게 던지지 않는다.

```text
내부 용어                  사용자에게 우선할 표현
product_mode               과거 성과를 볼지 / 최적 비중을 찾을지
min/max constraint         비중을 최소/최대 어디까지 허용할지
optimization objective     무엇을 최우선으로 볼지
target annual volatility   연간 변동성을 어디까지 허용할지
common overlap period      모든 자산 데이터가 함께 있는 전체 기간
benchmark                  비교대상
calendar_aligned           리밸런싱 시점을 달력 기준으로 맞출지
```

금지 패턴:

```text
- product가 모호한데 LLM이 임의 선택
- YAML field를 그대로 나열해 답을 요구
- 이미 받은 값을 다시 질문
- canonical default를 다시 선택하게 함
- Backtest에서 Optimization-only 질문을 함
- sanity-check를 승인 절차로 바꿈
```

좋은 응대는 다음 특성을 가진다.

```text
- 연구 의도를 먼저 확정
- 답에 따라 연구 의미가 실제로 달라지는 것만 질문
- default는 자동 적용
- 사용자가 이미 실행을 요청했다면 redundant approval 없음
```

---

# 7. Execution Gate

실행 전 최소 gate는 product별로 다르다.

## Optimization

```text
product_mode               = optimization 명시
Asset Universe             확정
Provided weights           필요하면 확정 및 합계 검증
Asset min/max bounds       사용자 결정 완료
Optimization Goal          확정
Target Volatility          해당 objective에서 확정
Analysis Period            사용자 지정 또는 default
Rebalancing                사용자 지정 또는 default
Benchmark                  explicit value
Risk-free                  사용자 지정 또는 default
```

## Backtest

```text
product_mode               = backtest 명시
Asset Universe             확정
Portfolio target weights   확정 및 합계 검증
Time Period                사용자 지정 또는 default
Initial Balance            사용자 지정 또는 default
Rebalancing                사용자 지정 또는 default
Calendar Aligned           사용자 지정 또는 default
Benchmark                  explicit value 또는 explicit none
Risk-free                  사용자 지정 또는 default
```

`product_mode`가 없으면 실행하지 않는다.

Product intent가 모호한 상태에서도 실행하지 않는다.

---

# 8. Persistence Principle

Research Frontend가 사용자와 결정한 effective condition은 사람이 읽을 수 있는 YAML에 명시적으로 저장한다.

특히 다음 값은 추후 대화 context에 의존해 복원하지 않는다.

```text
product_mode
asset universe
portfolio/provided weights
optimization constraints/objective if applicable
benchmark
period
rebalancing
Backtest initial balance / calendar alignment if applicable
risk-free convention
```

실제 실행 당시의 effective condition은 `runs/<run_id>/input.yaml`이 source of truth다.

결과 분석은 `runs/<run_id>/context.yaml` / `input.yaml`의 explicit `product_mode`를 기준으로 `docs/llm-analysis-framework.md`의 해당 branch를 선택한다.

---

# 핵심 원칙

> **Research Frontend는 먼저 사용자가 `정해진 포트의 역사적 행동`을 보려는지, `주어진 자산에서 더 효율적인 비중`을 찾으려는지 판단한다. 명확하면 바로 진행하고, 둘 다 가능한 요청이면 한 번 질문한다. Product가 결정되면 `product_mode`를 Optimization과 Backtest 모두 YAML에 명시적으로 기록하며 silent default를 사용하지 않는다. 그 다음에만 product별 필수 사용자 decision과 canonical default를 적용해 실행한다.**
