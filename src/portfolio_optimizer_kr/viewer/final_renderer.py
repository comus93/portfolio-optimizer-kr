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
  const NS = 'h' + 'ttp://www.w3.org/2000/svg';

  const finite = value => value !== null && value !== undefined && Number.isFinite(Number(value));
  const moneyFromCanonicalBalance = value => finite(value)
    ? (Number(value) * 10000).toLocaleString(undefined, {
        style:'currency', currency:'USD', maximumFractionDigits:0,
      })
    : 'N/A';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));

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

  const fixPortfolioGrowthHover = () => {
    const data = window.PORTFOLIO_REPORT_DATA || {};
    const rows = (data.portfolio_growth || []).filter(row => row.date);
    const host = document.querySelector('#portfolio-growth .chart');
    const svg = host?.querySelector('svg');
    const tip = document.querySelector('.tooltip');
    if (!svg || !tip || !rows.length) return;

    // The legacy renderer placed hover circles on the first available series
    // (normally Provided), so hovering the Optimized line could miss every hit
    // target. Disable those point targets and use one plot-wide overlay instead.
    svg.querySelectorAll('circle[fill="transparent"]').forEach(node => {
      node.setAttribute('pointer-events', 'none');
    });
    svg.querySelectorAll('.final-growth-hover-overlay').forEach(node => node.remove());

    const viewBox = svg.viewBox?.baseVal;
    const width = viewBox?.width || 1000;
    const height = viewBox?.height || 300;
    const left = 66;
    const right = 24;
    const top = 16;
    const bottom = 48;

    const shaped = rows.map(row => ({
      ...row,
      time: new Date(`${row.date}T00:00:00`).getTime(),
    })).filter(row => Number.isFinite(row.time));
    if (!shaped.length) return;

    const minTime = Math.min(...shaped.map(row => row.time));
    const maxTime = Math.max(...shaped.map(row => row.time));
    const overlay = document.createElementNS(NS, 'rect');
    overlay.setAttribute('class', 'final-growth-hover-overlay');
    overlay.setAttribute('x', String(left));
    overlay.setAttribute('y', String(top));
    overlay.setAttribute('width', String(width - left - right));
    overlay.setAttribute('height', String(height - top - bottom));
    overlay.setAttribute('fill', 'transparent');
    overlay.setAttribute('pointer-events', 'all');

    const show = (event, row) => {
      const optimizedLabel = data.objective_name || 'Optimized Portfolio';
      const benchmarkLabel = data.benchmark_name || data.benchmark_symbol || 'Benchmark';
      const lines = [
        `<b>${esc(row.date)}</b>`,
        `Provided Portfolio: ${moneyFromCanonicalBalance(row.provided_balance)}`,
        `${esc(optimizedLabel)}: ${moneyFromCanonicalBalance(row.optimized_balance)}`,
      ];
      if (finite(row.benchmark_balance)) {
        lines.push(`${esc(benchmarkLabel)}: ${moneyFromCanonicalBalance(row.benchmark_balance)}`);
      }
      tip.innerHTML = lines.join('<br>');
      tip.style.display = 'block';
      tip.style.left = `${event.clientX + 14}px`;
      tip.style.top = `${event.clientY + 14}px`;
    };

    overlay.addEventListener('mousemove', event => {
      const bounds = svg.getBoundingClientRect();
      if (!bounds.width) return;
      const localX = (event.clientX - bounds.left) * width / bounds.width;
      const ratio = Math.min(1, Math.max(0,
        (localX - left) / Math.max(width - left - right, 1)
      ));
      const targetTime = minTime + ratio * (maxTime - minTime);
      const nearest = shaped.reduce((best, row) =>
        Math.abs(row.time - targetTime) < Math.abs(best.time - targetTime) ? row : best,
        shaped[0]
      );
      show(event, nearest);
    });
    overlay.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
    svg.appendChild(overlay);
  };

  const annotatePartialYears = () => {
    const data = window.PORTFOLIO_REPORT_DATA || {};
    const rows = data.tables?.monthly_returns_calendar || [];
    if (!rows.length) return;

    const months = [
      ['Jan','Jan_pct'], ['Feb','Feb_pct'], ['Mar','Mar_pct'], ['Apr','Apr_pct'],
      ['May','May_pct'], ['Jun','Jun_pct'], ['Jul','Jul_pct'], ['Aug','Aug_pct'],
      ['Sep','Sep_pct'], ['Oct','Oct_pct'], ['Nov','Nov_pct'], ['Dec','Dec_pct'],
    ];
    const representativeByYear = new Map();
    rows.forEach(row => {
      const year = Number(row.year);
      if (Number.isFinite(year) && !representativeByYear.has(year)) {
        representativeByYear.set(year, row);
      }
    });

    const partial = [...representativeByYear.entries()]
      .sort((a,b) => a[0] - b[0])
      .map(([year,row]) => {
        const available = months
          .map(([label,key],index) => ({label,key,index}))
          .filter(item => finite(row[item.key]));
        if (!available.length || available.length === 12) return null;

        const first = available[0];
        const last = available[available.length - 1];
        const contiguous = available.every(
          (item,index) => item.index === first.index + index
        );
        let span;
        if (available.length === 1) span = `${first.label} only`;
        else if (contiguous) span = `${first.label}-${last.label}`;
        else span = available.map(item => item.label).join(', ');
        return `${year} is based on ${span}`;
      })
      .filter(Boolean);

    document.querySelectorAll('.final-partial-year-note').forEach(node => node.remove());
    if (!partial.length) return;

    const text = `Partial-year results: ${partial.join('; ')}. ` +
      'Returns for those years use only the available completed months.';
    ['annual-returns','monthly-returns'].forEach(id => {
      const host = document.getElementById(id);
      if (!host) return;
      const note = document.createElement('div');
      note.className = 'muted final-partial-year-note';
      note.style.marginTop = '10px';
      note.textContent = text;
      host.appendChild(note);
    });
  };

  const applyFinalPresentationFixes = () => {
    recolor();
    fixPortfolioGrowthHover();
    annotatePartialYears();
  };

  // feedback_v4 performs a delayed final render. Run this pass afterward so
  // final interaction and explanatory notes belong to the final DOM.
  if (document.readyState === 'complete') setTimeout(applyFinalPresentationFixes, 90);
  else window.addEventListener(
    'load',
    () => setTimeout(applyFinalPresentationFixes, 90),
    {once:true},
  );
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