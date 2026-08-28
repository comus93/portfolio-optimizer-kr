from portfolio_optimizer_kr.cli import _parser


def test_validate_command_accepts_yaml_path():
    args = _parser().parse_args(["validate", "configs/example.yaml"])
    assert args.command == "validate"
    assert str(args.config) == "configs/example.yaml"


def test_run_command_accepts_output_root():
    args = _parser().parse_args(["run", "configs/example.yaml", "--output-root", "tmp-runs"])
    assert args.command == "run"
    assert str(args.output_root) == "tmp-runs"


def test_execute_command_uses_tracked_control_defaults():
    args = _parser().parse_args(["execute"])
    assert args.command == "execute"
    assert str(args.repo_root) == "."
    assert str(args.control) == "control/execute.yaml"
    assert str(args.output_root) == "runs"
