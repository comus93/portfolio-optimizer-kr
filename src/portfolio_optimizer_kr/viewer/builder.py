from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml

from .loader import RunArtifacts, load_run_artifacts
from .report_model import (
    ActiveContributionPoint,
    AnnualizedActiveReturnPoint,
    AnnualAssetReturnPoint,
    AnnualReturnPoint,
    DrawdownPoint,
    FrontierAssetPoint,
    FrontierLandmark,
    FrontierPoint,
    PortfolioGrowthPoint,
    ReportModel,
    RollingActivePoint,
    RollingReturnPoint,
    UpDownMarketPoint,
    UpDownScatterPoint,
)


def _clean_scalar(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value.item() if hasattr(value, "item") else value


def _records(frame: pd.DataFrame) -> tuple[dict[str, Any], ...]:
    return tuple(
        {str(key): _clean_scalar(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    )


def _load_input(run_dir: Path) -> Mapping[str, Any]:
    path = run_dir / "input.yaml"
    if not path.is_file():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, Mapping) else {}


def _objective_name(config: Mapping[str, Any]) -> str:
    optimization = config.get("optimization")
    optimization = optimization if isinstance(optimization, Mapping) else {}
    objective = str(optimization.get("objective") or "max_sharpe")
    if objective == "max_sharpe":
        return "Maximum Sharpe Ratio"
    if objective == "target_volatility":
        target = optimization.get("target_volatility_pct")
        if target is None:
            return "Maximum Return at Target Volatility"
        return f"Maximum Return at {float(target):g}% Target Volatility"
    return objective


def _benchmark(config: Mapping[str, Any]) -> tuple[str | None, str | None]:
    raw = config.get("benchmark")
    if isinstance(raw, str):
        return raw.strip() or None, None
    if isinstance(raw, Mapping):
        symbol = str(raw.get("symbol") or "").strip() or None
        name = str(raw.get("name") or "").strip() or None
        return symbol, name
    return None, None


def _required_float(row: Any, field: str) -> float:
    if not hasattr(row, field):
        raise ValueError(f"missing required report field: {field}")
    value = getattr(row, field)
    if value is None or pd.isna(value):
        raise ValueError(f"missing required report value: {field}")
    return float(value)


def _frontier(frame: pd.DataFrame | None) -> tuple[FrontierPoint, ...]:
    if frame is None:
        return ()
    weight_columns = [
        column
        for column in frame.columns
        if column.startswith("weight_") and column.endswith("_pct")
    ]
    points: list[FrontierPoint] = []
    for row in frame.to_dict(orient="records"):
        weights = {
            column[len("weight_") : -len("_pct")]: float(row[column])
            for column in weight_columns
            if _clean_scalar(row.get(column)) is not None
        }
        points.append(
            FrontierPoint(
                volatility_pct=float(row["volatility_pct"]),
                expected_return_pct=float(row["expected_return_pct"]),
                sharpe_ratio=float(row["sharpe"]),
                weights_pct=weights,
            )
        )
    return tuple(points)


def _annual_returns(frame: pd.DataFrame | None) -> tuple[AnnualReturnPoint, ...]:
    if frame is None:
        return ()
    return tuple(
        AnnualReturnPoint(
            year=int(row.year),
            provided_return_pct=_required_float(row, "provided_return_pct"),
            optimized_return_pct=_required_float(row, "optimized_return_pct"),
            benchmark_return_pct=(
                None
                if not hasattr(row, "benchmark_return_pct")
                or pd.isna(row.benchmark_return_pct)
                else float(row.benchmark_return_pct)
            ),
        )
        for row in frame.itertuples(index=False)
    )


def _portfolio_growth(frame: pd.DataFrame | None) -> tuple[PortfolioGrowthPoint, ...]:
    if frame is None:
        return ()
    return tuple(
        PortfolioGrowthPoint(
            date=str(row.date),
            provided_balance=_required_float(row, "provided_balance"),
            optimized_balance=_required_float(row, "optimized_balance"),
            benchmark_balance=(
                None
                if not hasattr(row, "benchmark_balance")
                or pd.isna(row.benchmark_balance)
                else float(row.benchmark_balance)
            ),
        )
        for row in frame.itertuples(index=False)
    )


def _annualized_active_returns(
    frame: pd.DataFrame | None,
) -> tuple[AnnualizedActiveReturnPoint, ...]:
    if frame is None:
        return ()
    by_year: dict[int, dict[str, float]] = defaultdict(dict)
    for row in frame.itertuples(index=False):
        value = getattr(row, "annual_active_return_pct", None)
        if value is None or pd.isna(value):
            continue
        portfolio = str(row.portfolio)
        year = int(pd.Timestamp(row.date).year)
        numeric = float(value)
        previous = by_year[year].get(portfolio)
        if previous is not None and abs(previous - numeric) > 1e-9:
            raise ValueError(
                f"conflicting annual active return values for {portfolio} in {year}"
            )
        by_year[year][portfolio] = numeric
    return tuple(
        AnnualizedActiveReturnPoint(
            year=year,
            provided_active_return_pct=values["provided"],
            optimized_active_return_pct=values["optimized"],
        )
        for year, values in sorted(by_year.items())
        if "provided" in values and "optimized" in values
    )


def _rolling_active(
    frame: pd.DataFrame | None, portfolio: str
) -> tuple[RollingActivePoint, ...]:
    if frame is None:
        return ()
    points: list[RollingActivePoint] = []
    for row in frame.itertuples(index=False):
        if str(row.portfolio) != portfolio:
            continue
        active = getattr(row, "rolling_active_return_pct", None)
        tracking = getattr(row, "rolling_tracking_error_pct", None)
        if active is None or tracking is None or pd.isna(active) or pd.isna(tracking):
            continue
        points.append(
            RollingActivePoint(
                date=str(row.date),
                active_return_pct=float(active),
                tracking_error_pct=float(tracking),
            )
        )
    return tuple(points)


def _drawdowns(frame: pd.DataFrame | None) -> tuple[DrawdownPoint, ...]:
    if frame is None:
        return ()
    return tuple(
        DrawdownPoint(
            date=str(row.date),
            provided_drawdown_pct=_required_float(row, "provided_drawdown_pct"),
            optimized_drawdown_pct=_required_float(row, "optimized_drawdown_pct"),
            benchmark_drawdown_pct=(
                None
                if not hasattr(row, "benchmark_drawdown_pct")
                or pd.isna(row.benchmark_drawdown_pct)
                else float(row.benchmark_drawdown_pct)
            ),
        )
        for row in frame.itertuples(index=False)
    )


def _annual_asset_returns(
    frame: pd.DataFrame | None,
) -> tuple[AnnualAssetReturnPoint, ...]:
    if frame is None:
        return ()
    by_year: dict[int, dict[str, float]] = defaultdict(dict)
    for row in frame.itertuples(index=False):
        by_year[int(row.year)][str(row.ticker)] = float(row.return_pct)
    return tuple(
        AnnualAssetReturnPoint(year=year, returns_pct=returns)
        for year, returns in sorted(by_year.items())
    )


def _rolling_returns(frame: pd.DataFrame | None) -> tuple[RollingReturnPoint, ...]:
    if frame is None:
        return ()
    return tuple(
        RollingReturnPoint(
            date=str(row.date),
            provided_return_pct=_required_float(row, "provided_annualized_return_pct"),
            optimized_return_pct=_required_float(row, "optimized_annualized_return_pct"),
            benchmark_return_pct=(
                None
                if not hasattr(row, "benchmark_annualized_return_pct")
                or pd.isna(row.benchmark_annualized_return_pct)
                else float(row.benchmark_annualized_return_pct)
            ),
        )
        for row in frame.itertuples(index=False)
    )


def _active_contribution(
    frame: pd.DataFrame | None, portfolio: str
) -> tuple[ActiveContributionPoint, ...]:
    if frame is None:
        return ()
    grouped: dict[str, dict[str, float]] = defaultdict(dict)
    for row in frame.itertuples(index=False):
        if str(row.portfolio) != portfolio:
            continue
        value = getattr(row, "cumulative_active_contribution_pct", None)
        if value is None or pd.isna(value):
            continue
        grouped[str(row.date)][str(row.ticker)] = float(value)
    return tuple(
        ActiveContributionPoint(
            date=date, portfolio=portfolio, contributions_pct=values
        )
        for date, values in sorted(grouped.items())
    )


def _up_down_market(frame: pd.DataFrame | None) -> tuple[UpDownMarketPoint, ...]:
    if frame is None:
        return ()
    points: list[UpDownMarketPoint] = []
    for row in frame.itertuples(index=False):
        occurrences = getattr(row, "occurrences", None)
        points.append(
            UpDownMarketPoint(
                portfolio=str(row.portfolio),
                market_type=str(row.market_type),
                portfolio_return_pct=float(row.portfolio_return_pct),
                benchmark_return_pct=float(row.benchmark_return_pct),
                active_return_pct=float(row.active_return_pct),
                occurrences=None
                if occurrences is None or pd.isna(occurrences)
                else int(occurrences),
            )
        )
    return tuple(points)


def _up_down_scatter(
    frame: pd.DataFrame | None, portfolio: str
) -> tuple[UpDownScatterPoint, ...]:
    if frame is None:
        return ()
    points: list[UpDownScatterPoint] = []
    for row in frame.itertuples(index=False):
        if str(row.portfolio) != portfolio:
            continue
        fields = (
            getattr(row, "benchmark_return_pct", None),
            getattr(row, "portfolio_return_pct", None),
            getattr(row, "active_return_pct", None),
        )
        if any(value is None or pd.isna(value) for value in fields):
            continue
        points.append(
            UpDownScatterPoint(
                date=str(row.date),
                portfolio=portfolio,
                market_type=str(row.market_type),
                benchmark_return_pct=float(fields[0]),
                portfolio_return_pct=float(fields[1]),
                active_return_pct=float(fields[2]),
            )
        )
    return tuple(points)


def _frontier_assets(frame: pd.DataFrame | None) -> tuple[FrontierAssetPoint, ...]:
    if frame is None:
        return ()
    if "ticker" not in frame.columns or "expected_return_pct" not in frame.columns:
        return ()
    return tuple(
        FrontierAssetPoint(
            symbol=str(row.ticker),
            name=(
                None if not hasattr(row, "name") or pd.isna(row.name) else str(row.name)
            ),
            expected_return_pct=float(row.expected_return_pct),
            standard_deviation_pct=float(
                getattr(row, "standard_deviation_pct", None)
                if hasattr(row, "standard_deviation_pct")
                else getattr(row, "volatility_pct")
            ),
            sharpe_ratio=float(
                getattr(row, "sharpe_ratio", None)
                if hasattr(row, "sharpe_ratio")
                else getattr(row, "sharpe", float("nan"))
            ),
        )
        for row in frame.itertuples(index=False)
    )


def _frontier_landmarks(
    frame: pd.DataFrame | None, objective_name: str
) -> tuple[FrontierLandmark, ...]:
    if frame is None:
        return ()
    weight_columns = [
        column
        for column in frame.columns
        if column.startswith("weight_") and column.endswith("_pct")
    ]
    points: list[FrontierLandmark] = []
    for row in frame.to_dict(orient="records"):
        kind = str(row.get("kind") or "")
        volatility = _clean_scalar(row.get("volatility_pct"))
        expected_return = _clean_scalar(row.get("expected_return_pct"))
        if not kind or volatility is None or expected_return is None:
            continue
        weights = {
            column[len("weight_") : -len("_pct")]: float(row[column])
            for column in weight_columns
            if _clean_scalar(row.get(column)) is not None
        }
        label = str(row.get("label") or kind)
        if kind == "optimized":
            label = objective_name
        sharpe = _clean_scalar(row.get("sharpe"))
        points.append(
            FrontierLandmark(
                kind=kind,
                label=label,
                volatility_pct=float(volatility),
                expected_return_pct=float(expected_return),
                sharpe_ratio=None if sharpe is None else float(sharpe),
                weights_pct=weights,
            )
        )
    return tuple(points)


def build_report_model_from_artifacts(
    artifacts: RunArtifacts, config: Mapping[str, Any] | None = None
) -> ReportModel:
    config = config or _load_input(artifacts.run_dir)
    benchmark_symbol, benchmark_name = _benchmark(config)
    review = artifacts.review
    tables = {name: _records(frame) for name, frame in sorted(review.items())}
    objective_name = _objective_name(config)

    return ReportModel(
        run_id=str(config.get("run_id") or artifacts.run_dir.name),
        objective_name=objective_name,
        benchmark_symbol=benchmark_symbol,
        benchmark_name=benchmark_name,
        tables=tables,
        portfolio_growth=_portfolio_growth(review.get("portfolio_growth")),
        annual_returns=_annual_returns(review.get("annual_returns")),
        efficient_frontier=_frontier(review.get("efficient_frontier")),
        frontier_assets=_frontier_assets(
            review.get("efficient_frontier_assets", review.get("asset_statistics"))
        ),
        frontier_landmarks=_frontier_landmarks(
            review.get("frontier_landmarks"), objective_name
        ),
        annualized_active_returns=_annualized_active_returns(review.get("active_returns")),
        active_return_contribution_provided=_active_contribution(
            review.get("active_return_contribution"), "provided"
        ),
        active_return_contribution_optimized=_active_contribution(
            review.get("active_return_contribution"), "optimized"
        ),
        rolling_active_provided=_rolling_active(review.get("active_returns"), "provided"),
        rolling_active_optimized=_rolling_active(review.get("active_returns"), "optimized"),
        up_down_market_performance=_up_down_market(
            review.get("up_down_market_performance")
        ),
        up_down_scatter_provided=_up_down_scatter(
            review.get("up_down_market_scatter"), "provided"
        ),
        up_down_scatter_optimized=_up_down_scatter(
            review.get("up_down_market_scatter"), "optimized"
        ),
        drawdowns=_drawdowns(review.get("drawdown_series")),
        annual_asset_returns=_annual_asset_returns(review.get("annual_asset_returns")),
        rolling_returns_3y=_rolling_returns(review.get("rolling_returns_3y")),
        rolling_returns_5y=_rolling_returns(review.get("rolling_returns_5y")),
    )


def build_report_model(run_dir: str | Path) -> ReportModel:
    artifacts = load_run_artifacts(run_dir)
    return build_report_model_from_artifacts(artifacts)
