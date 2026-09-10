from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.portfolio import build_portfolio_path


UNDERWATER_EPSILON = 1e-12


def underwater_metrics(
    monthly_returns: pd.Series,
    *,
    epsilon: float = UNDERWATER_EPSILON,
) -> dict[str, float | int]:
    """Return realized drawdown-duration metrics for a monthly return path.

    Pain Area is the discrete area under the monthly underwater curve in
    percentage-point months. Pain Index normalizes that area by the full
    observation count, so peak months with zero drawdown remain in the
    denominator and duration is retained in the metric.
    """
    clean = monthly_returns.dropna().astype(float)
    if clean.empty:
        raise ValueError("monthly returns are empty")

    wealth = (1.0 + clean).cumprod()
    drawdown = wealth.div(wealth.cummax()).sub(1.0)
    underwater_depth = (-drawdown).clip(lower=0.0)
    underwater_mask = drawdown < -float(epsilon)

    longest = 0
    current = 0
    for is_underwater in underwater_mask.to_numpy(dtype=bool):
        if is_underwater:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    pain_area_pct_months = float(underwater_depth.sum() * 100.0)
    return {
        "maximum_drawdown_pct": float(drawdown.min() * 100.0),
        "mdd_depth_pct": float(underwater_depth.max() * 100.0),
        "tuw_pct": float(underwater_mask.mean() * 100.0),
        "pain_area_pct_months": pain_area_pct_months,
        "pain_index_pct": float(pain_area_pct_months / len(clean)),
        "max_underwater_months": int(longest),
        "observations": int(len(clean)),
    }


def _ex_post_sharpe(monthly_returns: pd.Series, annual_rf: float) -> float:
    clean = monthly_returns.dropna().astype(float)
    annualized_return = float(clean.mean() * 12.0)
    annualized_volatility = float(clean.std(ddof=1) * np.sqrt(12.0))
    if annualized_volatility <= 0.0:
        return float("nan")
    return float((annualized_return - float(annual_rf)) / annualized_volatility)


def frontier_risk_overlay(
    frontier: pd.DataFrame,
    monthly_asset_returns: pd.DataFrame,
    *,
    rebalancing: str = "monthly",
    annual_rf: float = 0.0,
    epsilon: float = UNDERWATER_EPSILON,
) -> pd.DataFrame:
    """Overlay realized drawdown-duration risk on persisted frontier points.

    `frontier` weights and ex-ante statistics are treated as immutable inputs.
    The function only appends realized-path analytics and descriptive deltas.
    """
    if frontier.empty:
        raise ValueError("frontier is empty")
    if monthly_asset_returns.empty:
        raise ValueError("monthly asset returns are empty")

    symbols = list(monthly_asset_returns.columns)
    weight_columns = {symbol: f"weight_{symbol}_pct" for symbol in symbols}
    missing = [column for column in weight_columns.values() if column not in frontier.columns]
    if missing:
        raise ValueError(f"frontier is missing weight columns: {missing}")

    rows: list[dict[str, float | int]] = []
    for _, source in frontier.sort_values("point").iterrows():
        weights: Mapping[str, float] = {
            symbol: float(source[column]) / 100.0
            for symbol, column in weight_columns.items()
        }
        path = build_portfolio_path(
            monthly_asset_returns,
            weights,
            rebalancing,
        )
        risk = underwater_metrics(path.returns, epsilon=epsilon)
        rows.append(
            {
                "point": int(source["point"]),
                "ex_ante_sharpe": float(source["sharpe"]),
                "ex_post_sharpe": _ex_post_sharpe(path.returns, annual_rf),
                "expected_return_pct": float(source["expected_return_pct"]),
                "volatility_pct": float(source["volatility_pct"]),
                **risk,
            }
        )

    result = pd.DataFrame(rows).sort_values("point").reset_index(drop=True)
    result["delta_sharpe"] = result["ex_post_sharpe"].diff()
    result["delta_mdd_depth_pct"] = result["mdd_depth_pct"].diff()
    result["delta_tuw_pct"] = result["tuw_pct"].diff()
    result["delta_pain_index_pct"] = result["pain_index_pct"].diff()

    increasing = result["delta_sharpe"] > float(epsilon)
    scale = 0.10 / result["delta_sharpe"].where(increasing)
    result["mdd_cost_per_0_10_sharpe"] = result["delta_mdd_depth_pct"] * scale
    result["tuw_cost_per_0_10_sharpe"] = result["delta_tuw_pct"] * scale
    result["pain_cost_per_0_10_sharpe"] = result["delta_pain_index_pct"] * scale

    max_sharpe_index = result["ex_post_sharpe"].idxmax()
    max_sharpe_point = int(result.loc[max_sharpe_index, "point"])
    result["segment"] = np.where(
        result["point"] <= max_sharpe_point,
        "gmv_to_max_sharpe",
        "post_max_sharpe",
    )
    return result
