from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class RunArtifacts:
    run_dir: Path
    result: dict[str, Any]
    parity: dict[str, Any] | None
    review: dict[str, pd.DataFrame]
    raw: dict[str, pd.DataFrame]

    def table(self, name: str, layer: str = "review") -> pd.DataFrame:
        tables = self.review if layer == "review" else self.raw if layer == "raw" else None
        if tables is None:
            raise ValueError("layer must be 'review' or 'raw'")
        if name not in tables:
            raise KeyError(f"{layer} table not found: {name}")
        return tables[name]


def _read_tables(directory: Path) -> dict[str, pd.DataFrame]:
    if not directory.is_dir():
        return {}
    return {
        path.stem: pd.read_csv(path)
        for path in sorted(directory.glob("*.csv"))
        if path.is_file()
    }


def load_run_artifacts(run_dir: str | Path) -> RunArtifacts:
    directory = Path(run_dir)
    result_path = directory / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"missing canonical result: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))

    parity_path = directory / "parity.json"
    parity = (
        json.loads(parity_path.read_text(encoding="utf-8"))
        if parity_path.is_file()
        else None
    )
    return RunArtifacts(
        run_dir=directory,
        result=result,
        parity=parity,
        review=_read_tables(directory / "review"),
        raw=_read_tables(directory / "raw"),
    )
