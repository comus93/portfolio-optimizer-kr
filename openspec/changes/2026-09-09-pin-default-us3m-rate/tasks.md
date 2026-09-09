# Tasks

- [x] Confirm source run and pinned U.S. 3-Month T-Bill effective annual rate.
- [x] Define Research Frontend default semantics and provenance.
- [x] Materialize fixed 3.8394827586206895% in `research.py::_apply_research_defaults()` when RF is omitted.
- [x] Preserve explicit custom `fixed` and explicit `us_3m_tbill` inputs.
- [x] Add Optimization and Backtest research-default regression tests.
- [x] Update examples and LLM handover to the final pinned-default semantics.
- [x] Verify affected regression scope: 23 targeted tests passed in GitHub Actions.
- [x] Update GitHub Issue #1 with the resolved default path and remaining explicit-dynamic scope.
- [ ] Archive this change after its requirement is folded into the canonical `research-input` baseline.
