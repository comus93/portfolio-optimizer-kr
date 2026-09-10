## ADDED Requirements

### Requirement: KAW benchmark preset override
Backtest Research Frontend는 기본 SPY benchmark를 유지하면서 사용자가 KAW baseline을 명시적으로 선택하면 한 줄 preset을 canonical fixed-weight portfolio benchmark 정의로 materialize해야 한다(MUST).

지원 preset alias는 최소 다음을 포함한다.

```text
kaw_short -> KAW Native Proxy
kaw_native -> KAW Native Proxy
kaw_long -> KAW Core Revised Internal
kaw_core -> KAW Core Revised Internal
```

#### Scenario: 최근 비교에서 KAW short 선택
- GIVEN 사용자가 `benchmark: kaw_short`를 선택한다
- WHEN effective Backtest input을 만든다
- THEN benchmark를 KAW Native Proxy 고정비중 portfolio로 materialize하고 필요한 benchmark constituent를 shared asset universe에 포함한다

#### Scenario: 장기 비교에서 KAW long 선택
- GIVEN 사용자가 `benchmark: kaw_long`을 선택한다
- WHEN effective Backtest input을 만든다
- THEN benchmark를 KAW Core Revised Internal 고정비중 portfolio로 materialize하고 필요한 constituent를 shared asset universe에 포함한다

### Requirement: Preset materialization is explicit and reproducible
KAW preset shortcut을 사용하더라도 persisted `input.yaml`에는 실제 benchmark name, preset id, constituent weights 및 필요한 asset rows가 명시되어야 한다(MUST).

#### Scenario: preset 실행 후 input 확인
- GIVEN `benchmark: kaw_core`로 research run을 실행했다
- WHEN `input.yaml`을 확인한다
- THEN 숨은 registry lookup 없이도 해당 run에 사용된 Core benchmark 종목과 target weights를 재구성할 수 있다

### Requirement: No hidden period-based KAW routing
Research Frontend는 requested period만 보고 Native와 Core를 자동 전환해서는 안 된다(MUST NOT). 사용자는 short/native 또는 long/core preset을 명시해야 한다.

#### Scenario: 2018년 시작인데 kaw_short 지정
- GIVEN 사용자가 장기 기간과 `benchmark: kaw_short`를 함께 명시한다
- WHEN input을 구성한다
- THEN 임의로 `kaw_long`으로 바꾸지 않고 명시된 Native preset을 보존한다
