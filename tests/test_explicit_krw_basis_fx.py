from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.data.preparation import prepare_monthly_returns
from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest
from portfolio_optimizer_kr.runner import run_yaml


class FakeLoader:
    def __init__(self):
        self.series_call = None

    def load_many(self, assets, start=None, end=None):
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return {
            asset.symbol: pd.Series([100.0, 100.0, 100.0, 100.0], index=index)
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        self.series_call = (symbol, start, end)
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return pd.Series([1000.0, 1100.0, 1210.0, 1331.0], index=index)

    def load_economic_series(self, symbol, start=None, end=None):
        raise AssertionError("fixed risk-free test should not load economic data")


def test_all_usd_run_with_explicit_fx_loads_usdkrw(tmp_path):
    config = tmp_path / "all-usd-krw-basis.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: all-usd-krw-basis
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    currency: USD
    provided_weight_pct: 50
benchmark:
  symbol: BM
  currency: USD
risk_free:
  mode: fixed
  annual_rate_pct: 0
fx:
  usdkrw_symbol: USDKRW_TEST
""",
        encoding="utf-8",
    )
    loader = FakeLoader()
    seen = {}

    def analyze(request, prices, usdkrw=None, annual_rf=None):
        seen["usdkrw"] = usdkrw
        return {"ok": True}

    def writer(result, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    run_yaml(
        config,
        tmp_path / "runs",
        loader=loader,
        analyze_fn=analyze,
        writer=writer,
    )

    assert loader.series_call == ("USDKRW_TEST", "2019-12-01", "2020-03-31")
    assert seen["usdkrw"] is not None


def test_all_usd_monthly_returns_convert_when_usdkrw_is_supplied():
    index = pd.to_datetime(["2023-12-31", "2024-01-31", "2024-02-29"])
    request = OptimizationRequest(
        assets=(AssetSpec("A", currency="USD"),),
        start="2024-01-01",
        end="2024-02-29",
    )
    usd_price = pd.Series([100.0, 100.0, 100.0], index=index)
    usdkrw = pd.Series([1000.0, 1100.0, 1210.0], index=index)

    returns = prepare_monthly_returns(request, {"A": usd_price}, usdkrw)

    assert returns["A"].tolist() == pytest.approx([0.1, 0.1])


def test_all_usd_monthly_returns_remain_usd_basis_without_explicit_fx():
    index = pd.to_datetime(["2023-12-31", "2024-01-31", "2024-02-29"])
    request = OptimizationRequest(
        assets=(AssetSpec("A", currency="USD"),),
        start="2024-01-01",
        end="2024-02-29",
    )
    usd_price = pd.Series([100.0, 110.0, 121.0], index=index)

    returns = prepare_monthly_returns(request, {"A": usd_price})

    assert returns["A"].tolist() == pytest.approx([0.1, 0.1])
