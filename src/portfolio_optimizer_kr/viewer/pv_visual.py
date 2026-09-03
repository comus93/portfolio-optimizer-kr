from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd

from . import historical_components as hc


def _tooltip_payload(
    title: str,
    items: list[tuple[str, str, str]],
    note: str | None = None,
) -> str:
    payload: dict[str, Any] = {
        "title": title,
        "items": [
            {"label": label, "value": value, "color": color}
            for label, value, color in items
        ],
    }
    if note:
        payload["note"] = note
    return hc.esc(json.dumps(payload, ensure_ascii=False))


def _legacy_tooltip(
    title: str,
    items: list[tuple[str, str, str]],
) -> str:
    return " | ".join([title] + [f"{label}: {value}" for label, value, _ in items])


def grouped_bar_chart(
    categories: list[str],
    series: list[tuple[str, list[float | None]]],
    *,
    chart_id: str,
    y_title: str,
    tooltip_rows: list[str] | None = None,
    x_title: str = "Year",
) -> str:
    values = [
        float(value)
        for _, row in series
        for value in row
        if hc.finite(value)
    ]
    if not categories or not series or not values:
        return '<p class="muted">N/A</p>'

    y_min, y_max = min(min(values), 0.0), max(max(values), 0.0)
    if math.isclose(y_min, y_max):
        y_max = y_min + 1.0
    padding = max((y_max - y_min) * 0.08, 1.0)
    y_min, y_max = y_min - padding, y_max + padding
    left, right, top, bottom = 78, 24, 24, 72
    plot_width = hc.WIDTH - left - right
    plot_height = hc.HEIGHT - top - bottom

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    zero_y = y_for(0.0)
    step = hc.nice_step(y_max - y_min, 6)
    tick = math.ceil(y_min / step) * step
    grid: list[str] = []
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" '
            f'y2="{y:.2f}" class="grid-line" />'
            f'<line x1="{left - 5}" y1="{y:.2f}" x2="{left}" '
            f'y2="{y:.2f}" class="axis-tick y-axis-tick" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    group_width = plot_width / max(len(categories), 1)
    inner_width = group_width * 0.76
    bar_width = inner_width / max(len(series), 1)
    marks: list[str] = []
    labels: list[str] = []
    zones: list[str] = []

    for category_index, category in enumerate(categories):
        center = left + group_width * (category_index + 0.5)
        if (
            len(categories) <= 16
            or category_index % max(1, len(categories) // 10) == 0
            or category_index == len(categories) - 1
        ):
            labels.append(
                f'<text x="{center:.2f}" y="{top + plot_height + 24}" '
                f'text-anchor="middle" class="axis-label x-tick-label">'
                f'{hc.esc(category)}</text>'
            )

        tooltip_items: list[tuple[str, str, str]] = []
        for series_index, (name, values_row) in enumerate(series):
            if category_index >= len(values_row) or not hc.finite(values_row[category_index]):
                continue
            value = float(values_row[category_index])
            color = hc.PALETTE[series_index % len(hc.PALETTE)]
            x = (
                center
                - inner_width / 2
                + series_index * bar_width
                + bar_width * 0.08
            )
            y_value = y_for(value)
            marks.append(
                f'<rect x="{x:.2f}" y="{min(zero_y, y_value):.2f}" '
                f'width="{bar_width * 0.84:.2f}" '
                f'height="{max(abs(zero_y - y_value), 1):.2f}" '
                f'fill="{color}" class="chart-mark grouped-bar" '
                'pointer-events="none" />'
            )
            tooltip_items.append((name, hc.pct(value), color))

        if tooltip_items:
            legacy = _legacy_tooltip(category, tooltip_items)
            note = None
            if tooltip_rows and category_index < len(tooltip_rows):
                candidate = str(tooltip_rows[category_index])
                if "Observations:" in candidate:
                    note = "Observations: " + candidate.split(
                        "Observations:", 1
                    )[1].strip()
            zones.append(
                f'<rect x="{left + group_width * category_index:.2f}" '
                f'y="{top}" width="{group_width:.2f}" height="{plot_height}" '
                'fill="transparent" '
                'class="chart-mark shared-hover-zone grouped-hover-zone" '
                'tabindex="0" '
                f'data-tooltip="{hc.esc(legacy)}" '
                f'data-tooltip-json="{_tooltip_payload(category, tooltip_items, note)}" '
                f'aria-label="{hc.esc(legacy)}" />'
            )

    svg = f"""<svg class="analysis-chart grouped-bar-chart" viewBox="0 0 {hc.WIDTH} {hc.HEIGHT}" role="img" aria-label="{hc.esc(chart_id)}">
      {''.join(grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left}" y1="{zero_y:.2f}" x2="{left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(marks)}{''.join(zones)}{''.join(labels)}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{hc.HEIGHT - 14}" text-anchor="middle" class="axis-title">{hc.esc(x_title)}</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">{hc.esc(y_title)}</text>
    </svg>"""
    return hc.chart_shell(
        chart_id,
        svg,
        hc.legend(
            (name, hc.PALETTE[index % len(hc.PALETTE)])
            for index, (name, _) in enumerate(series)
        ),
    )


def time_line_chart(
    frame: pd.DataFrame,
    series: list[tuple[str, str]],
    *,
    chart_id: str,
    y_title: str,
    value_scale: float = 1.0,
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    existing = [(column, label) for column, label in series if column in shaped]
    values = [
        float(value) * value_scale
        for column, _ in existing
        for value in pd.to_numeric(shaped[column], errors="coerce").dropna()
    ]
    if shaped.empty or not existing or not values:
        return '<p class="muted">N/A</p>'

    y_min, y_max = min(values), max(values)
    if y_title.endswith("%"):
        y_min, y_max = min(0.0, y_min), max(0.0, y_max)
    if math.isclose(y_min, y_max):
        y_min -= 1
        y_max += 1
    padding = max((y_max - y_min) * 0.08, 0.5)
    y_min, y_max = y_min - padding, y_max + padding

    left, right, top, bottom = 78, 24, 24, 70
    plot_width = hc.WIDTH - left - right
    plot_height = hc.HEIGHT - top - bottom
    date_min = shaped["date"].iloc[0]
    date_max = shaped["date"].iloc[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / date_span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    step = hc.nice_step(y_max - y_min, 6)
    tick = math.ceil(y_min / step) * step
    grid: list[str] = []
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" '
            f'y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    paths: list[str] = []
    for series_index, (column, _label) in enumerate(existing):
        color = hc.PALETTE[series_index % len(hc.PALETTE)]
        coords: list[tuple[float, float]] = []
        for _, row in shaped.iterrows():
            if not hc.finite(row[column]):
                continue
            date = pd.Timestamp(row["date"])
            value = float(row[column]) * value_scale
            coords.append((x_for(date), y_for(value)))
        if coords:
            paths.append(
                f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coords)}" '
                f'fill="none" stroke="{color}" stroke-width="2.2" '
                'class="line-series" />'
            )

    zones: list[str] = []
    rows = list(shaped.iterrows())
    for position, (_, row) in enumerate(rows):
        date = pd.Timestamp(row["date"])
        x = x_for(date)
        prev_x = (
            x_for(pd.Timestamp(rows[position - 1][1]["date"]))
            if position > 0
            else left
        )
        next_x = (
            x_for(pd.Timestamp(rows[position + 1][1]["date"]))
            if position + 1 < len(rows)
            else left + plot_width
        )
        x0 = (prev_x + x) / 2 if position > 0 else left
        x1 = (x + next_x) / 2 if position + 1 < len(rows) else left + plot_width
        items = [
            (
                label,
                hc.pct(float(row[column]) * value_scale),
                hc.PALETTE[index % len(hc.PALETTE)],
            )
            for index, (column, label) in enumerate(existing)
            if hc.finite(row.get(column))
        ]
        if items:
            legacy = _legacy_tooltip(date.strftime("%Y-%m-%d"), items)
            zones.append(
                f'<rect x="{x0:.2f}" y="{top}" '
                f'width="{max(x1 - x0, 1):.2f}" height="{plot_height}" '
                'fill="transparent" '
                'class="chart-mark shared-hover-zone line-hover-zone" '
                'tabindex="0" '
                f'data-tooltip="{hc.esc(legacy)}" '
                f'data-tooltip-json="{_tooltip_payload(date.strftime("%b %d, %Y"), items)}" '
                f'aria-label="{hc.esc(legacy)}" />'
            )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 24}" '
        f'text-anchor="middle" class="axis-label x-tick-label">'
        f'{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(shaped["date"])
    )

    svg = f"""<svg class="analysis-chart line-chart" viewBox="0 0 {hc.WIDTH} {hc.HEIGHT}" role="img" aria-label="{hc.esc(chart_id)}">
      {''.join(grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      {''.join(paths)}{''.join(zones)}{x_ticks}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{hc.HEIGHT - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">{hc.esc(y_title)}</text>
    </svg>"""
    return hc.chart_shell(
        chart_id,
        svg,
        hc.legend(
            (label, hc.PALETTE[index % len(hc.PALETTE)])
            for index, (_, label) in enumerate(existing)
        ),
    )


