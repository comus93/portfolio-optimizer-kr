# Change: LOYO report integration and Optimization correlation scope correction

## Why
LOYO is canonical analysis evidence but was not visible in the default HTML report. Separately, an earlier report requirement incorrectly expanded Optimization correlations to include Provided/Optimized/Benchmark series even though Asset Correlations already has a canonical asset-only matrix.

## What changes
- Make LOYO a default Optimization report section when LOYO artifacts exist.
- Keep Optimization Asset Correlations asset-only and preserve Name + Ticker presentation.
- Remove Portfolio / Asset Correlations from HTML and Optimization run semantics.
- Reuse the existing canonical asset correlation matrix; do not introduce a second calculation.
