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
