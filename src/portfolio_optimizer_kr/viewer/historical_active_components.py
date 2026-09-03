from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from . import asset_display as ad
from . import historical_components as hc
from . import pv_visual as pv


def _percent_series(frame: pd.DataFrame, pct_column: str, decimal_column: str) -> pd.Series:
    if pct_column in frame:
        return pd.to_numeric(frame[pct_column], errors="coerce")
    if decimal_column in frame:
        return pd.to_numeric(frame[decimal_column], errors="coerce") * 100.0
    return pd.Series(index=frame.index, dtype=float)


def _axis_bounds(values: list[float]) -> tuple[float, float, float]:
    finite = [float(value) for value in values if hc.finite(value)]
    if not finite:
        return -1.0, 1.0, 0.5
    lower = min(min(finite), 0.0)
    upper = max(max(finite), 0.0)
    span = max(upper - lower, 0.1)
    padding = max(span * 0.08, 0.25)
    lower -= padding
    upper += padding
    step = hc.nice_step(upper - lower, 5)
    lower = math.floor(lower / step) * step
    upper = math.ceil(upper / step) * step
    return lower, upper, step


def _annual_active_frame(frame: pd.DataFrame, portfolio_order: list[str]) -> pd.DataFrame:
    if frame.empty or not {"portfolio", "date"}.issubset(frame.columns):
        return pd.DataFrame()
    values = _percent_series(frame, "annual_active_return_pct", "annual_active_return")
    shaped = frame[["portfolio", "date"]].copy()
    shaped["annual_active_return_pct"] = values
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date", "annual_active_return_pct"])
    if shaped.empty:
        return pd.DataFrame()
    shaped["year"] = shaped["date"].dt.year
    latest = shaped.sort_values("date").groupby(["year", "portfolio"], as_index=False).tail(1)
    pivot = latest.pivot(index="year", columns="portfolio", values="annual_active_return_pct").sort_index()
    columns = [name for name in portfolio_order if name in pivot.columns]
    columns.extend(column for column in pivot.columns if column not in columns)
    return pivot.reindex(columns=columns).reset_index()


def annual_active_return(frame: pd.DataFrame, portfolio_order: list[str]) -> str:
    pivot = _annual_active_frame(frame, portfolio_order)
    if pivot.empty:
        return '<p class="muted">N/A</p>'
    categories = [str(int(value)) for value in pivot["year"]]
    series = [
        (name, [float(value) if hc.finite(value) else None for value in pivot[name]])
        for name in pivot.columns
        if name != "year"
    ]
    chart = pv.grouped_bar_chart(
        categories,
        series,
        chart_id="annual-active-return-chart",
        y_title="Active Return %",
        x_title="Year",
    )
    return (
        '<div class="analysis-panel annual-active-return-panel">'
        '<h4>Annualized Active Return</h4>'
        '<p class="panel-subtitle">Active Return vs Benchmark</p>'
        f"{chart}</div>"
    )


