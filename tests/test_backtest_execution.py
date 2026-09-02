from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from portfolio_optimizer_kr.research import execute_controlled_experiment
from portfolio_optimizer_kr.runner import run_yaml


class BacktestFakeLoader:
    def __init__(self):
        self.loaded_symbols: list[str] = []

    def load_many(self, assets, start=None, end=None):
        assets = list(assets)
        self.loaded_symbols = [asset.symbol for asset in assets]
        index = pd.date_range("2019-12-31", "2020-06-30", freq="ME")
        base = {
            "A": [100, 104, 102, 108, 111, 109, 116],
            "B": [100, 99, 103, 101, 106, 108, 107],
            "SPY": [100, 101, 102, 103, 104, 105, 106],
            "BM": [100, 101, 102, 103, 104, 105, 106],
        }
        return {
            asset.symbol: pd.Series(base[asset.symbol], index=index, dtype=float, name=asset.symbol)
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        raise AssertionError("FX should not be required for USD-only backtest")

    def load_economic_series(self, symbol, start=None, end=None):
        raise AssertionError("fixed risk-free mode should not load economic series")


def _backtest_yaml(run_id: str = "bt-execution") -> str:
    return f"""
product_mode: backtest
run_id: {run_id}
time_period:
  mode: month_to_month
  start_year: 2020
  first_month: Jan
  end_year: 2020
  last_month: Jun
assets:
  - symbol: A
    name: Asset A
    currency: USD
  - symbol: B
    name: Asset B
    currency: USD
portfolios:
  - name: Core
    weights_pct:
      A: 60
      B: 40
  - name: Defensive
    weights_pct:
      A: 30
      B: 70
benchmark:
  symbol: BM
  currency: USD
initial_balance: 10000
rebalancing:
  period: monthly
  calendar_aligned: true
risk_free:
  mode: fixed
  annual_rate_pct: 0
""".lstrip()


def test_run_yaml_dispatches_backtest_and_generates_self_contained_report(tmp_path):
    config = tmp_path / "backtest.yaml"
    config.write_text(_backtest_yaml(), encoding="utf-8")

    output = run_yaml(config, tmp_path / "runs", loader=BacktestFakeLoader())

    result = yaml.safe_load((output / "result.json").read_text(encoding="utf-8"))
    html = (output / "report.html").read_text(encoding="utf-8")
    assert result["configuration"]["product_mode"] == "backtest"
    assert set(result["portfolio_definitions"]) == {"Core", "Defensive"}
    assert (output / "raw" / "portfolio_growth.csv").is_file()
    assert (output / "review" / "target_allocations.csv").is_file()
    assert "Portfolio Backtest" in html
    assert "Target Allocation" in html
    assert "Portfolio Growth" in html
    assert "Efficient Frontier" not in html
    assert "Defensive" in html
    assert "benchmark-relative" in html.lower()


def _make_research_repo(tmp_path: Path, *, benchmark_line: str = "") -> Path:
    repo = tmp_path / "repo"
    experiment = repo / "studies" / "bt-study" / "experiments" / "001-ab.yaml"
    experiment.parent.mkdir(parents=True)
    experiment.write_text(
        (
            """
product_mode: backtest
assets:
  - symbol: A
    currency: USD
  - symbol: B
    currency: USD
portfolios:
  - weights_pct:
      A: 60
      B: 40
  - weights_pct:
      A: 20
      B: 80
risk_free:
  mode: fixed
  annual_rate_pct: 0
"""
            + benchmark_line
        ).lstrip(),
        encoding="utf-8",
    )
    (repo / "studies" / "bt-study" / "study.md").write_text("# Backtest Study\n", encoding="utf-8")
    control = repo / "control" / "execute.yaml"
    control.parent.mkdir(parents=True)
    control.write_text(
        "target: studies/bt-study/experiments/001-ab.yaml\n",
        encoding="utf-8",
    )
    return repo


def _minimal_writer(result, output_dir):
    Path(output_dir, "result.json").write_text("{}\n", encoding="utf-8")


def _minimal_analyze(request, prices, usdkrw=None, annual_rf=None):
    return {"product_mode": "backtest", "run_id": request.run_id}


def test_research_backtest_materializes_frontend_defaults_and_product_provenance(tmp_path):
    repo = _make_research_repo(tmp_path)
    loader = BacktestFakeLoader()

    output = execute_controlled_experiment(
        repo_root=repo,
        loader=loader,
        analyze_fn=_minimal_analyze,
        writer=_minimal_writer,
    )

    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))
    context = yaml.safe_load((output / "context.yaml").read_text(encoding="utf-8"))

    assert effective["product_mode"] == "backtest"
    assert effective["benchmark"]["symbol"] == "SPY"
    assert effective["initial_balance"] == 10000
    assert effective["time_period"] == {"mode": "month_to_month"}
    assert effective["rebalancing"] == {"period": "monthly", "calendar_aligned": True}
    assert [row["name"] for row in effective["portfolios"]] == ["Portfolio 1", "Portfolio 2"]
    assert context["product_mode"] == "backtest"
    assert "SPY" in loader.loaded_symbols


def test_research_backtest_explicit_no_benchmark_overrides_spy_default(tmp_path):
    repo = _make_research_repo(tmp_path, benchmark_line="\nbenchmark: null\n")
    loader = BacktestFakeLoader()

    output = execute_controlled_experiment(
        repo_root=repo,
        loader=loader,
        analyze_fn=_minimal_analyze,
        writer=_minimal_writer,
    )

    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))
    assert "benchmark" in effective and effective["benchmark"] is None
    assert "SPY" not in loader.loaded_symbols
