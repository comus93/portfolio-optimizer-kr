from __future__ import annotations

import pandas as pd
import pytest

from portfolio_optimizer_kr.backtest import analyze_backtest_prices
from portfolio_optimizer_kr.benchmark_presets import materialize_benchmark_preset
from portfolio_optimizer_kr.config import ConfigValidationError, request_from_config
from portfolio_optimizer_kr.research import _apply_research_defaults


def _candidate_config(benchmark: object) -> dict:
    return {
        "product_mode": "backtest",
        "run_id": "kaw-benchmark-test",
        "assets": [
            {"symbol": "AAA", "name": "Candidate Asset", "currency": "KRW"},
        ],
        "portfolios": [
            {"name": "Candidate", "weights_pct": {"AAA": 100}},
        ],
        "benchmark": benchmark,
        "risk_free": {"mode": "fixed", "annual_rate_pct": 2.0},
        "fx": {"usdkrw_symbol": "USD/KRW"},
    }


def test_kaw_short_materializes_native_proxy_and_constituents():
    effective = _apply_research_defaults(_candidate_config("kaw_short"))

    assert effective["benchmark"]["type"] == "portfolio"
    assert effective["benchmark"]["preset"] == "kaw_native"
    assert effective["benchmark"]["name"] == "KAW Native Proxy"
    assert effective["benchmark"]["usable_from"] == "2021-11"
    assert effective["benchmark"]["weights_pct"]["267440"] == 15.0
    assert effective["benchmark"]["weights_pct"]["385560"] == 15.0
    assert effective["benchmark"]["weights_pct"]["GLD"] == 20.0

    symbols = [str(row["symbol"]) for row in effective["assets"]]
    assert symbols[0] == "AAA"
    assert {"133690", "402970", "192090", "200250", "GLD"}.issubset(symbols)


def test_kaw_long_materializes_internal_core_and_parses_portfolio_benchmark():
    spec = request_from_config(_candidate_config("kaw_long"))
    request = spec.request

    assert request.benchmark is None
    assert request.benchmark_portfolio is not None
    assert request.benchmark_portfolio.name == "KAW Core Revised Internal"
    assert request.benchmark_portfolio.target_weights["QQQ"] == pytest.approx(0.10)
    assert request.benchmark_portfolio.target_weights["SCHD"] == pytest.approx(0.10)
    assert request.benchmark_portfolio.target_weights["192090"] == pytest.approx(0.085)
    assert request.benchmark_portfolio.target_weights["200250"] == pytest.approx(0.085)
    assert request.benchmark_portfolio.target_weights["TLT"] == pytest.approx(0.30)
    assert request.benchmark_portfolio.target_weights["GLD"] == pytest.approx(0.20)


def test_existing_asset_benchmark_semantics_are_preserved():
    spec = request_from_config(_candidate_config({"symbol": "SPY", "currency": "USD"}))
    request = spec.request

    assert request.benchmark is not None
    assert request.benchmark.symbol == "SPY"
    assert request.benchmark_portfolio is None


def test_explicit_no_benchmark_semantics_are_preserved():
    effective = _apply_research_defaults(_candidate_config(None))
    spec = request_from_config({**effective, "run_id": "no-benchmark"})

    assert effective["benchmark"] is None
    assert spec.request.benchmark is None
    assert spec.request.benchmark_portfolio is None


def test_optimization_rejects_kaw_portfolio_preset():
    config = {
        "product_mode": "optimization",
        "run_id": "optimization-kaw-benchmark",
        "assets": [{"symbol": "AAA", "currency": "KRW"}],
        "benchmark": "kaw_native",
    }
    with pytest.raises(ConfigValidationError, match="only in backtest"):
        request_from_config(config)


def test_generic_portfolio_benchmark_uses_shared_portfolio_path():
    config = {
        "product_mode": "backtest",
        "run_id": "composite-benchmark",
        "assets": [
            {"symbol": "AAA", "currency": "KRW"},
            {"symbol": "BBB", "currency": "KRW"},
        ],
        "portfolios": [
            {"name": "Candidate", "weights_pct": {"AAA": 100, "BBB": 0}},
        ],
        "benchmark": {
            "type": "portfolio",
            "name": "50/50 Baseline",
            "weights_pct": {"AAA": 50, "BBB": 50},
        },
        "risk_free": {"mode": "fixed", "annual_rate_pct": 0},
        "rebalancing": {"period": "monthly", "calendar_aligned": True},
    }
    request = request_from_config(config).request
    index = pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31"])
    prices = {
        "AAA": pd.Series([100.0, 110.0, 104.5], index=index),
        "BBB": pd.Series([100.0, 102.0, 101.0], index=index),
    }

    result = analyze_backtest_prices(request, prices, annual_rf=0.0)
    monthly = result["_tables"]["monthly_return_series"]

    assert list(monthly["Candidate"]) == pytest.approx([0.10, -0.05])
    assert list(monthly["benchmark"]) == pytest.approx(
        [0.06, (-0.05 + (101.0 / 102.0 - 1.0)) / 2.0]
    )
    assert result["configuration"]["benchmark"]["type"] == "portfolio"
    assert result["configuration"]["benchmark"]["name"] == "50/50 Baseline"


def test_materialization_is_idempotent():
    first = materialize_benchmark_preset(_candidate_config("kaw_core"))
    second = materialize_benchmark_preset(first)

    assert second == first
