from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml

from portfolio_optimizer_kr.models import (
    AssetSpec,
    BacktestPortfolio,
    BacktestRequest,
    OptimizationObjective,
    OptimizationRequest,
    ProductMode,
    RebalancingPeriod,
    RiskFreeConfig,
    RiskFreeMode,
    TimePeriodMode,
)


class ConfigValidationError(ValueError):
    pass


@dataclass(frozen=True)
class RunConfig:
    request: OptimizationRequest | BacktestRequest
    usdkrw_symbol: str | None = None
    product_mode: ProductMode = ProductMode.OPTIMIZATION


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
    except Exception as exc:
        raise ConfigValidationError(f"{field} is not a valid date") from exc


def _positive_number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(f"{field} must be numeric") from exc
    if number <= 0:
        raise ConfigValidationError(f"{field} must be positive")
    return number


def _parse_asset_rows(config: Mapping[str, Any]) -> tuple[AssetSpec, ...]:
    asset_rows = config.get("assets")
    if not isinstance(asset_rows, list) or not asset_rows:
        raise ConfigValidationError("assets must be a non-empty list")

    assets: list[AssetSpec] = []
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
    return tuple(assets)


def _parse_benchmark(config: Mapping[str, Any]) -> AssetSpec | None:
    benchmark_raw = config.get("benchmark")
    if not benchmark_raw:
        return None
    if isinstance(benchmark_raw, str):
        symbol = benchmark_raw.strip()
        if not symbol:
            return None
        return AssetSpec(symbol)
    row = _mapping(benchmark_raw, "benchmark")
    symbol = str(row.get("symbol") or "").strip()
    if not symbol:
        raise ConfigValidationError("benchmark.symbol is required")
    return AssetSpec(
        symbol=symbol,
        name=str(row["name"]).strip() if row.get("name") else None,
        currency=str(row.get("currency") or "KRW").upper(),
    )


def _parse_risk_free(config: Mapping[str, Any]) -> RiskFreeConfig:
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
    return RiskFreeConfig(mode=risk_mode, annual_rate=annual_rate)


def _parse_fx(config: Mapping[str, Any]) -> str | None:
    fx = _mapping(config.get("fx", {}), "fx")
    return str(fx.get("usdkrw_symbol") or "").strip() or None


def _normalise_product_mode(value: Any) -> ProductMode:
    text = str(value or "optimization").strip().lower().replace("-", "_")
    aliases = {
        "optimizer": "optimization",
        "optimize": "optimization",
        "portfolio_optimization": "optimization",
        "portfolio_backtest": "backtest",
    }
    try:
        return ProductMode(aliases.get(text, text))
    except ValueError as exc:
        raise ConfigValidationError("unsupported product_mode") from exc


def _normalise_time_period_mode(value: Any) -> TimePeriodMode:
    text = str(value or "month_to_month").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"monthly": "month_to_month", "yearly": "year_to_year"}
    try:
        return TimePeriodMode(aliases.get(text, text))
    except ValueError as exc:
        raise ConfigValidationError("unsupported time_period.mode") from exc


def _month_number(value: Any, field: str, default: int) -> int:
    if value in (None, ""):
        return default
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            value = int(text)
        else:
            try:
                value = pd.Timestamp(f"2000-{text[:3]}-01").month
            except Exception as exc:
                raise ConfigValidationError(f"{field} is not a valid month") from exc
    try:
        month = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError(f"{field} is not a valid month") from exc
    if not 1 <= month <= 12:
        raise ConfigValidationError(f"{field} must be between 1 and 12")
    return month


def _backtest_period(config: Mapping[str, Any]) -> tuple[TimePeriodMode, str | None, str | None]:
    raw = _mapping(config.get("time_period", {}), "time_period")
    mode = _normalise_time_period_mode(raw.get("mode", "month_to_month"))
    start_year = raw.get("start_year")
    end_year = raw.get("end_year")
    if start_year in (None, "") and end_year in (None, ""):
        return mode, None, None
    if start_year in (None, "") or end_year in (None, ""):
        raise ConfigValidationError("time_period.start_year and end_year must be specified together")
    try:
        start_year_int = int(start_year)
        end_year_int = int(end_year)
    except (TypeError, ValueError) as exc:
        raise ConfigValidationError("time_period years must be integers") from exc
    if mode is TimePeriodMode.MONTH_TO_MONTH:
        first_month = _month_number(raw.get("first_month"), "time_period.first_month", 1)
        last_month = _month_number(raw.get("last_month"), "time_period.last_month", 12)
        start = pd.Timestamp(start_year_int, first_month, 1)
        end = pd.Period(f"{end_year_int}-{last_month:02d}", freq="M").end_time.normalize()
    else:
        start = pd.Timestamp(start_year_int, 1, 1)
        end = pd.Timestamp(end_year_int, 12, 31)
    if start > end:
        raise ConfigValidationError("time_period start must not be after end")
    return mode, start.date().isoformat(), end.date().isoformat()


def _normalise_rebalancing(value: Any) -> RebalancingPeriod:
    text = str(value or "monthly").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "no_rebalancing": "none",
        "annual": "yearly",
        "annually": "yearly",
        "rebalance_annually": "yearly",
        "semi_annual": "semiannual",
        "semi_annually": "semiannual",
        "rebalance_semi_annually": "semiannual",
        "rebalance_quarterly": "quarterly",
        "rebalance_monthly": "monthly",
    }
    try:
        return RebalancingPeriod(aliases.get(text, text))
    except ValueError as exc:
        raise ConfigValidationError("unsupported rebalancing period") from exc


