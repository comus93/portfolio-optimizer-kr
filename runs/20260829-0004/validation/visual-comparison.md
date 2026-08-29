# Visual comparison

PV live comparison: PASS (semantic P0 review)
Static golden comparison: PASS (section and chart-type review)

P0 mismatches: 0
P1 mismatches: 5
Intentional deviations: 2

## Efficient Frontier

- X/Y semantics: PASS — Standard Deviation % / Expected Return %.
- ticks/units: PASS — percent axes are displayed from presentation data.
- landmarks: PASS — assets, Provided, Optimized, Benchmark and objective landmark are rendered.
- tooltip: PASS — risk, return, Sharpe and allocation values are presentation data.

## Transition Map

- stacked area: PASS
- X = Std Dev: PASS
- allocations sum 100%: PASS — contract-tested frontier weights.

## Active Return Contribution

- portfolio panels separated: PASS
- cross-portfolio path: NONE
- sawtooth artifact: NONE
- tooltip: PASS

## Browser evidence

The generated report was opened in a local browser session and rendered 14 SVG charts with no browser console errors. The same live PV shared result was opened for semantic comparison. Browser tooling did not provide a workspace screenshot-write facility, so no PNG files are included.

## Remaining differences

- Generic time-series charts still have simpler tick density/grid styling than PV.
- Allocation pie charts and correlation heatmaps are deferred P1 presentation work.
- PV expense-ratio and withdrawal-oriented detail is intentionally out of scope for this research report.
