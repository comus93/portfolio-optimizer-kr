from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from portfolio_optimizer_kr.backtest_pv import analyze_backtest_prices
from portfolio_optimizer_kr.config import RunConfig, load_run_config
from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.data.preparation import prepare_monthly_returns
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec, ProductMode, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.report import write_analysis_run


US_3M_TBILL_SERIES = "FRED:TB3MS"
US_CPI_SERIES = "FRED:CPIAUCSL"


def _warmup_start(start: str | pd.Timestamp | None) -> str | None:
    if start is None:
        return None
    period = pd.Timestamp(start).to_period("M") - 1
    return period.start_time.date().isoformat()


def _inflation_start(start: str | pd.Timestamp | None) -> str | None:
    if start is None:
        return None
    period = pd.Timestamp(start).to_period("M") - 13
    return period.start_time.date().isoformat()


def _market_assets(spec: RunConfig) -> list[AssetSpec]:
    by_symbol = {asset.symbol: asset for asset in spec.request.assets}
    if spec.request.benchmark is not None:
        by_symbol.setdefault(spec.request.benchmark.symbol, spec.request.benchmark)
    return list(by_symbol.values())


def _requires_usdkrw(spec: RunConfig) -> bool:
    currencies = {asset.currency.upper() for asset in spec.request.assets}
    if spec.request.benchmark is not None:
        currencies.add(spec.request.benchmark.currency.upper())
    return "KRW" in currencies and "USD" in currencies


def _tbill_effective_annual_rate(
    series: pd.Series, observation_index: pd.Index
) -> float:
    """Arithmetic mean of monthly FRED TB3MS percentage-point observations."""
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if values.empty:
        raise DataValidationError("U.S. 3-Month T-Bill series has no numeric observations")

    values.index = pd.DatetimeIndex(values.index)
    by_month = values.groupby(values.index.to_period("M")).mean()
    required_months = pd.DatetimeIndex(observation_index).to_period("M").unique().sort_values()
    missing = required_months.difference(by_month.index)
    if len(missing):
        preview = ", ".join(str(month) for month in missing[:6])
        suffix = "..." if len(missing) > 6 else ""
        raise DataValidationError(
            f"U.S. 3-Month T-Bill coverage is missing required months: {preview}{suffix}"
        )

    return float(by_month.reindex(required_months).mean() / 100.0)


def _resolve_annual_rf(
    spec: RunConfig,
    loader: FDRLoader,
    prices: dict[str, pd.Series],
    usdkrw: pd.Series | None,
    supplied_annual_rf: float | None,
) -> float | None:
    request = spec.request
    if request.risk_free.mode is RiskFreeMode.FIXED:
        return supplied_annual_rf

    if supplied_annual_rf is not None:
        return float(supplied_annual_rf)

    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)
    observation_index = monthly_returns.index
    start = observation_index.min().to_period("M").start_time.date().isoformat()
    end = observation_index.max().to_period("M").end_time.date().isoformat()
    tbill = loader.load_economic_series(US_3M_TBILL_SERIES, start=start, end=end)
    return _tbill_effective_annual_rate(tbill, observation_index)


def _load_inflation_series(spec: RunConfig, loader: FDRLoader) -> pd.Series | None:
    # CPI is a best-effort report enrichment at the real market-data boundary.
    # Custom/fake loaders used by callers and tests must not acquire a new
    # economic-series obligation merely because Backtest supports inflation.
    if spec.product_mode is not ProductMode.BACKTEST or type(loader) is not FDRLoader:
        return None
    try:
        return loader.load_economic_series(
            US_CPI_SERIES,
            start=_inflation_start(spec.request.start),
            end=spec.request.end,
        )
    except (DataValidationError, NotImplementedError, AttributeError):
        return None


