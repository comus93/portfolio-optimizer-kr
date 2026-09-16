# Proposal: LOYO readability and placement refinement

## Why

The LOYO tables now expose the right evidence, but the report still has three readability issues: the section appears too early in the report, year groups in Asset-Year Influence visually blend together, and ticker-only asset identity is hard to read for numeric Korean tickers.

## What changes

- Move the LOYO section to immediately after Portfolio Metrics and before Monthly Returns.
- Add four-row year-group zebra banding to the Year and Metric columns only, leaving numeric conditional backgrounds untouched.
- Render every Asset-Year Influence and Allocation Changes asset header as two lines: truncated Name then full Ticker.
- Keep LOYO Summary shift cells compact and ticker-only, and add a static wrapping asset legend below the summary.
- Do not add hover or new JavaScript interaction for asset identity.

## Non-goals

- No finance calculation changes.
- No LOYO optimizer rerun semantics changes.
- No change to Asset-Year Influence heatmap scales.
- No new tooltip/hover behavior.