def growth_svg(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    series_labels: dict[str, str] | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    labels = series_labels or {}
    columns = [
        column for column in frame if str(column).endswith("_balance")
    ]
    keys = [column[: -len("_balance")] for column in columns]
    order = [name for name in (portfolio_order or []) if name in keys]
    if "benchmark" in keys:
        order.append("benchmark")
    order.extend(key for key in keys if key not in order)

    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    series = [
        (f"{key}_balance", labels.get(key, key))
        for key in order
    ]
    values = [
        float(value)
        for column, _ in series
        for value in pd.to_numeric(shaped[column], errors="coerce").dropna()
    ]
    if not values:
        return '<p class="muted">N/A</p>'

    y_min, y_max = min(values), max(values)
    step = hc.nice_step(max(y_max - y_min, 1), 6)
    y_min = math.floor(y_min / step) * step
    y_max = math.ceil(y_max / step) * step
    if math.isclose(y_min, y_max):
        y_max += step

    left, right, top, bottom = 88, 24, 20, 74
    plot_width = hc.WIDTH - left - right
    plot_height = hc.HEIGHT - top - bottom
    date_min = shaped["date"].iloc[0]
    date_max = shaped["date"].iloc[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / date_span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    y_grid: list[str] = []
    tick = y_min
    while tick <= y_max + step * 0.1 and len(y_grid) < 20:
        y = y_for(tick)
        y_grid.append(
            f'<line x1="{left}" y1="{y:.2f}" '
            f'x2="{left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">'
            f'{hc.esc(hc.money(tick, currency))}</text>'
        )
        tick += step

    paths: list[str] = []
    for index, (column, _label) in enumerate(series):
        coords = [
            (
                x_for(pd.Timestamp(row["date"])),
                y_for(float(row[column])),
            )
            for _, row in shaped.iterrows()
            if hc.finite(row.get(column))
        ]
        if coords:
            paths.append(
                f'<polyline fill="none" '
                f'stroke="{hc.PALETTE[index % len(hc.PALETTE)]}" '
                'stroke-width="2.2" '
                f'points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coords)}" '
                'class="growth-series" />'
            )

    rows = list(shaped.iterrows())
    zones: list[str] = []
    for position, (_, row) in enumerate(rows):
        date = pd.Timestamp(row["date"])
        x = x_for(date)
        prev_x = (
            x_for(pd.Timestamp(rows[position - 1][1]["date"]))
            if position > 0
            else left
        )
        next_x = (
            x_for(pd.Timestamp(rows[position + 1][1]["date"]))
            if position + 1 < len(rows)
            else left + plot_width
        )
        x0 = (prev_x + x) / 2 if position > 0 else left
        x1 = (x + next_x) / 2 if position + 1 < len(rows) else left + plot_width
        items = [
            (
                label,
                hc.money(row[column], currency),
                hc.PALETTE[index % len(hc.PALETTE)],
            )
            for index, (column, label) in enumerate(series)
            if hc.finite(row.get(column))
        ]
        legacy = _legacy_tooltip(date.strftime("%Y-%m-%d"), items)
        zones.append(
            f'<rect x="{x0:.2f}" y="{top}" '
            f'width="{max(x1 - x0, 1):.2f}" height="{plot_height}" '
            'fill="transparent" '
            'class="chart-mark shared-hover-zone growth-hover-zone" '
            'tabindex="0" '
            f'data-tooltip="{hc.esc(legacy)}" '
            f'data-tooltip-json="{_tooltip_payload(date.strftime("%b %Y"), items)}" '
            f'aria-label="{hc.esc(legacy)}" />'
        )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 26}" '
        f'text-anchor="middle" class="axis-label x-tick-label">'
        f'{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(shaped["date"])
    )

    svg = f"""<svg class="growth-chart analysis-chart" viewBox="0 0 {hc.WIDTH} {hc.HEIGHT}" role="img" aria-label="Portfolio balance growth over time">
      {''.join(y_grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      {x_ticks}{''.join(paths)}{''.join(zones)}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{hc.HEIGHT - 14}" text-anchor="middle" class="axis-title">Year</text>
      <text x="22" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 22 {top + plot_height / 2:.2f})">Portfolio Balance ({hc.esc(hc.currency_label(currency))})</text>
    </svg>"""
    return hc.chart_shell(
        "portfolio-growth",
        svg,
        hc.legend(
            (label, hc.PALETTE[index % len(hc.PALETTE)])
            for index, (_, label) in enumerate(series)
        ),
    ).replace(
        '<div class="chart-tooltip generic-tooltip"',
        '<div id="growth-tooltip" class="chart-tooltip generic-tooltip"',
        1,
    )


