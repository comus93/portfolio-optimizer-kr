# LLM ↔ User Research Input Contract

## 목적

이 문서는 LLM과 사용자가 포트폴리오 최적화 연구를 시작할 때, 실제 experiment를 만들고 실행하기 전에 어떤 정보를 확정해야 하는지 정의한다.

핵심 원칙은 다음과 같다.

> **결과의 의미를 바꾸는 연구 조건은 LLM이 임의로 채우지 않는다. 다만 프로젝트가 명시적으로 정한 default가 있는 항목은 그 default를 안내하고, 사용자가 별도 값을 지정하지 않으면 default를 적용한다.**

이 문서는 optimizer의 금융 계산 규칙이 아니라 **연구 실행 전 사용자-LLM 상호작용 계약**이다.

---

## 1. 실행 전 결정 및 확정 규칙

다음 항목은 실제 persisted research run을 만들기 전에 사용자 입력 또는 프로젝트 default에 의해 결정되어야 한다.

### 1.1 연구 대상 자산

각 자산에 대해 최소한 ticker를 확인한다.

가능하면 다음도 함께 받는다.

- 자산명
- 통화
- 기존 portfolio 비중
- 최소 비중
- 최대 비중

사용자가 기존 비중을 제공하면 합계가 100%인지 확인한다.

기존 비중은 optimizer의 제약 조건이 아니라 **Provided Portfolio baseline**으로 취급한다.

### 1.2 Optimization Goal

LLM은 사용자가 명시하지 않은 optimization objective를 임의로 선택하지 않는다.

현재 기본 선택지는 다음 두 가지다.

#### A. Maximum Sharpe

Risk-adjusted return이 가장 높은 포트폴리오를 찾는다.

사용자 확인 예:

> 이번 실험은 Maximum Sharpe를 찾을까?

#### B. Maximum Return at Target Volatility

사용자가 허용하는 연환산 변동성 한도 안에서 Expected Return을 최대화한다.

이 objective를 선택하면 다음 값이 **추가 필수 입력**이다.

- Target annual volatility (%)

사용자 확인 예:

> 수익률 최대화를 원하면 허용 가능한 연환산 변동성 상한을 몇 %로 둘까?

Target volatility가 정해지지 않은 상태에서 LLM이 임의의 값을 넣어 실행하지 않는다.

### 1.3 Rebalancing Frequency

LLM은 rebalancing 주기를 임의로 정하지 않는다.

현재 지원 범위에서 최소한 다음 중 하나를 사용자에게 확인한다.

- Monthly
- Annual

사용자 확인 예:

> Provided/optimized portfolio의 과거 성과 계산은 월 리밸런싱으로 볼까, 연 리밸런싱으로 볼까?

### 1.4 Analysis Period

분석 기간은 Expected Return, covariance, correlation, Efficient Frontier를 직접 바꾸므로 사용자에게 기간 선택 가능성을 안내한다.

프로젝트 default는 다음과 같다.

> **사용자가 별도의 시작일/종료일을 지정하지 않으면, optimizer universe의 모든 자산에 유효한 데이터가 존재하는 공통 교집합 전체 기간을 사용한다.**

따라서 Analysis Period는 다음 방식으로 처리한다.

- 사용자가 시작일/종료일을 지정하면 그 기간을 우선한다.
- 사용자가 별도 기간을 지정하지 않으면 공통 데이터 교집합 전체 기간을 자동 적용한다.
- LLM은 기본값을 숨기지 않고, 기간을 물을 때 교집합 전체 기간이 default임을 함께 안내한다.
- benchmark는 optimizer universe의 공통 기간을 불필요하게 축소시키지 않는다.
- 실제 실행 후에는 계산에 사용된 실제 data coverage의 시작일, 종료일, observation 수를 보고한다.

사용자 확인 예:

> 분석 기간은 별도로 지정할까? 별도 지정이 없으면 모든 자산의 데이터가 존재하는 공통 교집합 전체 기간을 기본으로 사용할게.

특정 자산의 짧은 listing history 때문에 공통 분석 기간이 크게 줄어들면 실행 후 반드시 별도로 보고한다.

---

## 2. 기본값 제안이 가능한 항목

다음 항목은 연구 맥락에 따라 LLM이 기본값을 제안할 수 있다. 다만 중요한 비교 연구라면 사용자에게 함께 보여주는 것을 우선한다.

