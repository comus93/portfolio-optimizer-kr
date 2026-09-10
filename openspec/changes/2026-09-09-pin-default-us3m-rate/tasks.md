# Tasks

- [x] Confirm source run and pinned U.S. 3-Month T-Bill effective annual rate.
- [x] Define Research Frontend default semantics and provenance.
- [x] Materialize fixed 3.8394827586206895% in `research.py::_apply_research_defaults()` when RF is omitted.
- [x] Preserve explicit custom `fixed` and explicit `us_3m_tbill` inputs.
- [x] Add Optimization and Backtest research-default regression tests.
- [x] Update examples and LLM handover to the final pinned-default semantics.
- [x] Verify affected regression scope: 23 targeted tests passed in GitHub Actions.
- [x] Update GitHub Issue #1 with the resolved default path and remaining explicit-dynamic scope.
- [x] Strengthen the contract so materialized fixed RF must propagate into runtime analytics rather than persistence only.
- [x] Fix `runner._resolve_annual_rf()` so configured fixed RF is used when no explicit caller override is supplied.
- [x] Verify populated Backtest Risk and Return Metrics after the fix using KAW smoke runs `20260910-0004` and `20260910-0005`.
- [ ] Archive this change after its requirements are folded into the canonical `research-input` baseline.

Additional validation evidence:

- Pre-fix KAW smoke runs `20260910-0002` / `20260910-0003` persisted fixed RF but exposed missing PV-style Risk and Return Metrics.
- Root cause: normal research execution passed no external `annual_rf`, and the runner returned `None` instead of the parsed fixed rate.
- Corrected CI workflow run `34425892590` succeeded with fixed-RF propagation and PV metrics regression coverage.
- Corrected runs `20260910-0004` / `20260910-0005` generated `raw/review/risk_and_return_metrics.csv` and populated HTML metric sections.
