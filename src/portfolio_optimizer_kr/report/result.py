from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CanonicalResult:
    configuration: dict[str, Any]
    data_coverage: dict[str, Any]
    asset_statistics: dict[str, Any]
    optimization_result: dict[str, Any]
    efficient_frontier: list[dict[str, Any]] = field(default_factory=list)
    portfolio_performance: dict[str, Any] = field(default_factory=dict)
    benchmark_analytics: dict[str, Any] = field(default_factory=dict)
    correlations: dict[str, Any] = field(default_factory=dict)
    return_decomposition: dict[str, Any] = field(default_factory=dict)
    risk_decomposition: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
