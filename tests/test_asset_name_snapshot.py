from __future__ import annotations

import sys
from types import SimpleNamespace

import pandas as pd

from portfolio_optimizer_kr.config import hydrate_asset_names
from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.models import AssetSpec


def test_fdr_loader_uses_provider_etf_names_without_semantic_rewriting(monkeypatch):
    calls = []

    def stock_listing(kind):
        calls.append(kind)
        if kind == "ETF/US":
            return pd.DataFrame(
                {
                    "Symbol": ["SPY", "QQQ"],
                    "Name": [
                        "State Street SPDR S&P 500 ETF Trust",
                        "Invesco QQQ Trust  Series 1",
                    ],
                }
            )
        if kind == "ETF/KR":
            return pd.DataFrame(
                {"Code": ["069500"], "Name": ["KODEX 200"]}
            )
        raise AssertionError(kind)

    monkeypatch.setitem(
        sys.modules,
        "FinanceDataReader",
        SimpleNamespace(StockListing=stock_listing),
    )
    loader = FDRLoader()
    resolved = loader.load_asset_names(
        [
            AssetSpec("SPY", name="manual", currency="USD"),
            AssetSpec("QQQ", name="manual", currency="USD"),
            AssetSpec("NAVER:069500", name="manual", currency="KRW"),
        ]
    )
    assert resolved == {
        "SPY": "State Street SPDR S&P 500 ETF Trust",
        "QQQ": "Invesco QQQ Trust  Series 1",
        "NAVER:069500": "KODEX 200",
    }
    assert calls == ["ETF/US", "ETF/KR"]


def test_hydrate_asset_names_overwrites_manual_names_and_snapshots_benchmark():
    class Loader:
        def load_asset_names(self, assets):
            return {
                "SPY": "State Street SPDR S&P 500 ETF Trust",
                "GLD": "SPDR Gold Shares",
            }

    original = {
        "product_mode": "backtest",
        "run_id": "demo",
        "assets": [
            {"symbol": "SPY", "name": "S&P 500", "currency": "USD"},
            {"symbol": "GLD", "name": "Gold", "currency": "USD"},
        ],
        "benchmark": {
            "symbol": "SPY",
            "name": "Benchmark",
            "currency": "USD",
        },
    }
    hydrated = hydrate_asset_names(original, Loader())
    assert hydrated["assets"][0]["name"] == "State Street SPDR S&P 500 ETF Trust"
    assert hydrated["assets"][1]["name"] == "SPDR Gold Shares"
    assert hydrated["benchmark"]["name"] == "State Street SPDR S&P 500 ETF Trust"
    assert original["assets"][0]["name"] == "S&P 500"
