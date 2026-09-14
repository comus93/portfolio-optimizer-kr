# Tasks

- [x] Add LOYO robustness analyzer that reuses prepared monthly returns and `solve_optimization()`.
- [x] Reuse the existing baseline optimization result without an additional baseline solve.
- [x] Record feasible scenario allocation/objective deltas, partial-year observation counts, and infeasible scenarios.
- [x] Persist canonical `optimization_robustness.loyo` plus `loyo_robustness.csv` raw/review artifact.
- [x] Integrate LOYO only into default Optimization execution; Backtest and custom analyzer behavior remain unchanged.
- [x] Add synthetic tests for Max Sharpe stability, allocation turnover math, partial-year removal, and infeasible target-vol scenario.
- [x] Add affected runner/artifact regression proving normal Optimization result semantics remain unchanged and Backtest does not gain LOYO.
- [x] Run targeted regression on the feature branch and review diff against the OpenSpec delta before merging.

Verification: targeted affected-scope regression completed with 25 passed on GitHub Actions run `34805351848`.
