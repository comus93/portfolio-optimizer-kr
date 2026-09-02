from __future__ import annotations

import sys
from types import SimpleNamespace

import pandas as pd
import pytest

from portfolio_optimizer_kr.data import FDRLoader, select_total_return_price
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec


def _close_only_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [100, 101], "High": [102, 103], "Low": [99, 100], "Close": [101, 102], "Volume": [10, 11], "Change": [None, 0.0099]},
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    )


def test_total_return_price_accepts_close_only_when_source_semantics_are_verified():
    out = select_total_return_price(_close_only_frame(), close_is_total_return=True)

    assert out.tolist() == [101.0, 102.0]
    assert out.attrs["return_semantics"] == "total_return"
    assert out.attrs["source_column"] == "Close"


def test_fdr_loader_accepts_default_korean_etf_naver_close(monkeypatch):
    fake_fdr = SimpleNamespace(
        DataReader=lambda symbol, start=None, end=None: _close_only_frame(),
        StockListing=lambda market: pd.DataFrame({"Code": ["069500", "114800"]}),
    )
    monkeypatch.setitem(sys.modules, "FinanceDataReader", fake_fdr)

    out = FDRLoader().load(AssetSpec("069500", name="KODEX 200", currency="KRW"))

    assert out.tolist() == [101.0, 102.0]
    assert out.attrs["provider_symbol"] == "069500"
    assert out.attrs["source_column"] == "Close"
    assert out.attrs["provider_route"] == "NAVER"


def test_fdr_loader_does_not_extend_korean_etf_close_policy_to_common_stock(monkeypatch):
    fake_fdr = SimpleNamespace(
        DataReader=lambda symbol, start=None, end=None: _close_only_frame(),
        StockListing=lambda market: pd.DataFrame({"Code": ["069500", "114800"]}),
    )
    monkeypatch.setitem(sys.modules, "FinanceDataReader", fake_fdr)

    with pytest.raises(DataValidationError, match="total-return"):
        FDRLoader().load(AssetSpec("005930", name="Samsung Electronics", currency="KRW"))


def test_fdr_loader_does_not_treat_explicit_krx_close_as_total_return(monkeypatch):
    fake_fdr = SimpleNamespace(
        DataReader=lambda symbol, start=None, end=None: _close_only_frame(),
        StockListing=lambda market: pd.DataFrame({"Code": ["069500", "114800"]}),
    )
    monkeypatch.setitem(sys.modules, "FinanceDataReader", fake_fdr)

    with pytest.raises(DataValidationError, match="total-return"):
        FDRLoader().load(AssetSpec("KRX:069500", name="KODEX 200", currency="KRW"))