def _effective_backtest_input(source: Mapping[str, Any], spec: RunConfig) -> dict[str, Any]:
    """Materialize parser defaults so persisted Backtest input is reproducible."""
    effective = dict(source)
    request = spec.request
    effective["product_mode"] = ProductMode.BACKTEST.value
    effective.setdefault("initial_balance", request.initial_balance)

    time_period = effective.get("time_period")
    if not isinstance(time_period, Mapping):
        time_period = {}
    time_period = dict(time_period)
    time_period.setdefault("mode", request.time_period_mode.value)  # type: ignore[attr-defined]
    effective["time_period"] = time_period

    rebalancing = effective.get("rebalancing")
    if not isinstance(rebalancing, Mapping):
        rebalancing = {}
    rebalancing = dict(rebalancing)
    rebalancing.setdefault("period", request.rebalancing.value)
    rebalancing.setdefault("calendar_aligned", request.calendar_aligned)  # type: ignore[attr-defined]
    effective["rebalancing"] = rebalancing

    raw_portfolios = effective.get("portfolios")
    if isinstance(raw_portfolios, list):
        rows: list[Any] = []
        canonical = list(request.portfolios)  # type: ignore[attr-defined]
        for index, raw in enumerate(raw_portfolios):
            if isinstance(raw, Mapping):
                row = dict(raw)
                if index < len(canonical):
                    row["name"] = canonical[index].name
                rows.append(row)
            else:
                rows.append(raw)
        effective["portfolios"] = rows
    return effective


def execute_run(
    spec: RunConfig,
    output_root: str | Path = "runs",
    *,
    loader: FDRLoader | None = None,
    annual_rf: float | None = None,
    analyze_fn: Callable[..., dict[str, Any]] | None = None,
    writer: Callable[[dict[str, Any], str | Path], None] | None = None,
) -> Path:
    request = spec.request
    if not request.run_id:
        raise ValueError("run_id is required for persisted runs")

    output_dir = Path(output_root) / request.run_id
    if output_dir.exists():
        raise FileExistsError(f"run output already exists: {output_dir}")

    loader = loader or FDRLoader()
    using_default_analyzer = analyze_fn is None
    if analyze_fn is None:
        analyze_fn = (
            analyze_backtest_prices
            if spec.product_mode is ProductMode.BACKTEST
            else analyze_prices
        )
    writer = writer or write_analysis_run
    load_start = _warmup_start(request.start)
    prices = loader.load_many(_market_assets(spec), start=load_start, end=request.end)

    usdkrw = None
    if _requires_usdkrw(spec):
        if not spec.usdkrw_symbol:
            raise DataValidationError(
                "mixed KRW/USD run requires fx.usdkrw_symbol in the YAML config"
            )
        usdkrw = loader.load_series(spec.usdkrw_symbol, start=load_start, end=request.end)

    effective_annual_rf = _resolve_annual_rf(
        spec, loader, prices, usdkrw, annual_rf
    )
    if using_default_analyzer and spec.product_mode is ProductMode.BACKTEST:
        result = analyze_fn(
            request,
            prices,
            usdkrw=usdkrw,
            annual_rf=effective_annual_rf,
            inflation_series=_load_inflation_series(spec, loader),
        )
    else:
        result = analyze_fn(
            request, prices, usdkrw=usdkrw, annual_rf=effective_annual_rf
        )
    output_dir.mkdir(parents=True, exist_ok=False)
    writer(result, output_dir)
    return output_dir


def run_yaml(
    config_path: str | Path,
    output_root: str | Path = "runs",
    *,
    loader: FDRLoader | None = None,
    annual_rf: float | None = None,
    analyze_fn: Callable[..., dict[str, Any]] | None = None,
    writer: Callable[[dict[str, Any], str | Path], None] | None = None,
) -> Path:
    source = Path(config_path)
    loaded = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ValueError("YAML root must be a mapping")
    spec = load_run_config(source)
    output_dir = execute_run(
        spec,
        output_root,
        loader=loader,
        annual_rf=annual_rf,
        analyze_fn=analyze_fn,
        writer=writer,
    )
    if spec.product_mode is ProductMode.BACKTEST:
        effective = _effective_backtest_input(loaded, spec)
        (output_dir / "input.yaml").write_text(
            yaml.safe_dump(effective, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    else:
        (output_dir / "input.yaml").write_text(
            source.read_text(encoding="utf-8"), encoding="utf-8"
        )
    if (output_dir / "result.json").is_file():
        from portfolio_optimizer_kr.viewer import generate_report

        generate_report(output_dir)
    return output_dir