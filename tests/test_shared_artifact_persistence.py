from __future__ import annotations

import pandas as pd

from portfolio_optimizer_kr.report import write_analysis_run


def test_backtest_shared_artifacts_preserve_decimal_and_display_units(tmp_path):
    result = {
        "configuration": {
            "product_mode": "backtest",
            "run_id": "test-shared-artifacts",
            "assets": [
                {"symbol": "069500", "name": "KODEX 200", "currency": "KRW"},
                {"symbol": "GLD", "name": "SPDR Gold Shares", "currency": "USD"},
            ],
            "benchmark": None,
        },
        "data_coverage": {},
        "asset_statistics": {},
        "portfolio_definitions": {
            "Growth": {"target_weights": {"069500": 0.7, "GLD": 0.3}},
            "Balanced": {"target_weights": {"069500": 0.5, "GLD": 0.5}},
        },
        "portfolio_paths": {},
        "portfolio_performance": {
            "trailing_returns": {
                "Growth": {},
                "Balanced": {},
            }
        },
        "benchmark_analytics": {},
        "correlations": {},
        "return_decomposition": {},
        "risk_decomposition": {},
        "_tables": {
            "target_allocations": pd.DataFrame(
                [
                    {
                        "portfolio": "Growth",
                        "ticker": "069500",
                        "name": "KODEX 200",
                        "target_weight": 0.7,
                        "target_weight_pct": 70.0,
                    },
                    {
                        "portfolio": "Balanced",
                        "ticker": "069500",
                        "name": "KODEX 200",
                        "target_weight": 0.5,
                        "target_weight_pct": 50.0,
                    },
                ]
            ),
            "portfolio_performance": pd.DataFrame(
                [
                    {"portfolio": "Growth", "start_balance": 10000, "end_balance": 12000},
                    {"portfolio": "Balanced", "start_balance": 10000, "end_balance": 11500},
                ]
            ),
            "portfolio_asset_performance": pd.DataFrame(
                [
                    {
                        "ticker": "069500",
                        "name": "KODEX 200",
                        "cagr": 0.12,
                        "annualized_return": 0.13,
                        "annualized_volatility": 0.2,
                        "best_year": 0.3,
                        "worst_year": -0.15,
                        "max_drawdown": -0.22,
                        "sharpe_ratio": 0.65,
                        "sortino_ratio": 0.9,
                        "3m": 0.04,
                        "ytd": 0.08,
                        "1y": 0.12,
                        "3y": None,
                        "5y": None,
                        "10y": None,
                    }
                ]
            ),
            "up_down_market_performance": pd.DataFrame(
                [
                    {
                        "portfolio": "Growth",
                        "market_type": "up",
                        "portfolio_return": 0.02,
                        "benchmark_return": 0.015,
                        "active_return": 0.005,
                        "occurrences": 10,
                        "above_benchmark_count": 7,
                        "below_benchmark_count": 3,
                        "total_count": 10,
                        "pct_above_benchmark": 70.0,
                        "above_active_return": 0.008,
                        "below_active_return": -0.002,
                        "above_active_return_pct": 0.8,
                        "below_active_return_pct": -0.2,
                        "overall_active_return_pct": 0.5,
                    }
                ]
            ),
            "up_down_market_scatter": pd.DataFrame(
                [
                    {
                        "date": "2024-01-31",
                        "portfolio": "Growth",
                        "market_type": "up",
                        "benchmark_return": 0.01,
                        "portfolio_return": 0.02,
                        "active_return": 0.01,
                        "benchmark_return_pct": 1.0,
                        "portfolio_return_pct": 2.0,
                        "active_return_pct": 1.0,
                    }
                ]
            ),
        },
    }

    write_analysis_run(result, tmp_path)

    raw_allocations = pd.read_csv(
        tmp_path / "raw" / "target_allocations.csv", dtype={"ticker": str}
    )
    review_allocations = pd.read_csv(
        tmp_path / "review" / "target_allocations.csv", dtype={"ticker": str}
    )
    assert raw_allocations.loc[0, "target_weight"] == 0.7
    assert review_allocations.loc[0, "target_weight_pct"] == 70.0
    assert review_allocations.loc[0, "ticker"] == "069500"

    asset_performance = pd.read_csv(
        tmp_path / "review" / "portfolio_asset_performance.csv",
        dtype={"ticker": str},
    )
    assert asset_performance.loc[0, "cagr_pct"] == 12.0
    assert asset_performance.loc[0, "ticker"] == "069500"

    up_down = pd.read_csv(
        tmp_path / "review" / "up_down_market_performance.csv"
    )
    assert up_down.loc[0, "above_benchmark_count"] == 7
    assert up_down.loc[0, "pct_above_benchmark"] == 70.0
    assert up_down.loc[0, "overall_active_return_pct"] == 0.5
    assert (tmp_path / "review" / "up_down_market_scatter.csv").is_file()
