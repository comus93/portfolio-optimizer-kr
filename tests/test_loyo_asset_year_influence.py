from __future__ import annotations

import pandas as pd
import pytest

from portfolio_optimizer_kr.models import (
    AssetSpec,
    OptimizationObjective,
    OptimizationRequest,
    RiskFreeConfig,
    RiskFreeMode,
)
from portfolio_optimizer_kr.optimize.robustness import (
    attach_loyo_robustness,
    build_asset_year_influence_table,
)
from portfolio_optimizer_kr.report import write_analysis_run
from portfolio_optimizer_kr.report.loyo import asset_year_influence_review_table
from portfolio_optimizer_kr.stats import annualized_statistics
from portfolio_optimizer_kr.optimize.engine import solve_optimization


def _request() -> OptimizationRequest:
    return OptimizationRequest(
        assets=(AssetSpec("A", "Asset A"), AssetSpec("B", "Asset B")),
        objective=OptimizationObjective.MAX_SHARPE,
        risk_free=RiskFreeConfig(RiskFreeMode.FIXED, 0.0),
        frontier_points=3,
    )


def test_asset_year_influence_is_projection_of_existing_values():
    baseline = {
        "optimization_result": {
            "weights": {"A": 0.30, "B": 0.70},
        }
    }
    annual = pd.DataFrame(
        [
            {"year": 2022, "ticker": "A", "return": -0.25},
            {"year": 2022, "ticker": "B", "return": 0.10},
        ]
    )
    loyo = pd.DataFrame(
        [
            {
                "excluded_year": 2022,
                "status": "optimal",
                "weight_A": 0.50,
                "delta_weight_A": 0.20,
                "weight_B": 0.50,
                "delta_weight_B": -0.20,
            }
        ]
    )

    table = build_asset_year_influence_table(baseline, annual, loyo)

    assert table.to_dict(orient="records") == [
        {
            "year": 2022,
            "ticker": "A",
            "asset_annual_return": -0.25,
            "baseline_weight": 0.30,
            "excluded_year_weight": 0.50,
            "delta_weight": 0.20,
            "status": "optimal",
        },
        {
            "year": 2022,
            "ticker": "B",
            "asset_annual_return": 0.10,
            "baseline_weight": 0.70,
            "excluded_year_weight": 0.50,
            "delta_weight": -0.20,
            "status": "optimal",
        },
    ]


def test_asset_year_influence_preserves_unavailable_loyo_values():
    baseline = {"optimization_result": {"weights": {"A": 1.0}}}
    annual = pd.DataFrame([{"year": 2022, "ticker": "A", "return": -0.25}])
    loyo = pd.DataFrame(
        [
            {
                "excluded_year": 2022,
                "status": "infeasible",
                "weight_A": None,
                "delta_weight_A": None,
            }
        ]
    )

    row = build_asset_year_influence_table(baseline, annual, loyo).iloc[0]

    assert row["asset_annual_return"] == pytest.approx(-0.25)
    assert row["baseline_weight"] == pytest.approx(1.0)
    assert pd.isna(row["excluded_year_weight"])
    assert pd.isna(row["delta_weight"])
    assert row["status"] == "infeasible"


def test_asset_year_review_projection_uses_percentage_point_units():
    raw = pd.DataFrame(
        [
            {
                "year": 2022,
                "ticker": "QQQ",
                "asset_annual_return": -0.278234,
                "baseline_weight": 0.310628,
                "excluded_year_weight": 0.569341,
                "delta_weight": 0.258713,
                "status": "optimal",
            }
        ]
    )

    review = asset_year_influence_review_table(raw)

    assert "asset_annual_return" not in review
    assert review.iloc[0]["asset_annual_return_pct"] == pytest.approx(-27.8234)
    assert review.iloc[0]["baseline_weight_pct"] == pytest.approx(31.0628)
    assert review.iloc[0]["excluded_year_weight_pct"] == pytest.approx(56.9341)
    assert review.iloc[0]["delta_weight_pct"] == pytest.approx(25.8713)


def test_attach_reuses_existing_annual_asset_return_table_and_persists_review_units(tmp_path):
    returns = pd.DataFrame(
        {
            "A": [0.03, -0.02, 0.04, 0.01] * 6,
            "B": [0.01, 0.02, -0.01, 0.015] * 6,
        },
        index=pd.date_range("2021-01-31", periods=24, freq="ME"),
    )
    request = _request()
    stats = annualized_statistics(returns)
    optimized = solve_optimization(
        request.objective,
        stats.expected_returns,
        stats.covariance,
        bounds={"A": (0.0, 1.0), "B": (0.0, 1.0)},
        annual_rf=0.0,
    )
    annual = pd.DataFrame(
        [
            {"year": int(year), "ticker": ticker, "return": float(value)}
            for ticker in returns.columns
            for year, value in (
                (1.0 + returns[ticker]).groupby(returns.index.year).prod() - 1.0
            ).items()
        ]
    )
    result = {
        "configuration": {
            "run_id": "asset-year-influence",
            "assets": [
                {"symbol": "A", "name": "Asset A", "min_weight": 0.0, "max_weight": 1.0},
                {"symbol": "B", "name": "Asset B", "min_weight": 0.0, "max_weight": 1.0},
            ],
        },
        "data_coverage": {},
        "asset_statistics": {},
        "optimization_result": {
            "weights": optimized.weights.to_dict(),
            "expected_return": optimized.expected_return,
            "volatility": optimized.volatility,
            "sharpe": optimized.sharpe,
            "solver": optimized.solver,
            "status": optimized.status,
        },
        "efficient_frontier": [],
        "portfolio_performance": {},
        "benchmark_analytics": {},
        "correlations": {},
        "return_decomposition": {},
        "risk_decomposition": {},
        "_tables": {"annual_asset_returns": annual},
    }

    attach_loyo_robustness(result, request, returns, annual_rf=0.0)

    influence = result["_tables"]["asset_year_influence"]
    assert len(influence) == 4
    assert set(influence.columns) == {
        "year",
        "ticker",
        "asset_annual_return",
        "baseline_weight",
        "excluded_year_weight",
        "delta_weight",
        "status",
    }

    write_analysis_run(result, tmp_path)
    raw = pd.read_csv(tmp_path / "raw" / "asset_year_influence.csv")
    review = pd.read_csv(tmp_path / "review" / "asset_year_influence.csv")

    assert raw["baseline_weight"].abs().max() <= 1.0 + 1e-9
    assert "baseline_weight_pct" in review
    assert "asset_annual_return_pct" in review
    assert review["baseline_weight_pct"].abs().max() > 1.0
