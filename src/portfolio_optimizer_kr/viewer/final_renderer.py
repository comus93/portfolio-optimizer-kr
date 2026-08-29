from __future__ import annotations

import math
from dataclasses import replace
from pathlib import Path
from typing import Any

from .builder import build_report_model
from .feedback_v4 import render_report as _render_feedback_v4
from .report_model import FrontierAssetPoint, ReportModel


_SERIES_CONTRAST_SCRIPT = r"""
<script id="report-series-contrast">
(() => {
  const SECONDARY_OLD = '#7c3aed';
  const SECONDARY_GREEN = '#22c55e';
  const TARGET_SECTIONS = [
    'portfolio-growth',
    'annual-returns',
    'annualized-active-return',
    'drawdown-chart',
    'rolling-returns-3y',
    'rolling-returns-5y',
  ];

  const recolor = () => {
    TARGET_SECTIONS.forEach(id => {
      const host = document.getElementById(id);
      if (!host) return;

      host.querySelectorAll('svg [stroke], svg [fill]').forEach(node => {
        const stroke = (node.getAttribute('stroke') || '').trim().toLowerCase();
        const fill = (node.getAttribute('fill') || '').trim().toLowerCase();
        if (stroke === SECONDARY_OLD) node.setAttribute('stroke', SECONDARY_GREEN);
        if (fill === SECONDARY_OLD) node.setAttribute('fill', SECONDARY_GREEN);
      });

      host.querySelectorAll('.legend span').forEach(span => {
        const color = span.style.getPropertyValue('--color').trim().toLowerCase();
        if (color === SECONDARY_OLD) {
          span.style.setProperty('--color', SECONDARY_GREEN);
        }
      });
    });
  };

  // feedback_v4 renders after window.load with a short delay. Apply this
  // corrective presentation pass afterward so the final DOM owns the color.
  if (document.readyState === 'complete') setTimeout(recolor, 60);
  else window.addEventListener('load', () => setTimeout(recolor, 60), {once:true});
})();
</script>
"""


def _effective_risk_free_pct(model: ReportModel) -> float | None:
    configuration: Any = model.metadata.get("configuration", {})
    risk_free = configuration.get("risk_free", {}) if isinstance(configuration, dict) else {}
    value = risk_free.get("effective_annual_rate") if isinstance(risk_free, dict) else None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number * 100.0 if math.isfinite(number) else None


def _normalize_frontier_assets(model: ReportModel) -> ReportModel:
    rf_pct = _effective_risk_free_pct(model)
    normalized: list[FrontierAssetPoint] = []
    changed = False
    for asset in model.frontier_assets:
        sharpe = asset.sharpe_ratio
        if math.isfinite(sharpe):
            normalized.append(asset)
            continue
        if rf_pct is None or not math.isfinite(asset.standard_deviation_pct) or asset.standard_deviation_pct == 0:
            normalized.append(asset)
            continue
        normalized.append(
            replace(
                asset,
                sharpe_ratio=(asset.expected_return_pct - rf_pct) / asset.standard_deviation_pct,
            )
        )
        changed = True
    return replace(model, frontier_assets=tuple(normalized)) if changed else model


def _inject_series_contrast(output_path: str | Path) -> Path:
    path = Path(output_path)
    html = path.read_text(encoding="utf-8")
    if 'id="report-series-contrast"' in html:
        return path
    marker = "</body>"
    html = (
        html.replace(marker, f"{_SERIES_CONTRAST_SCRIPT}\n{marker}", 1)
        if marker in html
        else f"{html}\n{_SERIES_CONTRAST_SCRIPT}"
    )
    path.write_text(html, encoding="utf-8")
    return path


def render_report(
    model: ReportModel,
    output_path: str | Path,
    *,
    template_path: str | Path | None = None,
) -> Path:
    rendered = _render_feedback_v4(
        _normalize_frontier_assets(model),
        output_path,
        template_path=template_path,
    )
    return _inject_series_contrast(rendered)


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    root = Path(run_dir)
    model = build_report_model(root)
    target = Path(output_path) if output_path is not None else root / "report.html"
    return render_report(model, target, template_path=template_path)
