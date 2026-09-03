from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from . import historical_components as hc


def _percent_series(
    frame: pd.DataFrame,
    pct_column: str,
    decimal_column: str,
) -> pd.Series:
    if pct_column in frame:
        return pd.to_numeric(frame[pct_column], errors="coerce")
    if decimal_column in frame:
        return pd.to_numeric(frame[decimal_column], errors="coerce") * 100.0
    return pd.Series(index=frame.index, dtype=float)


def _axis_bounds(values: list[float]) -> tuple[float, float, float]:
    finite_values = [float(value) for value in values if hc.finite(value)]
    if not finite_values:
        return -1.0, 1.0, 0.5
    lower = min(min(finite_values), 0.0)
    upper = max(max(finite_values), 0.0)
    span = max(upper - lower, 0.1)
    padding = max(span * 0.08, 0.25)
    lower -= padding
    upper += padding
    step = hc.nice_step(upper - lower, 5)
    lower = math_floor_multiple(lower, step)
    upper = math_ceil_multiple(upper, step)
    if lower == upper:
        lower -= step
        upper += step
    return lower, upper, step


def _active_grouped_bar_chart(
    categories: list[str],
    series: list[tuple[str, list[float | None]]],
    *,
    chart_id: str,
    y_title: str,
    tooltip_rows: list[str] | None = None,
    x_title: str | None = None,
) -> str:
    if not categories or not series:
        return '<p class="muted">N/A</p>'

    width, height = hc.WIDTH, hc.HEIGHT
    margin_left, margin_right, margin_top, margin_bottom = 82, 28, 24, 72
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    values = [
        float(value)
        for _, data in series
        for value in data
        if hc.finite(value)
    ]
    y_min, y_max, step = _axis_bounds(values)

    def y_for(value: float) -> float:
        return margin_top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    zero_y = y_for(0.0)
    grid: list[str] = []
    tick = math_ceil_multiple(y_min, step)
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<line x1="{margin_left - 5}" y1="{y:.2f}" '
            f'x2="{margin_left}" y2="{y:.2f}" class="axis-tick y-axis-tick" />'
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-axis-label left-axis-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    category_width = plot_width / max(len(categories), 1)
    series_count = max(len(series), 1)
    group_width = min(category_width * 0.72, 68.0)
    bar_width = max(2.0, group_width / series_count)
    marks: list[str] = []
    labels: list[str] = []
    for category_index, category in enumerate(categories):
        center = margin_left + category_width * (category_index + 0.5)
        labels.append(
            f'<text x="{center:.2f}" y="{margin_top + plot_height + 24}" '
            f'text-anchor="middle" class="axis-label x-tick-label">{hc.esc(category)}</text>'
        )
        for series_index, (name, data) in enumerate(series):
            if category_index >= len(data) or not hc.finite(data[category_index]):
                continue
            value = float(data[category_index])
            y = y_for(value)
            x = center - group_width / 2 + series_index * bar_width
            tooltip = (
                tooltip_rows[category_index]
                if tooltip_rows and category_index < len(tooltip_rows)
                else f"{category} | {name}: {hc.pct(value)}"
            )
            marks.append(
                f'<rect x="{x + 0.6:.2f}" y="{min(y, zero_y):.2f}" '
                f'width="{max(bar_width - 1.2, 1):.2f}" '
                f'height="{max(abs(zero_y - y), 1):.2f}" '
                f'fill="{hc.PALETTE[series_index % len(hc.PALETTE)]}" '
                'class="chart-mark grouped-bar" tabindex="0" '
                f'data-tooltip="{hc.esc(tooltip)}" aria-label="{hc.esc(tooltip)}" />'
            )

    x_title_markup = (
        f'<text x="{margin_left + plot_width / 2:.2f}" y="{height - 12}" '
        f'text-anchor="middle" class="axis-title">{hc.esc(x_title)}</text>'
        if x_title
        else ""
    )
    svg = f'''<svg class="analysis-chart active-bar-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{hc.esc(y_title)}">
      <g class="y-axis y-axis-left" data-axis="y-left">{''.join(grid)}</g>
      <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" class="axis y-axis-line" />
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(marks)}
      <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis x-axis-line" />
      {''.join(labels)}
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">{hc.esc(y_title)}</text>
      {x_title_markup}
    </svg>'''
    return hc.chart_shell(
        chart_id,
        svg,
        hc.legend(
            [
                (name, hc.PALETTE[index % len(hc.PALETTE)])
                for index, (name, _) in enumerate(series)
            ]
        ),
    )


