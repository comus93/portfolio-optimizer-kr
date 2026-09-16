from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGE = ROOT / "openspec/changes/2026-09-16-loyo-readability-layout"


def update_template() -> None:
    path = ROOT / "site/report-template.html"
    lines = path.read_text(encoding="utf-8").splitlines()
    loyo_index = next(i for i, line in enumerate(lines) if 'id="loyo-robustness"' in line)
    loyo_line = lines.pop(loyo_index)
    metrics_index = next(i for i, line in enumerate(lines) if 'id="portfolio-metrics"' in line)
    lines.insert(metrics_index + 1, loyo_line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_ui_spec() -> None:
    path = ROOT / "docs/report-ui-specification.md"
    text = path.read_text(encoding="utf-8")
    marker = "### 26.5 Placement and asset identity"
    if marker in text:
        return
    addition = r'''

### 26.5 Placement and asset identity

LOYO section은 report reading flow에서 다음 위치를 사용한다.

```text
Portfolio Metrics
Leave-One-Year-Out Robustness
Monthly Returns
```

Asset-Year Influence의 Year와 Metric 영역은 4-row year group 단위로 alternating zebra background를 사용한다. Zebra background는 Year/Metric 두 column에만 적용하고 numeric asset cell의 metric-specific conditional background를 덮어쓰지 않는다.

Asset-Year Influence와 Allocation Changes의 asset column header는 다음 2-line identity를 사용한다.

```text
<Name, single-line ellipsis within column width>
<Ticker, full value>
```

모든 자산에 같은 identity convention을 적용한다. Name 전체를 보기 위한 추가 hover/tooltip interaction은 만들지 않는다.

LOYO Summary의 Allocation Shift cell은 compact `Ticker + signed delta` 표현을 유지한다. Summary table 바로 아래에는 다음 mapping을 static wrapping legend로 표시한다.

```text
Ticker · Name
```

Legend는 한 줄에 가능한 여러 asset을 배치하고 viewport 폭이 부족하면 CSS wrapping한다. Asset identity를 위해 browser-side finance calculation 또는 추가 interactive JavaScript를 사용하지 않는다.
'''.rstrip()
    path.write_text(text.rstrip() + "\n" + addition + "\n", encoding="utf-8")


def promote_openspec() -> None:
    target = ROOT / "openspec/specs/research-report/spec.md"
    delta = CHANGE / "specs/research-report/spec.md"
    marker = "### Requirement: LOYO section placement follows result-reading flow"
    base = target.read_text(encoding="utf-8")
    if marker not in base:
        addition = delta.read_text(encoding="utf-8")
        addition = addition.replace("## ADDED Requirements\n", "", 1).strip()
        target.write_text(base.rstrip() + "\n\n" + addition + "\n", encoding="utf-8")


def complete_tasks() -> None:
    path = CHANGE / "tasks.md"
    text = path.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
    path.write_text(text, encoding="utf-8")


def update_handover() -> None:
    path = ROOT / "ai-share/llm-to-llm.md"
    text = path.read_text(encoding="utf-8")
    start = "<!-- latest-loyo-readability:start -->"
    end = "<!-- latest-loyo-readability:end -->"
    block = f'''{start}
## Latest Update — 2026-09-16 LOYO readability refinement

- LOYO section placement: Portfolio Metrics → Leave-One-Year-Out Robustness → Monthly Returns.
- Asset-Year Influence uses four-row year-group zebra banding on Year/Metric columns only; numeric conditional backgrounds remain unchanged.
- Asset-Year Influence and Allocation Changes use two-line asset headers: Name with CSS ellipsis, then full Ticker. No new hover/tooltip interaction was added.
- LOYO Summary keeps compact ticker + signed delta shift cells and adds a static wrapping `Ticker · Name` legend below the table.
- This change is presentation-only. LOYO/annual-return/optimization calculations and persisted finance artifacts are unchanged.
{end}'''
    if start in text and end in text:
        left, rest = text.split(start, 1)
        _, right = rest.split(end, 1)
        text = left.rstrip() + "\n\n" + block + right
    else:
        first_break = text.find("\n")
        if first_break >= 0:
            text = text[: first_break + 1] + "\n" + block + "\n\n" + text[first_break + 1 :]
        else:
            text = text + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    update_template()
    update_ui_spec()
    promote_openspec()
    complete_tasks()
    update_handover()


if __name__ == "__main__":
    main()
