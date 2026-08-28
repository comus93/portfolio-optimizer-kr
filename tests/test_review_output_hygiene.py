from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.report import write_analysis_run


def _result_with_pipeline_style_tables() -> dict:
    return {
        "configuration": {
            "run_id": "review-hygiene",
            "assets": [
                {"symbol": "AAA", "name": "Asset A", "currency": "USD", "min_weight": 0.0, "max_weight": 1.0},
                {"symbol": "BBB", "name": "Asset B", "currency": "USD", "min_weight": 0.0, "max_weight": 1.0},
            ],
            "provided_weights": {"AAA": 0.5, "BBB": 0.5},
            "benchmark": {"symbol": "SPY", "currency": "USD"},
        },
        "data_coverage": {
            "benchmark_overlap": {"start": "2020-01-31", "end": "2025-12-31", "observations": 72}
        },
        "asset_statistics": {},
        "optimization_result": {"weights": {"AAA": 0.6, "BBB": 0.4}},
        "efficient_frontier": [],
        "portfolio_performance": {"trailing_returns": {}},
        "benchmark_analytics": {},
        "correlations": {},
        "return_decomposition": {},
        "risk_decomposition": {},
        "_tables": {
            "return_decomposition": pd.DataFrame(
                [
                    {"asset": "contribution_AAA", "provided": 0.4, "optimized": 0.5},
                    {"asset": "contribution_BBB", "provided": 0.3, "optimized": 0.4},
                ]
            ),
            "benchmark_analytics": pd.DataFrame(
                [
                    {"portfolio": "optimized", "active_return": 0.02, "tracking_error": 0.05, "information_ratio": 0.4},
                    {"portfolio": "provided", "active_return": 0.01, "tracking_error": 0.06, "information_ratio": 0.1667},
                    {"portfolio": "coverage", "start": "2020-01-31", "end": "2025-12-31", "observations": 72},
                ]
            ),
            "active_returns": pd.DataFrame(
                [
                    {
                        "portfolio": "optimized",
                        "date": "2025-12-31",
                        "portfolio_return": 0.03,
                        "benchmark_return": 0.02,
                        "active_return": 0.01,
                        "cumulative_active_return": 0.15,
                        "annual_active_return": 0.04,
                        "rolling_active_return": 0.05,
                        "rolling_tracking_error": 0.06,
                    }
                ]
            ),
            "monthly_return_series": pd.DataFrame(
                [{"date": "2025-12-31", "asset_AAA": 0.02, "asset_BBB": -0.01, "optimized": 0.01, "provided": 0.005, "benchmark": 0.008}]
            ),
        },
    }


def test_review_return_decomposition_uses_real_tickers(tmp_path: Path):
    write_analysis_run(_result_with_pipeline_style_tables(), tmp_path)
    table = pd.read_csv(tmp_path / "review" / "return_decomposition.csv")
    assert table["ticker"].tolist() == ["AAA", "BBB"]
    assert table["unit"].eq("monetary_initial_value_1").all()


def test_benchmark_summary_does_not_use_dummy_coverage_row(tmp_path: Path):
    write_analysis_run(_result_with_pipeline_style_tables(), tmp_path)
    table = pd.read_csv(tmp_path / "review" / "benchmark_summary.csv")
    assert table["portfolio"].tolist() == ["optimized", "provided"]
    assert {"overlap_start", "overlap_end", "observations"} <= set(table.columns)
    assert table["overlap_start"].eq("2020-01-31").all()
    assert table["overlap_end"].eq("2025-12-31").all()
    assert table["observations"].eq(72).all()


def test_review_detail_return_series_have_explicit_percentage_units(tmp_path: Path):
    write_analysis_run(_result_with_pipeline_style_tables(), tmp_path)

    active_path = tmp_path / "review" / "active_returns.csv"
    monthly_path = tmp_path / "review" / "monthly_return_series.csv"

    if active_path.exists():
        active = pd.read_csv(active_path)
        expected = {
            "portfolio_return_pct",
            "benchmark_return_pct",
            "active_return_pct",
            "cumulative_active_return_pct",
            "annual_active_return_pct",
            "rolling_active_return_pct",
            "rolling_tracking_error_pct",
        }
        assert expected <= set(active.columns)
        assert active.loc[0, "portfolio_return_pct"] == pytest.approx(3.0)
        assert active.loc[0, "rolling_tracking_error_pct"] == pytest.approx(6.0)

    if monthly_path.exists():
        monthly = pd.read_csv(monthly_path)
        expected = {"asset_AAA_return_pct", "asset_BBB_return_pct", "optimized_return_pct", "provided_return_pct", "benchmark_return_pct"}
        assert expected <= set(monthly.columns)
        assert monthly.loc[0, "asset_AAA_return_pct"] == pytest.approx(2.0)
        assert monthly.loc[0, "asset_BBB_return_pct"] == pytest.approx(-1.0)
