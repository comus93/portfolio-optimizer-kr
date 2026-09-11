from __future__ import annotations

from pathlib import Path


def replace_block(path: str, start_marker: str, end_marker: str, replacement: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    target.write_text(text[:start] + replacement.rstrip() + "\n\n\n" + text[end:], encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"pattern not found in {path}: {old[:160]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


pv_overlay = r'''def _drawdown_overlay_chart(
    frame: pd.DataFrame,
    targets: list[tuple[str, str, str]],
    chart_id: str = "drawdown-comparison",
) -> str:
    available = [target for target in targets if target[1] in frame.columns]
    if frame.empty or "date" not in frame or not available:
        return '<p class="muted">N/A</p>'

    shaped = frame[["date"] + [column for _, column, _ in available]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    for _, column, _ in available:
        shaped[column] = pd.to_numeric(shaped[column], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    shaped = shaped[
        shaped[[column for _, column, _ in available]].notna().any(axis=1)
    ]
    if shaped.empty:
        return '<p class="muted">N/A</p>'

    values = [
        float(value)
        for _, column, _ in available
        for value in shaped[column]
        if hc.finite(value)
    ]
    if not values:
        return '<p class="muted">N/A</p>'

    left, right, top, bottom = 78, 24, 24, 70
    plot_width = hc.WIDTH - left - right
    plot_height = hc.HEIGHT - top - bottom
    y_min = min(min(values), -1.0)
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

    base_paths: list[str] = []
    focus_paths: list[str] = []
    colors: list[str] = []
    for index, (_, column, label) in enumerate(available):
        color = hc.PALETTE[index % len(hc.PALETTE)]
        colors.append(color)
        part = shaped[["date", column]].dropna()
        coords = [
            (
                x_for(pd.Timestamp(row["date"])),
                y_for(float(row[column])),
            )
            for _, row in part.iterrows()
        ]
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)
        if not points:
            continue
        base_paths.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'data-series-index="{index}" data-series-label="{hc.esc(label)}" '
            'class="drawdown-base-series" />'
        )
        focus_paths.append(
            f'<polyline points="{points}" fill="none" stroke="{color}" '
            f'data-series-index="{index}" data-series-label="{hc.esc(label)}" '
            'class="drawdown-focus-series" pointer-events="none" />'
        )

    rows = list(shaped.iterrows())
    zones: list[str] = []
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
            (label, hc.pct(row[column]), colors[index])
            for index, (_, column, label) in enumerate(available)
            if hc.finite(row.get(column))
        ]
        if not items:
            continue
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

    svg = f"""<svg class="analysis-chart drawdown-chart drawdown-comparison-chart" viewBox="0 0 {hc.WIDTH} {hc.HEIGHT}" role="img" aria-label="Drawdown comparison">
      {''.join(grid)}
      <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" class="axis y-axis-line" />
      <line x1="{left}" y1="{y_for(0):.2f}" x2="{left + plot_width}" y2="{y_for(0):.2f}" class="axis zero-axis" />
      {''.join(base_paths)}{''.join(focus_paths)}{''.join(zones)}{x_ticks}
      <line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" class="axis x-axis-line" />
      <text x="{left + plot_width / 2:.2f}" y="{hc.HEIGHT - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">Drawdown %</text>
    </svg>"""
    return hc.chart_shell(chart_id, svg)
'''

replace_block(
    "src/portfolio_optimizer_kr/viewer/pv_visual.py",
    "def _drawdown_chart(\n",
    "def _canonical_month_value(\n",
    pv_overlay,
)

pv_presentation = r'''def _drawdown_resilience_kpi(part: pd.DataFrame) -> str:
    if part.empty:
        value_text = "N/A"
        sample_text = ""
    else:
        row = part.iloc[0]
        value = row.get("normalized_underwater_duration_months_per_10pct")
        value_text = f"{float(value):.1f}개월 / 10% DD" if hc.finite(value) else "N/A"
        count = row.get("completed_episode_count")
        sample_text = (
            f" · completed {int(float(count))}/10 episodes"
            if hc.finite(count)
            else ""
        )
    return (
        '<p class="panel-subtitle drawdown-elasticity-kpi">'
        '<strong>탄성회복도</strong> · '
        f'{hc.esc(value_text)} · 낮을수록 좋음{hc.esc(sample_text)}</p>'
    )


def drawdown_presentation(
    series_frame: pd.DataFrame,
    episodes_frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    resilience_frame: pd.DataFrame | None = None,
) -> str:
    targets = [
        (name, f"{name}_drawdown_pct", name)
        for name in portfolio_order
        if f"{name}_drawdown_pct" in series_frame
    ]
    if "benchmark_drawdown_pct" in series_frame:
        targets.append(
            (
                "benchmark",
                "benchmark_drawdown_pct",
                benchmark_label or "Benchmark",
            )
        )
    if not targets:
        return '<p class="muted">N/A</p>'

    selector_inputs: list[str] = []
    selector_labels: list[str] = []
    detail_blocks: list[str] = []
    selector_rules: list[str] = []

    for index, (key, _column, label) in enumerate(targets):
        control_id = f"drawdown-select-{index}"
        color = hc.PALETTE[index % len(hc.PALETTE)]
        selector_inputs.append(
            f'<input class="drawdown-choice" type="radio" name="drawdown-selected-series" '
            f'id="{control_id}" value="{hc.esc(key)}" '
            + ("checked " if index == 0 else "")
            + '/>'
        )
        selector_labels.append(
            f'<label class="drawdown-selector-label" for="{control_id}" '
            f'data-series-index="{index}" style="--color:{color}">'
            '<span class="drawdown-selector-dot" aria-hidden="true"></span>'
            f'{hc.esc(label)}</label>'
        )

        if not episodes_frame.empty and "portfolio" in episodes_frame:
            part = episodes_frame[
                episodes_frame["portfolio"].astype(str) == key
            ].copy()
        else:
            part = pd.DataFrame()
        if (
            resilience_frame is not None
            and not resilience_frame.empty
            and "portfolio" in resilience_frame
        ):
            resilience_part = resilience_frame[
                resilience_frame["portfolio"].astype(str) == key
            ].copy()
        else:
            resilience_part = pd.DataFrame()

        detail_blocks.append(
            f'<div class="drawdown-detail" data-portfolio="{hc.esc(key)}" '
            f'data-series-index="{index}">'
            f'<h3>Drawdowns for {hc.esc(label)}</h3>'
            f'{_drawdown_resilience_kpi(resilience_part)}'
            '<h4>Drawdown Episodes</h4>'
            f'{_drawdown_episode_table(part)}</div>'
        )
        selector_rules.extend(
            [
                f'#{control_id}:checked ~ .drawdown-selector label[for="{control_id}"]'
                '{background:#eef4ff;border-color:var(--color);color:#0f172a;font-weight:700}',
                f'#{control_id}:checked ~ .drawdown-chart-host '
                f'.drawdown-focus-series[data-series-index="{index}"]'
                '{opacity:1;stroke-width:3.6}',
                f'#{control_id}:checked ~ .drawdown-details '
                f'.drawdown-detail[data-series-index="{index}"]'
                '{display:block}',
            ]
        )

    style = (
        '<style class="drawdown-comparison-style">'
        '.drawdown-comparison-panel{border-top:1px solid #eef1f5;padding-top:8px;margin-top:18px}'
        '.drawdown-comparison-panel>.panel-subtitle{margin-bottom:10px}'
        '.drawdown-choice{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}'
        '.drawdown-selector{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:8px 0 10px}'
        '.drawdown-selector-label{display:inline-flex;align-items:center;gap:7px;padding:6px 10px;border:1px solid #d7dee8;border-radius:999px;background:#fff;color:#475569;font-size:12px;cursor:pointer;user-select:none;transition:background .15s,border-color .15s,color .15s}'
        '.drawdown-selector-label:hover{background:#f8fafc}'
        '.drawdown-selector-label:focus-visible{outline:2px solid #2563eb;outline-offset:2px}'
        '.drawdown-selector-dot{width:12px;height:3px;border-radius:99px;background:var(--color);display:inline-block}'
        '.drawdown-base-series{opacity:.34;stroke-width:1.6;transition:opacity .15s,stroke-width .15s}'
        '.drawdown-focus-series{opacity:0;stroke-width:3.6;transition:opacity .15s}'
        '.drawdown-details{margin-top:16px}'
        '.drawdown-detail{display:none}'
        + ''.join(selector_rules)
        + '</style>'
    )
    chart = _drawdown_overlay_chart(series_frame, targets)
    return (
        '<div class="analysis-panel drawdown-comparison-panel">'
        '<h3>Drawdown Comparison</h3>'
        '<p class="panel-subtitle">Select a portfolio to foreground its drawdown path and review its recovery details.</p>'
        f'{style}{"".join(selector_inputs)}'
        f'<div class="drawdown-selector" role="radiogroup" aria-label="Drawdown portfolio selection">{"".join(selector_labels)}</div>'
        f'<div class="drawdown-chart-host">{chart}</div>'
        f'<div class="drawdown-details">{"".join(detail_blocks)}</div>'
        '</div>'
    )
'''

replace_block(
    "src/portfolio_optimizer_kr/viewer/pv_visual.py",
    "def _drawdown_resilience_kpi(\n",
    "def rolling_summary_table(\n",
    pv_presentation,
)

round1_shared = r'''def _combined_drawdowns(
    series_frame: pd.DataFrame,
    episodes_frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    resilience_frame: pd.DataFrame | None = None,
) -> str:
    return pv.drawdown_presentation(
        series_frame,
        episodes_frame,
        portfolio_order,
        benchmark_label,
        resilience_frame,
    )
'''
replace_block(
    "src/portfolio_optimizer_kr/viewer/pv_round1_overlay.py",
    "def _combined_drawdowns(\n",
    "def _assets_section(\n",
    round1_shared,
)
replace_once(
    "src/portfolio_optimizer_kr/viewer/pv_round1_overlay.py",
    'f\'{_combined_drawdowns(_artifact(root, "drawdown_series.csv"), _artifact(root, "drawdowns.csv"), portfolio_order, benchmark_label)}\'',
    'f\'{_combined_drawdowns(_artifact(root, "drawdown_series.csv"), _artifact(root, "drawdowns.csv"), portfolio_order, benchmark_label, _artifact(root, "drawdown_resilience.csv"))}\'',
)
replace_once(
    "src/portfolio_optimizer_kr/viewer/pv_round1_overlay.py",
    '    html = _move_chart_legend_after(html, "drawdown-combined")\n',
    '',
)

replace_once(
    "src/portfolio_optimizer_kr/viewer/final_renderer.py",
    "      host.querySelectorAll('.legend span').forEach(span => {\n",
    "      host.querySelectorAll('.legend span, .drawdown-selector-label').forEach(span => {\n",
)

contract_test = r'''def test_drawdowns_share_one_overlay_chart_and_selected_detail_markup():
    series = pd.DataFrame(
        [
            {"date": "2024-01-31", "Growth 70/30_drawdown_pct": -2.0, "Balanced 50/50_drawdown_pct": -1.0, "benchmark_drawdown_pct": -3.0},
            {"date": "2024-02-29", "Growth 70/30_drawdown_pct": -4.0, "Balanced 50/50_drawdown_pct": -2.0, "benchmark_drawdown_pct": -5.0},
            {"date": "2024-03-31", "Growth 70/30_drawdown_pct": 0.0, "Balanced 50/50_drawdown_pct": 0.0, "benchmark_drawdown_pct": -1.0},
        ]
    )
    episodes = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": "2024-03-31", "maximum_drawdown_pct": -4.0},
            {"portfolio": "Balanced 50/50", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": "2024-03-31", "maximum_drawdown_pct": -2.0},
            {"portfolio": "benchmark", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": None, "maximum_drawdown_pct": -5.0},
        ]
    )
    episodes["decline_months"] = 2
    episodes["recovery_months"] = [1, 1, None]
    episodes["underwater_months"] = [3, 3, 3]
    episodes["annualized_recovery_rate_pct"] = [63.2, 26.8, None]
    resilience = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "normalized_underwater_duration_months_per_10pct": 4.2, "completed_episode_count": 7},
            {"portfolio": "Balanced 50/50", "normalized_underwater_duration_months_per_10pct": 5.1, "completed_episode_count": 6},
            {"portfolio": "benchmark", "normalized_underwater_duration_months_per_10pct": 6.3, "completed_episode_count": 8},
        ]
    )
    rendered = _drawdown_presentation(series, episodes, PORTFOLIOS, BENCHMARK, resilience)
    assert rendered.count('data-chart="drawdown-comparison"') == 1
    assert rendered.count('class="drawdown-base-series"') == 3
    assert rendered.count('class="drawdown-focus-series"') == 3
    assert rendered.count('class="drawdown-choice"') == 3
    assert rendered.count('class="drawdown-detail"') == 3
    assert 'id="drawdown-select-0" value="Growth 70/30" checked' in rendered
    assert 'data-series-index="1"' in rendered
    assert "Drawdown %" in rendered
    assert "Month / Year" in rendered
    assert "drawdown-hover-zone" in rendered
    assert "Growth 70/30" in rendered
    assert "Balanced 50/50" in rendered
    assert html.escape(BENCHMARK) in rendered
    assert "탄성회복도" in rendered
    assert "4.2개월 / 10% DD" in rendered
    for header in ["Start", "End", "Length", "Recovery By", "Recovery Time", "Underwater Period", "Recovery Rate", "Drawdown"]:
        assert header in rendered
    assert "Mar 2024" in rendered
    assert "Worst 10 drawdowns" in rendered
'''
replace_block(
    "tests/test_backtest_report_content_contract.py",
    "def test_drawdowns_have_axes_calendar_ticks_and_recovery_episode_fields():\n",
    "def test_annual_asset_returns_preserve_ticker_series_and_shared_year_hover():\n",
    contract_test,
)

replace_once(
    "tests/test_backtest_pv_round1.py",
    "    assert 'data-chart=\"drawdown-combined\"' in html\n    assert \"drawdown-panel\" not in html\n    assert \"drawdown-episodes-panel\" in html\n",
    "    assert html.count('data-chart=\"drawdown-comparison\"') == 1\n    assert html.count('class=\"drawdown-choice\"') == 3\n    assert html.count('class=\"drawdown-detail\"') == 3\n    assert \"drawdown-comparison-panel\" in html\n    assert \"drawdown-episodes-panel\" not in html\n",
)
replace_once(
    "tests/test_backtest_shared_end_to_end.py",
    "        'data-chart=\"drawdown-combined\"',\n",
    "        'data-chart=\"drawdown-comparison\"',\n",
)
replace_once(
    "tests/test_backtest_shared_end_to_end.py",
    "    assert \"drawdown-panel\" not in html\n    assert html.count(\"drawdown-episodes-panel\") >= 3\n",
    "    assert \"drawdown-comparison-panel\" in html\n    assert html.count('class=\"drawdown-choice\"') == 3\n    assert html.count('class=\"drawdown-detail\"') == 3\n",
)

browser_old = r'''    const drawdowns = page.locator('#drawdowns');
    const drawdownPanels = drawdowns.locator('.drawdown-panel');
    await expect(drawdownPanels).not.toHaveCount(0);
    const drawdownCount = await drawdownPanels.count();
    for (let i = 0; i < drawdownCount; i += 1) {
      const panel = drawdownPanels.nth(i);
      await expect(panel.locator('[data-chart^="drawdown-"]')).toBeVisible();
      await expect(panel.getByText('Drawdown %', { exact: true })).toBeVisible();
      await expect(panel.getByText('Recovery By', { exact: true })).toBeVisible();
      await expect(panel.getByText('Recovery Time', { exact: true })).toBeVisible();
      await expect(panel.getByText('Underwater Period', { exact: true })).toBeVisible();
    }
'''
browser_new = r'''    const drawdowns = page.locator('#drawdowns');
    await expect(drawdowns.locator('[data-chart="drawdown-comparison"]')).toHaveCount(1);
    await expect(drawdowns.locator('.drawdown-selector-label')).not.toHaveCount(0);
    await expect(drawdowns.locator('.drawdown-base-series')).not.toHaveCount(0);
    await expect(drawdowns.locator('.drawdown-focus-series')).not.toHaveCount(0);
    const firstChoice = drawdowns.locator('.drawdown-choice').first();
    const secondChoice = drawdowns.locator('.drawdown-choice').nth(1);
    await expect(firstChoice).toBeChecked();
    await expect(drawdowns.locator('.drawdown-detail').first()).toBeVisible();
    await expect(drawdowns.locator('.drawdown-detail').nth(1)).toBeHidden();
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '1');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '0');
    await drawdowns.locator('.drawdown-selector-label').nth(1).click();
    await expect(secondChoice).toBeChecked();
    await expect(drawdowns.locator('.drawdown-detail').first()).toBeHidden();
    const activeDetail = drawdowns.locator('.drawdown-detail').nth(1);
    await expect(activeDetail).toBeVisible();
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '0');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '1');
    await expect(activeDetail.getByText('Recovery By', { exact: true })).toBeVisible();
    await expect(activeDetail.getByText('Recovery Time', { exact: true })).toBeVisible();
    await expect(activeDetail.getByText('Underwater Period', { exact: true })).toBeVisible();
'''
replace_once(
    "verification/browser/backtest-report-content.spec.mjs",
    browser_old,
    browser_new,
)

# A product-neutral browser contract is run twice: once against Optimization and once against Backtest.
Path("verification/browser/drawdown-overlay.spec.mjs").write_text(
    r'''import path from 'node:path';
import { expect, test } from '@playwright/test';

const reportPath = process.env.DRAWDOWN_REPORT_PATH?.trim();
const sectionSelector = process.env.DRAWDOWN_SECTION?.trim() || '#drawdowns';

function servedPath(value) {
  const relative = path.isAbsolute(value) ? path.relative(process.cwd(), value) : value;
  if (relative.startsWith('..')) throw new Error('DRAWDOWN_REPORT_PATH must be inside repository root');
  return `/${relative.replaceAll('\\\\', '/').replace(/^\\.\\//, '')}`;
}

test.describe('shared drawdown overlay interaction', () => {
  test.skip(!reportPath, 'set DRAWDOWN_REPORT_PATH to a generated report');

  test('keeps context lines and foregrounds the selected portfolio', async ({ page }) => {
    await page.goto(servedPath(reportPath));
    const section = page.locator(sectionSelector);
    await expect(section).toBeVisible();
    await expect(section.locator('[data-chart="drawdown-comparison"]')).toHaveCount(1);

    const choices = section.locator('.drawdown-choice');
    const labels = section.locator('.drawdown-selector-label');
    const details = section.locator('.drawdown-detail');
    const baseLines = section.locator('.drawdown-base-series');
    const focusLines = section.locator('.drawdown-focus-series');
    const count = await choices.count();
    expect(count).toBeGreaterThanOrEqual(2);
    await expect(labels).toHaveCount(count);
    await expect(details).toHaveCount(count);
    await expect(baseLines).toHaveCount(count);
    await expect(focusLines).toHaveCount(count);

    await expect(choices.first()).toBeChecked();
    await expect(details.first()).toBeVisible();
    await expect(focusLines.first()).toHaveCSS('opacity', '1');
    await expect(baseLines.first()).toHaveCSS('opacity', '0.34');

    await labels.nth(1).click();
    await expect(choices.nth(1)).toBeChecked();
    await expect(details.first()).toBeHidden();
    await expect(details.nth(1)).toBeVisible();
    await expect(focusLines.first()).toHaveCSS('opacity', '0');
    await expect(focusLines.nth(1)).toHaveCSS('opacity', '1');
    await expect(baseLines.first()).toHaveCSS('opacity', '0.34');
    await expect(details.nth(1).getByText('탄성회복도', { exact: true })).toBeVisible();
    await expect(details.nth(1).getByText('Recovery By', { exact: true })).toBeVisible();
  });
});
''',
    encoding="utf-8",
)
