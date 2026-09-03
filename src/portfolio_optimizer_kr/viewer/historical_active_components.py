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
    chart = hc.grouped_bar_chart(
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
            f'{hc.time_line_chart(pivot, series, chart_id=f"active-contribution-{portfolio}", y_title="Cumulative Active Contribution %")}'
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

    margin_left, margin_right, margin_top, margin_bottom = 78, 78, 24, 72
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
    axes: list[str] = []
    left_step = hc.nice_step(left_max - left_min, 5)
    tick = math_ceil_multiple(left_min, left_step)
    while tick <= left_max + left_step * 0.1 and len(axes) < 20:
        y = y_left(tick)
        axes.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" '
            'text-anchor="end" class="axis-label left-axis-label">'
            f'{hc.esc(hc.pct(tick))}</text>'
        )
        tick += left_step
    right_step = hc.nice_step(right_max - right_min, 5)
    tick = right_min
    while tick <= right_max + right_step * 0.1 and len(axes) < 40:
        y = y_right(tick)
        axes.append(
            f'<text x="{margin_left + plot_width + 10}" y="{y + 4:.2f}" '
            'text-anchor="start" class="axis-label right-axis-label">'
            f'{hc.esc(hc.pct(tick))}</text>'
        )
        tick += right_step

    svg = f'''<svg class="analysis-chart rolling-active-risk-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Rolling Active Return and Risk 36 months">
      {''.join(axes)}
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(bars)}
      <polyline points="{' '.join(f'{x:.2f},{y:.2f}' for x, y in line_coordinates)}" fill="none" stroke="{hc.PALETTE[1]}" stroke-width="2.4" class="tracking-error-line" />
      {''.join(points)}{x_ticks}
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
        categories.append(str(index))
        portfolio_values.append(portfolio_return)
        benchmark_values.append(benchmark_return)
        tooltips.append(
            f"Group {index} | {portfolio}: {hc.pct(portfolio_return)} | "
            f"Benchmark: {hc.pct(benchmark_return)} | Observations: {len(group)}"
        )
    return hc.grouped_bar_chart(
        categories,
        [(portfolio, portfolio_values), ("Benchmark", benchmark_values)],
        chart_id=f"return-vs-benchmark-{portfolio}",
        y_title="Average Monthly Return %",
        tooltip_rows=tooltips,
        x_title="Benchmark Return Quantile Group",
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
