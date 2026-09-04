# OpenSpec Deferred TODO

현재는 Backtest/Optimization 코어 제품과 `bt-module`의 main 승격에 집중한다.
아래 항목은 명시적으로 post-release 범위이며 `bt-module` 코어 release blocker가 아니다.

## Deferred specification maintenance

- [ ] `docs/`에 남아 있는 specification 성격 문서를 capability ownership 기준으로 재검토하고, 필요 시 OpenSpec으로 단계적으로 이관한다.
  - 후보: `docs/report-ui-specification.md`
  - 후보: `docs/input-ui-contract.md`
  - 후보: `docs/architecture.md`
  - 후보: `docs/visual-acceptance-contract.md`
  - 후보: `docs/research-operation-pipeline.md`
  - 후보: `docs/llm-research-input-contract.md`
  - 후보: `docs/llm-analysis-framework.md`
- [ ] 이관 전까지 위 문서는 현재 위치와 역할을 유지하며, 코어 기능 작업을 위한 선행 조건으로 만들지 않는다.
- [ ] 향후 spec 정비 시 중복 requirement, source-of-truth 충돌, archive 가능한 historical contract를 함께 정리한다.

## Deferred standalone Input UI

현재 canonical Research Frontend는 LLM 기반 입력 계약과 Experiment YAML이다. 별도 interactive Input UI는 이번 코어 release 범위에서 제외한다.

- [ ] Optimization / Backtest product-mode selector와 Backtest Settings / Portfolio Assets UI를 구현한다.
- [ ] Month-to-Month / Year-to-Year selector, month field applicability, Calendar Aligned, Initial Amount, Rebalancing UI를 구현한다.
- [ ] data-supported year range를 이용한 dynamic period selector를 구현한다.
- [ ] shared asset search/add/remove/edit와 portfolio별 allocation input을 연결한다.
- [ ] 최대 3 portfolio, default portfolio naming, Backtest에서 optimization-only control 비노출을 UI acceptance로 검증한다.
- [ ] cashflow / band rebalance / leverage / Display Income / style / factor / regime 등 v1 제외 advanced setting이 UI에 노출되지 않도록 검증한다.

## Deferred Research workflow automation

현재 Study / Experiment / Run 운영 계약과 union-ticker Experiment identity는 Research Frontend 문서와 OpenSpec에 정의되어 있다. 자동 lifecycle enforcement는 후속 자동화 범위로 둔다.

- [ ] union ticker set으로 Backtest Experiment identity를 자동 판정하는 lifecycle helper를 구현한다.
- [ ] union 동일 + portfolio membership/weights 변경은 same Experiment/new Run으로 자동 판정하는 regression을 추가한다.
- [ ] union ticker 변경은 new Experiment으로 자동 판정하는 regression을 추가한다.

## Deferred market-data coverage expansion

현재 canonical total-return policy는 verified adjusted/distribution-adjusted series만 허용하고 unsupported route는 명시적으로 거부한다. 지원 범위 확대는 별도 change로 다룬다.

- [ ] 현재 total-return guarantee가 없는 provider/instrument route를 추가 지원할 필요가 생기면 data source 보강안을 제안한다.
- [ ] 새 source를 추가할 때 Optimization + Backtest affected regression을 함께 정의한다.
