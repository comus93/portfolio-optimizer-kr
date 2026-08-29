from types import SimpleNamespace

import pandas as pd
import pytest

from portfolio_optimizer_kr.pipeline import (
    _frontier_landmarks_table,
    _up_down_scatter_table,
)


def test_frontier_landmarks_use_optimizer_moments_for_provided_and_optimized():
    request = SimpleNamespace(provided_weights={"AAA": 0.6, "BBB": 0.4})
    stats = SimpleNamespace(
        expected_returns=pd.Series({"AAA": 0.12, "BBB": 0.06}),
        covariance=pd.DataFrame(
            [[0.04, 0.0], [0.0, 0.01]],
            index=["AAA", "BBB"],
            columns=["AAA", "BBB"],
        ),
    )
    optimized = SimpleNamespace(
        expected_return=0.11,
        volatility=0.13,
        sharpe=0.70,
        weights=pd.Series({"AAA": 0.8, "BBB": 0.2}),
    )
    benchmark = pd.Series(
        [0.01, -0.02, 0.03],
        index=pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31"]),
    )

    table = _frontier_landmarks_table(
        request, stats, optimized, benchmark, rf=0.02
    ).set_index("kind")

    # Same optimizer mu/cov coordinate system: w'mu and sqrt(w'Sigma w).
    assert table.loc["provided", "expected_return"] == pytest.approx(0.096)
    assert table.loc["provided", "volatility"] == pytest.approx(
        (0.6**2 * 0.04 + 0.4**2 * 0.01) ** 0.5
    )
    assert table.loc["provided", "weight_AAA"] == pytest.approx(0.6)
    assert table.loc["optimized", "expected_return"] == pytest.approx(0.11)
    assert table.loc["optimized", "volatility"] == pytest.approx(0.13)
    assert table.loc["optimized", "sharpe"] == pytest.approx(0.70)
    assert table.loc["benchmark", "expected_return"] == pytest.approx(
        benchmark.mean() * 12.0
    )
    assert table.loc["benchmark", "volatility"] == pytest.approx(
        benchmark.std(ddof=1) * (12.0**0.5)
    )


def test_up_down_scatter_contains_each_aligned_month_not_summary_rows():
    index = pd.to_datetime(["2025-01-31", "2025-02-28", "2025-03-31"])
    benchmark = pd.Series([0.01, -0.02, 0.0], index=index)
    provided = SimpleNamespace(returns=pd.Series([0.015, -0.01, 0.005], index=index))
    optimized = SimpleNamespace(returns=pd.Series([0.012, -0.015, 0.004], index=index))

    table = _up_down_scatter_table(
        {"provided": provided, "optimized": optimized}, benchmark
    )

    assert len(table) == 6
    assert set(table["portfolio"]) == {"provided", "optimized"}
    provided_rows = table[table["portfolio"] == "provided"].reset_index(drop=True)
    assert list(provided_rows["market_type"]) == ["up", "down", "flat"]
    assert provided_rows.loc[0, "benchmark_return_pct"] == pytest.approx(1.0)
    assert provided_rows.loc[0, "portfolio_return_pct"] == pytest.approx(1.5)
    assert provided_rows.loc[0, "active_return_pct"] == pytest.approx(0.5)
    assert provided_rows.loc[1, "benchmark_return_pct"] == pytest.approx(-2.0)
    assert provided_rows.loc[1, "portfolio_return_pct"] == pytest.approx(-1.0)
