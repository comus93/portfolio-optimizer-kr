from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from portfolio_optimizer_kr.backtest import analyze_backtest_prices
from portfolio_optimizer_kr.config import request_from_config
from portfolio_optimizer_kr.report.backtest import write_backtest_analysis_run
from portfolio_optimizer_kr.viewer import generate_report


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / ".playwright" / "backtest-browser"


def _price_series(base: float, monthly_pattern: tuple[float, ...], index: pd.DatetimeIndex, name: str) -> pd.Series:
    values = [float(base)]
    for position in range(1, len(index)):
        monthly_return = monthly_pattern[(position - 1) % len(monthly_pattern)]
        values.append(values[-1] * (1.0 + monthly_return))
    return pd.Series(values, index=index, name=name, dtype=float)


def _prices() -> dict[str, pd.Series]:
    index = pd.date_range("2017-12-31", "2023-12-31", freq="ME")
    return {
        "QQQ": _price_series(100.0, (0.030, -0.012, 0.018, 0.006, -0.004, 0.021), index, "QQQ"),
        "GLD": _price_series(100.0, (0.008, 0.011, -0.006, 0.014, 0.003, -0.002), index, "GLD"),
        "SPY": _price_series(100.0, (0.021, -0.008, 0.014, 0.005, -0.003, 0.016), index, "SPY"),
    }


def _config(*, benchmark: bool) -> dict:
    config: dict = {
        "product_mode": "backtest",
        "run_id": "browser-fixture-benchmark" if benchmark else "browser-fixture-no-benchmark",
        "time_period": {
            "mode": "month_to_month",
            "start_year": 2018,
            "first_month": 1,
            "end_year": 2023,
            "last_month": 12,
        },
        "assets": [
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "currency": "USD"},
            {"symbol": "GLD", "name": "SPDR Gold Shares", "currency": "USD"},
        ],
        "portfolios": [
            {"name": "Growth Tilt", "weights_pct": {"QQQ": 70, "GLD": 30}},
            {"name": "Balanced", "weights_pct": {"QQQ": 50, "GLD": 50}},
        ],
        "initial_balance": 10000,
        "rebalancing": {"period": "monthly", "calendar_aligned": True},
        "risk_free": {"mode": "fixed", "annual_rate_pct": 2},
    }
    if benchmark:
        config["benchmark"] = {
            "symbol": "SPY",
            "name": "SPDR S&P 500 ETF Trust",
            "currency": "USD",
        }
    return config


def _build(name: str, *, benchmark: bool) -> Path:
    target = FIXTURE_ROOT / name
    target.mkdir(parents=True, exist_ok=True)
    spec = request_from_config(_config(benchmark=benchmark))
    available = _prices()
    symbols = {asset.symbol for asset in spec.request.assets}
    if spec.request.benchmark is not None:
        symbols.add(spec.request.benchmark.symbol)
    prices = {symbol: available[symbol] for symbol in symbols}
    result = analyze_backtest_prices(spec.request, prices, annual_rf=0.02)
    write_backtest_analysis_run(result, target)
    generate_report(target)
    return target


def main() -> int:
    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT)
    _build("with-benchmark", benchmark=True)
    _build("without-benchmark", benchmark=False)
    print(FIXTURE_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
