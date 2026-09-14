from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from portfolio_optimizer_kr.errors import InfeasibleOptimizationError
from portfolio_optimizer_kr.models import OptimizationRequest
from portfolio_optimizer_kr.stats import annualized_statistics

from .engine import solve_optimization


def _baseline_weights(result: Mapping[str, Any], symbols: list[str]) -> pd.Series:
    payload = result.get("optimization_result")
    if not isinstance(payload, Mapping):
        raise ValueError("optimization_result is required for LOYO robustness")
    weights = payload.get("weights")
    if not isinstance(weights, Mapping):
        raise ValueError("optimization_result.weights is required for LOYO robustness")
    out = pd.Series({symbol: float(weights[symbol]) for symbol in symbols}, dtype=float)
    return out.reindex(symbols)


def _baseline_metrics(result: Mapping[str, Any]) -> dict[str, float]:
    payload = result.get("optimization_result")
    if not isinstance(payload, Mapping):
        raise ValueError("optimization_result is required for LOYO robustness")
    return {
        "expected_return": float(payload["expected_return"]),
        "volatility": float(payload["volatility"]),
        "sharpe": float(payload["sharpe"]),
    }


def analyze_loyo_robustness(
    request: OptimizationRequest,
    monthly_returns: pd.DataFrame,
    baseline_result: Mapping[str, Any],
    *,
    annual_rf: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Measure one-calendar-year-out sensitivity using the shared optimizer.

    The baseline result is reused rather than solved again. Each scenario only
    rebuilds annualized moments from the year-excluded monthly return sample and
    calls the canonical objective-solving boundary. Frontier generation,
    portfolio simulation, historical analytics, market-data acquisition and
    rendering are intentionally outside this function.
    """
    if monthly_returns.empty:
        raise ValueError("monthly_returns cannot be empty for LOYO robustness")

    symbols = list(monthly_returns.columns)
    baseline_weights = _baseline_weights(baseline_result, symbols)
    baseline_metrics = _baseline_metrics(baseline_result)
    bounds = {
        asset.symbol: (asset.min_weight, asset.max_weight)
        for asset in request.assets
    }

    index = pd.DatetimeIndex(monthly_returns.index)
    years = sorted({int(year) for year in index.year})
    rows: list[dict[str, Any]] = []

    for year in years:
        excluded_mask = index.year == year
        removed = monthly_returns.loc[excluded_mask]
        remaining = monthly_returns.loc[~excluded_mask]
        row: dict[str, Any] = {
            "excluded_year": year,
            "removed_observations": int(len(removed)),
            "remaining_observations": int(len(remaining)),
            "removed_start": (
                str(pd.DatetimeIndex(removed.index).min().date())
                if not removed.empty
                else None
            ),
            "removed_end": (
                str(pd.DatetimeIndex(removed.index).max().date())
                if not removed.empty
                else None
            ),
            "feasible": False,
            "status": "insufficient_data" if len(remaining) < 2 else "pending",
            "solver": None,
            "expected_return": None,
            "volatility": None,
            "sharpe": None,
            "delta_expected_return": None,
            "delta_volatility": None,
            "delta_sharpe": None,
            "allocation_turnover": None,
            "max_abs_weight_change": None,
            "most_changed_asset": None,
            "message": None,
        }
        for symbol in symbols:
            row[f"weight_{symbol}"] = None
            row[f"delta_weight_{symbol}"] = None

        if len(remaining) < 2:
            row["message"] = "fewer than two monthly observations remain"
            rows.append(row)
            continue

        stats = annualized_statistics(remaining)
        try:
            optimized = solve_optimization(
                request.objective,
                stats.expected_returns,
                stats.covariance,
                bounds=bounds,
                annual_rf=float(annual_rf),
                target_volatility=request.target_volatility,
            )
        except InfeasibleOptimizationError as exc:
            row["status"] = "infeasible"
            row["message"] = str(exc)
            rows.append(row)
            continue

        weights = optimized.weights.reindex(symbols).astype(float)
        delta = weights - baseline_weights
        absolute_delta = delta.abs()
        most_changed_asset = str(absolute_delta.idxmax())

        row.update(
            {
                "feasible": True,
                "status": str(optimized.status),
                "solver": optimized.solver,
                "expected_return": float(optimized.expected_return),
                "volatility": float(optimized.volatility),
                "sharpe": float(optimized.sharpe),
                "delta_expected_return": float(
                    optimized.expected_return - baseline_metrics["expected_return"]
                ),
                "delta_volatility": float(
                    optimized.volatility - baseline_metrics["volatility"]
                ),
                "delta_sharpe": float(
                    optimized.sharpe - baseline_metrics["sharpe"]
                ),
                "allocation_turnover": float(0.5 * absolute_delta.sum()),
                "max_abs_weight_change": float(absolute_delta.max()),
                "most_changed_asset": most_changed_asset,
            }
        )
        for symbol in symbols:
            row[f"weight_{symbol}"] = float(weights[symbol])
            row[f"delta_weight_{symbol}"] = float(delta[symbol])
        rows.append(row)

    table = pd.DataFrame(rows)
    feasible_rows = table.loc[table["feasible"] == True] if not table.empty else table  # noqa: E712
    most_influential_year = None
    if not feasible_rows.empty:
        most_influential_year = int(
            feasible_rows.sort_values(
                ["allocation_turnover", "excluded_year"],
                ascending=[False, True],
            ).iloc[0]["excluded_year"]
        )

    robustness = {
        "method": "leave_one_calendar_year_out",
        "effective_annual_risk_free_rate": float(annual_rf),
        "baseline": {
            "weights": baseline_weights.to_dict(),
            **baseline_metrics,
        },
        "scenario_count": int(len(table)),
        "feasible_scenario_count": int(table["feasible"].sum()) if not table.empty else 0,
        "infeasible_years": (
            [
                int(value)
                for value in table.loc[table["status"] == "infeasible", "excluded_year"]
            ]
            if not table.empty
            else []
        ),
        "insufficient_data_years": (
            [
                int(value)
                for value in table.loc[
                    table["status"] == "insufficient_data", "excluded_year"
                ]
            ]
            if not table.empty
            else []
        ),
        "most_influential_year_by_allocation": most_influential_year,
        "scenarios": table.to_dict(orient="records"),
    }
    return robustness, table


def attach_loyo_robustness(
    result: dict[str, Any],
    request: OptimizationRequest,
    monthly_returns: pd.DataFrame,
    *,
    annual_rf: float,
) -> dict[str, Any]:
    """Attach canonical LOYO JSON and its persisted table to an Optimization result."""
    robustness, table = analyze_loyo_robustness(
        request,
        monthly_returns,
        result,
        annual_rf=annual_rf,
    )
    result["optimization_robustness"] = {"loyo": robustness}
    tables = result.setdefault("_tables", {})
    if not isinstance(tables, dict):
        raise ValueError("result._tables must be a mapping")
    tables["loyo_robustness"] = table
    return result
