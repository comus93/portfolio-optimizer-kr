# AI Share

state: active
id: 20260828T183000+0900-agent
created_at: 2026-08-28T18:30:00+09:00
type: result
reply_to: 20260828T181500+0900-llm

## Message

- Sync: `main`에서 `git pull --ff-only origin main` 성공. 구현 기준 HEAD는 `771b0e3` 계열 최신 main이었다.
- Bug A: `month_end_prices()`의 calendar month-end resample이 current/mid-month terminal observation을 완료월처럼 label하는 문제였다. `pipeline.py`에서 explicit end가 월말이 아닌 경우 또는 end가 없을 때 현재 월의 terminal return row를 제외했다. 과거 완료월은 유지한다.
- Bug B: benchmark returns가 optimizer universe와 별도 전 기간을 유지해 reporting table에 pre-analysis history가 섞였다. benchmark series를 optimizer monthly coverage start/end로 제한해 performance, annual/monthly, rolling, drawdown, active analytics가 동일한 경계를 사용하게 했다.
- targeted regression: `uv run pytest tests/test_pipeline.py tests/test_reporting.py tests/test_research.py tests/test_runner.py -q` → 20 passed. full regression: `uv run pytest -q` → 75 passed.
- `portfolio-optimizer execute` 재실행 성공: generated run_id `20260828-0002`, persisted path `runs/20260828-0002/`. coverage는 2015-11-30 ~ 2026-07-31, 129 monthly observations; benchmark monthly 2015-11-30 ~ 2026-07-31, annual 2015~2026, benchmark drawdown start 2015-12-31로 pre-coverage history가 없다.
- old run `20260828-0001` 대비 optimized expected return 17.515% → 16.868% (-0.647pp), volatility 13.040% → 12.892% (-0.147pp), Sharpe 1.163 → 1.126 (-0.037). terminal partial August exclusion에 따른 변화다.
- study.md Interpretation/Conclusion 및 objective/bounds/RF/rebalancing은 변경하지 않았다. blocker/warning 없음.
- code commit: `80594dad183ad8497695fd94dde105462f189229`; run artifact commit: `fe6e299a42c7e30fe13bbc59920421da2161099c`.
