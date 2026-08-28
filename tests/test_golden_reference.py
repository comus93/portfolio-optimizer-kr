from pathlib import Path

import pytest


GOLDEN_DIR = Path(__file__).parent / "golden" / "pv"


@pytest.mark.golden
def test_pv_golden_reference_files_are_present():
    assert (GOLDEN_DIR / "260828_PTF_maxsharpe.md").is_file()
    assert (GOLDEN_DIR / "260828_PTF_maxsharpe.jpg").is_file()


@pytest.mark.golden
def test_pv_golden_markdown_contains_reference_portfolio():
    text = (GOLDEN_DIR / "260828_PTF_maxsharpe.md").read_text(encoding="utf-8")
    for token in ["Maximum Sharpe Ratio", "QQQ", "SPMO", "GLD", "XLE", "17.21%", "13.10%"]:
        assert token in text
