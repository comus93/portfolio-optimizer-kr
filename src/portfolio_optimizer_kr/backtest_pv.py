from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from portfolio_optimizer_kr.analytics.pv_metric_parity import apply_pv_metric_parity
from portfolio_optimizer_kr.analytics.pv_metrics import (
    annual_inflation_yoy,
    risk_and_return_metrics_table,
)
from portfolio_optimizer_kr.backtest import analyze_backtest_prices as _base_analyze_backtest_prices
from portfolio_optimizer_kr.models import BacktestRequest


def _series_returns(monthly_series: pd.DataFrame, portfolio_order: list[str]) -> dict[str, pd.Series]:
    if monthly_series.empty or "date" not in monthly_series:
        return {}
    shaped = monthly_series.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).set_index("date").sort_index()
    names = [name for name in portfolio_order if name in shaped.columns]
    if "benchmark" in shaped.columns:
        names.append("benchmark")
    return {
        name: pd.to_numeric(shaped[name], errors="coerce").dropna().rename(name)
        for name in names
    }


def _held_active_contribution(
    frame: pd.DataFrame,
    request: BacktestRequest,
) -> pd.DataFrame:
    if frame.empty or not {"portfolio", "ticker"}.issubset(frame.columns):
        return frame
    held = {
        portfolio.name: {
            str(ticker)
            for ticker, weight in portfolio.target_weights.items()
            if abs(float(weight)) > 1e-12
        }
        for portfolio in request.portfolios
    }
    mask = frame.apply(
        lambda row: str(row["ticker"]) in held.get(str(row["portfolio"]), set()),
        axis=1,
    )
    return frame.loc[mask].reset_index(drop=True)


def _growth_lookup(growth: pd.DataFrame) -> pd.DataFrame:
    if growth.empty or "date" not in growth:
        return pd.DataFrame()
    shaped = growth.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    return shaped.dropna(subset=["date"]).sort_values("date")


def _annual_detail_table(
    monthly_series: pd.DataFrame,
    growth: pd.DataFrame,
    request: BacktestRequest,
    inflation_index: pd.Series | None,
) -> pd.DataFrame:
    if monthly_series.empty or "date" not in monthly_series:
        return pd.DataFrame()
    shaped = monthly_series.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    growth_frame = _growth_lookup(growth)
    inflation = annual_inflation_yoy(inflation_index)
    assets = [asset.symbol for asset in request.assets]
    series_names = [portfolio.name for portfolio in request.portfolios]
    if "benchmark" in shaped.columns:
        series_names.append("benchmark")

    rows: list[dict[str, object]] = []
    for year, part in shaped.groupby(shaped["date"].dt.year):
        row: dict[str, object] = {
            "year": int(year),
            "inflation": inflation.get(int(year)),
        }
        for name in series_names:
            if name not in part:
                continue
            values = pd.to_numeric(part[name], errors="coerce").dropna()
            row[f"series::{name}::return"] = (
                float((1.0 + values).prod() - 1.0) if not values.empty else None
            )
            balance_col = f"{name}_balance"
            if balance_col in growth_frame:
                balance_part = growth_frame[
                    growth_frame["date"].dt.year == int(year)
                ]
                balance_values = pd.to_numeric(
                    balance_part[balance_col], errors="coerce"
                ).dropna()
                row[f"series::{name}::balance"] = (
                    float(balance_values.iloc[-1]) if not balance_values.empty else None
                )
        for ticker in assets:
            column = f"asset_{ticker}"
            if column not in part:
                continue
            values = pd.to_numeric(part[column], errors="coerce").dropna()
            row[f"asset::{ticker}::return"] = (
                float((1.0 + values).prod() - 1.0) if not values.empty else None
            )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("year", ascending=False).reset_index(drop=True)


def _monthly_detail_table(
    monthly_series: pd.DataFrame,
    growth: pd.DataFrame,
    request: BacktestRequest,
) -> pd.DataFrame:
    if monthly_series.empty or "date" not in monthly_series:
        return pd.DataFrame()
    shaped = monthly_series.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    growth_frame = _growth_lookup(growth)
    merged = shaped.merge(growth_frame, on="date", how="left") if not growth_frame.empty else shaped
    assets = [asset.symbol for asset in request.assets]
    series_names = [portfolio.name for portfolio in request.portfolios]
    if "benchmark" in merged.columns:
        series_names.append("benchmark")

    rows: list[dict[str, object]] = []
    for _, source in merged.sort_values("date", ascending=False).iterrows():
        date = pd.Timestamp(source["date"])
        row: dict[str, object] = {
            "date": date,
            "year": int(date.year),
            "month": int(date.month),
        }
        for name in series_names:
            row[f"series::{name}::return"] = source.get(name)
            row[f"series::{name}::balance"] = source.get(f"{name}_balance")
        for ticker in assets:
            row[f"asset::{ticker}::return"] = source.get(f"asset_{ticker}")
        rows.append(row)
    return pd.DataFrame(rows)


def analyze_backtest_prices(
    request: BacktestRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
    annual_rf: float | None = None,
    inflation_series: pd.Series | None = None,
) -> dict[str, Any]:
    result = _base_analyze_backtest_prices(
        request,
        prices,
        usdkrw=usdkrw,
        annual_rf=annual_rf,
    )
    tables = result.get("_tables")
    if not isinstance(tables, dict):
        return result

    monthly_series = tables.get("monthly_return_series", pd.DataFrame())
    growth = tables.get("portfolio_growth", pd.DataFrame())
    portfolio_order = [portfolio.name for portfolio in request.portfolios]
    series_returns = _series_returns(monthly_series, portfolio_order)
    benchmark = series_returns.get("benchmark")
    if benchmark is not None and annual_rf is not None:
        metrics = risk_and_return_metrics_table(
            series_returns,
            benchmark,
            float(annual_rf),
            inflation_index=inflation_series,
        )
        tables["risk_and_return_metrics"] = apply_pv_metric_parity(
            metrics,
            series_returns,
            benchmark,
            float(annual_rf),
            inflation_series,
        )

    tables["annual_returns_detail"] = _annual_detail_table(
        monthly_series,
        growth,
        request,
        inflation_series,
    )
    tables["monthly_returns_detail"] = _monthly_detail_table(
        monthly_series,
        growth,
        request,
    )
    contribution = tables.get("active_return_contribution", pd.DataFrame())
    tables["active_return_contribution"] = _held_active_contribution(
        contribution,
        request,
    )

    if inflation_series is not None and not inflation_series.dropna().empty:
        observed = inflation_series.dropna()
        result["inflation"] = {
            "source": "FRED:CPIAUCSL",
            "start": str(pd.Timestamp(observed.index.min()).date()),
            "end": str(pd.Timestamp(observed.index.max()).date()),
            "annual_yoy": annual_inflation_yoy(inflation_series),
        }
    return result