def _time_grouped_bar_chart(
    frame: pd.DataFrame,
    series: list[tuple[str, str]],
    *,
    chart_id: str,
    y_title: str,
) -> str:
    if frame.empty or "date" not in frame or not series:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    rendered["date"] = pd.to_datetime(rendered["date"], errors="coerce")
    rendered = rendered.dropna(subset=["date"]).sort_values("date")
    if rendered.empty:
        return '<p class="muted">N/A</p>'

    width, height = hc.WIDTH, hc.HEIGHT
    margin_left, margin_right, margin_top, margin_bottom = 82, 28, 24, 86
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    all_values = [
        float(value)
        for column, _ in series
        if column in rendered
        for value in pd.to_numeric(rendered[column], errors="coerce")
        if hc.finite(value)
    ]
    y_min, y_max, step = _axis_bounds(all_values)

    def y_for(value: float) -> float:
        return margin_top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    dates = list(rendered["date"])
    date_min, date_max = dates[0], dates[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return margin_left + plot_width * (date - date_min).total_seconds() / date_span

    zero_y = y_for(0.0)
    grid: list[str] = []
    tick = math_ceil_multiple(y_min, step)
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<line x1="{margin_left - 5}" y1="{y:.2f}" '
            f'x2="{margin_left}" y2="{y:.2f}" class="axis-tick y-axis-tick" />'
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-axis-label left-axis-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    group_span = plot_width / max(len(rendered), 1)
    group_width = min(group_span * 0.82, 18.0)
    bar_width = max(1.2, group_width / max(len(series), 1))
    bars: list[str] = []
    for _, row in rendered.iterrows():
        date = pd.Timestamp(row["date"])
        center = x_for(date)
        for series_index, (column, label) in enumerate(series):
            if column not in row or not hc.finite(row[column]):
                continue
            value = float(row[column])
            y = y_for(value)
            x = center - group_width / 2 + series_index * bar_width
            tooltip = f"{date.strftime('%Y-%m-%d')} | {label}: {hc.pct(value)}"
            bars.append(
                f'<rect x="{x + 0.35:.2f}" y="{min(y, zero_y):.2f}" '
                f'width="{max(bar_width - 0.7, 0.8):.2f}" '
                f'height="{max(abs(zero_y - y), 1):.2f}" '
                f'fill="{hc.PALETTE[series_index % len(hc.PALETTE)]}" '
                'class="chart-mark active-contribution-bar" tabindex="0" '
                f'data-tooltip="{hc.esc(tooltip)}" aria-label="{hc.esc(tooltip)}" />'
            )

    x_ticks: list[str] = []
    for date in hc.calendar_ticks(rendered["date"]):
        x = x_for(date)
        label = hc.esc(date.strftime("%b %Y"))
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{margin_top + plot_height}" '
            f'x2="{x:.2f}" y2="{margin_top + plot_height + 5}" class="axis-tick x-axis-tick" />'
            f'<text x="{x:.2f}" y="{margin_top + plot_height + 24}" '
            f'text-anchor="end" transform="rotate(-45 {x:.2f} {margin_top + plot_height + 24})" '
            f'class="axis-label x-tick-label">{label}</text>'
        )

    svg = f'''<svg class="analysis-chart active-contribution-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{hc.esc(y_title)}">
      <g class="y-axis y-axis-left" data-axis="y-left">{''.join(grid)}</g>
      <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" class="axis y-axis-line" />
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(bars)}
      <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis x-axis-line" />
      {''.join(x_ticks)}
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">{hc.esc(y_title)}</text>
      <text x="{margin_left + plot_width / 2:.2f}" y="{height - 10}" text-anchor="middle" class="axis-title">Month / Year</text>
    </svg>'''
    return hc.chart_shell(
        chart_id,
        svg,
        hc.legend(
            [
                (label, hc.PALETTE[index % len(hc.PALETTE)])
                for index, (_, label) in enumerate(series)
            ]
        ),
    )


