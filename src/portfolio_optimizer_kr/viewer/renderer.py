from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .builder import build_report_model
from .report_model import ReportModel

_REPORT_DATA_TOKEN = "__REPORT_DATA_JSON__"

_VISUAL_IDENTITY_SCRIPT = r"""
<script id="report-legend-identity">
(() => {
  const data = window.PORTFOLIO_REPORT_DATA || {};
  const BLUE = '#2563eb';
  const PURPLE = '#7c3aed';
  const GRAY = '#64748b';
  const ORANGE = '#f97316';
  const RED = '#e11d48';

  const paintLegend = (legend, colorList) => {
    if (!legend) return;
    legend.querySelectorAll('span').forEach((span, index) => {
      const color = colorList[index];
      if (color) span.style.setProperty('--color', color);
    });
  };

  const paintSectionLegends = (sectionId, colorList) => {
    document.querySelectorAll(`#${sectionId} .legend`).forEach(
      legend => paintLegend(legend, colorList),
    );
  };

  // These bar/line renderers use fixed series colors. Keep the legend tied to
  // the actual plotted series rather than recomputing fallback colors from
  // human-readable legend labels.
  paintSectionLegends('annual-returns', [BLUE, PURPLE, GRAY]);
  paintSectionLegends('annualized-active-return', [BLUE, PURPLE]);
  paintSectionLegends('rolling-active-return', [BLUE, ORANGE]);
  paintSectionLegends('up-down-market', [BLUE, RED]);
  paintSectionLegends('annual-asset-returns', [BLUE]);

  // Efficient Frontier uses three visual identities in the current renderer:
  // curve points/line = blue, individual asset markers = gray,
  // portfolio/benchmark/objective landmarks = red.
  const frontierAssets = new Set(
    (data.frontier_assets || []).map(asset => String(asset.symbol)),
  );
  document.querySelectorAll('#efficient-frontier .legend span').forEach(span => {
    const label = (span.textContent || '').trim();
    const color = label === 'Efficient Frontier'
      ? BLUE
      : frontierAssets.has(label)
        ? GRAY
        : RED;
    span.style.setProperty('--color', color);
  });
})();
</script>
""".strip()


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


def _inject_visual_identity_script(html: str) -> str:
    closing_body = "</body>"
    if closing_body not in html:
        raise ValueError("report template missing closing body tag")
    return html.replace(
        closing_body,
        f"  {_VISUAL_IDENTITY_SCRIPT}\n{closing_body}",
        1,
    )


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
    html = _inject_visual_identity_script(html)

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
