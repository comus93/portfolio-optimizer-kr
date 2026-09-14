from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer_kr.config import RunConfig
from portfolio_optimizer_kr.errors import InfeasibleOptimizationError
from portfolio_optimizer_kr.models import (
    AssetSpec,
    OptimizationObjective,
    OptimizationRequest,
    OptimizationResult,
    ProductMode,
    RiskFreeConfig,
    RiskFreeMode,
)
from portfolio_optimizer_kr.optimize.engine import solve_optimization
from portfolio_optimizer_kr.optimize.robustness import (
    analyze_loyo_robustness,
    attach_loyo_robustness,
)
from portfolio_optimizer_kr.report import write_analysis_run
from portfolio_optimizer_kr.runner import execute_run
from portfolio_optimizer_kr.stats import annualized_statistics


def _monthly_returns(start: str = "2020-01-31", periods: int = 36) -> pd.DataFrame:
    rng = np.random.default_rng(20260914)
    values = rng.normal(
        loc=np.array([0.020, 0.012]),
        scale=np.array([0.015, 0.010]),
        size=(periods, 2),
    )
    return pd.DataFrame(
        values,
        index=pd.date_range(start, periods=periods, freq="ME"),
        columns=["A", "B"],
    )


def _request(**kwargs) -> OptimizationRequest:
    return OptimizationRequest(
        assets=(
            AssetSpec("A", "Asset A", min_weight=0.0, max_weight=1.0),
            AssetSpec("B", "Asset B", min_weight=0.0, max_weight=1.0),
        ),
        objective=OptimizationObjective.MAX_SHARPE,
        risk_free=RiskFreeConfig(RiskFreeMode.FIXED, 0.0),
        frontier_points=5,
        **kwargs,
    )


def _baseline_result(request: OptimizationRequest, returns: pd.DataFrame) -> dict:
    stats = annualized_statistics(returns)
    bounds = {
        asset.symbol: (asset.min_weight, asset.max_weight)
        for asset in request.assets
    }
    optimized = solve_optimization(
        request.objective,
        stats.expected_returns,
        stats.covariance,
        bounds=bounds,
        annual_rf=0.0,
        target_volatility=request.target_volatility,
    )
    return {
        "optimization_result": {
            "weights": optimized.weights.to_dict(),
            "expected_return": optimized.expected_return,
            "volatility": optimized.volatility,
            "sharpe": optimized.sharpe,
            "solver": optimized.solver,
            "status": optimized.status,
        },
        "_tables": {},
    }


def test_loyo_reoptimizes_each_calendar_year_and_turnover_matches_weight_deltas():
    returns = _monthly_returns()
    request = _request()
    baseline = _baseline_result(request, returns)

    robustness, table = analyze_loyo_robustness(
        request,
        returns,
        baseline,
        annual_rf=0.0,
    )

    assert robustness["scenario_count"] == 3
    assert robustness["feasible_scenario_count"] == 3
    assert table["excluded_year"].tolist() == [2020, 2021, 2022]
    assert table["removed_observations"].tolist() == [12, 12, 12]

    first = table.iloc[0]
    expected_turnover = 0.5 * (
        abs(first["delta_weight_A"]) + abs(first["delta_weight_B"])
    )
    assert first["allocation_turnover"] == pytest.approx(expected_turnover)
    assert first["max_abs_weight_change"] == pytest.approx(
        max(abs(first["delta_weight_A"]), abs(first["delta_weight_B"]))
    )
    assert first["most_changed_asset"] in {"A", "B"}


def test_loyo_records_partial_calendar_year_observation_count():
    returns = _monthly_returns(start="2020-11-30", periods=26)
    request = _request()
    baseline = _baseline_result(request, returns)

    _, table = analyze_loyo_robustness(
        request,
        returns,
        baseline,
        annual_rf=0.0,
    )

    assert table["excluded_year"].tolist() == [2020, 2021, 2022]
    assert table["removed_observations"].tolist() == [2, 12, 12]
    assert table.iloc[0]["removed_start"] == "2020-11-30"
    assert table.iloc[0]["removed_end"] == "2020-12-31"


def test_loyo_infeasible_scenario_is_recorded_without_failing_run(monkeypatch):
    returns = _monthly_returns(periods=24)
    request = _request()
    baseline = _baseline_result(request, returns)
    calls = []

    def fake_solve(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise InfeasibleOptimizationError("synthetic infeasible scenario")
        return OptimizationResult(
            weights=pd.Series({"A": 0.6, "B": 0.4}),
            expected_return=0.1,
            volatility=0.12,
            sharpe=0.8,
            solver="OSQP",
            status="optimal",
        )

    monkeypatch.setattr(
        "portfolio_optimizer_kr.optimize.robustness.solve_optimization",
        fake_solve,
    )

    robustness, table = analyze_loyo_robustness(
        request,
        returns,
        baseline,
        annual_rf=0.0,
    )

    assert len(calls) == 2  # one solve per year; baseline is not re-solved
    assert table.iloc[0]["feasible"] == False  # noqa: E712
    assert table.iloc[0]["status"] == "infeasible"
    assert "synthetic infeasible" in table.iloc[0]["message"]
    assert table.iloc[1]["feasible"] == True  # noqa: E712
    assert robustness["infeasible_years"] == [2020]


def test_attach_loyo_persists_canonical_and_csv_artifacts(tmp_path):
    returns = _monthly_returns()
    request = _request()
    result = _baseline_result(request, returns)
    result.update(
        {
            "configuration": {"run_id": "loyo-artifact", "assets": []},
            "data_coverage": {},
            "asset_statistics": {},
            "efficient_frontier": [],
            "portfolio_performance": {},
            "benchmark_analytics": {},
            "correlations": {},
            "return_decomposition": {},
            "risk_decomposition": {},
        }
    )

    attach_loyo_robustness(
        result,
        request,
        returns,
        annual_rf=0.0,
    )
    write_analysis_run(result, tmp_path)

    payload = json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert payload["optimization_robustness"]["loyo"]["scenario_count"] == 3
    assert (tmp_path / "raw" / "loyo_robustness.csv").is_file()
    assert (tmp_path / "review" / "loyo_robustness.csv").is_file()


class _PriceLoader:
    def __init__(self, prices: dict[str, pd.Series]):
        self.prices = prices

    def load_many(self, assets, start=None, end=None):
        return {asset.symbol: self.prices[asset.symbol] for asset in assets}


def test_default_optimization_execute_run_attaches_loyo(tmp_path):
    returns = _monthly_returns(start="2020-01-31", periods=36)
    price_index = pd.date_range("2019-12-31", periods=37, freq="ME")
    prices = {}
    for symbol in returns.columns:
        values = np.concatenate(
            [[100.0], 100.0 * np.cumprod(1.0 + returns[symbol].to_numpy())]
        )
        prices[symbol] = pd.Series(values, index=price_index, name=symbol)

    request = _request(
        run_id="loyo-runner",
        start="2020-01-01",
        end="2022-12-31",
    )
    spec = RunConfig(request=request, product_mode=ProductMode.OPTIMIZATION)

    output = execute_run(
        spec,
        tmp_path,
        loader=_PriceLoader(prices),
    )

    payload = json.loads((output / "result.json").read_text(encoding="utf-8"))
    assert payload["optimization_robustness"]["loyo"]["scenario_count"] == 3
    assert (output / "raw" / "loyo_robustness.csv").is_file()
