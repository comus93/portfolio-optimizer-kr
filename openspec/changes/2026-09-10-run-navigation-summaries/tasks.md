# Tasks

- [x] Implement shared run navigation renderer.
- [x] Replace one-line per-run README with the fixed navigation summary format.
- [x] Generate/update `runs/README.md` aggregate catalog from persisted run artifacts.
- [x] Refresh navigation after canonical YAML/research execution finishes writing effective input/context/report artifacts.
- [x] Add Optimization and Backtest regression tests for per-run README and aggregate catalog.
- [x] Verify navigation refresh does not mutate canonical artifacts.
- [x] Run affected tests and record evidence.

## Validation evidence

- GitHub Actions workflow: `Validate run navigation summaries`
- Successful run: `34436533186`
- Result: `19 passed in 2.94s`
- Coverage: run-navigation renderer/index tests plus affected report writer, reporting, Backtest execution and shared end-to-end regression.
- Canonical immutability regression verifies `result.json` bytes are unchanged by navigation refresh.
- Initial aggregate catalog was generated from existing persisted artifacts and committed as `runs/README.md` without rewriting historical run directories.
- Manual rebuild utility: `python scripts/rebuild_run_navigation.py`
- Historical per-run README rewrite is explicit-only via `--include-run-readmes` to preserve existing run immutability by default.