def _column(frame: pd.DataFrame, *names: str) -> str | None:
    return next((name for name in names if name in frame.columns), None)


def trailing_returns_table(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    columns = {
        "3m": _column(frame, "return_3m_pct", "3m_pct"),
        "ytd": _column(frame, "ytd_pct"),
        "1y": _column(frame, "return_1y_pct", "1y_pct"),
        "3y": _column(frame, "annualized_3y_pct", "3y_pct"),
        "5y": _column(frame, "annualized_5y_pct", "5y_pct"),
        "full": _column(
            frame, "full_period_cagr_pct", "full_period_pct"
        ),
        "vol3": _column(
            frame,
            "volatility_3y_pct",
            "3y_annualized_volatility_pct",
        ),
        "vol5": _column(
            frame,
            "volatility_5y_pct",
            "5y_annualized_volatility_pct",
        ),
    }
    ranking = {
        name: index for index, name in enumerate(portfolio_order or [])
    }
    rendered = frame.copy()
    rendered["_order"] = rendered["portfolio"].map(
        lambda value: len(ranking)
        if str(value) == "benchmark"
        else ranking.get(str(value), len(ranking) + 1)
    )
    rendered = rendered.sort_values("_order")
    rows: list[str] = []
    for _, row in rendered.iterrows():
        label = hc.display_portfolio(row["portfolio"], benchmark_label)
        values = [
            hc.pct(row[columns[key]]) if columns[key] else "N/A"
            for key in (
                "3m",
                "ytd",
                "1y",
                "3y",
                "5y",
                "full",
                "vol3",
                "vol5",
            )
        ]
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(label)}</td>'
            + "".join(f"<td>{hc.esc(value)}</td>" for value in values)
            + "</tr>"
        )
    return (
        '<div class="table-wrap"><table id="trailing-returns" '
        'class="pv-grouped-table"><thead>'
        '<tr><th rowspan="2">Name</th>'
        '<th colspan="3">Total Return</th>'
        '<th colspan="3">Annualized Return</th>'
        '<th colspan="2">Annualized Standard Deviation</th></tr>'
        '<tr><th>3 Month</th><th>Year To Date</th><th>1 Year</th>'
        '<th>3 Year</th><th>5 Year</th><th>Full</th>'
        '<th>3 Year</th><th>5 Year</th></tr>'
        f"</thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def annual_returns_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if frame.empty or "year" not in frame:
        return '<p class="muted">N/A</p>'
    series: list[tuple[str, list[float | None]]] = []
    for name in portfolio_order:
        column = f"{name}_return_pct"
        if column in frame:
            series.append(
                (
                    name,
                    [
                        float(value) if hc.finite(value) else None
                        for value in frame[column]
                    ],
                )
            )
    if "benchmark_return_pct" in frame:
        series.append(
            (
                benchmark_label or "Benchmark",
                [
                    float(value) if hc.finite(value) else None
                    for value in frame["benchmark_return_pct"]
                ],
            )
        )
    return grouped_bar_chart(
        [str(int(value)) for value in frame["year"]],
        series,
        chart_id="annual-returns-chart",
        y_title="Annual Return %",
        x_title="Year",
    )


def annual_asset_returns_chart(
    frame: pd.DataFrame,
    asset_names: dict[str, str] | None = None,
) -> str:
    if frame.empty or not {"year", "ticker"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    value_column = (
        "return_pct"
        if "return_pct" in frame
        else "return"
        if "return" in frame
        else None
    )
    if value_column is None:
        return '<p class="muted">N/A</p>'

    shaped = frame.copy()
    values = pd.to_numeric(shaped[value_column], errors="coerce")
    if value_column == "return":
        values = values * 100.0
    shaped["_return_pct"] = values
    years = sorted(int(value) for value in shaped["year"].dropna().unique())
    tickers: list[str] = []
    for ticker in shaped["ticker"].astype(str):
        if ticker not in tickers:
            tickers.append(ticker)

    names = asset_names or {}
    series: list[tuple[str, list[float | None]]] = []
    for ticker in tickers:
        part = shaped[
            shaped["ticker"].astype(str) == ticker
        ].set_index("year")["_return_pct"]
        name = names.get(ticker, "").strip()
        label = f"{name} ({ticker})" if name else ticker
        series.append(
            (
                label,
                [
                    float(part.loc[year])
                    if year in part.index and hc.finite(part.loc[year])
                    else None
                    for year in years
                ],
            )
        )

    return grouped_bar_chart(
        [str(year) for year in years],
        series,
        chart_id="annual-asset-returns-chart",
        y_title="Return %",
        x_title="Year",
    )


def correlations_table(
    frame: pd.DataFrame,
    benchmark_label: str | None = None,
    asset_names: dict[str, str] | None = None,
    portfolio_order: list[str] | None = None,
) -> str:
    if frame.empty or "series" not in frame:
        return '<p class="muted">N/A</p>'

    names = asset_names or {}
    all_series = [str(value) for value in frame["series"]]
    row_keys = (
        [key for key in names if key in all_series]
        if names
        else all_series
    )
    if not row_keys:
        row_keys = all_series

    if names:
        asset_columns = [
            key for key in names if key in frame.columns
        ]
    else:
        asset_columns = [
            column for column in frame.columns if column != "series"
        ]

    extra_columns = [
        name
        for name in (portfolio_order or [])
        if name in frame.columns and name not in asset_columns
    ]
    if "benchmark" in frame.columns and "benchmark" not in asset_columns:
        extra_columns.append("benchmark")
    columns = asset_columns + [
        column for column in extra_columns if column not in asset_columns
    ]
    if not columns:
        columns = [
            column for column in frame.columns if column != "series"
        ]

    lookup = frame.copy()
    lookup["series"] = lookup["series"].astype(str)
    lookup = lookup.set_index("series")

    header = "".join(
        f"<th>{hc.esc(hc.display_portfolio(column, benchmark_label))}</th>"
        for column in columns
    )

    rows: list[str] = []
    for key in row_keys:
        if key not in lookup.index:
            continue
        source = lookup.loc[key]
        if isinstance(source, pd.DataFrame):
            source = source.iloc[0]
        cells: list[str] = []
        for column in columns:
            value = source.get(column)
            numeric = (
                float(value) if hc.finite(value) else float("nan")
            )
            if math.isfinite(numeric):
                alpha = 0.04 + 0.58 * max(
                    0.0, min(1.0, numeric)
                )
                style = f"background:rgba(49,109,181,{alpha:.3f})"
                text = hc.correlation(numeric)
            else:
                style = ""
                text = "N/A"
            cells.append(
                f'<td class="heatmap-cell" style="{style}">'
                f"{hc.esc(text)}</td>"
            )
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(key)}</td>'
            f'<td class="identity-cell">{hc.esc(names.get(key, ""))}</td>'
            + "".join(cells)
            + "</tr>"
        )

    return (
        '<div class="table-wrap correlation-wrap">'
        '<table id="correlations-heatmap" '
        'class="heatmap monthly-correlations">'
        f"<thead><tr><th>Ticker</th><th>Name</th>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _percent_or_fraction(
    row: pd.Series,
    percent_name: str,
    raw_name: str | None = None,
) -> str:
    if percent_name in row and hc.finite(row.get(percent_name)):
        return hc.pct(row.get(percent_name))
    if raw_name and raw_name in row and hc.finite(row.get(raw_name)):
        return hc.fraction_pct(row.get(raw_name))
    return "N/A"