def _stacked_contribution_chart(
    pivot: pd.DataFrame,
    series: list[tuple[str, str]],
    *,
    chart_id: str,
    color_map: dict[str, str] | None = None,
) -> str:
    if pivot.empty or "date" not in pivot or not series:
        return '<p class="muted">N/A</p>'
    shaped = pivot.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    if shaped.empty:
        return '<p class="muted">N/A</p>'

    positives: list[float] = []
    negatives: list[float] = []
    for _, row in shaped.iterrows():
        pos = sum(float(row[col]) for col, _ in series if hc.finite(row.get(col)) and float(row[col]) > 0)
        neg = sum(float(row[col]) for col, _ in series if hc.finite(row.get(col)) and float(row[col]) < 0)
        positives.append(pos)
        negatives.append(neg)
    y_min, y_max, step = _axis_bounds(positives + negatives)

    width, height = hc.WIDTH, hc.HEIGHT
    left, right, top, bottom = 82, 28, 24, 84
    plot_width = width - left - right
    plot_height = height - top - bottom
    dates = list(shaped["date"])
    date_min, date_max = dates[0], dates[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / date_span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    grid: list[str] = []
    tick = math.ceil(y_min / step) * step
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" class="axis-label y-axis-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    bar_width = max(3.0, min(15.0, plot_width / max(len(shaped), 1) * 0.72))
    marks: list[str] = []
    zones: list[str] = []
    rows = list(shaped.iterrows())
    for position, (_, row) in enumerate(rows):
        date = pd.Timestamp(row["date"])
        x = x_for(date)
        positive_base = 0.0
        negative_base = 0.0
        tooltip_items: list[tuple[str, str, str]] = []
        for index, (column, label) in enumerate(series):
            if not hc.finite(row.get(column)):
                continue
            value = float(row[column])
            color = (color_map or {}).get(column, hc.PALETTE[index % len(hc.PALETTE)])
            if value >= 0:
                start, end = positive_base, positive_base + value
                positive_base = end
            else:
                start, end = negative_base, negative_base + value
                negative_base = end
            marks.append(
                f'<rect x="{x - bar_width / 2:.2f}" y="{min(y_for(start), y_for(end)):.2f}" '
                f'width="{bar_width:.2f}" height="{max(abs(y_for(start) - y_for(end)), 1):.2f}" '
                f'fill="{color}" class="active-contribution-bar stacked-bar" pointer-events="none" />'
            )
            tooltip_items.append((label, hc.pct(value), color))

        prev_x = x_for(pd.Timestamp(rows[position - 1][1]["date"])) if position else left
        next_x = x_for(pd.Timestamp(rows[position + 1][1]["date"])) if position + 1 < len(rows) else left + plot_width
        x0 = (prev_x + x) / 2 if position else left
        x1 = (x + next_x) / 2 if position + 1 < len(rows) else left + plot_width
        legacy = pv._legacy_tooltip(date.strftime("%Y-%m-%d"), tooltip_items)
        zones.append(
            f'<rect x="{x0:.2f}" y="{top}" width="{max(x1 - x0, 1):.2f}" height="{plot_height}" fill="transparent" '
            'class="chart-mark shared-hover-zone active-contribution-hover-zone" tabindex="0" '
            f'data-tooltip="{hc.esc(legacy)}" data-tooltip-json="{pv._tooltip_payload(date.strftime("%b %Y"), tooltip_items)}" '
            f'aria-label="{hc.esc(legacy)}" />'
        )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 24}" text-anchor="end" '
        f'transform="rotate(-45 {x_for(date):.2f} {top + plot_height + 24})" class="axis-label x-tick-label">{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(shaped["date"])
    )
    zero_y = y_for(0.0)
    svg = f'''<svg class="analysis-chart active-contribution-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Cumulative Active Return Contribution">
      {''.join(grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left}" y1="{zero_y:.2f}" x2="{left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(marks)}{''.join(zones)}{x_ticks}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{height - 10}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">Cumulative Active Return %</text>
    </svg>'''
    return hc.chart_shell(
        chart_id,
        svg,
        hc.legend((label, (color_map or {}).get(column, hc.PALETTE[index % len(hc.PALETTE)])) for index, (column, label) in enumerate(series)),
    )


