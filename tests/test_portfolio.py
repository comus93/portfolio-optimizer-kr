import pandas as pd
import pytest

from portfolio_optimizer_kr.models import RebalancingPeriod
from portfolio_optimizer_kr.portfolio import build_portfolio_path


def test_monthly_rebalancing_resets_target_weights():
    returns = pd.DataFrame(
        {"A": [0.10, 0.10], "B": [0.0, 0.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29"]),
    )
    path = build_portfolio_path(returns, {"A": 0.5, "B": 0.5}, RebalancingPeriod.MONTHLY)
    assert path.returns.tolist() == pytest.approx([0.05, 0.05])
    assert path.weights.iloc[1]["A"] == pytest.approx(0.5)


def test_yearly_rebalancing_allows_intra_year_weight_drift():
    returns = pd.DataFrame(
        {"A": [0.10, 0.10], "B": [0.0, 0.0]},
        index=pd.to_datetime(["2024-01-31", "2024-02-29"]),
    )
    path = build_portfolio_path(returns, {"A": 0.5, "B": 0.5}, RebalancingPeriod.YEARLY)
    expected_a_weight_feb = 0.55 / 1.05
    assert path.weights.iloc[1]["A"] == pytest.approx(expected_a_weight_feb)
    assert path.returns.iloc[1] == pytest.approx(expected_a_weight_feb * 0.10)


def test_yearly_rebalancing_resets_at_new_calendar_year():
    returns = pd.DataFrame(
        {"A": [0.10, 0.10], "B": [0.0, 0.0]},
        index=pd.to_datetime(["2024-12-31", "2025-01-31"]),
    )
    path = build_portfolio_path(returns, {"A": 0.5, "B": 0.5}, RebalancingPeriod.YEARLY)
    assert path.weights.iloc[1]["A"] == pytest.approx(0.5)
