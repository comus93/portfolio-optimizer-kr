# OpenSpec Deferred TODO

현재는 Backtest/Optimization 코어 제품과 `bt-module`의 main 승격에 집중한다.

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
