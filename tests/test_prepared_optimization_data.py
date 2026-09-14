from pathlib import Path

import pandas as pd

import portfolio_optimizer_kr.runner as runner_module
from portfolio_optimizer_kr.data.preparation import PreparedOptimizationData
from portfolio_optimizer_kr.runner import run_yaml


class PreparedDataFakeLoader:
    def load_many(self, assets, start=None, end=None):
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return {
            asset.symbol: pd.Series(
                [100.0, 101.0, 102.0, 103.0],
                index=index,
                name=asset.symbol,
            )
            for asset in assets
        }

    def load_economic_series(self, symbol, start=None, end=None):
        index = pd.date_range("2020-01-01", periods=3, freq="MS")
        return pd.Series([1.0, 2.0, 3.0], index=index, name=symbol)


def test_default_optimization_shares_prepared_dataset_with_rf_and_analyzer(
    tmp_path,
    monkeypatch,
):
    config = tmp_path / "run.yaml"
    config.write_text(
        """
product_mode: optimization
run_id: prepared-once
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    name: Asset A
    currency: USD
    provided_weight_pct: 50
  - symbol: B
    name: Asset B
    currency: USD
    provided_weight_pct: 50
risk_free:
  mode: us_3m_tbill
""",
        encoding="utf-8",
    )

    index = pd.date_range("2020-01-31", periods=3, freq="ME")
    prepared = PreparedOptimizationData(
        monthly_returns=pd.DataFrame(
            {
                "A": [0.01, 0.02, 0.01],
                "B": [0.00, 0.01, 0.02],
            },
            index=index,
        ),
        benchmark_returns=None,
    )
    calls = {"prepare": 0}
    seen = {}

    def fake_prepare(request, prices, usdkrw=None):
        calls["prepare"] += 1
        return prepared

    def should_not_reprepare(*args, **kwargs):
        raise AssertionError("monthly returns must come from PreparedOptimizationData")

    def fake_analyze(
        request,
        prices,
        usdkrw=None,
        annual_rf=None,
        prepared_data=None,
    ):
        seen["annual_rf"] = annual_rf
        seen["prepared_data"] = prepared_data
        return {"ok": True}

    def writer(result, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(runner_module, "prepare_optimization_data", fake_prepare)
    monkeypatch.setattr(runner_module, "prepare_monthly_returns", should_not_reprepare)
    monkeypatch.setattr(runner_module, "analyze_prices", fake_analyze)

    run_yaml(
        config,
        tmp_path / "runs",
        loader=PreparedDataFakeLoader(),
        writer=writer,
    )

    assert calls["prepare"] == 1
    assert seen["prepared_data"] is prepared
    assert seen["annual_rf"] == 0.02
