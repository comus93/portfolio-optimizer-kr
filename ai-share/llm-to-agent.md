# AI Share

state: active
id: 20260903T125200+0900-llm
created_at: 2026-09-03T12:52:00+09:00
type: request
reply_to: 20260903T121200+0900-agent

## Context

User and LLM performed the first explicit visual review against the captured Portfolio Visualizer Backtest reference:

- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- extracted `source/page.part-*.html`
- source URL recorded in the reference README

This request supersedes the prior validation handoff.

LLM fixed the first confirmed Active-section visual discrepancies in `src/portfolio_optimizer_kr/viewer/historical_active_components.py`:

1. Annual Active Return now reserves a real left y-axis area with readable percent labels, tick marks, grid and axis title.
2. Active Return Contribution is now a time-based multi-series **column/bar chart**, matching the PV visual grammar instead of a line chart.
3. Active Return Contribution has readable y-axis percent scale/ticks/grid and calendar x ticks.
4. Rolling Active Return / Risk explicitly exposes both left Active Return and right Tracking Error y scales/ticks.
5. Return vs Benchmark uses a readable y scale/ticks and paired bars.
6. The presentation-only changes do not recalculate finance analytics.

Regression added:
- `tests/test_active_visual_reference_contract.py`

GitHub Actions run `33712862481` is green with **102 passed** at HEAD `8fd73c6b3b481d790b256c4a3bd1066e46465140`.

## Agent request

Sync latest `bt-module` and regenerate only the benchmarked representative US Backtest from its unchanged persisted input:

`runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/input.yaml`

Use the existing safe Windows/local procedure if needed: copy the input outside the run directory, recreate that one run directory, and execute the copied YAML with the current repository CLI. Do not alter financial inputs or run id.

Then validate the freshly generated report in a real browser at desktop and mobile widths. In addition to the existing Backtest browser/content checks, explicitly inspect the Active section for these visual requirements:

- Annual Active Return: visible/readable left percent y-axis labels and ticks; no clipping.
- Active Return Contribution: asset series are rendered as columns/bars, not polylines; visible/readable left percent y-axis labels and ticks; calendar x labels remain legible.
- Rolling Active Return / Risk: bars + Tracking Error line; both left and right percent y scales visible/readable; neither side clipped.
- Return vs Benchmark: paired portfolio/benchmark bars with visible/readable percent y scale and legible benchmark-return x labels.
- Horizontal grid lines align with y ticks and do not obscure marks.
- Tooltips still work.

Run at minimum:

```text
uv run python -m pytest -q tests/test_active_visual_reference_contract.py tests/test_backtest_report_content_contract.py tests/test_backtest_shared_end_to_end.py
```

and the targeted Playwright content/general Backtest specs against the regenerated US report.

If a real local/browser defect is exposed, fix it within this Active-chart presentation scope, add the smallest regression needed, and rerun.

Refresh desktop/mobile screenshot evidence for the US run, commit the regenerated run/evidence and any necessary validation fix, push `bt-module`, and confirm the Publish research reports workflow completes.

Replace `ai-share/agent-to-llm.md` with the result and report:

- start/final HEAD
- pytest and Playwright results
- whether each of the four Active visual requirements above passed in the real browser
- any defect/fix made locally
- screenshot evidence paths
- Pages workflow id/status
- final public US report URL

Do not broaden into unrelated report cleanup. The user is continuing a separate visual review and will send additional findings in another batch.
