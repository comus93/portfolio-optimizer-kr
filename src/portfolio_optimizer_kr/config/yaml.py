from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml

from portfolio_optimizer_kr.models import (
    AssetSpec,
    OptimizationObjective,
    OptimizationRequest,
    RebalancingPeriod,
    RiskFreeConfig,
    RiskFreeMode,
)


class ConfigValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RunConfig:
    request: OptimizationRequest
    usdkrw_symbol: str | None = None


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConfigValidationError(f"{field} must be a mapping")
    return value


def _pct_weight(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(f"{field} must be numeric percentage points") from exc
    if not 0.0 <= number <= 100.0:
        raise ConfigValidationError(f"{field} must be between 0 and 100")
    return number / 100.0


def _pct_rate(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(f"{field} must be numeric percentage points") from exc
    if number <= -100.0:
        raise ConfigValidationError(f"{field} must be greater than -100")
    return number / 100.0


def _date(value: Any, field: str) -> str | None:
    if value in (None, ""):
        return None
    try:
        return pd.Timestamp(value).date().isoformat()
    except Exception as exc:  # pandas gives several parser exception types
        raise ConfigValidationError(f"{field} is not a valid date") from exc


def request_from_config(config: Mapping[str, Any]) -> RunConfig:
    run_id = str(config.get("run_id") or "").strip()
    if not run_id:
        raise ConfigValidationError("run_id is required")

    period = _mapping(config.get("analysis_period", {}), "analysis_period")
    start = _date(period.get("start"), "analysis_period.start")
    end = _date(period.get("end"), "analysis_period.end")
    if start and end and pd.Timestamp(start) > pd.Timestamp(end):
        raise ConfigValidationError("analysis_period.start must not be after end")

    asset_rows = config.get("assets")
    if not isinstance(asset_rows, list) or not asset_rows:
        raise ConfigValidationError("assets must be a non-empty list")

    assets: list[AssetSpec] = []
    provided: dict[str, float] = {}
    provided_presence: list[bool] = []
    seen: set[str] = set()
    for index, raw in enumerate(asset_rows):
        row = _mapping(raw, f"assets[{index}]")
        symbol = str(row.get("symbol") or "").strip()
        if not symbol:
            raise ConfigValidationError(f"assets[{index}].symbol is required")
        if symbol in seen:
            raise ConfigValidationError(f"duplicate asset symbol: {symbol}")
        seen.add(symbol)

        minimum = _pct_weight(row.get("min_weight_pct", 0), f"assets[{index}].min_weight_pct")
        maximum = _pct_weight(row.get("max_weight_pct", 100), f"assets[{index}].max_weight_pct")
        if minimum > maximum:
            raise ConfigValidationError(f"assets[{index}] min weight exceeds max weight")

        assets.append(
            AssetSpec(
                symbol=symbol,
                name=str(row["name"]).strip() if row.get("name") else None,
                currency=str(row.get("currency") or "KRW").upper(),
                min_weight=minimum,
                max_weight=maximum,
            )
        )
        has_provided = "provided_weight_pct" in row and row.get("provided_weight_pct") is not None
        provided_presence.append(has_provided)
        if has_provided:
            provided[symbol] = _pct_weight(
                row.get("provided_weight_pct"), f"assets[{index}].provided_weight_pct"
            )

    if any(provided_presence) and not all(provided_presence):
        raise ConfigValidationError(
            "provided_weight_pct must be specified for every asset or omitted for every asset"
        )
    provided_weights = provided if all(provided_presence) else None
    if provided_weights is not None and abs(sum(provided_weights.values()) - 1.0) > 1e-8:
        raise ConfigValidationError("provided weights must sum to 100%")
    if sum(asset.min_weight for asset in assets) > 1.0 + 1e-8:
        raise ConfigValidationError("asset minimum weights are infeasible")
    if sum(asset.max_weight for asset in assets) < 1.0 - 1e-8:
        raise ConfigValidationError("asset maximum weights are infeasible")

    benchmark_raw = config.get("benchmark")
    benchmark = None
    if benchmark_raw:
        if isinstance(benchmark_raw, str):
            benchmark = AssetSpec(benchmark_raw.strip())
        else:
            row = _mapping(benchmark_raw, "benchmark")
            symbol = str(row.get("symbol") or "").strip()
            if not symbol:
                raise ConfigValidationError("benchmark.symbol is required")
            benchmark = AssetSpec(
                symbol=symbol,
                name=str(row["name"]).strip() if row.get("name") else None,
                currency=str(row.get("currency") or "KRW").upper(),
            )

    optimization = _mapping(config.get("optimization", {}), "optimization")
    try:
        objective = OptimizationObjective(str(optimization.get("objective", "max_sharpe")))
    except ValueError as exc:
        raise ConfigValidationError("unsupported optimization.objective") from exc
    target_volatility = None
    if optimization.get("target_volatility_pct") is not None:
        target_volatility = _pct_weight(
            optimization.get("target_volatility_pct"), "optimization.target_volatility_pct"
        )
    if objective is OptimizationObjective.TARGET_VOLATILITY and target_volatility is None:
        raise ConfigValidationError("target-volatility objective requires target_volatility_pct")
    frontier_points = int(optimization.get("frontier_points", 100))
    if frontier_points < 2:
        raise ConfigValidationError("optimization.frontier_points must be at least 2")

    portfolio = _mapping(config.get("portfolio", {}), "portfolio")
    try:
        rebalancing = RebalancingPeriod(
            str(portfolio.get("rebalancing_period", "monthly"))
        )
    except ValueError as exc:
        raise ConfigValidationError("unsupported portfolio.rebalancing_period") from exc

    risk = _mapping(config.get("risk_free", {}), "risk_free")
    try:
        risk_mode = RiskFreeMode(str(risk.get("mode", "us_3m_tbill")))
    except ValueError as exc:
        raise ConfigValidationError("unsupported risk_free.mode") from exc
    annual_rate = None
    if risk.get("annual_rate_pct") is not None:
        annual_rate = _pct_rate(risk.get("annual_rate_pct"), "risk_free.annual_rate_pct")
    if risk_mode is RiskFreeMode.FIXED and annual_rate is None:
        raise ConfigValidationError("fixed risk-free mode requires annual_rate_pct")

    fx = _mapping(config.get("fx", {}), "fx")
    usdkrw_symbol = str(fx.get("usdkrw_symbol") or "").strip() or None

    request = OptimizationRequest(
        assets=tuple(assets),
        run_id=run_id,
        start=start,
        end=end,
        provided_weights=provided_weights,
        benchmark=benchmark,
        objective=objective,
        target_volatility=target_volatility,
        rebalancing=rebalancing,
        risk_free=RiskFreeConfig(mode=risk_mode, annual_rate=annual_rate),
        frontier_points=frontier_points,
    )
    return RunConfig(request=request, usdkrw_symbol=usdkrw_symbol)


def load_run_config(path: str | Path) -> RunConfig:
    source = Path(path)
    loaded = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ConfigValidationError("YAML root must be a mapping")
    return request_from_config(loaded)


def write_user_config(config: Mapping[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        yaml.safe_dump(dict(config), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return target
