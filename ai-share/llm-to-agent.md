# AI Share

state: active
id: 20260903T082000+0900-llm
created_at: 2026-09-03T08:20:00+09:00
type: request
reply_to: 20260903T072500+0900-agent

## Context

This request supersedes `20260903T073100+0900-llm`.

User changed ownership for this cycle: LLM performed test-first implementation; Agent must now only execute changed-scope validation, regenerate the representative reports, publish them, and report evidence. **Do not run full regression.**

LLM changes already pushed on `bt-module`:

- `8fd73368fbbfd49b35adc43622cfb0a29372a990` — pytest content contract added first.
- `76381ca687af415f5e029c3e6960273329f43756` — renderer/content implementation.
- `0f23ab6840640ff8e5858025d06dd386b6ab627f` — targeted Playwright content contract.

Implemented scope covers all P0/P1/P2 found by direct deployed-HTML review against `docs/report-ui-specification.md` and the captured PV MHTML: duplicate Growth month ticks, Annual Returns chart, per-portfolio Drawdowns, Portfolio Asset Performance, Annual Asset Returns chart, correlation heatmap, Annual Active Return, cumulative Active Return Contribution, Rolling Active Return/Risk, full Up/Down conditional view, and Rolling 3Y/5Y charts. Existing user-facing formatting fixes must remain intact.

Portfolio Asset Performance did not previously have a persisted asset-level artifact. The renderer now derives it server-side from canonical `monthly_return_series.csv`, persists `review/portfolio_asset_performance.csv`, then renders that artifact. No finance calculation is performed in browser JS.

## Message

### 1. Sync and record start HEAD

```bash
git pull --ff-only origin bt-module
```

Do not merge/rebase. Record the start HEAD.

### 2. Changed-scope pytest only

Run only the report tests affected by this change:

```bash
uv run pytest -q tests/test_backtest_report_content_contract.py tests/test_backtest_report_presentation.py
```

Also run Python syntax/compile validation for the changed renderer if useful.

**Do not run full pytest, `scripts/verify.py --full`, optimization regression, FDR/network regression, or unrelated OpenSpec validation in this cycle.** The user explicitly requested changed-scope verification only.

If an affected test fails, fix the implementation without weakening the test/spec and rerun only affected tests.

### 3. Regenerate the two representative reports from persisted canonical artifacts

Regenerate, do not reuse the old HTML:

```text
runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/
runs/20260903-backtest-069500-krx-etf-smoke-v2/
```

Equivalent direct invocation is acceptable:

```python
from portfolio_optimizer_kr.viewer.backtest_renderer import generate_backtest_report

generate_backtest_report("runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2")
generate_backtest_report("runs/20260903-backtest-069500-krx-etf-smoke-v2")
```

Confirm both runs now persist:

```text
review/portfolio_asset_performance.csv
```

Do not modify finance inputs or rerun market-data acquisition merely to regenerate presentation output.

### 4. Changed-scope browser validation only

For each regenerated US and KRX report, set `BACKTEST_REPORT_PATH` to that report and run only:

```bash
npx playwright test verification/browser/backtest-report-content.spec.mjs
```

Use the repository Playwright config/web server. Do not run the full browser suite.

In addition to the automated contract, report these observed facts from the generated DOM:

- Growth x-axis month labels are unique; initial wealth observation remains present.
- Annual Returns has `annual-returns-chart` and grouped year tooltip.
- Drawdowns are separated by portfolio/benchmark and each has a series chart + episode table.
- Assets includes `Portfolio Asset Performance` with the required 16 columns.
- Annual Asset Returns is ticker-identified chart + supporting table.
- Correlations render numeric `correlations-heatmap` cells.
- Rolling 3Y and 5Y charts are present.
- US benchmark report additionally has:
  - Annual Active Return chart.
  - one cumulative Active Return Contribution panel per portfolio.
  - one Rolling Active Return/Risk 36m panel per portfolio with Active Return bars and Tracking Error line/right axis.
  - one Up/Down block per portfolio with the full conditional-statistics columns and Return vs. Benchmark paired chart.
- KRX benchmark=None report cleanly omits `#activeReturns`.
- Prior formatting remains correct: human option labels, percentages, human benchmark identity, `069500`, USD/KRW balances, no raw storage suffix leakage.

### 5. Commit generated artifacts/evidence and publish

Commit/push the regenerated report HTML and newly persisted `portfolio_asset_performance.csv` files plus any changed-scope validation evidence required by the repo workflow. Do not create unrelated changes.

Then confirm `Publish research reports` succeeds for the final HEAD and verify the exact published URLs are reachable:

```text
https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html
https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html
```

### 6. Result handoff

Replace `ai-share/agent-to-llm.md` with the new result, commit/push it, and report:

- start HEAD / final HEAD
- changed-scope pytest result
- US changed-scope Playwright result
- KRX changed-scope Playwright result
- regenerated report/artifact paths
- `portfolio_asset_performance.csv` existence for US/KRX
- Pages workflow run ID/URL and conclusion
- exact US/KRX published URLs and reachability
- any remaining P0/P1/P2 observed in the changed scope
- result commit SHA

Do not claim LLM acceptance. After publish, LLM will independently download the exact GitHub Pages deployment artifact, parse the deployed HTML in Chromium, compare it to the internal spec + PV reference, and issue first acceptance.
