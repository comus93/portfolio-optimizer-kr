# Tasks

- [x] Implement shared run navigation renderer.
- [x] Replace one-line per-run README with the fixed navigation summary format.
- [x] Generate/update `runs/README.md` aggregate catalog from persisted run artifacts.
- [x] Refresh navigation after canonical YAML/research execution finishes writing effective input/context/report artifacts.
- [x] Add Optimization and Backtest regression tests for per-run README and aggregate catalog.
- [x] Verify navigation refresh does not mutate canonical artifacts.
- [x] Run affected tests and record evidence.
- [x] Persist executor-supplied exact public report URL as non-canonical run publication metadata.
- [x] Add `Public Report` to per-run README artifacts.
- [x] Add `Report` column to aggregate `runs/README.md` and pass through the registered URL.
- [x] Preserve registered public report links across navigation/report regeneration.
- [x] Backfill existing persisted reports with publication metadata and regenerate navigation.
- [x] Keep publication-link navigation enrichment best-effort so it cannot invalidate a completed finance run.

## Validation evidence

- GitHub Actions workflow: `Validate run navigation summaries`
- Initial navigation validation run: `34436533186`
- Initial result: `19 passed in 2.94s`
- Public-link regression run: `34438584972` — success.
- Public-link backfill workflow run: `34438638949` — success.
- Coverage includes exact arbitrary URL pass-through, per-run `Public Report`, aggregate `Report` column, rebuild persistence, run-navigation renderer/index, report writer/viewer, Backtest execution and shared end-to-end regression.
- Canonical immutability regression verifies `result.json` bytes are unchanged by navigation refresh.
- Public report location is persisted separately in `runs/<run_id>/links.yaml`; navigation code does not calculate GitHub Pages owner/domain/path conventions.
- Research execution orchestration resolves the current Pages base URL, combines it with the actual generated report path, then passes the resulting exact URL to `scripts/register_public_report_url.py` before the run commit.
- Existing persisted reports were backfilled and `runs/README.md` now exposes direct `Open` links.
- Manual rebuild utility: `python scripts/rebuild_run_navigation.py`.
- Exact URL registration utility: `python scripts/register_public_report_url.py <run_dir> <url>`.
