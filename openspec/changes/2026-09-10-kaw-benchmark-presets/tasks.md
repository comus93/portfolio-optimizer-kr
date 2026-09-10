# Tasks

- [x] Add canonical KAW benchmark preset registry and aliases.
- [x] Materialize preset shortcuts into explicit asset rows + fixed-weight portfolio benchmark input.
- [x] Extend Backtest config/model to support composite portfolio benchmark while preserving asset benchmark compatibility.
- [x] Reuse shared portfolio simulation to build benchmark path and existing benchmark-relative analytics.
- [x] Persist fully materialized benchmark definition in `input.yaml`.
- [x] Render composite benchmark identity/name in report metadata.
- [x] Add regression tests for SPY asset benchmark, no benchmark, KAW Native preset, KAW Core preset, and composite benchmark analytics.
- [x] Run affected Backtest tests and real research smoke runs using both KAW Native and KAW Core presets.
- [x] Fix configured fixed-RF propagation so normal research execution generates PV `Risk and Return Metrics`.
- [x] Re-run both KAW benchmark smoke experiments and verify populated metrics artifacts and HTML sections.

Validation evidence:

- Initial smoke runs `20260910-0002` and `20260910-0003` exposed a reporting defect: configured fixed RF was parsed and persisted but dropped by the runner, so the PV risk/return table was skipped.
- Source fix: fixed RF now falls back to the parsed `risk_free.annual_rate` when no explicit caller override is supplied; dynamic `us_3m_tbill` behavior and explicit overrides remain unchanged.
- CI workflow run `34425892590` succeeded with KAW benchmark, Backtest execution/persistence, fixed-RF propagation, and PV metrics regression coverage.
- Corrected short preset smoke: `runs/20260910-0004` using `benchmark: kaw_short`; `raw/review/risk_and_return_metrics.csv` and populated HTML metrics verified.
- Corrected long preset smoke: `runs/20260910-0005` using `benchmark: kaw_long`; `raw/review/risk_and_return_metrics.csv` and populated HTML metrics verified.
- Historical runs `20260910-0002` and `20260910-0003` remain immutable evidence of the pre-fix behavior.
