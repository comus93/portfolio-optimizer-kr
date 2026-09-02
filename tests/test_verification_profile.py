from pathlib import Path

import yaml


def test_agent_verification_profile_has_backtest_and_regression_stages():
    root = Path(__file__).resolve().parents[1]
    profile = yaml.safe_load((root / "verification" / "profile.yaml").read_text(encoding="utf-8"))

    assert profile["version"] == 1
    assert "tests/test_backtest.py" in " ".join(profile["tests"]["targeted"])
    assert "tests/test_runner.py" in " ".join(profile["tests"]["affected_regression"])
    assert profile["real_run"]["config"] == "configs/backtest-example.yaml"
    assert profile["browser"]["required_for_report_changes"] is True
    assert profile["human_visual_review"]["when"] == "material_layout_or_interaction_change"
