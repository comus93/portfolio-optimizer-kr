from pathlib import Path

import pandas as pd
import pytest
import yaml

from portfolio_optimizer_kr.backtest import analyze_backtest_prices
from portfolio_optimizer_kr.config import ConfigValidationError, request_from_config
from portfolio_optimizer_kr.models import (
    BacktestRequest,
    ProductMode,
    RebalancingPeriod,
    TimePeriodMode,
)
from portfolio_optimizer_kr.portfolio import build_portfolio_path
from portfolio_optimizer_kr.report import write_analysis_run


def _backtest_config(**overrides):
    config = {
        "product_mode": "backtest",
        "run_id": "bt-001",
        "time_period": {
            "mode": "month_to_month",
            "start_year": 2020,
            "first_month": 3,
            "end_year": 2021,
            "last_month": 2,
        },
        "assets": [
            {"symbol": "A", "name": "Asset A", "currency": "USD"},
            {"symbol": "B", "name": "Asset B", "currency": "USD"},
        ],
        "portfolios": [
            {"name": "Balanced", "weights_pct": {"A": 60, "B": 40}},
            {"weights_pct": {"A": 25, "B": 75}},
        ],
        "benchmark": {"symbol": "BM", "currency": "USD"},
        "initial_balance": 10000,
        "rebalancing": {
            "period": "monthly",
            "calendar_aligned": True,
        },
        "risk_free": {"mode": "fixed", "annual_rate_pct": 0},
    }
    config.update(overrides)
    return config


def test_backtest_config_builds_collection_and_month_boundaries():
    spec = request_from_config(_backtest_config())

    assert spec.product_mode is ProductMode.BACKTEST
    assert isinstance(spec.request, BacktestRequest)
    assert spec.request.time_period_mode is TimePeriodMode.MONTH_TO_MONTH
    assert str(spec.request.start) == "2020-03-01"
    assert str(spec.request.end) == "2021-02-28"
    assert spec.request.initial_balance == 10000
    assert spec.request.rebalancing is RebalancingPeriod.MONTHLY
    assert spec.request.calendar_aligned is True
    assert [portfolio.name for portfolio in spec.request.portfolios] == [
        "Balanced",
        "Portfolio 2",
    ]
    assert spec.request.portfolios[1].target_weights == {"A": 0.25, "B": 0.75}


def test_year_to_year_period_uses_full_calendar_year_boundaries():
    config = _backtest_config(
        time_period={"mode": "year_to_year", "start_year": 2020, "end_year": 2025}
    )
    spec = request_from_config(config)

    assert spec.request.time_period_mode is TimePeriodMode.YEAR_TO_YEAR
    assert str(spec.request.start) == "2020-01-01"
    assert str(spec.request.end) == "2025-12-31"


def test_backtest_rejects_more_than_three_portfolios():
    config = _backtest_config()
    config["portfolios"] = [
        {"weights_pct": {"A": 50, "B": 50}},
        {"weights_pct": {"A": 60, "B": 40}},
        {"weights_pct": {"A": 70, "B": 30}},
        {"weights_pct": {"A": 80, "B": 20}},
    ]

    with pytest.raises(ConfigValidationError, match="at most 3"):
        request_from_config(config)


def test_backtest_rejects_unknown_portfolio_asset():
    config = _backtest_config()
    config["portfolios"][0]["weights_pct"]["C"] = 10

    with pytest.raises(ConfigValidationError, match="unknown asset"):
        request_from_config(config)


def test_non_calendar_quarterly_rebalancing_anchors_to_first_active_month():
    returns = pd.DataFrame(
        {"A": [0.10, 0.10, 0.10, 0.10], "B": [0.00, 0.00, 0.00, 0.00]},
        index=pd.to_datetime(["2024-02-29", "2024-03-31", "2024-04-30", "2024-05-31"]),
    )

    path = build_portfolio_path(
        returns,
        {"A": 0.5, "B": 0.5},
        RebalancingPeriod.QUARTERLY,
        calendar_aligned=False,
    )

    assert path.weights.iloc[1]["A"] > 0.5
    assert path.weights.iloc[2]["A"] > path.weights.iloc[1]["A"]
    assert path.weights.iloc[3]["A"] == pytest.approx(0.5)


