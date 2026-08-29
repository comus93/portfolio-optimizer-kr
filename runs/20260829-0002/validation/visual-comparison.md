# P0 follow-up validation

PV live comparison: not re-run in this partial validation
Static report check: PASS

P0 mismatches: remaining

## Completed

- Efficient Frontier curve source is now restricted to `kind === frontier` points.
- Asset, Provided, Optimized, Benchmark and objective landmarks remain marker-only.
- Report is self-contained with embedded data and no external HTTP assets.

## Remaining P0 work

- Supply Provided/Benchmark landmark coordinates from explicitly ex-ante-compatible upstream artifacts.
- Replace Up/Down bars with real monthly-observation scatter panels and presentation-ready percentage fields.
- Add contribution and rolling-active hover hit targets.
- Enforce missing-is-not-zero in all generic chart paths.
- Select Transition tooltip point by nearest actual volatility, not row index.
- Convert Growth display to a balance convention such as Growth of $10,000.
