from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.report import write_analysis_run


def _representative_result() -> dict:
    performance_rows = pd.DataFrame(
        [
            {
                "portfolio": "optimized",
                "start_balance": 1.0,
                "end_balance": 2.0,
                "cagr": 0.10,
                "annualized_return": 0.11,
                "annualized_volatility": 0.12,
                "best_year": 0.25,
                "worst_year": -0.15,
                "max_drawdown": -0.20,
                "sharpe_ex_post": 0.75,
                "sortino": 1.1,
                "expected_return": 0.115,
            },
            {
                "portfolio": "provided",
                "start_balance": 1.0,
                "end_balance": 1.8,
                "cagr": 0.09,
                "annualized_return": 0.10,
                "annualized_volatility": 0.14,
                "best_year": 0.22,
                "worst_year": -0.18,
                "max_drawdown": -0.24,
                "sharpe_ex_post": 0.60,
                "sortino": 0.9,
                "expected_return": 0.105,
            },
            {
                "portfolio": "benchmark",
                "start_balance": 1.0,
                "end_balance": 1.7,
                "cagr": 0.08,
                "annualized_return": 0.09,
                "annualized_volatility": 0.15,
                "best_year": 0.20,
                "worst_year": -0.20,
                "max_drawdown": -0.25,
                "sharpe_ex_post": 0.50,
                "sortino": 0.8,
                "expected_return": 0.095,
            },
        ]
    )
    trailing = {
        "optimized": {
            "3m": 0.03,
            "ytd": 0.04,
            "1y": 0.12,
            "3y": 0.10,
            "5y": 0.09,
            "10y": None,
            "full_period": 0.095,
            "3y_annualized_volatility": 0.13,
            "5y_annualized_volatility": 0.12,
        },
        "provided": {
            "3m": 0.02,
            "ytd": 0.03,
            "1y": 0.10,
            "3y": 0.09,
            "5y": 0.08,
            "10y": None,
            "full_period": 0.085,
            "3y_annualized_volatility": 0.15,
            "5y_annualized_volatility": 0.14,
        },
        "benchmark": {
            "3m": 0.01,
            "ytd": 0.02,
            "1y": 0.08,
            "3y": 0.07,
            "5y": 0.06,
            "10y": None,
            "full_period": 0.075,
            "3y_annualized_volatility": 0.16,
            "5y_annualized_volatility": 0.15,
        },
    }
    return {
        "configuration": {
            "run_id": "review-contract",
            "assets": [
                {
                    "symbol": "AAA",
                    "name": "Asset A",
                    "currency": "USD",
                    "min_weight": 0.0,
                    "max_weight": 0.8,
                },
                {
                    "symbol": "BBB",
                    "name": "Asset B",
                    "currency": "USD",
                    "min_weight": 0.2,
                    "max_weight": 1.0,
                },
            ],
            "provided_weights": {"AAA": 0.6, "BBB": 0.4},
            "benchmark": {"symbol": "SPY", "name": "S&P 500", "currency": "USD"},
            "objective": "max_sharpe",
            "analysis_period": {"start": "2020-01-01", "end": "2025-12-31"},
            "rebalancing_period": "monthly",
            "risk_free": {"requested_mode": "fixed", "effective_annual_rate": 0.02},
            "frontier_points": 100,
            "solver_routing": {"qp": "OSQP", "socp": "CLARABEL"},
        },
        "data_coverage": {},
        "asset_statistics": {},
        "optimization_result": {
            "weights": {"AAA": 0.7, "BBB": 0.3},
            "expected_return": 0.115,
            "volatility": 0.12,
            "sharpe": 0.79,
            "solver": "OSQP",
            "status": "optimal",
        },
        "efficient_frontier": [],
        "portfolio_performance": {"summary": {}, "trailing_returns": trailing},
        "benchmark_analytics": {},
        "correlations": {},
        "return_decomposition": {},
        "risk_decomposition": {},
        "_tables": {
            "portfolio_performance": performance_rows,
            "annual_returns": pd.DataFrame(
                [{"year": 2025, "optimized": 0.21, "provided": 0.18, "benchmark": 0.16}]
            ),
            "monthly_returns": pd.DataFrame(
                [{"year": 2025, "Jan": 0.01, "Feb": -0.02, "ytd": -0.0102, "portfolio": "optimized"}]
            ),
            "efficient_frontier": pd.DataFrame(
                [{"point": 1, "expected_return": 0.11, "volatility": 0.12, "sharpe": 0.75, "weight_AAA": 0.7, "weight_BBB": 0.3}]
            ),
            "risk_decomposition": pd.DataFrame(
                [{"asset": "AAA", "optimized": 0.65, "provided": 0.55}, {"asset": "BBB", "optimized": 0.35, "provided": 0.45}]
            ),
            "return_decomposition": pd.DataFrame(
                [{"asset": "AAA", "optimized": 0.60, "provided": 0.50}, {"asset": "BBB", "optimized": 0.40, "provided": 0.30}]
            ),
            "benchmark_analytics": pd.DataFrame(
                [
                    {"portfolio": "optimized", "active_return": 0.02, "tracking_error": 0.05, "information_ratio": 0.4},
                    {"portfolio": "provided", "active_return": 0.01, "tracking_error": 0.06, "information_ratio": 0.1667},
                ]
            ),
        },
    }