def _optimization_request_from_config(
    config: Mapping[str, Any], run_id: str, assets: tuple[AssetSpec, ...]
) -> OptimizationRequest:
    period = _mapping(config.get("analysis_period", {}), "analysis_period")
    start = _date(period.get("start"), "analysis_period.start")
    end = _date(period.get("end"), "analysis_period.end")
    if start and end and pd.Timestamp(start) > pd.Timestamp(end):
        raise ConfigValidationError("analysis_period.start must not be after end")

    asset_rows = config.get("assets") or []
    provided: dict[str, float] = {}
    provided_presence: list[bool] = []
    for index, raw in enumerate(asset_rows):
        row = _mapping(raw, f"assets[{index}]")
        has_provided = "provided_weight_pct" in row and row.get("provided_weight_pct") is not None
        provided_presence.append(has_provided)
        if has_provided:
            provided[assets[index].symbol] = _pct_weight(
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
    rebalancing = _normalise_rebalancing(portfolio.get("rebalancing_period", "monthly"))
    if rebalancing not in {RebalancingPeriod.MONTHLY, RebalancingPeriod.YEARLY}:
        raise ConfigValidationError(
            "optimization portfolio.rebalancing_period supports monthly or yearly"
        )

    return OptimizationRequest(
        assets=assets,
        run_id=run_id,
        start=start,
        end=end,
        provided_weights=provided_weights,
        benchmark=_parse_benchmark(config),
        objective=objective,
        target_volatility=target_volatility,
        rebalancing=rebalancing,
        risk_free=_parse_risk_free(config),
        frontier_points=frontier_points,
    )


def _backtest_request_from_config(
    config: Mapping[str, Any], run_id: str, assets: tuple[AssetSpec, ...]
) -> BacktestRequest:
    excluded_fields = {
        "cashflows",
        "leverage",
        "display_income",
        "style_analysis",
        "factor_regression",
        "regime_performance",
        "rebalance_bands",
    }
    for field in sorted(excluded_fields):
        if field in config and config.get(field) not in (None, False, "", "none", "None"):
            raise ConfigValidationError(f"{field} is not supported in backtest v1")

    mode, start, end = _backtest_period(config)
    portfolio_rows = config.get("portfolios")
    if not isinstance(portfolio_rows, list) or not portfolio_rows:
        raise ConfigValidationError("portfolios must be a non-empty list")
    if len(portfolio_rows) > 3:
        raise ConfigValidationError("backtest v1 supports at most 3 portfolios")

    asset_symbols = [asset.symbol for asset in assets]
    asset_set = set(asset_symbols)
    portfolios: list[BacktestPortfolio] = []
    names: set[str] = set()
    for index, raw in enumerate(portfolio_rows):
        row = _mapping(raw, f"portfolios[{index}]")
        if row.get("rebalancing") is not None or row.get("rebalancing_period") is not None:
            raise ConfigValidationError(
                "backtest v1 rebalancing is run-level; portfolio-specific rebalancing is not supported"
            )
        name = str(row.get("name") or f"Portfolio {index + 1}").strip()
        if not name:
            name = f"Portfolio {index + 1}"
        if name in names:
            raise ConfigValidationError(f"duplicate portfolio name: {name}")
        names.add(name)
        raw_weights = _mapping(row.get("weights_pct", {}), f"portfolios[{index}].weights_pct")
        unknown = set(str(symbol) for symbol in raw_weights) - asset_set
        if unknown:
            raise ConfigValidationError(
                f"portfolios[{index}] contains unknown asset: {sorted(unknown)[0]}"
            )
        weights = {
            symbol: _pct_weight(raw_weights.get(symbol, 0), f"portfolios[{index}].weights_pct.{symbol}")
            for symbol in asset_symbols
        }
        if abs(sum(weights.values()) - 1.0) > 1e-8:
            raise ConfigValidationError(f"portfolios[{index}] weights must sum to 100%")
        portfolios.append(BacktestPortfolio(name=name, target_weights=weights))

    rebalancing_raw = _mapping(config.get("rebalancing", {}), "rebalancing")
    if "bands" in rebalancing_raw or str(rebalancing_raw.get("period", "")).strip().lower() in {
        "bands",
        "rebalance_bands",
    }:
        raise ConfigValidationError("rebalance bands is not supported in backtest v1")
    rebalancing = _normalise_rebalancing(rebalancing_raw.get("period", "monthly"))
    calendar_aligned_raw = rebalancing_raw.get("calendar_aligned", True)
    if not isinstance(calendar_aligned_raw, bool):
        raise ConfigValidationError("rebalancing.calendar_aligned must be boolean")

    return BacktestRequest(
        assets=assets,
        portfolios=tuple(portfolios),
        run_id=run_id,
        start=start,
        end=end,
        time_period_mode=mode,
        benchmark=_parse_benchmark(config),
        initial_balance=_positive_number(config.get("initial_balance", 10000), "initial_balance"),
        rebalancing=rebalancing,
        calendar_aligned=calendar_aligned_raw,
        risk_free=_parse_risk_free(config),
    )


def request_from_config(config: Mapping[str, Any]) -> RunConfig:
    run_id = str(config.get("run_id") or "").strip()
    if not run_id:
        raise ConfigValidationError("run_id is required")

    product_mode = _normalise_product_mode(config.get("product_mode", "optimization"))
    assets = _parse_asset_rows(config)
    if product_mode is ProductMode.BACKTEST:
        request: OptimizationRequest | BacktestRequest = _backtest_request_from_config(
            config, run_id, assets
        )
    else:
        request = _optimization_request_from_config(config, run_id, assets)
    return RunConfig(
        request=request,
        usdkrw_symbol=_parse_fx(config),
        product_mode=product_mode,
    )


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