def test_calendar_quarterly_rebalancing_uses_calendar_quarter_boundary():
    returns = pd.DataFrame(
        {"A": [0.10, 0.10, 0.10], "B": [0.00, 0.00, 0.00]},
        index=pd.to_datetime(["2024-02-29", "2024-03-31", "2024-04-30"]),
    )

    path = build_portfolio_path(
        returns,
        {"A": 0.5, "B": 0.5},
        RebalancingPeriod.QUARTERLY,
        calendar_aligned=True,
    )

    assert path.weights.iloc[1]["A"] > 0.5
    assert path.weights.iloc[2]["A"] == pytest.approx(0.5)


def test_backtest_pipeline_produces_realized_multi_portfolio_result():
    spec = request_from_config(
        _backtest_config(
            time_period={
                "mode": "month_to_month",
                "start_year": 2020,
                "first_month": 1,
                "end_year": 2020,
                "last_month": 6,
            },
            rebalancing={"period": "quarterly", "calendar_aligned": False},
        )
    )
    index = pd.date_range("2019-12-31", "2020-06-30", freq="ME")
    prices = {
        "A": pd.Series([100, 104, 102, 108, 111, 109, 116], index=index, dtype=float),
        "B": pd.Series([100, 99, 103, 101, 106, 108, 107], index=index, dtype=float),
        "BM": pd.Series([100, 101, 102, 103, 104, 105, 106], index=index, dtype=float),
    }

    result = analyze_backtest_prices(spec.request, prices, annual_rf=0.0)

    assert result["configuration"]["product_mode"] == "backtest"
    assert result["configuration"]["rebalancing_period"] == "quarterly"
    assert result["configuration"]["calendar_aligned"] is False
    assert "optimization_result" not in result
    assert set(result["portfolio_definitions"]) == {"Balanced", "Portfolio 2"}
    assert set(result["portfolio_performance"]["summary"]) >= {
        "Balanced",
        "Portfolio 2",
        "benchmark",
    }
    assert result["portfolio_performance"]["summary"]["Balanced"]["start_balance"] == 10000
    assert result["portfolio_performance"]["summary"]["Portfolio 2"]["start_balance"] == 10000
    assert result["data_coverage"]["backtest_monthly_returns"]["observations"] == 6
    assert result["benchmark_analytics"]["Balanced"]["tracking_error"] is not None

    growth = result["_tables"]["portfolio_growth"]
    assert {"Balanced_balance", "Portfolio 2_balance", "benchmark_balance"}.issubset(growth.columns)
    assert growth.iloc[0]["Balanced_balance"] != pytest.approx(1.0)


def test_backtest_writer_persists_canonical_result_without_optimizer_fields(tmp_path):
    spec = request_from_config(
        _backtest_config(
            time_period={
                "mode": "month_to_month",
                "start_year": 2020,
                "first_month": 1,
                "end_year": 2020,
                "last_month": 3,
            }
        )
    )
    index = pd.date_range("2019-12-31", "2020-03-31", freq="ME")
    prices = {
        "A": pd.Series([100, 102, 101, 104], index=index, dtype=float),
        "B": pd.Series([100, 99, 103, 105], index=index, dtype=float),
        "BM": pd.Series([100, 101, 102, 103], index=index, dtype=float),
    }
    result = analyze_backtest_prices(spec.request, prices, annual_rf=0.0)

    write_analysis_run(result, tmp_path)

    persisted = yaml.safe_load((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert persisted["configuration"]["product_mode"] == "backtest"
    assert "optimization_result" not in persisted
    assert (tmp_path / "raw" / "portfolio_growth.csv").is_file()
    assert (tmp_path / "review" / "performance_summary.csv").is_file()
    assert "Backtest run" in (tmp_path / "README.md").read_text(encoding="utf-8")