### 2.1 Benchmark

사용자가 benchmark를 지정하지 않으면 연구 목적에 맞는 benchmark를 제안할 수 있다.

예:

- 미국 주식 중심 portfolio: SPY
- benchmark 없이 순수 portfolio 구조만 보는 연구: 생략 가능

Benchmark는 optimizer universe의 공통 기간을 불필요하게 축소시키지 않아야 한다.

### 2.2 Risk-free Rate

Risk-free 방식은 specification의 지원 범위 안에서 선택한다.

- U.S. 3-Month T-Bill
- Fixed annual rate

PV parity 또는 이전 experiment와 직접 비교하는 연구라면 같은 risk-free convention을 우선 사용하고 그 사실을 명시한다.

### 2.3 Efficient Frontier Point Count

사용자가 별도로 요구하지 않으면 project 기본값을 사용할 수 있다.

Frontier point count는 해석을 위한 sampling density이며, 연구 질문 자체를 바꾸는 입력으로 취급하지 않는다.

---

## 3. LLM의 질문 방식

사용자가 이미 제공한 정보를 다시 묻지 않는다.

빠진 필수 결정값과 default가 있는 확인 항목만 한 번에 묶어서 간결하게 질문한다.

예를 들어 사용자가 자산, 기존 비중, min/max만 제공했다면 다음 정도면 충분하다.

> 종목/비중/제약은 확정됐어. 실행 전에 다음만 정하면 돼.  
> 1. Optimization Goal: Maximum Sharpe / Maximum Return at target annual vol  
> 2. Maximum Return이면 허용 annual vol (%)  
> 3. Rebalancing: Monthly / Annual  
> 4. Analysis Period: 별도 지정 가능. 지정하지 않으면 모든 자산의 공통 데이터 교집합 전체 기간을 사용

이미 연구 목적상 명확한 값은 선택지를 불필요하게 늘리지 않는다.

---

## 4. Execution Gate

다음 조건이 모두 충족되기 전에는 LLM이 정식 Experiment를 GitHub Actions 실행 대상으로 지정하지 않는다.

- Asset universe 확정
- 필요한 경우 Provided Portfolio 확정 및 합계 검증
- Asset min/max constraints 확정
- Optimization Goal 확정
- Maximum Return at Target Volatility인 경우 target annual volatility 확정
- Rebalancing frequency 확정
- Analysis Period가 사용자 지정 기간 또는 project default인 공통 데이터 교집합 전체 기간 중 하나로 결정됨

사용자가 Analysis Period를 별도로 지정하지 않은 것은 미확정 상태가 아니다. 이 경우 **공통 데이터 교집합 전체 기간이 자동으로 확정값**이 된다.

그 외 필수값이 미확정이면 Experiment YAML을 초안으로 작성할 수는 있지만 **실행 가능한 최종 Experiment로 간주하지 않는다.**

특히 미확정 Experiment를 `control/execute.yaml`의 실제 실행 대상으로 지정하지 않는다.

정식 실행 경로는 `docs/research-operation-pipeline.md`를 따른다.

---

## 5. 실행 직전 LLM 확인 요약

사용자가 별도로 요구하지 않는 한 장황한 승인 절차를 만들 필요는 없다.

실행 직전에 LLM은 확정된 조건을 짧게 요약하고 바로 다음 단계로 진행한다.

권장 형식:

```text
Assets / provided weights / bounds
Optimization Goal
Target Volatility (해당 시)
Analysis Period 또는 common-overlap default
Rebalancing
Benchmark
Risk-free convention
```

이 요약은 사용자의 선택을 다시 승인받기 위한 형식 절차가 아니라, LLM이 잘못 이해한 입력을 실행 전에 발견하기 위한 sanity check다.

---

## 6. Guiding Rule

값이 누락됐을 때 다음 질문을 한다.

> **이 값을 다르게 선택하면 Efficient Frontier, 최적 비중 또는 historical portfolio 성과의 의미가 달라지는가?**

그렇다면 사용자에게 확인하거나, 프로젝트가 명시적으로 정한 default가 있으면 그 default를 안내해 적용한다.

Analysis Period의 default는 **optimizer universe의 공통 데이터 교집합 전체 기간**이다.

단순한 출력 형식, 저장 경로, frontier sampling density처럼 연구 결론의 의미를 바꾸지 않는 구현 세부사항은 project default를 사용할 수 있다.