def _contribution_summary(part: pd.DataFrame, asset_names: dict[str, str], asset_order: list[str] | None = None) -> str:
    if part.empty:
        return ""
    part = part.copy()
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part = part.dropna(subset=["date"]).sort_values("date")
    if part.empty:
        return ""
    value_col = "cumulative_active_contribution_pct"
    if value_col not in part:
        return ""
    last_date = part["date"].max()
    rows = []
    available = list(dict.fromkeys(part["ticker"].astype(str)))
    ordered = [ticker for ticker in (asset_order or []) if ticker in available]
    ordered.extend(ticker for ticker in available if ticker not in ordered)
    for ticker in ordered:
        ticker_part = part[part["ticker"].astype(str) == ticker].sort_values("date")
        end_value = pd.to_numeric(ticker_part[value_col], errors="coerce").dropna()
        if end_value.empty:
            continue
        cells = []
        for years in (1, 3, 5):
            cutoff = last_date - pd.DateOffset(years=years)
            before = ticker_part[ticker_part["date"] <= cutoff]
            start_value = 0.0 if before.empty else float(pd.to_numeric(before[value_col], errors="coerce").dropna().iloc[-1])
            cells.append(float(end_value.iloc[-1]) - start_value)
        name = asset_names.get(str(ticker), "")
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(ticker)}</td>'
            f'<td class="identity-cell">{hc.esc(name)}</td>'
            + "".join(f"<td>{hc.esc(hc.pct(value))}</td>" for value in cells)
            + "</tr>"
        )
    if not rows:
        return ""
    return (
        '<div class="table-wrap"><table class="active-contribution-summary">'
        '<thead><tr><th>Ticker</th><th>Name</th><th>1 Year</th><th>3 Year</th><th>5 Year</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def active_contribution(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str] | None = None,
) -> str:
    if frame.empty or not {"date", "portfolio", "ticker"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    values = _percent_series(frame, "cumulative_active_contribution_pct", "cumulative_active_contribution")
    if values.isna().all():
        return '<p class="muted">N/A</p>'
    shaped = frame.copy()
    shaped["cumulative_active_contribution_pct"] = values
    asset_names = asset_names or {}
    blocks: list[str] = []
    for portfolio in portfolio_order:
        part = shaped[shaped["portfolio"].astype(str) == portfolio].copy()
        if part.empty:
            continue
        pivot = part.pivot(index="date", columns="ticker", values="cumulative_active_contribution_pct").reset_index()
        global_order = list(asset_names)
        colors = ad.asset_color_map(global_order)
        available = [str(ticker) for ticker in pivot.columns if ticker != "date"]
        ordered = [ticker for ticker in global_order if ticker in available]
        ordered.extend(ticker for ticker in available if ticker not in ordered)
        series: list[tuple[str, str]] = []
        for ticker in ordered:
            name = asset_names.get(str(ticker), "").strip()
            label = f"{name} ({ticker})" if name else str(ticker)
            series.append((str(ticker), label))
        blocks.append(
            f'<div class="analysis-panel active-contribution-panel" data-portfolio="{hc.esc(portfolio)}">'
            '<h4>Cumulative Active Return</h4>'
            f'<p class="panel-subtitle">{hc.esc(portfolio)} vs Benchmark</p>'
            f'{_stacked_contribution_chart(pivot, series, chart_id=f"active-contribution-{portfolio}", color_map=colors)}'
            f'{_contribution_summary(part, asset_names, global_order)}</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def rolling_active_risk_panel(frame: pd.DataFrame, portfolio: str, benchmark_label: str | None) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    part = frame[frame["portfolio"].astype(str) == portfolio].copy()
    if part.empty or "date" not in part:
        return '<p class="muted">N/A</p>'
    part["rolling_active_return_pct"] = _percent_series(part, "rolling_active_return_pct", "rolling_active_return")
    part["rolling_tracking_error_pct"] = _percent_series(part, "rolling_tracking_error_pct", "rolling_tracking_error")
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part = part.dropna(subset=["date", "rolling_active_return_pct", "rolling_tracking_error_pct"]).sort_values("date")
    if part.empty:
        return '<p class="muted">N/A</p>'

    active_values = pd.to_numeric(part["rolling_active_return_pct"], errors="coerce")
    tracking_values = pd.to_numeric(part["rolling_tracking_error_pct"], errors="coerce")
    left_min, left_max, left_step = _axis_bounds(active_values.tolist())
    right_min = 0.0
    right_max = max(float(tracking_values.max()) * 1.08, 0.5)
    right_step = hc.nice_step(right_max, 5)
    right_max = math.ceil(right_max / right_step) * right_step

    width, height = hc.WIDTH, hc.HEIGHT
    left, right, top, bottom = 82, 82, 24, 72
    plot_width = width - left - right
    plot_height = height - top - bottom
    dates = list(part["date"])
    date_min, date_max = dates[0], dates[-1]
    span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / span

    def y_left(value: float) -> float:
        return top + plot_height * (left_max - value) / max(left_max - left_min, 1e-12)

    def y_right(value: float) -> float:
        return top + plot_height * (right_max - value) / max(right_max - right_min, 1e-12)

    left_axes: list[str] = []
    tick = math.ceil(left_min / left_step) * left_step
    while tick <= left_max + left_step * 0.1 and len(left_axes) < 20:
        y = y_left(tick)
        left_axes.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" class="axis-label left-axis-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += left_step
    right_axes: list[str] = []
    tick = 0.0
    while tick <= right_max + right_step * 0.1 and len(right_axes) < 20:
        y = y_right(tick)
        right_axes.append(
            f'<text x="{left + plot_width + 10}" y="{y + 4:.2f}" text-anchor="start" class="axis-label right-axis-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += right_step

    zero_y = y_left(0.0)
    bar_width = max(3.0, min(14.0, plot_width / max(len(part), 1) * 0.65))
    bars: list[str] = []
    line_coords: list[tuple[float, float]] = []
    zones: list[str] = []
    rows = list(part.iterrows())
    for position, (_, row) in enumerate(rows):
        date = pd.Timestamp(row["date"])
        active_value = float(row["rolling_active_return_pct"])
        tracking = float(row["rolling_tracking_error_pct"])
        x = x_for(date)
        active_y = y_left(active_value)
        bars.append(
            f'<rect x="{x - bar_width / 2:.2f}" y="{min(active_y, zero_y):.2f}" width="{bar_width:.2f}" '
            f'height="{max(abs(zero_y - active_y), 1):.2f}" fill="{hc.PALETTE[0]}" class="active-return-bar" pointer-events="none" />'
        )
        line_coords.append((x, y_right(tracking)))
        items = [
            ("Active Return", hc.pct(active_value), hc.PALETTE[0]),
            ("Tracking Error", hc.pct(tracking), hc.PALETTE[1]),
        ]
        prev_x = x_for(pd.Timestamp(rows[position - 1][1]["date"])) if position else left
        next_x = x_for(pd.Timestamp(rows[position + 1][1]["date"])) if position + 1 < len(rows) else left + plot_width
        x0 = (prev_x + x) / 2 if position else left
        x1 = (x + next_x) / 2 if position + 1 < len(rows) else left + plot_width
        legacy = pv._legacy_tooltip(date.strftime("%Y-%m-%d"), items)
        zones.append(
            f'<rect x="{x0:.2f}" y="{top}" width="{max(x1 - x0, 1):.2f}" height="{plot_height}" fill="transparent" '
            'class="chart-mark shared-hover-zone rolling-active-hover-zone" tabindex="0" '
            f'data-tooltip="{hc.esc(legacy)}" data-tooltip-json="{pv._tooltip_payload(date.strftime("%b %Y"), items)}" aria-label="{hc.esc(legacy)}" />'
        )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 24}" text-anchor="middle" class="axis-label x-tick-label">{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(part["date"])
    )
    svg = f'''<svg class="analysis-chart rolling-active-risk-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Rolling Active Return and Risk 36 months">
      <g data-axis="y-left">{''.join(left_axes)}</g><g data-axis="y-right">{''.join(right_axes)}</g>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left + plot_width}" y1="{top}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left}" y1="{zero_y:.2f}" x2="{left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(bars)}
      <polyline points="{' '.join(f'{x:.2f},{y:.2f}' for x, y in line_coords)}" fill="none" stroke="{hc.PALETTE[1]}" stroke-width="2.4" class="tracking-error-line" />
      {''.join(zones)}{x_ticks}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">Active Return %</text>
      <text x="{width - 20}" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(90 {width - 20} {top + plot_height / 2:.2f})">Tracking Error %</text>
    </svg>'''
    chart = hc.chart_shell(
        f"rolling-active-risk-{portfolio}",
        svg,
        hc.legend([("Active Return", hc.PALETTE[0]), ("Tracking Error", hc.PALETTE[1])]),
    )
    return (
        f'<div class="analysis-panel rolling-active-risk-panel" data-portfolio="{hc.esc(portfolio)}">'
        '<h4>Rolling Active Return and Risk (36 months)</h4>'
        f'<p class="panel-subtitle">{hc.esc(portfolio)} vs. {hc.esc(benchmark_label or "Benchmark")}</p>'
        f"{chart}</div>"
    )


def _total_up_down_row(part: pd.DataFrame) -> dict[str, Any] | None:
    if part.empty:
        return None
    if (part.get("market_type", pd.Series(dtype=str)).astype(str).str.lower() == "total").any():
        return None
    counts = pd.to_numeric(part.get("total_count", part.get("occurrences")), errors="coerce").fillna(0)
    total = int(counts.sum())
    if total <= 0:
        return None
    above = int(pd.to_numeric(part.get("above_benchmark_count"), errors="coerce").fillna(0).sum())
    below = int(pd.to_numeric(part.get("below_benchmark_count"), errors="coerce").fillna(0).sum())

    def weighted(column: str) -> float | None:
        if column not in part:
            return None
        values = pd.to_numeric(part[column], errors="coerce")
        valid = values.notna() & counts.gt(0)
        if not valid.any():
            return None
        return float(np.average(values[valid], weights=counts[valid]))

    return {
        "market_type": "Total",
        "above_benchmark_count": above,
        "below_benchmark_count": below,
        "total_count": total,
        "pct_above_benchmark": above / total * 100.0,
        "above_active_return_pct": weighted("above_active_return_pct"),
        "below_active_return_pct": weighted("below_active_return_pct"),
        "overall_active_return_pct": weighted("overall_active_return_pct"),
    }


def up_down_statistics_table(frame: pd.DataFrame, portfolio: str) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    part = frame[frame["portfolio"].astype(str) == portfolio].copy()
    if part.empty:
        return '<p class="muted">N/A</p>'
    total = _total_up_down_row(part)
    records = part.to_dict(orient="records")
    if total is not None:
        records.append(total)
    rows = []
    for row in records:
        market = str(row.get("market_type", "")).strip().title()
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(market)}</td>'
            f"<td>{hc.esc(row.get('above_benchmark_count', ''))}</td>"
            f"<td>{hc.esc(row.get('below_benchmark_count', ''))}</td>"
            f"<td>{hc.esc(row.get('total_count', row.get('occurrences', '')))}</td>"
            f"<td>{hc.esc(hc.pct(row.get('pct_above_benchmark')))}</td>"
            f"<td>{hc.esc(hc.pct(row.get('above_active_return_pct')))}</td>"
            f"<td>{hc.esc(hc.pct(row.get('below_active_return_pct')))}</td>"
            f"<td>{hc.esc(hc.pct(row.get('overall_active_return_pct', row.get('active_return_pct'))))}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table class="up-down-statistics pv-grouped-table">'
        '<thead><tr><th rowspan="2">Market Type</th><th colspan="4">Occurrences</th><th colspan="3">Average Active Return</th></tr>'
        '<tr><th>Above Benchmark</th><th>Below Benchmark</th><th>Total</th><th>% Above Benchmark</th>'
        '<th>Above</th><th>Below</th><th>Total</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def up_down_paired_chart(observations: pd.DataFrame, portfolio: str, benchmark_label: str | None = None) -> str:
    if observations.empty or "portfolio" not in observations:
        return '<p class="muted">N/A</p>'
    part = observations[observations["portfolio"].astype(str) == portfolio].copy()
    if part.empty:
        return '<p class="muted">N/A</p>'
    part["_benchmark_pct"] = _percent_series(part, "benchmark_return_pct", "benchmark_return")
    part["_portfolio_pct"] = _percent_series(part, "portfolio_return_pct", "portfolio_return")
    part = part.dropna(subset=["_benchmark_pct", "_portfolio_pct"]).sort_values("_benchmark_pct").reset_index(drop=True)
    if part.empty:
        return '<p class="muted">N/A</p>'
    groups = np.array_split(np.arange(len(part)), min(20, len(part)))
    categories: list[str] = []
    portfolio_values: list[float] = []
    benchmark_values: list[float] = []
    tooltips: list[str] = []
    for index, indices in enumerate(groups, start=1):
        if len(indices) == 0:
            continue
        group = part.iloc[indices]
        benchmark_return = float(group["_benchmark_pct"].mean())
        portfolio_return = float(group["_portfolio_pct"].mean())
        categories.append(f"{benchmark_return:.1f}%")
        portfolio_values.append(portfolio_return)
        benchmark_values.append(benchmark_return)
        tooltips.append(f"Group {index} | Observations: {len(group)}")
    return pv.grouped_bar_chart(
        categories,
        [(portfolio, portfolio_values), (benchmark_label or "Benchmark", benchmark_values)],
        chart_id=f"return-vs-benchmark-{portfolio}",
        y_title="Return %",
        tooltip_rows=tooltips,
        x_title="Benchmark Return",
    )