def test_review_layer_contains_purpose_built_summary_tables(tmp_path: Path):
    write_analysis_run(_representative_result(), tmp_path)
    review = tmp_path / "review"

    required = {
        "optimization_results.csv",
        "performance_summary.csv",
        "trailing_returns.csv",
        "annual_returns.csv",
        "monthly_returns_calendar.csv",
        "risk_decomposition.csv",
        "return_decomposition.csv",
        "benchmark_summary.csv",
        "efficient_frontier.csv",
    }
    assert required <= {path.name for path in review.glob("*.csv")}


def test_optimization_results_is_human_readable_and_percentage_based(tmp_path: Path):
    write_analysis_run(_representative_result(), tmp_path)
    table = pd.read_csv(tmp_path / "review" / "optimization_results.csv")

    assert list(table.columns) == [
        "ticker",
        "name",
        "min_weight_pct",
        "max_weight_pct",
        "provided_weight_pct",
        "optimized_weight_pct",
    ]
    aaa = table.set_index("ticker").loc["AAA"]
    assert aaa["max_weight_pct"] == pytest.approx(80.0)
    assert aaa["provided_weight_pct"] == pytest.approx(60.0)
    assert aaa["optimized_weight_pct"] == pytest.approx(70.0)


def test_performance_summary_uses_metric_orientation_and_explicit_units(tmp_path: Path):
    write_analysis_run(_representative_result(), tmp_path)
    table = pd.read_csv(tmp_path / "review" / "performance_summary.csv")

    assert list(table.columns) == ["metric", "unit", "provided", "optimized", "benchmark"]
    rows = table.set_index("metric")
    assert rows.loc["CAGR", "unit"] == "pct"
    assert rows.loc["CAGR", "optimized"] == pytest.approx(10.0)
    assert rows.loc["Annualized Return", "optimized"] == pytest.approx(11.0)
    assert rows.loc["Best Year", "optimized"] == pytest.approx(25.0)
    assert rows.loc["Worst Year", "optimized"] == pytest.approx(-15.0)
    assert rows.loc["Sharpe Ratio (ex-post)", "unit"] == "ratio"
    assert rows.loc["Sharpe Ratio (ex-post)", "optimized"] == pytest.approx(0.75)


def test_trailing_and_period_return_review_tables_use_percentage_points(tmp_path: Path):
    write_analysis_run(_representative_result(), tmp_path)

    trailing = pd.read_csv(tmp_path / "review" / "trailing_returns.csv").set_index("portfolio")
    assert trailing.loc["optimized", "return_3m_pct"] == pytest.approx(3.0)
    assert trailing.loc["optimized", "annualized_3y_pct"] == pytest.approx(10.0)
    assert trailing.loc["optimized", "full_period_cagr_pct"] == pytest.approx(9.5)
    assert trailing.loc["optimized", "volatility_3y_pct"] == pytest.approx(13.0)

    annual = pd.read_csv(tmp_path / "review" / "annual_returns.csv")
    assert list(annual.columns) == [
        "year",
        "optimized_return_pct",
        "provided_return_pct",
        "benchmark_return_pct",
    ]
    assert annual.loc[0, "optimized_return_pct"] == pytest.approx(21.0)

    monthly = pd.read_csv(tmp_path / "review" / "monthly_returns_calendar.csv")
    assert {"Jan_pct", "Feb_pct", "YTD_pct"} <= set(monthly.columns)
    assert monthly.loc[0, "Jan_pct"] == pytest.approx(1.0)
    assert monthly.loc[0, "Feb_pct"] == pytest.approx(-2.0)


def test_decomposition_and_benchmark_review_tables_have_explicit_meaning(tmp_path: Path):
    write_analysis_run(_representative_result(), tmp_path)

    risk = pd.read_csv(tmp_path / "review" / "risk_decomposition.csv")
    assert list(risk.columns) == [
        "ticker",
        "provided_risk_contribution_pct",
        "optimized_risk_contribution_pct",
    ]
    assert risk["optimized_risk_contribution_pct"].sum() == pytest.approx(100.0)

    returns = pd.read_csv(tmp_path / "review" / "return_decomposition.csv")
    assert {"ticker", "provided_contribution", "optimized_contribution", "unit"} <= set(returns.columns)

    benchmark = pd.read_csv(tmp_path / "review" / "benchmark_summary.csv")
    assert list(benchmark.columns) == [
        "portfolio",
        "active_return_pct",
        "tracking_error_pct",
        "information_ratio",
    ]
    assert benchmark.set_index("portfolio").loc["optimized", "active_return_pct"] == pytest.approx(2.0)
