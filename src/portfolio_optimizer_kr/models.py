from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping

import pandas as pd


class OptimizationObjective(StrEnum):
    MAX_SHARPE = "max_sharpe"
    TARGET_VOLATILITY = "target_volatility"


class RebalancingPeriod(StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RiskFreeMode(StrEnum):
    US_3M_TBILL = "us_3m_tbill"
    FIXED = "fixed"


@dataclass(frozen=True)
class AssetSpec:
    symbol: str
    name: str | None = None
    currency: str = "KRW"
    min_weight: float = 0.0
    max_weight: float = 1.0


@dataclass(frozen=True)
class RiskFreeConfig:
    mode: RiskFreeMode = RiskFreeMode.US_3M_TBILL
    annual_rate: float | None = None


@dataclass(frozen=True)
class OptimizationRequest:
    assets: tuple[AssetSpec, ...]
    start: str | pd.Timestamp | None = None
    end: str | pd.Timestamp | None = None
    provided_weights: Mapping[str, float] | None = None
    benchmark: AssetSpec | None = None
    objective: OptimizationObjective = OptimizationObjective.MAX_SHARPE
    target_volatility: float | None = None
    rebalancing: RebalancingPeriod = RebalancingPeriod.MONTHLY
    risk_free: RiskFreeConfig = field(default_factory=RiskFreeConfig)
    frontier_points: int = 100


@dataclass(frozen=True)
class OptimizationResult:
    weights: pd.Series
    expected_return: float
    volatility: float
    sharpe: float
    solver: str
    status: str