def _annual_active_frame(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> pd.DataFrame:
    if frame.empty or not {"portfolio", "date"}.issubset(frame.columns):
        return pd.DataFrame()
    values = _percent_series(
        frame, "annual_active_return_pct", "annual_active_return"
    )
    if values.isna().all():
        return pd.DataFrame()
    shaped = frame[["portfolio", "date"]].copy()
    shaped["annual_active_return_pct"] = values
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date", "annual_active_return_pct"])
    shaped["year"] = shaped["date"].dt.year
    latest = (
        shaped.sort_values("date")
        .groupby(["year", "portfolio"], as_index=False)
        .tail(1)
    )
    pivot = latest.pivot(
        index="year",
        columns="portfolio",
        values="annual_active_return_pct",
    ).sort_index()
    columns = [name for name in portfolio_order if name in pivot.columns]
    columns.extend(column for column in pivot.columns if column not in columns)
    return pivot.reindex(columns=columns).reset_index()


def annual_active_return(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> str:
    pivot = _annual_active_frame(frame, portfolio_order)
    if pivot.empty:
        return '<p class="muted">N/A</p>'
    categories = [str(int(value)) for value in pivot["year"]]
    series = [
        (
            name,
            [float(value) if hc.finite(value) else None for value in pivot[name]],
        )
        for name in pivot.columns
        if name != "year"
    ]
    tooltips = [
        " | ".join(
            [categories[index]]
            + [
                f"{name}: {hc.pct(values[index])}"
                for name, values in series
                if index < len(values) and hc.finite(values[index])
            ]
        )
        for index in range(len(categories))
    ]
    chart = _active_grouped_bar_chart(
        categories,
        series,
        chart_id="annual-active-return-chart",
        y_title="Active Return %",
        tooltip_rows=tooltips,
    )
    rendered = pivot.copy()
    for column in rendered.columns:
        if column != "year":
            rendered[column] = rendered[column].map(hc.pct)
    return chart + hc.table(rendered.rename(columns={"year": "Year"}))


def active_contribution(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str] | None = None,
) -> str:
    if frame.empty or not {"date", "portfolio", "ticker"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    values = _percent_series(
        frame,
        "cumulative_active_contribution_pct",
        "cumulative_active_contribution",
    )
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
        pivot = part.pivot(
            index="date",
            columns="ticker",
            values="cumulative_active_contribution_pct",
        ).reset_index()
        series: list[tuple[str, str]] = []
        for ticker in pivot.columns:
            if ticker == "date":
                continue
            name = asset_names.get(str(ticker), "").strip()
            label = f"{name} ({ticker})" if name else str(ticker)
            series.append((str(ticker), label))
        blocks.append(
            f'<div class="analysis-panel active-contribution-panel" '
            f'data-portfolio="{hc.esc(portfolio)}"><h4>{hc.esc(portfolio)}</h4>'
            f'{_time_grouped_bar_chart(pivot, series, chart_id=f"active-contribution-{portfolio}", y_title="Cumulative Active Contribution %")}'
            "</div>"
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def rolling_active_risk_panel(
    frame: pd.DataFrame,
    portfolio: str,
    benchmark_label: str | None,
) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    part = frame[frame["portfolio"].astype(str) == portfolio].copy()
    if part.empty or "date" not in part:
        return '<p class="muted">N/A</p>'
    part["rolling_active_return_pct"] = _percent_series(
        part, "rolling_active_return_pct", "rolling_active_return"
    )
    part["rolling_tracking_error_pct"] = _percent_series(
        part, "rolling_tracking_error_pct", "rolling_tracking_error"
    )
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part = part.dropna(
        subset=[
            "date",
            "rolling_active_return_pct",
            "rolling_tracking_error_pct",
        ]
    ).sort_values("date")
    if part.empty:
        return '<p class="muted">N/A</p>'

    active = pd.to_numeric(part["rolling_active_return_pct"], errors="coerce")
    tracking = pd.to_numeric(
        part["rolling_tracking_error_pct"], errors="coerce"
    )
    left_min = min(float(active.min()), 0.0)
    left_max = max(float(active.max()), 0.0)
    right_min = 0.0
    right_max = max(float(tracking.max()), 0.1)
    left_padding = max((left_max - left_min) * 0.08, 0.5)
    right_padding = max((right_max - right_min) * 0.08, 0.5)
    left_min, left_max = left_min - left_padding, left_max + left_padding
    right_max += right_padding

    margin_left, margin_right, margin_top, margin_bottom = 82, 82, 24, 72
    width, height = hc.WIDTH, hc.HEIGHT
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    dates = list(part["date"])
    date_min, date_max = dates[0], dates[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return (
            margin_left
            + plot_width * (date - date_min).total_seconds() / date_span
        )

    def y_left(value: float) -> float:
        return (
            margin_top
            + plot_height
            * (left_max - value)
            / max(left_max - left_min, 1e-12)
        )

    def y_right(value: float) -> float:
        return (
            margin_top
            + plot_height
            * (right_max - value)
            / max(right_max - right_min, 1e-12)
        )

    zero_y = y_left(0.0)
    bar_width = max(
        3.0, min(14.0, plot_width / max(len(part), 1) * 0.65)
    )
    bars: list[str] = []
    line_coordinates: list[tuple[float, float]] = []
    points: list[str] = []
    for _, row in part.iterrows():
        date = pd.Timestamp(row["date"])
        active_value = float(row["rolling_active_return_pct"])
        tracking_error = float(row["rolling_tracking_error_pct"])
        x = x_for(date)
        active_y = y_left(active_value)
        tooltip = (
            f"{date.strftime('%Y-%m-%d')} | Active Return: "
            f"{hc.pct(active_value)} | Tracking Error: {hc.pct(tracking_error)}"
        )
        bars.append(
            f'<rect x="{x - bar_width / 2:.2f}" '
            f'y="{min(active_y, zero_y):.2f}" width="{bar_width:.2f}" '
            f'height="{max(abs(zero_y - active_y), 1):.2f}" '
            f'fill="{hc.PALETTE[0]}" class="chart-mark active-return-bar" '
            f'tabindex="0" data-tooltip="{hc.esc(tooltip)}" '
            f'aria-label="{hc.esc(tooltip)}" />'
        )
        tracking_y = y_right(tracking_error)
        line_coordinates.append((x, tracking_y))
        points.append(
            f'<circle cx="{x:.2f}" cy="{tracking_y:.2f}" r="4.5" '
            f'fill="{hc.PALETTE[1]}" '
            'class="chart-mark tracking-error-point" tabindex="0" '
            f'data-tooltip="{hc.esc(tooltip)}" aria-label="{hc.esc(tooltip)}" />'
        )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" '
        f'y="{margin_top + plot_height + 24}" text-anchor="middle" '
        f'class="axis-label x-tick-label">{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(part["date"])
    )
    left_axes: list[str] = []
    left_step = hc.nice_step(left_max - left_min, 5)
    tick = math_ceil_multiple(left_min, left_step)
    while tick <= left_max + left_step * 0.1 and len(left_axes) < 20:
        y = y_left(tick)
        left_axes.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
            f'<line x1="{margin_left - 5}" y1="{y:.2f}" '
            f'x2="{margin_left}" y2="{y:.2f}" class="axis-tick y-axis-tick" />'
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" '
            'text-anchor="end" class="axis-label y-axis-label left-axis-label">'
            f'{hc.esc(hc.pct(tick))}</text>'
        )
        tick += left_step
    right_axes: list[str] = []
    right_step = hc.nice_step(right_max - right_min, 5)
    tick = right_min
    while tick <= right_max + right_step * 0.1 and len(right_axes) < 20:
        y = y_right(tick)
        right_axes.append(
            f'<line x1="{margin_left + plot_width}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width + 5}" y2="{y:.2f}" class="axis-tick y-axis-tick" />'
            f'<text x="{margin_left + plot_width + 10}" y="{y + 4:.2f}" '
            'text-anchor="start" class="axis-label y-axis-label right-axis-label">'
            f'{hc.esc(hc.pct(tick))}</text>'
        )
        tick += right_step

    svg = f'''<svg class="analysis-chart rolling-active-risk-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Rolling Active Return and Risk 36 months">
      <g class="y-axis y-axis-left" data-axis="y-left">{''.join(left_axes)}</g>
      <g class="y-axis y-axis-right" data-axis="y-right">{''.join(right_axes)}</g>
      <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" class="axis y-axis-line" />
      <line x1="{margin_left + plot_width}" y1="{margin_top}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis y-axis-line" />
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(bars)}
      <polyline points="{' '.join(f'{x:.2f},{y:.2f}' for x, y in line_coordinates)}" fill="none" stroke="{hc.PALETTE[1]}" stroke-width="2.4" class="tracking-error-line" />
      {''.join(points)}{x_ticks}
      <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis x-axis-line" />
      <text x="{margin_left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">Active Return %</text>
      <text x="{width - 20}" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(90 {width - 20} {margin_top + plot_height / 2:.2f})">Tracking Error %</text>
    </svg>'''
    chart = hc.chart_shell(
        f"rolling-active-risk-{portfolio}",
        svg,
        hc.legend(
            [
                ("Active Return", hc.PALETTE[0]),
                ("Tracking Error", hc.PALETTE[1]),
            ]
        ),
    )
    subtitle = f"{portfolio} vs. {benchmark_label or 'Benchmark'}"
    return (
        f'<div class="analysis-panel rolling-active-risk-panel" '
        f'data-portfolio="{hc.esc(portfolio)}">'
        '<h4>Rolling Active Return / Risk · 36 months</h4>'
        f'<p class="panel-subtitle">{hc.esc(subtitle)}</p>{chart}</div>'
    )


def math_ceil_multiple(value: float, step: float) -> float:
    if step <= 0:
        return value
    return float(np.ceil(value / step) * step)


def math_floor_multiple(value: float, step: float) -> float:
    if step <= 0:
        return value
    return float(np.floor(value / step) * step)


def up_down_statistics_table(
    frame: pd.DataFrame,
    portfolio: str,
) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    part = frame[frame["portfolio"].astype(str) == portfolio].copy()
    if part.empty:
        return '<p class="muted">N/A</p>'
    aliases = {
        "market_type": "Market Type",
        "above_benchmark_count": "Above Benchmark Count",
        "below_benchmark_count": "Below Benchmark Count",
        "total_count": "Total",
        "occurrences": "Total",
        "pct_above_benchmark": "% Above Benchmark",
        "above_active_return_pct": "Average Active Return Above",
        "below_active_return_pct": "Average Active Return Below",
        "overall_active_return_pct": "Average Active Return Total",
        "active_return_pct": "Average Active Return Total",
    }
    selected: list[str] = []
    used_labels: set[str] = set()
    for column, label in aliases.items():
        if column in part and label not in used_labels:
            selected.append(column)
            used_labels.add(label)
    rendered = part[selected].copy()
    for column in rendered.columns:
        if column.endswith("_pct") or column == "pct_above_benchmark":
            rendered[column] = rendered[column].map(hc.pct)
    return hc.table(
        rendered.rename(columns=aliases),
        table_class="up-down-statistics",
    )


def up_down_paired_chart(
    observations: pd.DataFrame,
    portfolio: str,
) -> str:
    if observations.empty or "portfolio" not in observations:
        return '<p class="muted">N/A</p>'
    part = observations[
        observations["portfolio"].astype(str) == portfolio
    ].copy()
    if part.empty:
        return '<p class="muted">N/A</p>'
    benchmark = _percent_series(
        part, "benchmark_return_pct", "benchmark_return"
    )
    portfolio_returns = _percent_series(
        part, "portfolio_return_pct", "portfolio_return"
    )
    part = part.assign(
        _benchmark_pct=benchmark,
        _portfolio_pct=portfolio_returns,
    ).dropna(subset=["_benchmark_pct", "_portfolio_pct"])
    if part.empty:
        return '<p class="muted">N/A</p>'
    part = part.sort_values("_benchmark_pct").reset_index(drop=True)
    group_count = min(20, len(part))
    groups = np.array_split(np.arange(len(part)), group_count)
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
        tooltips.append(
            f"Group {index} | {portfolio}: {hc.pct(portfolio_return)} | "
            f"Benchmark: {hc.pct(benchmark_return)} | Observations: {len(group)}"
        )
    return _active_grouped_bar_chart(
        categories,
        [(portfolio, portfolio_values), ("Benchmark", benchmark_values)],
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
        rolling_active_risk_panel(
            active_returns, portfolio, benchmark_label
        )
        for portfolio in portfolio_order
    )
    observations = (
        up_down_observations
        if up_down_observations is not None
        else pd.DataFrame()
    )
    up_down_blocks = "".join(
        f'<div class="analysis-panel up-down-panel" '
        f'data-portfolio="{hc.esc(portfolio)}"><h4>{hc.esc(portfolio)}</h4>'
        f'{up_down_statistics_table(up_down, portfolio)}'
        '<h5>Return vs. Benchmark</h5>'
        f'{up_down_paired_chart(observations, portfolio)}</div>'
        for portfolio in portfolio_order
    )
    return (
        f"<h3>Benchmark Summary</h3>{summary}"
        f"<h3>Annual Active Return</h3>{annual_active_return(active_returns, portfolio_order)}"
        f"<h3>Active Return Contribution</h3>{active_contribution(active_contribution_frame, portfolio_order, asset_names)}"
        f"<h3>Rolling Active Return and Risk</h3>{rolling}"
        f"<h3>Up / Down Market Performance</h3>{up_down_blocks}"
    )
