# Tasks

- [x] Add canonical KAW benchmark preset registry and aliases.
- [x] Materialize preset shortcuts into explicit asset rows + fixed-weight portfolio benchmark input.
- [x] Extend Backtest config/model to support composite portfolio benchmark while preserving asset benchmark compatibility.
- [x] Reuse shared portfolio simulation to build benchmark path and existing benchmark-relative analytics.
- [x] Persist fully materialized benchmark definition in `input.yaml`.
- [x] Render composite benchmark identity/name in report metadata.
- [x] Add regression tests for SPY asset benchmark, no benchmark, KAW Native preset, KAW Core preset, and composite benchmark analytics.
- [x] Run affected Backtest tests and real research smoke runs using both KAW Native and KAW Core presets.

Validation evidence:

- CI workflow `Validate KAW benchmark presets`: 24 passed.
- Short preset smoke: `runs/20260910-0002` using `benchmark: kaw_short`.
- Long preset smoke: `runs/20260910-0003` using `benchmark: kaw_long`.
