import pandas as pd
import pytest

from portfolio_optimizer_kr.data import (
    align_common_prices,
    convert_usd_price_to_krw,
    month_end_prices,
    select_canonical_price,
    to_monthly_returns,
)
from portfolio_optimizer_kr.errors import DataValidationError


def test_adj_close_has_priority():
    index = pd.to_datetime(["2024-01-01", "2024-01-02"])
    frame = pd.DataFrame({"Close": [100, 200], "Adj Close": [10, 20]}, index=index)
    assert select_canonical_price(frame).tolist() == [10.0, 20.0]


def test_common_period_is_intersection():
    a = pd.Series([1, 2, 3], index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]))
    b = pd.Series([4, 5, 6], index=pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]))
    out = align_common_prices({"A": a, "B": b})
    assert out.index.tolist() == list(pd.to_datetime(["2024-01-02", "2024-01-03"]))


def test_month_end_uses_last_available_observation():
    index = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-27", "2024-02-29"])
    prices = pd.DataFrame({"A": [10, 11, 12, 13]}, index=index)
    out = month_end_prices(prices)
    assert out["A"].tolist() == [11, 13]


def test_monthly_return_is_simple_return():
    prices = pd.DataFrame({"A": [100.0, 110.0, 99.0]}, index=pd.date_range("2024-01-31", periods=3, freq="ME"))
    returns = to_monthly_returns(prices)
    assert returns.iloc[0, 0] == pytest.approx(0.10)
    assert returns.iloc[1, 0] == pytest.approx(-0.10)


def test_fx_alignment_never_uses_future_rate():
    price = pd.Series([10.0, 10.0], index=pd.to_datetime(["2024-01-02", "2024-01-04"]), name="US")
    fx = pd.Series([1300.0, 1400.0], index=pd.to_datetime(["2024-01-01", "2024-01-03"]))
    out = convert_usd_price_to_krw(price, fx)
    assert out.tolist() == [13000.0, 14000.0]


def test_fx_requires_prior_observation():
    price = pd.Series([10.0], index=pd.to_datetime(["2024-01-01"]), name="US")
    fx = pd.Series([1300.0], index=pd.to_datetime(["2024-01-02"]))
    with pytest.raises(DataValidationError):
        convert_usd_price_to_krw(price, fx)