def portfolio_assets_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rows = []
    for _, row in frame.iterrows():
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(row.get("ticker", ""))}</td>'
            f'<td class="identity-cell">{hc.esc(row.get("name", ""))}</td>'
            f'<td>{hc.esc(_percent_or_fraction(row, "cagr_pct", "cagr"))}</td>'
            f'<td>{hc.esc(_percent_or_fraction(row, "annualized_volatility_pct", "annualized_volatility"))}</td>'
            f'<td>{hc.esc(_percent_or_fraction(row, "best_year_pct", "best_year"))}</td>'
            f'<td>{hc.esc(_percent_or_fraction(row, "worst_year_pct", "worst_year"))}</td>'
            f'<td>{hc.esc(_percent_or_fraction(row, "max_drawdown_pct", "max_drawdown"))}</td>'
            f'<td>{hc.esc(hc.ratio(row.get("sharpe_ratio")))}</td>'
            f'<td>{hc.esc(hc.ratio(row.get("sortino_ratio")))}</td>'
            "</tr>"
        )
    return (
        '<div class="table-wrap"><table id="portfolio-assets">'
        "<thead><tr><th>Ticker</th><th>Name</th><th>CAGR</th>"
        "<th>Stdev</th><th>Best Year</th><th>Worst Year</th>"
        "<th>Max Drawdown</th><th>Sharpe Ratio</th>"
        f"<th>Sortino Ratio</th></tr></thead><tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def portfolio_asset_trailing_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rows = []
    for _, row in frame.iterrows():
        def value(name: str) -> str:
            return (
                hc.fraction_pct(row.get(name))
                if hc.finite(row.get(name))
                else "N/A"
            )
        rows.append(
            "<tr>"
            f'<td class="identity-cell">{hc.esc(row.get("name") or row.get("ticker", ""))}</td>'
            f"<td>{hc.esc(value('3m'))}</td>"
            f"<td>{hc.esc(value('ytd'))}</td>"
            f"<td>{hc.esc(value('1y'))}</td>"
            f"<td>{hc.esc(value('3y'))}</td>"
            f"<td>{hc.esc(value('5y'))}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table id="portfolio-asset-performance" class="pv-grouped-table">'
        '<thead><tr><th rowspan="2">Name</th>'
        '<th colspan="3">Total Return</th>'
        '<th colspan="2">Annualized Return</th></tr>'
        "<tr><th>3 Month</th><th>Year To Date</th><th>1 Year</th>"
        "<th>3 Year</th><th>5 Year</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _month_delta(
    start: Any,
    end: Any,
    *,
    inclusive: bool = False,
) -> int | None:
    start_ts = pd.to_datetime(start, errors="coerce")
    end_ts = pd.to_datetime(end, errors="coerce")
    if pd.isna(start_ts) or pd.isna(end_ts):
        return None
    months = (
        (end_ts.year - start_ts.year) * 12
        + end_ts.month
        - start_ts.month
    )
    return months + (1 if inclusive else 0)


def _duration_label(months: int | None) -> str:
    if months is None or months < 0:
        return "N/A"
    if months < 12:
        return f"{months} month" + ("" if months == 1 else "s")
    years, remainder = divmod(months, 12)
    parts = [
        f"{years} year" + ("" if years == 1 else "s")
    ]
    if remainder:
        parts.append(
            f"{remainder} month" + ("" if remainder == 1 else "s")
        )
    return " ".join(parts)


def _drawdown_chart(
    frame: pd.DataFrame,
    column: str,
    label: str,
    chart_id: str,
) -> str:
    if frame.empty or "date" not in frame or column not in frame:
        return '<p class="muted">N/A</p>'
    shaped = frame[["date", column]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped[column] = pd.to_numeric(shaped[column], errors="coerce")
    shaped = shaped.dropna().sort_values("date")
    if shaped.empty:
        return '<p class="muted">N/A</p>'

    left, right, top, bottom = 78, 24, 24, 70
    plot_width = hc.WIDTH - left - right
    plot_height = hc.HEIGHT - top - bottom

    y_min = min(float(shaped[column].min()), -1.0)
    step = hc.nice_step(abs(y_min), 5)
    y_min = math.floor(y_min / step) * step
    y_max = 0.0

    date_min = shaped["date"].iloc[0]
    date_max = shaped["date"].iloc[-1]
    span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    grid: list[str] = []
    tick = y_min
    while tick <= step * 0.1 and len(grid) < 20:
        y = y_for(tick)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" '
            f'x2="{left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">{hc.esc(hc.pct(tick))}</text>'
        )
        tick += step

    coords = [
        (
            x_for(pd.Timestamp(row["date"])),
            y_for(float(row[column])),
        )
        for _, row in shaped.iterrows()
    ]
    path = (
        f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coords)}" '
        f'fill="none" stroke="{hc.PALETTE[0]}" stroke-width="2.2" '
        'class="drawdown-series" />'
    )

    rows = list(shaped.iterrows())
    zones = []
    for position, (_, row) in enumerate(rows):
        date = pd.Timestamp(row["date"])
        x = x_for(date)
        prev_x = (
            x_for(pd.Timestamp(rows[position - 1][1]["date"]))
            if position
            else left
        )
        next_x = (
            x_for(pd.Timestamp(rows[position + 1][1]["date"]))
            if position + 1 < len(rows)
            else left + plot_width
        )
        x0 = (prev_x + x) / 2 if position else left
        x1 = (
            (x + next_x) / 2
            if position + 1 < len(rows)
            else left + plot_width
        )
        items = [
            (label, hc.pct(row[column]), hc.PALETTE[0])
        ]
        legacy = _legacy_tooltip(date.strftime("%Y-%m-%d"), items)
        zones.append(
            f'<rect x="{x0:.2f}" y="{top}" '
            f'width="{max(x1 - x0, 1):.2f}" height="{plot_height}" '
            'fill="transparent" '
            'class="chart-mark shared-hover-zone drawdown-hover-zone" '
            'tabindex="0" '
            f'data-tooltip="{hc.esc(legacy)}" '
            f'data-tooltip-json="{_tooltip_payload(date.strftime("%b %Y"), items)}" '
            f'aria-label="{hc.esc(legacy)}" />'
        )

    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 24}" '
        'text-anchor="middle" class="axis-label x-tick-label">'
        f'{hc.esc(date.strftime("%b %Y"))}</text>'
        for date in hc.calendar_ticks(shaped["date"])
    )

    svg = f"""<svg class="analysis-chart drawdown-chart" viewBox="0 0 {hc.WIDTH} {hc.HEIGHT}" role="img" aria-label="{hc.esc(label)} drawdown">
      {''.join(grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left}" y1="{y_for(0):.2f}" x2="{left + plot_width}" y2="{y_for(0):.2f}" class="axis zero-axis" />
      {path}{''.join(zones)}{x_ticks}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{hc.HEIGHT - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">Drawdown %</text>
    </svg>"""
    return hc.chart_shell(chart_id, svg)


