from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


JSONRecord = dict[str, Any]


@dataclass(frozen=True)
class PortfolioGrowthPoint:
    date: str
    provided_balance: float
    optimized_balance: float
    benchmark_balance: float | None = None


@dataclass(frozen=True)
class AnnualReturnPoint:
    year: int
    provided_return_pct: float
    optimized_return_pct: float
    benchmark_return_pct: float | None = None


@dataclass(frozen=True)
class FrontierPoint:
    volatility_pct: float
    expected_return_pct: float
    sharpe_ratio: float
    weights_pct: Mapping[str, float]


@dataclass(frozen=True)
class FrontierAssetPoint:
    symbol: str
    name: str | None
    expected_return_pct: float
    standard_deviation_pct: float
    sharpe_ratio: float


@dataclass(frozen=True)
class ActiveReturnPoint:
    date: str
    provided_active_return_pct: float
    optimized_active_return_pct: float


@dataclass(frozen=True)
class RollingActivePoint:
    date: str
    active_return_pct: float
    tracking_error_pct: float


@dataclass(frozen=True)
class DrawdownPoint:
    date: str
    provided_drawdown_pct: float
    optimized_drawdown_pct: float
    benchmark_drawdown_pct: float | None = None


@dataclass(frozen=True)
class AnnualAssetReturnPoint:
    year: int
    returns_pct: Mapping[str, float]


@dataclass(frozen=True)
class RollingReturnPoint:
    date: str
    provided_return_pct: float
    optimized_return_pct: float
    benchmark_return_pct: float | None = None


@dataclass(frozen=True)
class ActiveContributionPoint:
    date: str
    portfolio: str
    contributions_pct: Mapping[str, float]


@dataclass(frozen=True)
class UpDownMarketPoint:
    portfolio: str
    market_type: str
    portfolio_return_pct: float
    benchmark_return_pct: float
    active_return_pct: float
    occurrences: int | None = None


@dataclass(frozen=True)
class ReportModel:
    run_id: str
    objective_name: str
    benchmark_symbol: str | None = None
    benchmark_name: str | None = None
    tables: Mapping[str, tuple[JSONRecord, ...]] = field(default_factory=dict)
    portfolio_growth: tuple[PortfolioGrowthPoint, ...] = ()
    annual_returns: tuple[AnnualReturnPoint, ...] = ()
    efficient_frontier: tuple[FrontierPoint, ...] = ()
    frontier_assets: tuple[FrontierAssetPoint, ...] = ()
    annualized_active_returns: tuple[ActiveReturnPoint, ...] = ()
    active_return_contribution: tuple[ActiveContributionPoint, ...] = ()
    rolling_active_provided: tuple[RollingActivePoint, ...] = ()
    rolling_active_optimized: tuple[RollingActivePoint, ...] = ()
    up_down_market_performance: tuple[UpDownMarketPoint, ...] = ()
    drawdowns: tuple[DrawdownPoint, ...] = ()
    annual_asset_returns: tuple[AnnualAssetReturnPoint, ...] = ()
    rolling_returns_3y: tuple[RollingReturnPoint, ...] = ()
    rolling_returns_5y: tuple[RollingReturnPoint, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
