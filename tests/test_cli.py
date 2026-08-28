from pathlib import Path

from portfolio_optimizer_kr.cli import main


def test_cli_validate_uses_same_yaml_contract(tmp_path: Path, capsys):
    config = tmp_path / "run.yaml"
    config.write_text(
        """
run_id: cli-demo
assets:
  - symbol: A
  - symbol: B
risk_free:
  mode: fixed
  annual_rate_pct: 0
""",
        encoding="utf-8",
    )

    assert main(["validate", str(config)]) == 0
    assert "valid: cli-demo" in capsys.readouterr().out
