from __future__ import annotations

import argparse
from pathlib import Path

from portfolio_optimizer_kr.report.navigation import write_run_readme, write_runs_index
from portfolio_optimizer_kr.report.public_links import refresh_all_public_report_links


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild derived run navigation artifacts.")
    parser.add_argument("--runs-root", default="runs")
    parser.add_argument(
        "--include-run-readmes",
        action="store_true",
        help="Also rewrite per-run README.md files from persisted artifacts.",
    )
    args = parser.parse_args()

    root = Path(args.runs_root)
    if args.include_run_readmes and root.is_dir():
        for run_dir in sorted(root.iterdir()):
            if run_dir.is_dir() and (run_dir / "result.json").is_file():
                write_run_readme(run_dir)

    target = write_runs_index(root)
    refresh_all_public_report_links(root)
    print(target)


if __name__ == "__main__":
    main()