def _drawdown_episode_table(part: pd.DataFrame) -> str:
    if part.empty:
        return '<p class="muted">N/A</p>'
    ordered = (
        part.sort_values("rank")
        if "rank" in part
        else part
    ).head(10)
    rows = []
    for _, row in ordered.iterrows():
        start = pd.to_datetime(row.get("start"), errors="coerce")
        bottom = pd.to_datetime(row.get("bottom"), errors="coerce")
        recovery = pd.to_datetime(row.get("recovery"), errors="coerce")
        length = _duration_label(
            _month_delta(start, bottom, inclusive=True)
        )
        recovery_time = _duration_label(
            _month_delta(bottom, recovery)
        )
        underwater = _duration_label(
            _month_delta(start, recovery, inclusive=True)
        )
        drawdown = row.get(
            "maximum_drawdown_pct",
            row.get("max_drawdown_pct"),
        )
        rows.append(
            "<tr>"
            f"<td>{hc.esc(row.get('rank', ''))}</td>"
            f"<td>{hc.esc(start.strftime('%b %Y') if not pd.isna(start) else 'N/A')}</td>"
            f"<td>{hc.esc(bottom.strftime('%b %Y') if not pd.isna(bottom) else 'N/A')}</td>"
            f"<td>{hc.esc(length)}</td>"
            f"<td>{hc.esc(recovery.strftime('%b %Y') if not pd.isna(recovery) else 'N/A')}</td>"
            f"<td>{hc.esc(recovery_time)}</td>"
            f"<td>{hc.esc(underwater)}</td>"
            f"<td>{hc.esc(hc.pct(drawdown))}</td>"
            "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table class="drawdown-episodes pv-drawdown-table">'
        "<thead><tr><th>Rank</th><th>Start</th><th>End</th>"
        "<th>Length</th><th>Recovery By</th><th>Recovery Time</th>"
        "<th>Underwater Period</th><th>Drawdown</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        '<p class="muted">Worst 10 drawdowns included above</p>'
    )


