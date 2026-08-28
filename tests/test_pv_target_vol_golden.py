import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer_kr.golden import TARGET_VOL_SYMBOLS, load_target_vol_golden
from portfolio_optimizer_kr.optimize import target_volatility


from pathlib import Path


GOLDEN = Path(__file__).parent / "golden" / "pv" / "260828_PTF_maxRetVol15.md"
SYMBOLS = TARGET_VOL_SYMBOLS


@pytest.mark.golden
def test_pv_target_volatility_golden_is_present_and_identifiable():
    assert GOLDEN.is_file()
    text = GOLDEN.read_text(encoding="utf-8")
    for token in [
        "maximize return subject to 15.00% targeted annual volatility",
        "Maximum Return at 15.00% Volatility",
        "18.76%",
        "14.89%",
        "26.24%",
    ]:
        assert token in text


@pytest.mark.golden
def test_pv_target_volatility_golden_has_distinct_30pct_ptf_qld_caps():
    bounds = load_target_vol_golden(GOLDEN).bounds

    assert bounds["QQQ"] == pytest.approx((0.0, 0.50))
    assert bounds["SPMO"] == pytest.approx((0.0, 0.50))
    assert bounds["PTF"] == pytest.approx((0.0, 0.30))
    assert bounds["QLD"] == pytest.approx((0.0, 0.30))


@pytest.mark.golden
def test_pv_published_weights_evaluate_near_displayed_1489_vol_with_rounded_moments():
    golden = load_target_vol_golden(GOLDEN)
    expected, volatility, correlation = golden.expected_returns, golden.volatilities, golden.correlation
    published = golden.published_weights
    covariance = pd.DataFrame(
        np.outer(volatility, volatility) * correlation.to_numpy(),
        index=SYMBOLS,
        columns=SYMBOLS,
    )

    expected_return = float(published.to_numpy() @ expected.to_numpy())
    published_vol = float(np.sqrt(published.to_numpy() @ covariance.to_numpy() @ published.to_numpy()))

    assert published.sum() == pytest.approx(1.0, abs=1e-8)
    assert expected_return == pytest.approx(0.18755, abs=0.0003)
    assert published_vol == pytest.approx(0.14899, abs=0.0003)


@pytest.mark.golden
def test_target_volatility_solver_is_in_pv_rounded_moment_neighborhood():
    golden = load_target_vol_golden(GOLDEN)
    expected, volatility, correlation, bounds = golden.expected_returns, golden.volatilities, golden.correlation, golden.bounds
    published = golden.published_weights
    covariance = pd.DataFrame(
        np.outer(volatility, volatility) * correlation.to_numpy(),
        index=SYMBOLS,
        columns=SYMBOLS,
    )

    result = target_volatility(expected, covariance, 0.15, bounds=bounds)

    # Public PV moments/correlations/weights are rounded, so this is a
    # neighborhood parity test rather than an exact equality assertion.
    assert result.volatility <= 0.15005
    assert result.volatility >= 0.1490
    assert result.expected_return == pytest.approx(0.1884, abs=0.0020)
    assert np.max(np.abs(result.weights.to_numpy() - published.to_numpy())) < 0.015
    assert result.weights["GLD"] == pytest.approx(0.30, abs=5e-4)
    assert result.weights[["GDX", "SLV", "AIA", "PTF"]].sum() < 0.01
