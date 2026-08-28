from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shutil
from typing import Any

import pandas as pd

from portfolio_optimizer_kr.config import RunConfig, load_run_config
from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.report import write_analysis_run


def _warmup_start(start: str | pd.Timestamp | None) -> str | None:
    if start is None:
        return None
    period = pd.Timestamp(start).to_period("M") - 1
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

    loader = loader or FDRLoader()
    analyze_fn = analyze_fn or analyze_prices
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

    result = analyze_fn(request, prices, usdkrw=usdkrw, annual_rf=annual_rf)
    output_dir = Path(output_root) / request.run_id
    output_dir.mkdir(parents=True, exist_ok=True)
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
    spec = load_run_config(source)
    output_dir = execute_run(
        spec,
        output_root,
        loader=loader,
        annual_rf=annual_rf,
        analyze_fn=analyze_fn,
        writer=writer,
    )
    shutil.copyfile(source, output_dir / "input.yaml")
    return output_dir
