from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer_kr.optimize import target_volatility


GOLDEN = Path(__file__).parent / "golden" / "pv" / "260828_PTF_maxRetVol15.md"
SYMBOLS = ("QQQ", "SPMO", "GDX", "GLD", "SLV", "AIA", "XLE", "PTF", "QLD")


def _cells(line: str) -> list[str]:
    return [cell.strip().replace("\\-", "-") for cell in line.split("|")[1:-1]]


def _golden_moments_and_bounds(text: str):
    section = text.split("#### Efficient Frontier Assets", 1)[1].split("#### Asset Correlations", 1)[0]
    rows = []
    for line in section.splitlines():
        cells = _cells(line)
        if len(cells) == 7 and cells[0].isdigit() and cells[2].endswith("%"):
            rows.append(cells)
    assert len(rows) >= 9
    rows = rows[:9]
    expected = pd.Series([float(row[2].rstrip("%")) / 100 for row in rows], index=SYMBOLS)
    volatility = pd.Series([float(row[3].rstrip("%")) / 100 for row in rows], index=SYMBOLS)
    bounds = {
        symbol: (
            float(row[5].rstrip("%")) / 100,
            float(row[6].rstrip("%")) / 100,
        )
        for symbol, row in zip(SYMBOLS, rows)
    }

    corr_section = text.split("#### Asset Correlations", 1)[1].split("#### Efficient Frontier", 1)[0]
    corr_rows = []
    for line in corr_section.splitlines():
        cells = _cells(line)
        if len(cells) == 11 and cells[1] in SYMBOLS:
            corr_rows.append([float(value) for value in cells[2:]])
    assert len(corr_rows) == 9
    correlation = pd.DataFrame(corr_rows, index=SYMBOLS, columns=SYMBOLS)
    return expected, volatility, correlation, bounds


def _published_weights(text: str) -> pd.Series:
    section = text.split("#### Maximum Return at 15.00% Volatility", 1)[1].split("#### Performance Summary", 1)[0]
    weights = pd.Series(0.0, index=SYMBOLS)
    for line in section.splitlines():
        cells = _cells(line)
        if len(cells) == 3 and cells[0] in SYMBOLS and cells[2].endswith("%"):
            weights[cells[0]] = float(cells[2].rstrip("%")) / 100
    return weights


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
    text = GOLDEN.read_text(encoding="utf-8")
    _, _, _, bounds = _golden_moments_and_bounds(text)

    assert bounds["QQQ"] == pytest.approx((0.0, 0.50))
    assert bounds["SPMO"] == pytest.approx((0.0, 0.50))
    assert bounds["PTF"] == pytest.approx((0.0, 0.30))
    assert bounds["QLD"] == pytest.approx((0.0, 0.30))


@pytest.mark.golden
def test_pv_published_weights_evaluate_near_displayed_1489_vol_with_rounded_moments():
    text = GOLDEN.read_text(encoding="utf-8")
    expected, volatility, correlation, _ = _golden_moments_and_bounds(text)
    published = _published_weights(text)
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
    text = GOLDEN.read_text(encoding="utf-8")
    expected, volatility, correlation, bounds = _golden_moments_and_bounds(text)
    published = _published_weights(text)
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
