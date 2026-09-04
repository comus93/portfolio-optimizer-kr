from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.runner import run_yaml


class FakeLoader:
    def __init__(self):
        self.many_call = None
        self.series_call = None
        self.economic_call = None
        self.economic_values = [1.0, 2.0, 3.0]

    def load_many(self, assets, start=None, end=None):
        assets = list(assets)
        self.many_call = ([asset.symbol for asset in assets], start, end)
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return {
            asset.symbol: pd.Series([100.0, 101.0, 102.0, 103.0], index=index, name=asset.symbol)
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        self.series_call = (symbol, start, end)
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return pd.Series([1100.0, 1110.0, 1120.0, 1130.0], index=index, name=symbol)

    def load_economic_series(self, symbol, start=None, end=None):
        self.economic_call = (symbol, start, end)
        index = pd.date_range("2020-01-01", periods=len(self.economic_values), freq="MS")
        return pd.Series(self.economic_values, index=index, name=symbol)


def test_run_yaml_uses_prior_month_warmup_and_preserves_input(tmp_path):
    config = tmp_path / "run.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: demo-run
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    currency: USD
    provided_weight_pct: 50
benchmark:
  symbol: BM
  currency: USD
risk_free:
  mode: fixed
  annual_rate_pct: 1
""",
        encoding="utf-8",
    )
    loader = FakeLoader()
    calls = {}

    def analyze(request, prices, usdkrw=None, annual_rf=None):
        calls["request"] = request
        calls["prices"] = prices
        calls["usdkrw"] = usdkrw
        calls["annual_rf"] = annual_rf
        return {"ok": True}

    def writer(result, output_dir):
        calls["result"] = result
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "result.json").write_text("{}\n", encoding="utf-8")

    output = run_yaml(
        config,
        tmp_path / "runs",
        loader=loader,
        analyze_fn=analyze,
        writer=writer,
    )

    assert output == tmp_path / "runs" / "demo-run"
    assert loader.many_call == (["A", "B", "BM"], "2019-12-01", "2020-03-31")
    assert loader.economic_call is None
    assert calls["usdkrw"] is None
    assert calls["annual_rf"] is None
    assert (output / "input.yaml").read_text(encoding="utf-8") == config.read_text(encoding="utf-8")


def test_default_risk_free_loads_tb3ms_for_effective_return_months(tmp_path):
    config = tmp_path / "run.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: tbill-default
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    currency: USD
    provided_weight_pct: 50
""",
        encoding="utf-8",
    )
    loader = FakeLoader()
    seen = {}

    def analyze(request, prices, usdkrw=None, annual_rf=None):
        seen["mode"] = request.risk_free.mode
        seen["annual_rf"] = annual_rf
        return {"ok": True}

    def writer(result, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    run_yaml(
        config,
        tmp_path / "runs",
        loader=loader,
        analyze_fn=analyze,
        writer=writer,
    )

    assert str(seen["mode"]) == "us_3m_tbill"
    assert seen["annual_rf"] == pytest.approx(0.02)
    assert loader.economic_call == (
        "FRED:TB3MS",
        "2020-01-01",
        "2020-03-31",
    )


def test_us_3m_tbill_requires_every_effective_return_month(tmp_path):
    config = tmp_path / "run.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: tbill-gap
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    currency: USD
    provided_weight_pct: 50
risk_free:
  mode: us_3m_tbill
""",
        encoding="utf-8",
    )
    loader = FakeLoader()
    loader.economic_values = [1.0, 2.0]

    with pytest.raises(DataValidationError, match="missing required months"):
        run_yaml(
            config,
            tmp_path / "runs",
            loader=loader,
            analyze_fn=lambda *a, **k: {},
            writer=lambda *a, **k: None,
        )


def test_mixed_currency_run_requires_explicit_fx_symbol(tmp_path):
    config = tmp_path / "mixed.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: mixed
assets:
  - symbol: KR
    currency: KRW
    provided_weight_pct: 50
  - symbol: US
    currency: USD
    provided_weight_pct: 50
risk_free:
  mode: fixed
  annual_rate_pct: 0
""",
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="usdkrw_symbol"):
        run_yaml(config, tmp_path / "runs", loader=FakeLoader(), analyze_fn=lambda *a, **k: {})


def test_mixed_currency_run_loads_configured_fx_series(tmp_path):
    config = tmp_path / "mixed.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: mixed
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: KR
    currency: KRW
    provided_weight_pct: 50
  - symbol: US
    currency: USD
    provided_weight_pct: 50
risk_free:
  mode: fixed
  annual_rate_pct: 0
fx:
  usdkrw_symbol: USDKRW_TEST
""",
        encoding="utf-8",
    )
    loader = FakeLoader()
    seen = {}

    def analyze(request, prices, usdkrw=None, annual_rf=None):
        seen["usdkrw"] = usdkrw
        return {"ok": True}

    def writer(result, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    run_yaml(
        config,
        tmp_path / "runs",
        loader=loader,
        analyze_fn=analyze,
        writer=writer,
    )
    assert loader.series_call == ("USDKRW_TEST", "2019-12-01", "2020-03-31")
    assert seen["usdkrw"] is not None
