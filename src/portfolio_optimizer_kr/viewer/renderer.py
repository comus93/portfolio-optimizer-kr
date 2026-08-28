from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .builder import build_report_model
from .report_model import ReportModel

_REPORT_DATA_TOKEN = "__REPORT_DATA_JSON__"


def _json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def default_template_path() -> Path:
    return Path(__file__).resolve().parents[3] / "site" / "report-template.html"


def render_report(
    model: ReportModel,
    output_path: str | Path,
    *,
    template_path: str | Path | None = None,
) -> Path:
    template_file = Path(template_path) if template_path is not None else default_template_path()
    template = template_file.read_text(encoding="utf-8")
    if _REPORT_DATA_TOKEN not in template:
        raise ValueError(f"report template missing token: {_REPORT_DATA_TOKEN}")

    payload = json.dumps(
        _json_safe(model.to_dict()),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    html = template.replace(_REPORT_DATA_TOKEN, payload)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    directory = Path(run_dir)
    model = build_report_model(directory)
    target = Path(output_path) if output_path is not None else directory / "report.html"
    return render_report(model, target, template_path=template_path)
