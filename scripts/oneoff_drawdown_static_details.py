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
        raise SystemExit(f"pattern not found in {path}: {old[:180]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


pv_path = Path("src/portfolio_optimizer_kr/viewer/pv_visual.py")
pv_text = pv_path.read_text(encoding="utf-8")
start = pv_text.index("def _drawdown_overlay_chart(\n")
end = pv_text.index("def _canonical_month_value(", start)
overlay = pv_text[start:end]
if 'drawdown_colors = ("#2563eb", "#16a34a", "#f97316")' not in overlay:
    overlay = overlay.replace(
        '    colors: list[str] = []\n',
        '    drawdown_colors = ("#2563eb", "#16a34a", "#f97316")\n'
        '    colors: list[str] = []\n',
        1,
    )
    overlay = overlay.replace(
        '        color = hc.PALETTE[index % len(hc.PALETTE)]\n',
        '        color = drawdown_colors[index % len(drawdown_colors)]\n',
        1,
    )
pv_text = pv_text[:start] + overlay + pv_text[end:]
pv_path.write_text(pv_text, encoding="utf-8")


presentation = r'''def _drawdown_resilience_table(
    resilience_frame: pd.DataFrame | None,
    targets: list[tuple[str, str, str]],
) -> str:
    rows: list[str] = []
    for key, _column, label in targets:
        if (
            resilience_frame is not None
            and not resilience_frame.empty
            and "portfolio" in resilience_frame
        ):
            part = resilience_frame[
                resilience_frame["portfolio"].astype(str) == key
            ]
        else:
            part = pd.DataFrame()

        if part.empty:
            value_text = "N/A"
            completed_text = "N/A"
        else:
            row = part.iloc[0]
            value = row.get("normalized_underwater_duration_months_per_10pct")
            value_text = (
                f"{float(value):.1f}개월 / 10% DD"
                if hc.finite(value)
                else "N/A"
            )
            count = row.get("completed_episode_count")
            limit = row.get("episode_limit")
            if hc.finite(count) and hc.finite(limit):
                completed_text = f"{int(float(count))}/{int(float(limit))}"
            elif hc.finite(count):
                completed_text = str(int(float(count)))
            else:
                completed_text = "N/A"

        rows.append(
            '<tr class="drawdown-resilience-row" '
            f'data-portfolio="{hc.esc(key)}">'
            f'<td class="identity-cell">{hc.esc(label)}</td>'
            f'<td>{hc.esc(value_text)}</td>'
            f'<td>{hc.esc(completed_text)}</td>'
            '</tr>'
        )

    return (
        '<div class="drawdown-resilience-summary">'
        '<p class="panel-subtitle"><strong>탄성회복도</strong> · '
        'Normalized Underwater Duration · 낮을수록 좋음</p>'
        '<div class="table-wrap"><table class="drawdown-resilience-table">'
        '<thead><tr><th>Portfolio</th><th>탄성회복도</th>'
        '<th>Completed Episodes</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></div>'
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

    drawdown_colors = ("#2563eb", "#16a34a", "#f97316")
    selector_inputs: list[str] = []
    selector_labels: list[str] = []
    detail_blocks: list[str] = []
    selector_rules: list[str] = []

    for index, (key, _column, label) in enumerate(targets):
        control_id = f"drawdown-select-{index}"
        color = drawdown_colors[index % len(drawdown_colors)]
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

        detail_blocks.append(
            f'<div class="drawdown-detail" data-portfolio="{hc.esc(key)}" '
            f'data-series-index="{index}">'
            f'<h3>Drawdowns for {hc.esc(label)}</h3>'
            '<h4>Drawdown Episodes</h4>'
            f'{_drawdown_episode_table(part)}</div>'
        )
        selector_rules.extend(
            [
                f'#{control_id}:checked ~ .drawdown-selector label[for="{control_id}"]'
                '{background:#eef4ff;border-color:var(--color);color:#0f172a;font-weight:700}',
                f'#{control_id}:checked ~ .drawdown-chart-host '
                f'.drawdown-focus-series[data-series-index="{index}"]'
                '{opacity:1;stroke-width:3.8}',
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
        '.drawdown-base-series{opacity:.58;stroke-width:1.9;transition:opacity .15s,stroke-width .15s}'
        '.drawdown-focus-series{opacity:0;stroke-width:3.8;transition:opacity .15s}'
        '.drawdown-resilience-summary{margin-top:14px}'
        '.drawdown-resilience-table{min-width:520px}'
        '.drawdown-details{margin-top:20px}'
        '.drawdown-detail{margin-top:24px}'
        + ''.join(selector_rules)
        + '</style>'
    )
    chart = _drawdown_overlay_chart(series_frame, targets)
    resilience = _drawdown_resilience_table(resilience_frame, targets)
    return (
        '<div class="analysis-panel drawdown-comparison-panel">'
        '<h3>Drawdown Comparison</h3>'
        '<p class="panel-subtitle">Select a portfolio to foreground its drawdown path. Comparison metrics and Worst Drawdowns remain visible for every portfolio.</p>'
        f'{style}{"".join(selector_inputs)}'
        f'<div class="drawdown-selector" role="radiogroup" aria-label="Drawdown portfolio selection">{"".join(selector_labels)}</div>'
        f'<div class="drawdown-chart-host">{chart}</div>'
        f'{resilience}'
        f'<div class="drawdown-details">{"".join(detail_blocks)}</div>'
        '</div>'
    )
'''

replace_block(
    "src/portfolio_optimizer_kr/viewer/pv_visual.py",
    "def _drawdown_resilience_kpi(",
    "def rolling_summary_table(",
    presentation,
)


replace_once(
    "tests/test_drawdown_elasticity.py",
    '    assert "completed 7/10 episodes" in rendered\n',
    '    assert \'class="drawdown-resilience-table"\' in rendered\n'
    '    assert "Completed Episodes" in rendered\n'
    '    assert ">7/10</td>" in rendered\n',
)

replace_once(
    "tests/test_backtest_report_content_contract.py",
    "def test_drawdowns_share_one_overlay_chart_and_selected_detail_markup():\n",
    "def test_drawdowns_share_one_overlay_chart_and_static_comparison_details():\n",
)
replace_once(
    "tests/test_backtest_report_content_contract.py",
    '            {"portfolio": "Growth 70/30", "normalized_underwater_duration_months_per_10pct": 4.2, "completed_episode_count": 7},\n'
    '            {"portfolio": "Balanced 50/50", "normalized_underwater_duration_months_per_10pct": 5.1, "completed_episode_count": 6},\n'
    '            {"portfolio": "benchmark", "normalized_underwater_duration_months_per_10pct": 6.3, "completed_episode_count": 8},\n',
    '            {"portfolio": "Growth 70/30", "normalized_underwater_duration_months_per_10pct": 4.2, "completed_episode_count": 7, "episode_limit": 10},\n'
    '            {"portfolio": "Balanced 50/50", "normalized_underwater_duration_months_per_10pct": 5.1, "completed_episode_count": 6, "episode_limit": 10},\n'
    '            {"portfolio": "benchmark", "normalized_underwater_duration_months_per_10pct": 6.3, "completed_episode_count": 8, "episode_limit": 10},\n',
)
replace_once(
    "tests/test_backtest_report_content_contract.py",
    '    assert "4.2개월 / 10% DD" in rendered\n',
    '    assert \'class="drawdown-resilience-table"\' in rendered\n'
    '    assert "4.2개월 / 10% DD" in rendered\n'
    '    assert "5.1개월 / 10% DD" in rendered\n'
    '    assert "6.3개월 / 10% DD" in rendered\n'
    '    assert rendered.index("Growth 70/30") < rendered.index("Balanced 50/50") < rendered.index(html.escape(BENCHMARK))\n'
    '    assert "#2563eb" in rendered and "#16a34a" in rendered and "#f97316" in rendered\n'
    '    assert "opacity:.58" in rendered\n',
)


browser_path = Path("verification/browser/backtest-report-content.spec.mjs")
browser = browser_path.read_text(encoding="utf-8")
old = '''    const firstChoice = drawdowns.locator('.drawdown-choice').first();
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
new = '''    const firstChoice = drawdowns.locator('.drawdown-choice').first();
    const secondChoice = drawdowns.locator('.drawdown-choice').nth(1);
    const details = drawdowns.locator('.drawdown-detail');
    const resilienceRows = drawdowns.locator('.drawdown-resilience-table tbody tr');
    const choiceCount = await drawdowns.locator('.drawdown-choice').count();
    await expect(details).toHaveCount(choiceCount);
    await expect(resilienceRows).toHaveCount(choiceCount);
    await expect(firstChoice).toBeChecked();
    for (let index = 0; index < choiceCount; index += 1) {
      await expect(details.nth(index)).toBeVisible();
      await expect(resilienceRows.nth(index)).toBeVisible();
    }
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '1');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '0');
    await expect(drawdowns.locator('.drawdown-base-series').first()).toHaveCSS('opacity', '0.58');
    await drawdowns.locator('.drawdown-selector-label').nth(1).click();
    await expect(secondChoice).toBeChecked();
    await expect(drawdowns.locator('.drawdown-focus-series').first()).toHaveCSS('opacity', '0');
    await expect(drawdowns.locator('.drawdown-focus-series').nth(1)).toHaveCSS('opacity', '1');
    for (let index = 0; index < choiceCount; index += 1) {
      await expect(details.nth(index)).toBeVisible();
      await expect(resilienceRows.nth(index)).toBeVisible();
    }
    await expect(details.nth(1).getByText('Recovery By', { exact: true })).toBeVisible();
    await expect(details.nth(1).getByText('Recovery Time', { exact: true })).toBeVisible();
    await expect(details.nth(1).getByText('Underwater Period', { exact: true })).toBeVisible();
'''
if old not in browser:
    raise SystemExit("backtest browser drawdown block not found")
browser_path.write_text(browser.replace(old, new, 1), encoding="utf-8")


# Mark implementation tasks complete; representative report regeneration remains for the workflow tail.
task_path = Path("openspec/changes/2026-09-11-drawdown-recovery-episodes/tasks.md")
tasks = task_path.read_text(encoding="utf-8")
for task in [
    "overlay context line 가시성 상향 및 Drawdown 전용 blue/green/orange color order 적용",
    "overlay chart 아래 모든 portfolio 탄성회복도 comparison table 상시 표시",
    "Worst Drawdowns episode table을 Provided/Optimized/Benchmark 순서로 모두 상시 표시",
    "foreground 선택이 chart line emphasis에만 영향을 주도록 browser contract 수정",
]:
    tasks = tasks.replace(f"- [ ] {task}", f"- [x] {task}")
task_path.write_text(tasks, encoding="utf-8")