def drawdown_presentation(
    series_frame: pd.DataFrame,
    episodes_frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    blocks = []
    targets = [
        (name, f"{name}_drawdown_pct", name)
        for name in portfolio_order
    ]
    if "benchmark_drawdown_pct" in series_frame:
        targets.append(
            (
                "benchmark",
                "benchmark_drawdown_pct",
                benchmark_label or "Benchmark",
            )
        )

    for key, column, label in targets:
        if column not in series_frame:
            continue
        if not episodes_frame.empty and "portfolio" in episodes_frame:
            part = episodes_frame[
                episodes_frame["portfolio"].astype(str) == key
            ].copy()
        else:
            part = pd.DataFrame()
        blocks.append(
            f'<div class="analysis-panel drawdown-panel" '
            f'data-portfolio="{hc.esc(key)}">'
            f"<h3>Drawdowns for {hc.esc(label)}</h3>"
            f'{_drawdown_chart(series_frame, column, label, f"drawdown-{key}")}'
            "<h4>Drawdown Episodes</h4>"
            f"{_drawdown_episode_table(part)}</div>"
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def rolling_summary_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if frame.empty or "roll_period_years" not in frame:
        return '<p class="muted">N/A</p>'

    groups = list(portfolio_order)
    if any(
        column.startswith("benchmark_")
        for column in frame.columns
    ):
        groups.append("benchmark")

    top = ['<th rowspan="2">Roll Period</th>']
    second: list[str] = []
    for group in groups:
        top.append(
            f'<th colspan="3">'
            f'{hc.esc(hc.display_portfolio(group, benchmark_label))}</th>'
        )
        second.extend(
            ["<th>Average</th>", "<th>High</th>", "<th>Low</th>"]
        )

    rows: list[str] = []
    periods = pd.to_numeric(
        frame["roll_period_years"],
        errors="coerce",
    )
    for years in (1, 3, 5):
        part = frame[periods == years]
        if part.empty:
            continue
        row = part.iloc[0]
        cells = [
            f"<td>{years} year" + ("" if years == 1 else "s") + "</td>"
        ]
        for group in groups:
            for metric in ("average", "high", "low"):
                column = f"{group}_{metric}_pct"
                value = row.get(column)
                cls = (
                    ' class="negative-value"'
                    if (
                        metric == "low"
                        and hc.finite(value)
                        and float(value) < 0
                    )
                    else ""
                )
                cells.append(
                    f"<td{cls}>{hc.esc(hc.pct(value))}</td>"
                )
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<div class="table-wrap">'
        '<table id="rolling-returns-summary" class="pv-grouped-table">'
        f"<thead><tr>{''.join(top)}</tr>"
        f"<tr>{''.join(second)}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def rolling_returns_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    years: int,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    series: list[tuple[str, str]] = []
    for name in portfolio_order:
        column = f"{name}_annualized_return_pct"
        if column in frame:
            series.append((column, name))
    if "benchmark_annualized_return_pct" in frame:
        series.append(
            (
                "benchmark_annualized_return_pct",
                benchmark_label or "Benchmark",
            )
        )
    return time_line_chart(
        frame,
        series,
        chart_id=f"rolling-{years}y-annualized-return",
        y_title="Annualized Return %",
    )


def return_decomposition_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str] | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty or "asset" not in frame:
        return '<p class="muted">N/A</p>'
    names = asset_names or {}
    headers = "".join(
        f"<th>{hc.esc(name)}</th>" for name in portfolio_order
    )
    rows = []
    for _, row in frame.iterrows():
        ticker = str(row["asset"])
        if ticker.startswith("contribution_"):
            ticker = ticker[len("contribution_") :]
        cells = []
        for portfolio in portfolio_order:
            column = f"{portfolio}_contribution_balance"
            cells.append(
                f"<td>{hc.esc(hc.money(row.get(column), currency) if hc.finite(row.get(column)) else '')}</td>"
            )
        rows.append(
            f'<tr><td class="identity-cell">{hc.esc(ticker)}</td>'
            f'<td class="identity-cell">{hc.esc(names.get(ticker, ""))}</td>'
            + "".join(cells)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table id="portfolio-return-decomposition">'
        f"<thead><tr><th>Ticker</th><th>Name</th>{headers}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        '<p class="muted">Return attribution decomposes portfolio gains '
        "into constituent assets and identifies each asset contribution "
        "to returns.</p>"
    )


def risk_decomposition_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str] | None = None,
) -> str:
    if frame.empty or "asset" not in frame:
        return '<p class="muted">N/A</p>'
    names = asset_names or {}
    headers = "".join(
        f"<th>{hc.esc(name)}</th>" for name in portfolio_order
    )
    rows = []
    for _, row in frame.iterrows():
        ticker = str(row["asset"])
        cells = []
        for portfolio in portfolio_order:
            column = f"{portfolio}_risk_contribution_pct"
            cells.append(
                f"<td>{hc.esc(hc.pct(row.get(column)) if hc.finite(row.get(column)) else '')}</td>"
            )
        rows.append(
            f'<tr><td class="identity-cell">{hc.esc(ticker)}</td>'
            f'<td class="identity-cell">{hc.esc(names.get(ticker, ""))}</td>'
            + "".join(cells)
            + "</tr>"
        )
    return (
        '<div class="table-wrap">'
        '<table id="portfolio-risk-decomposition">'
        f"<thead><tr><th>Ticker</th><th>Name</th>{headers}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
        '<p class="muted">Risk attribution decomposes portfolio risk '
        "into constituent assets and identifies each asset contribution "
        "to overall volatility.</p>"
    )
