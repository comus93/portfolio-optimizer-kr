# Tasks

- [ ] Add LOYO robustness analyzer that reuses prepared monthly returns and `solve_optimization()`.
- [ ] Reuse the existing baseline optimization result without an additional baseline solve.
- [ ] Record feasible scenario allocation/objective deltas, partial-year observation counts, and infeasible scenarios.
- [ ] Persist canonical `optimization_robustness.loyo` plus `loyo_robustness.csv` raw/review artifact.
- [ ] Integrate LOYO only into default Optimization execution; Backtest and custom analyzer behavior remain unchanged.
- [ ] Add synthetic tests for Max Sharpe stability, allocation turnover math, partial-year removal, and infeasible target-vol scenario.
- [ ] Add affected runner/artifact regression proving normal Optimization result semantics remain unchanged and Backtest does not gain LOYO.
- [ ] Run targeted regression on the feature branch and review diff against the OpenSpec delta before merging.