def active_returns_presentation(
    active_returns: pd.DataFrame,
    active_contribution_frame: pd.DataFrame,
    benchmark_summary: pd.DataFrame,
    up_down: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str] | None = None,
    up_down_observations: pd.DataFrame | None = None,
) -> str:
    summary = hc.friendly_table(
        benchmark_summary,
        portfolio_order=portfolio_order,
        column_labels={
            "active_return_pct": "Active Return",
            "tracking_error_pct": "Tracking Error",
            "information_ratio": "Information Ratio",
        },
    )
    rolling = "".join(
        rolling_active_risk_panel(active_returns, portfolio, benchmark_label)
        for portfolio in portfolio_order
    )
    observations = up_down_observations if up_down_observations is not None else pd.DataFrame()
    up_down_blocks = "".join(
        f'<div class="analysis-panel up-down-panel" data-portfolio="{hc.esc(portfolio)}">'
        f'<h4>{hc.esc(portfolio)} vs. {hc.esc(benchmark_label or "Benchmark")}</h4>'
        f'{up_down_statistics_table(up_down, portfolio)}'
        '<h5>Return vs. Benchmark</h5>'
        f'{up_down_paired_chart(observations, portfolio, benchmark_label)}</div>'
        for portfolio in portfolio_order
    )
    return (
        f"<h3>Benchmark Summary</h3>{summary}"
        f"<h3>Annualized Active Return</h3>{annual_active_return(active_returns, portfolio_order)}"
        f"<h3>Cumulative Active Return</h3>{active_contribution(active_contribution_frame, portfolio_order, asset_names)}"
        f"<h3>Rolling Active Return and Risk</h3>{rolling}"
        f"<h3>Up / Down Market Performance</h3>{up_down_blocks}"
    )
