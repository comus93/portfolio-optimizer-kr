from pathlib import Path

import pytest

from portfolio_optimizer_kr.config.yaml import ConfigValidationError, load_run_config
from portfolio_optimizer_kr.models import OptimizationObjective, RebalancingPeriod, RiskFreeMode


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "run.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_yaml_percent_fields_convert_to_canonical_request(tmp_path):
    path = _write(
        tmp_path,
        """
run_id: demo
analysis_period:
  start: 2020-01-01
  end: 2024-12-31
assets:
  - symbol: QQQ
    currency: usd
    provided_weight_pct: 60
    min_weight_pct: 10
    max_weight_pct: 80
  - symbol: GLD
    currency: USD
    provided_weight_pct: 40
    min_weight_pct: 0
    max_weight_pct: 60
benchmark:
  symbol: SPY
  currency: USD
optimization:
  objective: max_sharpe
  frontier_points: 25
portfolio:
  rebalancing_period: yearly
risk_free:
  mode: fixed
  annual_rate_pct: 2.5
fx: {}
""",
    )
    spec = load_run_config(path)
    request = spec.request

    assert request.run_id == "demo"
    assert request.start == "2020-01-01"
    assert request.end == "2024-12-31"
    assert request.assets[0].currency == "USD"
    assert request.assets[0].min_weight == pytest.approx(0.10)
    assert request.assets[0].max_weight == pytest.approx(0.80)
    assert request.provided_weights == pytest.approx({"QQQ": 0.60, "GLD": 0.40})
    assert request.benchmark.symbol == "SPY"
    assert request.objective is OptimizationObjective.MAX_SHARPE
    assert request.rebalancing is RebalancingPeriod.YEARLY
    assert request.risk_free.mode is RiskFreeMode.FIXED
    assert request.risk_free.annual_rate == pytest.approx(0.025)
    assert request.frontier_points == 25


def test_yaml_rejects_partial_or_non_100_provided_weights(tmp_path):
    partial = _write(
        tmp_path,
        """
run_id: bad
assets:
  - symbol: A
    provided_weight_pct: 50
  - symbol: B
risk_free:
  mode: fixed
  annual_rate_pct: 0
""",
    )
    with pytest.raises(ConfigValidationError, match="every asset"):
        load_run_config(partial)

    non_100 = _write(
        tmp_path,
        """
run_id: bad
assets:
  - symbol: A
    provided_weight_pct: 40
  - symbol: B
    provided_weight_pct: 40
risk_free:
  mode: fixed
  annual_rate_pct: 0
""",
    )
    with pytest.raises(ConfigValidationError, match="sum to 100"):
        load_run_config(non_100)


def test_target_volatility_requires_explicit_percent_value(tmp_path):
    path = _write(
        tmp_path,
        """
run_id: target
assets:
  - symbol: A
  - symbol: B
optimization:
  objective: target_volatility
risk_free:
  mode: fixed
  annual_rate_pct: 0
""",
    )
    with pytest.raises(ConfigValidationError, match="target_volatility_pct"):
        load_run_config(path)
