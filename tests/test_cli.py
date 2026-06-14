import json
from pathlib import Path

import pytest

from enterprise_data_strategy_agent.cli import DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_PATH, build_parser, main


def test_analyze_parser_uses_demo_defaults():
    args = build_parser().parse_args(["analyze"])

    assert args.command == "analyze"
    assert args.input == str(DEFAULT_INPUT_PATH)
    assert args.output == str(DEFAULT_OUTPUT_PATH)
    assert args.format == "markdown"
    assert args.print_summary is False


def test_analyze_parser_accepts_json_and_summary():
    args = build_parser().parse_args(["analyze", "--format", "json", "--print-summary"])

    assert args.format == "json"
    assert args.print_summary is True


def test_validate_parser_uses_demo_default_input():
    args = build_parser().parse_args(["validate"])

    assert args.command == "validate"
    assert args.input == str(DEFAULT_INPUT_PATH)
    assert args.print_summary is False


def test_analyze_writes_json_output_and_summary(tmp_path, capsys):
    output_path = tmp_path / "nested" / "analysis.json"

    result = main(["analyze", "--output", str(output_path), "--format", "json", "--print-summary"])

    assert result == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["platform"].startswith("Domo")
    assert "analysis" in payload
    captured = capsys.readouterr()
    assert "generated" in captured.out
    assert "Health Scores:" in captured.out
    assert "Top Risks:" in captured.out


def test_validate_returns_nonzero_for_lint_findings(capsys):
    result = main(["validate"])

    assert result == 1
    captured = capsys.readouterr()
    assert "Inventory validation passed" in captured.out
    assert "Lint results:" in captured.out


def test_missing_input_returns_error(tmp_path, capsys):
    missing = tmp_path / "missing.json"

    result = main(["analyze", "--input", str(missing), "--output", str(tmp_path / "out.md")])

    assert result == 2
    captured = capsys.readouterr()
    assert "inventory file not found" in captured.err


def test_invalid_json_returns_error(tmp_path, capsys):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{not json", encoding="utf-8")

    result = main(["validate", "--input", str(invalid)])

    assert result == 2
    captured = capsys.readouterr()
    assert "invalid JSON" in captured.err


def test_validation_failure_returns_error(tmp_path, capsys):
    invalid_inventory = tmp_path / "inventory.json"
    invalid_inventory.write_text(json.dumps({"platform": "Domo"}), encoding="utf-8")

    result = main(["validate", "--input", str(invalid_inventory)])

    assert result == 2
    captured = capsys.readouterr()
    assert "inventory validation failed" in captured.err


def test_invalid_format_rejected_by_parser():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["analyze", "--format", "xml"])

def test_lint_command_succeeds_with_findings_and_writes_report(tmp_path, capsys):
    output_path = tmp_path / "lint.md"

    result = main(["lint", "--input", str(DEFAULT_INPUT_PATH), "--output", str(output_path)])

    assert result == 0
    captured = capsys.readouterr()
    assert "Inventory structural validation passed" in captured.out
    assert "Metadata lint summary:" in captured.out
    assert "Total findings" in captured.out
    report = output_path.read_text(encoding="utf-8")
    assert "# Enterprise Data Metadata Lint Report" in report
    assert "## Recommended Fix Order" in report


def test_plan_command_writes_markdown_and_json_with_config(tmp_path, capsys):
    markdown = tmp_path / "plan.md"
    backlog = tmp_path / "backlog.json"

    result = main([
        "plan",
        "--input", str(DEFAULT_INPUT_PATH),
        "--output", str(markdown),
        "--json-output", str(backlog),
        "--config", "config/sample_strategy_policy.yml",
    ])

    assert result == 0
    assert "Enterprise data remediation plan generated" in capsys.readouterr().out
    plan = markdown.read_text(encoding="utf-8")
    assert "# Enterprise Data Remediation Plan" in plan
    assert "## Executive Summary" in plan
    assert "## P0 Immediate Actions" in plan
    assert "## 30/60/90 Day Execution Plan" in plan
    payload = json.loads(backlog.read_text(encoding="utf-8"))
    assert payload["remediation_items"]
    assert payload["summary"]["total_items"] == len(payload["remediation_items"])


def test_plan_command_works_without_config(tmp_path):
    markdown = tmp_path / "plan.md"

    result = main(["plan", "--input", str(DEFAULT_INPUT_PATH), "--output", str(markdown)])

    assert result == 0
    assert "Custom policy used: no" in markdown.read_text(encoding="utf-8")

import os
import subprocess
import sys


def _run_cli(args, tmp_path=None):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    return subprocess.run(
        [sys.executable, "-m", "enterprise_data_strategy_agent.cli", *args],
        cwd=Path.cwd(),
        env=env,
        input=b"",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
    )


def test_module_help_exits_successfully_without_stdin(tmp_path):
    result = _run_cli(["--help"], tmp_path)
    assert result.returncode == 0
    assert b"doctor" in result.stdout


def test_doctor_command_exits_successfully_from_repo_root(tmp_path):
    result = _run_cli(["doctor"], tmp_path)
    assert result.returncode == 0, result.stderr.decode()
    assert b"[OK] Found pyproject.toml" in result.stdout


def test_lint_analyze_plan_subprocesses_generate_outputs_without_stdin(tmp_path):
    lint_out = tmp_path / "lint.md"
    brief_out = tmp_path / "brief.md"
    plan_out = tmp_path / "plan.md"
    backlog_out = tmp_path / "backlog.json"

    commands = [
        ["lint", "--input", "data/sample_domo_inventory.json", "--output", str(lint_out), "--config", "config/sample_strategy_policy.yml"],
        ["analyze", "--input", "data/sample_domo_inventory.json", "--output", str(brief_out), "--config", "config/sample_strategy_policy.yml"],
        ["plan", "--input", "data/sample_domo_inventory.json", "--output", str(plan_out), "--json-output", str(backlog_out), "--config", "config/sample_strategy_policy.yml"],
    ]
    for command in commands:
        result = _run_cli(command, tmp_path)
        assert result.returncode == 0, result.stderr.decode()
        assert b"Done." in result.stdout

    assert lint_out.exists()
    assert brief_out.exists()
    assert plan_out.exists()
    assert backlog_out.exists()


def test_cli_import_does_not_import_streamlit():
    code = "import sys; import enterprise_data_strategy_agent.cli; print('streamlit' in sys.modules)"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd() / "src")
    result = subprocess.run([sys.executable, "-c", code], cwd=Path.cwd(), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    assert result.returncode == 0, result.stderr.decode()
    assert result.stdout.strip() == b"False"
