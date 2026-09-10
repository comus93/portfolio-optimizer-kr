from __future__ import annotations

import argparse
from pathlib import Path

from portfolio_optimizer_kr.report.public_links import register_public_report_url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Persist an exact public report URL for a completed run."
    )
    parser.add_argument("run_dir", help="Path to runs/<run_id>")
    parser.add_argument("url", help="Exact public report URL supplied by the executor")
    args = parser.parse_args()

    target = register_public_report_url(Path(args.run_dir), args.url)
    print(target)


if __name__ == "__main__":
    main()
