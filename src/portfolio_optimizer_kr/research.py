from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from portfolio_optimizer_kr.config import ConfigValidationError, request_from_config
from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.runner import execute_run


class ResearchControlError(ValueError):
    """Raised when the tracked research execution pointer is invalid."""


@dataclass(frozen=True)
class ResearchTarget:
    repo_root: Path
    experiment: Path
    study: Path

    @property
    def experiment_relative(self) -> Path:
        return self.experiment.relative_to(self.repo_root)

    @property
    def study_relative(self) -> Path:
        return self.study.relative_to(self.repo_root)


def _load_mapping(path: Path, *, label: str) -> dict[str, Any]:
    if not path.exists():
        raise ResearchControlError(f"{label} does not exist: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ResearchControlError(f"{label} root must be a mapping")
    return dict(loaded)


def resolve_control_target(
    repo_root: str | Path = ".",
    control_path: str | Path = "control/execute.yaml",
) -> ResearchTarget:
    root = Path(repo_root).resolve()
    control = Path(control_path)
    if not control.is_absolute():
        control = root / control

    payload = _load_mapping(control, label="control file")
    target_value = str(payload.get("target") or "").strip()
    if not target_value:
        raise ResearchControlError("control file requires target")

    target = (root / target_value).resolve()
    if not target.is_relative_to(root):
        raise ResearchControlError("target must stay inside repository root")
    if not target.exists() or not target.is_file():
        raise ResearchControlError(f"target does not exist: {target_value}")
    if target.suffix.lower() not in {".yaml", ".yml"}:
        raise ResearchControlError("target must be a YAML file")

    relative = target.relative_to(root)
    parts = relative.parts
    if len(parts) < 4 or parts[0] != "studies" or parts[2] != "experiments":
        raise ResearchControlError(
            "target must be under studies/<study-id>/experiments/"
        )

    study = root / "studies" / parts[1] / "study.md"
    return ResearchTarget(repo_root=root, experiment=target, study=study)


def next_run_id(output_root: str | Path, *, day: date | None = None) -> str:
    root = Path(output_root)
    prefix = (day or date.today()).strftime("%Y%m%d")
    sequence = 1
    while (root / f"{prefix}-{sequence:04d}").exists():
        sequence += 1
    return f"{prefix}-{sequence:04d}"


def execute_controlled_experiment(
    repo_root: str | Path = ".",
    control_path: str | Path = "control/execute.yaml",
    output_root: str | Path = "runs",
    *,
    loader: FDRLoader | None = None,
    annual_rf: float | None = None,
    analyze_fn: Callable[..., dict[str, Any]] | None = None,
    writer: Callable[[dict[str, Any], str | Path], None] | None = None,
) -> Path:
    target = resolve_control_target(repo_root, control_path)
    output = Path(output_root)
    if not output.is_absolute():
        output = target.repo_root / output

    effective = _load_mapping(target.experiment, label="experiment")
    if not str(effective.get("run_id") or "").strip():
        effective["run_id"] = next_run_id(output)

    try:
        spec = request_from_config(effective)
    except ConfigValidationError:
        raise

    output_dir = execute_run(
        spec,
        output,
        loader=loader,
        annual_rf=annual_rf,
        analyze_fn=analyze_fn,
        writer=writer,
    )

    (output_dir / "input.yaml").write_text(
        yaml.safe_dump(effective, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    context = {
        "run_id": spec.request.run_id,
        "study": target.study_relative.as_posix(),
        "experiment": target.experiment_relative.as_posix(),
    }
    (output_dir / "context.yaml").write_text(
        yaml.safe_dump(context, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return output_dir
