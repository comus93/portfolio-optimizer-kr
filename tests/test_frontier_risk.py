from __future__ import annotations

import math

import pandas as pd

from portfolio_optimizer_kr.analytics.frontier_risk import (
    frontier_risk_overlay,
    underwater_metrics,
)


def test_underwater_metrics_include_depth_and_duration() -> None:
    returns = pd.Series(
        [0.10, -0.10, 0.0, 1.0 / 9.0],
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
    )

    metrics = underwater_metrics(returns)

    assert math.isclose(metrics["maximum_drawdown_pct"], -10.0, abs_tol=1e-10)
    assert math.isclose(metrics["mdd_depth_pct"], 10.0, abs_tol=1e-10)
    assert math.isclose(metrics["tuw_pct"], 50.0, abs_tol=1e-10)
    assert math.isclose(metrics["pain_area_pct_months"], 20.0, abs_tol=1e-10)
    assert math.isclose(metrics["pain_index_pct"], 5.0, abs_tol=1e-10)
    assert metrics["max_underwater_months"] == 2
    assert metrics["observations"] == 4


def test_pain_index_is_normalized_by_full_sample_length() -> None:
    base = pd.Series(
        [0.10, -0.10, 1.0 / 9.0],
        index=pd.date_range("2024-01-31", periods=3, freq="ME"),
    )
    repeated = pd.concat(
        [
            base.reset_index(drop=True),
            base.reset_index(drop=True),
        ],
        ignore_index=True,
    )
    repeated.index = pd.date_range("2024-01-31", periods=6, freq="ME")

    first = underwater_metrics(base)
    second = underwater_metrics(repeated)

    assert math.isclose(first["pain_index_pct"], second["pain_index_pct"], abs_tol=1e-10)
    assert math.isclose(
        second["pain_area_pct_months"],
        first["pain_area_pct_months"] * 2.0,
        abs_tol=1e-10,
    )


def test_frontier_overlay_preserves_frontier_identity_and_adds_deltas() -> None:
    dates = pd.date_range("2024-01-31", periods=6, freq="ME")
    assets = pd.DataFrame(
        {
            "A": [0.02, -0.02, 0.03, 0.01, -0.01, 0.02],
            "B": [0.01, 0.00, 0.01, -0.01, 0.02, 0.00],
        },
        index=dates,
    )
    frontier = pd.DataFrame(
        [
            {
                "point": 1,
                "sharpe": 0.5,
                "expected_return_pct": 5.0,
                "volatility_pct": 6.0,
                "weight_A_pct": 20.0,
                "weight_B_pct": 80.0,
            },
            {
                "point": 2,
                "sharpe": 0.7,
                "expected_return_pct": 6.0,
                "volatility_pct": 7.0,
                "weight_A_pct": 60.0,
                "weight_B_pct": 40.0,
            },
        ]
    )

    result = frontier_risk_overlay(frontier, assets, annual_rf=0.0)

    assert result["point"].tolist() == [1, 2]
    assert result["ex_ante_sharpe"].tolist() == [0.5, 0.7]
    assert math.isnan(result.loc[0, "delta_sharpe"])
    assert math.isfinite(result.loc[1, "delta_sharpe"])
    assert "tuw_cost_per_0_10_sharpe" in result.columns
    assert "pain_cost_per_0_10_sharpe" in result.columns
