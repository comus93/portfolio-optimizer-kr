from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
import yaml

from portfolio_optimizer_kr.research import (
    DEFAULT_RESEARCH_BENCHMARK,
    ResearchControlError,
    execute_controlled_experiment,
    next_run_id,
    resolve_control_target,
)


EXPERIMENT_YAML = """
analysis_period:
  start: 2020-01-01
  end: 2020-03-31
assets:
  - symbol: A
    name: Asset A
    currency: USD
    provided_weight_pct: 50
    min_weight_pct: 0
    max_weight_pct: 100
  - symbol: B
    name: Asset B
    currency: USD
    provided_weight_pct: 50
    min_weight_pct: 0
    max_weight_pct: 100
optimization:
  objective: max_sharpe
  frontier_points: 10
portfolio:
  rebalancing_period: monthly
risk_free:
  mode: fixed
  annual_rate_pct: 1
"""


class FakeLoader:
    def load_many(self, assets, start=None, end=None):
        index = pd.date_range("2019-12-31", periods=4, freq="ME")
        return {
            asset.symbol: pd.Series(
                [100.0, 101.0, 102.0, 103.0], index=index, name=asset.symbol
            )
            for asset in assets
        }

    def load_series(self, symbol, start=None, end=None):
        raise AssertionError("FX should not be requested for this fixture")


def _make_repo(tmp_path: Path, experiment_text: str = EXPERIMENT_YAML) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    experiment = repo / "studies" / "demo-study" / "experiments" / "001-base-r01.yaml"
    experiment.parent.mkdir(parents=True)
    experiment.write_text(experiment_text.lstrip(), encoding="utf-8")
    (repo / "studies" / "demo-study" / "study.md").write_text(
        "# Demo Study\n", encoding="utf-8"
    )
    control = repo / "control" / "execute.yaml"
    control.parent.mkdir(parents=True)
    control.write_text(
        "target: studies/demo-study/experiments/001-base-r01.yaml\n",
        encoding="utf-8",
    )
    return repo, experiment


def _analyze(request, prices, usdkrw=None, annual_rf=None):
    return {"run_id": request.run_id, "ok": True}


def _writer(result, output_dir):
    Path(output_dir, "result.json").write_text("{}\n", encoding="utf-8")


def test_resolve_control_target_returns_research_artifacts(tmp_path):
    repo, experiment = _make_repo(tmp_path)

    target = resolve_control_target(repo)

    assert target.experiment == experiment.resolve()
    assert target.experiment_relative.as_posix() == (
        "studies/demo-study/experiments/001-base-r01.yaml"
    )
    assert target.study_relative.as_posix() == "studies/demo-study/study.md"


def test_resolve_control_target_requires_control_file(tmp_path):
    with pytest.raises(ResearchControlError, match="control file does not exist"):
        resolve_control_target(tmp_path)


def test_resolve_control_target_requires_target_field(tmp_path):
    repo, _ = _make_repo(tmp_path)
    (repo / "control" / "execute.yaml").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ResearchControlError, match="requires target"):
        resolve_control_target(repo)


def test_resolve_control_target_rejects_missing_target(tmp_path):
    repo, _ = _make_repo(tmp_path)
    (repo / "control" / "execute.yaml").write_text(
        "target: studies/demo-study/experiments/missing.yaml\n", encoding="utf-8"
    )

    with pytest.raises(ResearchControlError, match="target does not exist"):
        resolve_control_target(repo)


def test_resolve_control_target_rejects_non_research_yaml(tmp_path):
    repo, _ = _make_repo(tmp_path)
    other = repo / "configs" / "other.yaml"
    other.parent.mkdir(parents=True)
    other.write_text(EXPERIMENT_YAML.lstrip(), encoding="utf-8")
    (repo / "control" / "execute.yaml").write_text(
        "target: configs/other.yaml\n", encoding="utf-8"
    )

    with pytest.raises(ResearchControlError, match="studies/<study-id>/experiments"):
        resolve_control_target(repo)


def test_resolve_control_target_rejects_path_traversal(tmp_path):
    repo, _ = _make_repo(tmp_path)
    outside = tmp_path / "outside.yaml"
    outside.write_text(EXPERIMENT_YAML.lstrip(), encoding="utf-8")
    (repo / "control" / "execute.yaml").write_text(
        "target: ../outside.yaml\n", encoding="utf-8"
    )

    with pytest.raises(ResearchControlError, match="inside repository root"):
        resolve_control_target(repo)


def test_next_run_id_uses_next_available_daily_sequence(tmp_path):
    runs = tmp_path / "runs"
    (runs / "20260828-0001").mkdir(parents=True)
    (runs / "20260828-0002").mkdir()

    assert next_run_id(runs, day=date(2026, 8, 28)) == "20260828-0003"


def test_controlled_execution_generates_effective_input_and_context(tmp_path):
    repo, _ = _make_repo(tmp_path)

    output = execute_controlled_experiment(
        repo_root=repo,
        loader=FakeLoader(),
        analyze_fn=_analyze,
        writer=_writer,
    )

    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))
    context = yaml.safe_load((output / "context.yaml").read_text(encoding="utf-8"))

    assert output.parent == repo / "runs"
    assert effective["run_id"] == output.name
    assert effective["benchmark"] == DEFAULT_RESEARCH_BENCHMARK
    assert context == {
        "run_id": output.name,
        "study": "studies/demo-study/study.md",
        "experiment": "studies/demo-study/experiments/001-base-r01.yaml",
    }
    assert (output / "result.json").exists()


def test_explicit_benchmark_is_preserved(tmp_path):
    experiment = (
        EXPERIMENT_YAML.lstrip()
        + "\nbenchmark:\n  symbol: QQQ\n  name: Invesco QQQ Trust\n  currency: USD\n"
    )
    repo, _ = _make_repo(tmp_path, experiment)

    output = execute_controlled_experiment(
        repo_root=repo,
        loader=FakeLoader(),
        analyze_fn=_analyze,
        writer=_writer,
    )

    effective = yaml.safe_load((output / "input.yaml").read_text(encoding="utf-8"))
    assert effective["benchmark"]["symbol"] == "QQQ"


def test_same_experiment_can_be_executed_twice_as_distinct_runs(tmp_path):
    repo, _ = _make_repo(tmp_path)

    first = execute_controlled_experiment(
        repo_root=repo,
        loader=FakeLoader(),
        analyze_fn=_analyze,
        writer=_writer,
    )
    second = execute_controlled_experiment(
        repo_root=repo,
        loader=FakeLoader(),
        analyze_fn=_analyze,
        writer=_writer,
    )

    assert first != second
    assert first.exists()
    assert second.exists()


def test_explicit_run_id_is_preserved_and_never_silently_overwritten(tmp_path):
    repo, _ = _make_repo(tmp_path, "run_id: fixed-run\n" + EXPERIMENT_YAML.lstrip())

    first = execute_controlled_experiment(
        repo_root=repo,
        loader=FakeLoader(),
        analyze_fn=_analyze,
        writer=_writer,
    )
    assert first.name == "fixed-run"

    with pytest.raises(FileExistsError, match="run output already exists"):
        execute_controlled_experiment(
            repo_root=repo,
            loader=FakeLoader(),
            analyze_fn=_analyze,
            writer=_writer,
        )
