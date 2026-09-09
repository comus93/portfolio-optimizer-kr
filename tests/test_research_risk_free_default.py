from pathlib import Path

import pandas as pd
import pytest
import yaml

from portfolio_optimizer_kr.models import RiskFreeMode
from portfolio_optimizer_kr.research import (
    DEFAULT_RESEARCH_RISK_FREE,
    _apply_research_defaults,
    execute_controlled_experiment,
)


PINNED_RF = 0.038394827586206895


class NoEconomicSeriesLoader:
    def load_many(self, assets, start=None, end=None):
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return {
            asset.symbol: pd.Series(
                [100.0, 101.0, 102.0, 103.0], index=index, name=asset.symbol
            )
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        raise AssertionError("FX should not be required")

    def load_economic_series(self, symbol, start=None, end=None):
        raise AssertionError("default research RF must not fetch an economic series")


def _make_repo(tmp_path: Path, experiment_text: str) -> Path:
    repo = tmp_path / "repo"
    experiment = repo / "studies" / "rf-study" / "experiments" / "001-base.yaml"
    experiment.parent.mkdir(parents=True)
    experiment.write_text(experiment_text.lstrip(), encoding="utf-8")
    (repo / "studies" / "rf-study" / "study.md").write_text(
        "# RF Study\n", encoding="utf-8"
    )
    control = repo / "control" / "execute.yaml"
    control.parent.mkdir(parents=True)
    control.write_text(
        "target: studies/rf-study/experiments/001-base.yaml\n",
        encoding="utf-8",
    )
    return repo


def _run_and_capture(tmp_path: Path, experiment_text: str):
    repo = _make_repo(tmp_path, experiment_text)
    seen = {}

    def analyze(request, prices, usdkrw=None, annual_rf=None):
        seen["request"] = request
        seen["annual_rf"] = annual_rf
        return {"ok": True}

    output = execute_controlled_experiment(
        repo_root=repo,
        loader=NoEconomicSeriesLoader(),
        analyze_fn=analyze,
        writer=lambda result, output_dir: None,
    )
    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))
    return seen, effective


def test_research_default_constant_is_pinned_us3m_value():
    assert DEFAULT_RESEARCH_RISK_FREE == {
        "mode": "fixed",
        "annual_rate_pct": 3.8394827586206895,
    }


def test_optimization_research_without_user_rf_materializes_pinned_value(tmp_path):
    seen, effective = _run_and_capture(
        tmp_path,
        """
product_mode: optimization
assets:
  - symbol: A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    currency: USD
    provided_weight_pct: 50
""",
    )

    assert seen["request"].risk_free.mode is RiskFreeMode.FIXED
    assert seen["request"].risk_free.annual_rate == pytest.approx(PINNED_RF)
    assert seen["annual_rf"] is None
    assert effective["risk_free"] == DEFAULT_RESEARCH_RISK_FREE


def test_backtest_research_without_user_rf_materializes_same_pinned_value(tmp_path):
    seen, effective = _run_and_capture(
        tmp_path,
        """
product_mode: backtest
assets:
  - symbol: A
    currency: USD
  - symbol: B
    currency: USD
portfolios:
  - weights_pct:
      A: 50
      B: 50
""",
    )

    assert seen["request"].risk_free.mode is RiskFreeMode.FIXED
    assert seen["request"].risk_free.annual_rate == pytest.approx(PINNED_RF)
    assert seen["annual_rf"] is None
    assert effective["risk_free"] == DEFAULT_RESEARCH_RISK_FREE


def test_explicit_user_rf_is_preserved():
    dynamic = _apply_research_defaults(
        {
            "product_mode": "optimization",
            "risk_free": {"mode": "us_3m_tbill"},
        }
    )
    custom_fixed = _apply_research_defaults(
        {
            "product_mode": "backtest",
            "risk_free": {"mode": "fixed", "annual_rate_pct": 2.25},
        }
    )

    assert dynamic["risk_free"] == {"mode": "us_3m_tbill"}
    assert custom_fixed["risk_free"] == {"mode": "fixed", "annual_rate_pct": 2.25}
