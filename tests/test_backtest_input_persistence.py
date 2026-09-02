from __future__ import annotations

import pandas as pd
import yaml

from portfolio_optimizer_kr.runner import run_yaml


class FakeLoader:
    def load_many(self, assets, start=None, end=None):
        index = pd.date_range("2019-12-31", "2020-06-30", freq="ME")
        return {
            asset.symbol: pd.Series(
                [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0],
                index=index,
                name=asset.symbol,
            )
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        raise AssertionError("FX is not expected")

    def load_economic_series(self, symbol, start=None, end=None):
        raise AssertionError("fixed RF is used")


def test_run_yaml_materializes_effective_backtest_defaults(tmp_path):
    source = tmp_path / "minimal-backtest.yaml"
    source.write_text(
        """
product_mode: backtest
run_id: minimal-backtest
assets:
  - symbol: A
    currency: USD
  - symbol: B
    currency: USD
portfolios:
  - weights_pct:
      A: 50
      B: 50
risk_free:
  mode: fixed
  annual_rate_pct: 0
""".lstrip(),
        encoding="utf-8",
    )

    output = run_yaml(source, tmp_path / "runs", loader=FakeLoader())
    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))

    assert effective["product_mode"] == "backtest"
    assert effective["initial_balance"] == 10000
    assert effective["time_period"] == {"mode": "month_to_month"}
    assert effective["rebalancing"] == {"period": "monthly", "calendar_aligned": True}
    assert effective["portfolios"][0]["name"] == "Portfolio 1"
    assert "benchmark" not in effective
