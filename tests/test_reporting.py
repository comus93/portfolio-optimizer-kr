import json

import pandas as pd

from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest, RiskFreeConfig, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.report import write_analysis_run


def _price(start: float, slope: float) -> pd.Series:
    index = pd.date_range("2019-12-31", periods=1600, freq="D")
    return pd.Series(start + slope * pd.RangeIndex(len(index)), index=index)


def _price_range(start_date: str, end_date: str, start: float, slope: float) -> pd.Series:
    index = pd.date_range(start_date, end_date, freq="D")
    return pd.Series(start + slope * pd.RangeIndex(len(index)), index=index)


def test_benchmark_and_canonical_run_outputs(tmp_path):
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        benchmark=AssetSpec("BM"),
        provided_weights={"A": 0.5, "B": 0.5},
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=3,
    )
    result = analyze_prices(request, {"A": _price(100, 0.12), "B": _price(100, 0.07), "BM": _price(100, 0.09)})
    assert set(result) >= {"configuration", "benchmark_analytics", "correlations", "return_decomposition", "risk_decomposition"}
    assert result["benchmark_analytics"]["coverage"]["observations"] > 0
    assert {"provided", "optimized", "benchmark"}.issubset(result["portfolio_performance"])
    assert result["risk_decomposition"]["provided"]
    write_analysis_run(result, tmp_path)
    assert (tmp_path / "result.json").is_file()
    assert (tmp_path / "active_returns.csv").is_file()
    assert json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["configuration"]["benchmark"]["symbol"] == "BM"


def test_benchmark_performance_is_limited_to_optimizer_analysis_coverage():
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        benchmark=AssetSpec("BM"),
        provided_weights={"A": 0.5, "B": 0.5},
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=3,
    )
    prices = {
        "A": _price_range("2021-01-01", "2022-12-31", 100, 0.12),
        "B": _price_range("2021-01-01", "2022-12-31", 100, 0.07),
        "BM": _price_range("2019-01-01", "2022-12-31", 100, 0.09),
    }

    result = analyze_prices(request, prices)
    coverage_start = pd.Timestamp(result["data_coverage"]["optimization_monthly_returns"]["start"])
    coverage_end = pd.Timestamp(result["data_coverage"]["optimization_monthly_returns"]["end"])

    monthly = result["_tables"]["monthly_return_series"]
    benchmark_months = monthly.loc[monthly["benchmark"].notna(), "date"]
    assert benchmark_months.min() >= coverage_start
    assert benchmark_months.max() <= coverage_end

    drawdowns = result["_tables"]["drawdowns"]
    benchmark_drawdowns = drawdowns.loc[drawdowns["portfolio"] == "benchmark"]
    if not benchmark_drawdowns.empty:
        assert pd.to_datetime(benchmark_drawdowns["start"]).min() >= coverage_start

    annual = result["_tables"]["annual_returns"]
    benchmark_years = annual.loc[annual["benchmark"].notna(), "year"]
    assert benchmark_years.min() >= coverage_start.year
    assert benchmark_years.max() <= coverage_end.year


def test_interactive_report_source_tables_are_persisted_by_analytics(tmp_path):
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        benchmark=AssetSpec("BM"),
        provided_weights={"A": 0.5, "B": 0.5},
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=3,
    )
    prices = {
        "A": _price_range("2019-01-01", "2022-12-31", 100, 0.12),
        "B": _price_range("2019-01-01", "2022-12-31", 100, 0.07),
        "BM": _price_range("2019-01-01", "2022-12-31", 100, 0.09),
    }
    result = analyze_prices(request, prices)
    write_analysis_run(result, tmp_path)

    review = tmp_path / "review"
    expected = {
        "portfolio_growth.csv": {"date", "provided_balance", "optimized_balance", "benchmark_balance"},
        "drawdown_series.csv": {"date", "provided_drawdown_pct", "optimized_drawdown_pct", "benchmark_drawdown_pct"},
        "annual_asset_returns.csv": {"year", "ticker", "return_pct"},
        "active_return_contribution.csv": {"date", "portfolio", "ticker", "cumulative_active_contribution_pct"},
        "up_down_market_performance.csv": {"portfolio", "market_type", "portfolio_return_pct", "benchmark_return_pct", "active_return_pct", "occurrences"},
        "stress_periods.csv": {"stress_period", "start", "end", "provided_return_pct", "optimized_return_pct", "benchmark_return_pct"},
        "portfolio_metrics.csv": {"metric", "provided", "optimized"},
    }
    for name, columns in expected.items():
        assert columns <= set(pd.read_csv(review / name).columns)
