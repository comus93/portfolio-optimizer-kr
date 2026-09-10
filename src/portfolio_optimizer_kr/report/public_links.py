from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Any, Mapping

import yaml


_LINKS_FILE = "links.yaml"
_PUBLIC_REPORT_KEY = "public_report_url"
_RUN_CELL_RE = re.compile(r"^\[([^\]]+)\]\([^)]*\)$")


def _read_links(run_dir: Path) -> dict[str, Any]:
    path = run_dir / _LINKS_FILE
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return {}
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def public_report_url(run_dir: str | Path) -> str | None:
    value = _read_links(Path(run_dir)).get(_PUBLIC_REPORT_KEY)
    text = str(value or "").strip()
    return text or None


def register_public_report_url(
    run_dir: str | Path,
    url: str,
    *,
    refresh_navigation: bool = True,
) -> Path:
    directory = Path(run_dir)
    target = directory / _LINKS_FILE
    value = str(url).strip()
    if not value:
        raise ValueError("public report URL must not be blank")

    links = _read_links(directory)
    links[_PUBLIC_REPORT_KEY] = value
    target.write_text(
        yaml.safe_dump(links, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    if refresh_navigation:
        apply_public_report_links(directory, update_index=True)
    return target


def _apply_run_readme(run_dir: Path) -> None:
    readme_path = run_dir / "README.md"
    if not readme_path.is_file():
        return

    url = public_report_url(run_dir)
    text = readme_path.read_text(encoding="utf-8")
    text = re.sub(
        r"(?m)^- \[Public Report\]\([^\n]*\)\n?",
        "",
        text,
    )
    if url:
        marker = "## Artifacts\n\n"
        link = f"- [Public Report]({url})\n"
        if marker in text:
            text = text.replace(marker, marker + link, 1)
        else:
            text = text.rstrip() + f"\n\n## Artifacts\n\n{link}"
    readme_path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _run_id_from_cell(cell: str) -> str | None:
    match = _RUN_CELL_RE.match(cell.strip())
    return match.group(1) if match else None


def _report_cell(runs_root: Path, run_cell: str) -> str:
    run_id = _run_id_from_cell(run_cell)
    if not run_id:
        return "N/A"
    url = public_report_url(runs_root / run_id)
    return f"[Open]({url})" if url else "N/A"


def _split_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _join_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def _apply_runs_index(runs_root: Path) -> None:
    index_path = runs_root / "README.md"
    if not index_path.is_file():
        return

    lines = index_path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    for line in lines:
        cells = _split_row(line)
        if cells[:6] == [
            "Run",
            "Product",
            "Study / Experiment",
            "Period",
            "Benchmark",
            "Summary",
        ]:
            output.append(
                _join_row(
                    [
                        "Run",
                        "Product",
                        "Study / Experiment",
                        "Period",
                        "Benchmark",
                        "Report",
                        "Summary",
                    ]
                )
            )
            continue
        if cells[:7] == [
            "Run",
            "Product",
            "Study / Experiment",
            "Period",
            "Benchmark",
            "Report",
            "Summary",
        ]:
            output.append(line)
            continue
        if cells == ["---", "---", "---", "---", "---", "---"]:
            output.append(_join_row(["---"] * 7))
            continue
        if len(cells) == 6 and cells[0] != "Run":
            output.append(
                _join_row(cells[:5] + [_report_cell(runs_root, cells[0])] + [cells[5]])
            )
            continue
        if len(cells) == 7 and cells[0] != "Run":
            cells[5] = _report_cell(runs_root, cells[0])
            output.append(_join_row(cells))
            continue
        output.append(line)

    index_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")


def apply_public_report_links(
    run_dir: str | Path,
    *,
    update_index: bool = True,
) -> None:
    directory = Path(run_dir)
    _apply_run_readme(directory)
    if update_index:
        _apply_runs_index(directory.parent)


def try_apply_public_report_links(
    run_dir: str | Path,
    *,
    update_index: bool = True,
) -> bool:
    """Best-effort navigation enrichment that cannot invalidate a completed run."""
    try:
        apply_public_report_links(run_dir, update_index=update_index)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        warnings.warn(
            f"public report link refresh failed: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return False
    return True


def refresh_all_public_report_links(runs_root: str | Path) -> None:
    root = Path(runs_root)
    if root.is_dir():
        for run_dir in sorted(root.iterdir()):
            if run_dir.is_dir():
                _apply_run_readme(run_dir)
    _apply_runs_index(root)
