import pytest

from portfolio_optimizer_kr.config import ConfigValidationError, request_from_config


def _base_config():
    return {
        "product_mode": "backtest",
        "run_id": "scope-test",
        "assets": [
            {"symbol": "A", "currency": "USD"},
            {"symbol": "B", "currency": "USD"},
        ],
        "portfolios": [
            {"weights_pct": {"A": 50, "B": 50}},
        ],
        "risk_free": {"mode": "fixed", "annual_rate_pct": 0},
    }


def test_portfolio_specific_rebalancing_is_rejected_in_v1():
    config = _base_config()
    config["portfolios"][0]["rebalancing"] = "yearly"

    with pytest.raises(ConfigValidationError, match="run-level"):
        request_from_config(config)


@pytest.mark.parametrize(
    "field",
    [
        "cashflows",
        "leverage",
        "display_income",
        "style_analysis",
        "factor_regression",
        "regime_performance",
    ],
)
def test_excluded_v1_advanced_setting_is_rejected(field):
    config = _base_config()
    config[field] = True

    with pytest.raises(ConfigValidationError, match="not supported in backtest v1"):
        request_from_config(config)
