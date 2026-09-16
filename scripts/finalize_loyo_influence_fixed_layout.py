from pathlib import Path

CHANGE = Path("openspec/changes/2026-09-16-loyo-influence-fixed-layout")


def update_overlay() -> None:
    path = Path("src/portfolio_optimizer_kr/viewer/loyo_overlay.py")
    text = path.read_text(encoding="utf-8")
    marker = "#loyo-robustness .loyo-asset-ticker { display: block; margin-top: 2px; color: #64748b; font-size: 11px; font-weight: 700; }\n"
    addition = """#loyo-robustness table.loyo-influence { width: 100%; min-width: 0; table-layout: fixed; }\n#loyo-robustness .loyo-influence thead th:first-child { width: 56px; }\n#loyo-robustness .loyo-influence thead th:nth-child(2) { width: 176px; }\n#loyo-robustness .loyo-influence .loyo-year,\n#loyo-robustness .loyo-influence .loyo-metric,\n#loyo-robustness .loyo-influence .loyo-asset-head,\n#loyo-robustness .loyo-influence .loyo-value { min-width: 0; }\n#loyo-robustness .loyo-influence .loyo-metric { white-space: nowrap; }\n#loyo-robustness .loyo-influence .loyo-asset-name { max-width: 100%; }\n"""
    if "table.loyo-influence { width: 100%;" not in text:
        if marker not in text:
            raise SystemExit("LOYO asset ticker CSS marker not found")
        text = text.replace(marker, marker + addition, 1)
    path.write_text(text, encoding="utf-8")


def update_ui_spec() -> None:
    path = Path("docs/report-ui-specification.md")
    text = path.read_text(encoding="utf-8")
    old = """- wide asset matrix는 horizontal scroll 허용\n- missing LOYO value는 `N/A`, 0으로 대체하지 않음\n"""
    new = """- Asset-Year Influence는 normal desktop report width에서 `width: 100%` fixed layout을 사용해 horizontal scrollbar 없이 한 화면에 표시한다. Year는 compact fixed width, Metric은 현실적인 fixed width에서 한 줄을 유지하고, 나머지 폭은 asset columns가 균등 분배한다.\n- LOYO Summary / Allocation Changes처럼 내용 자체가 더 넓은 표는 horizontal scroll을 허용한다.\n- missing LOYO value는 `N/A`, 0으로 대체하지 않음\n"""
    if old in text:
        text = text.replace(old, new, 1)
    elif "Asset-Year Influence는 normal desktop report width" not in text:
        raise SystemExit("LOYO precision/overflow section marker not found")
    path.write_text(text, encoding="utf-8")


def promote_spec() -> None:
    target = Path("openspec/specs/research-report/spec.md")
    delta = CHANGE / "specs/research-report/spec.md"
    marker = "### Requirement: Asset-Year Influence fits the primary desktop report width"
    base = target.read_text(encoding="utf-8")
    if marker not in base:
        addition = delta.read_text(encoding="utf-8").replace("## ADDED Requirements\n", "", 1).strip()
        target.write_text(base.rstrip() + "\n\n" + addition + "\n", encoding="utf-8")


def complete_tasks() -> None:
    path = CHANGE / "tasks.md"
    text = path.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
    path.write_text(text, encoding="utf-8")


def update_handover() -> None:
    path = Path("ai-share/llm-to-llm.md")
    text = path.read_text(encoding="utf-8")
    marker = "<!-- latest-loyo-fixed-layout -->"
    block = """<!-- latest-loyo-fixed-layout -->\n## Latest LOYO UI refinement — fixed Asset-Year Influence width\n\n- Asset-Year Influence now uses `width:100%` + `table-layout:fixed` at normal desktop width.\n- Year column is 56px, Metric column 176px and remains single-line; remaining width is evenly shared by asset columns.\n- Generic LOYO matrix natural-width behavior remains for LOYO Summary / Allocation Changes.\n- Existing Name/Ticker two-line identity, ellipsis, year zebra banding and numeric heatmap are preserved.\n- Run `20260914-0003` report is regenerated from persisted artifacts only; no optimization/LOYO recalculation.\n"""
    if marker not in text:
        first_break = text.find("\n")
        if first_break >= 0:
            text = text[:first_break + 1] + "\n" + block + "\n" + text[first_break + 1:]
        else:
            text = text + "\n\n" + block
    path.write_text(text, encoding="utf-8")


update_overlay()
update_ui_spec()
promote_spec()
complete_tasks()
update_handover()
