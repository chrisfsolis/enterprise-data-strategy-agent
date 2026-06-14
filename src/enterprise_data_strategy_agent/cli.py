"""Command line interface for the Enterprise Data Strategy Agent."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from json import JSONDecodeError
from pathlib import Path

from enterprise_data_strategy_agent.analyzer import AnalysisResult, analyze_inventory
from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.doctor import run_doctor
from enterprise_data_strategy_agent.linting import generate_markdown_lint_report, lint_inventory
from enterprise_data_strategy_agent.models import Inventory
from enterprise_data_strategy_agent.policy import StrategyPolicy, load_policy
from enterprise_data_strategy_agent.planning import generate_json_backlog, generate_markdown_remediation_plan
from enterprise_data_strategy_agent.report import generate_markdown_report

DEFAULT_INPUT_PATH = Path("data/sample_domo_inventory.json")
DEFAULT_OUTPUT_PATH = Path("examples/generated_strategy_brief.md")
DEFAULT_POLICY_PATH = Path("config/sample_strategy_policy.yml")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Analyze enterprise analytics metadata and generate strategy artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check that the repo is ready to run")

    analyze = subparsers.add_parser("analyze", help="Generate an enterprise data strategy brief")
    analyze.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to inventory JSON (default: {DEFAULT_INPUT_PATH})")
    analyze.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help=f"Path to write output (default: {DEFAULT_OUTPUT_PATH})")
    analyze.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format (default: markdown)")
    analyze.add_argument("--print-summary", action="store_true", help="Print top risks and health scores to stdout")
    analyze.add_argument("--config", help="Optional strategy policy YAML file")

    validate = subparsers.add_parser("validate", help="Validate and lint an inventory without generating a strategy brief")
    validate.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to inventory JSON (default: {DEFAULT_INPUT_PATH})")
    validate.add_argument("--print-summary", action="store_true", help="Print top risks and health scores to stdout")

    lint = subparsers.add_parser("lint", help="Run metadata quality and governance lint checks")
    lint.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to inventory JSON (default: {DEFAULT_INPUT_PATH})")
    lint.add_argument("--output", help="Optional path to write a markdown lint report")
    lint.add_argument("--config", help="Optional strategy policy YAML file")

    plan = subparsers.add_parser("plan", help="Generate an actionable enterprise data remediation plan")
    plan.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to inventory JSON (default: {DEFAULT_INPUT_PATH})")
    plan.add_argument("--output", required=True, help="Path to write the markdown remediation plan")
    plan.add_argument("--json-output", help="Optional path to write a machine-readable JSON remediation backlog")
    plan.add_argument("--config", help="Optional strategy policy YAML file")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the non-interactive CLI."""

    args = build_parser().parse_args(argv)
    if args.command == "doctor":
        return run_doctor()
    if args.command == "analyze":
        return _run_analyze(args)
    if args.command == "lint":
        return _run_lint(args)
    if args.command == "plan":
        return _run_plan(args)
    if args.command == "validate":
        return _run_validate(args)
    return 1


def _run_analyze(args: argparse.Namespace) -> int:
    print("Loading inventory...")
    inventory = _load_inventory(Path(args.input))
    if inventory is None:
        return 2
    print("Loading policy...")
    policy = _load_policy(args.config)
    if policy is None:
        return 2
    print("Running analysis...")
    analysis = analyze_inventory(inventory, policy)
    print("Generating report...")
    output = _format_analysis(inventory, analysis, args.format, policy)
    print("Writing output...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    print(f"Enterprise data strategy {args.format} output generated: {output_path}")
    if args.print_summary:
        _print_summary(analysis)
    print("Done.")
    return 0


def _run_lint(args: argparse.Namespace) -> int:
    print("Loading inventory...")
    inventory = _load_inventory(Path(args.input))
    if inventory is None:
        return 2
    print("Loading policy...")
    policy = _load_policy(args.config)
    if policy is None:
        return 2
    print("Running lint...")
    findings = lint_inventory(inventory, policy)
    print(f"Inventory structural validation passed: {args.input}")
    print(f"Datasets: {len(inventory.datasets)}")
    print(f"Dashboards/cards: {len(inventory.dashboards)}")
    _print_lint_summary(findings)
    if args.output:
        print("Generating report...")
        print("Writing output...")
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(generate_markdown_lint_report(inventory, findings, policy), encoding="utf-8")
        print(f"Metadata lint report generated: {output_path}")
    print("Done.")
    return 0


def _run_plan(args: argparse.Namespace) -> int:
    print("Loading inventory...")
    inventory = _load_inventory(Path(args.input))
    if inventory is None:
        return 2
    print("Loading policy...")
    policy = _load_policy(args.config)
    if policy is None:
        return 2
    print("Running analysis...")
    analysis = analyze_inventory(inventory, policy)
    print("Generating report...")
    markdown = generate_markdown_remediation_plan(inventory, analysis, policy)
    print("Writing output...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Enterprise data remediation plan generated: {output_path}")
    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(generate_json_backlog(inventory, analysis, policy), encoding="utf-8")
        print(f"Enterprise data remediation backlog JSON generated: {json_path}")
    print("Done.")
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    print("Loading inventory...")
    inventory = _load_inventory(Path(args.input))
    if inventory is None:
        return 2
    print("Running analysis...")
    analysis = analyze_inventory(inventory)
    print(f"Inventory validation passed: {args.input}")
    print(f"Datasets: {len(inventory.datasets)}")
    print(f"Dashboards: {len(inventory.dashboards)}")
    lint_count = _print_lint_results(analysis)
    if args.print_summary:
        _print_summary(analysis)
    print("Done.")
    return 1 if lint_count else 0


def _load_policy(config_path: str | None) -> StrategyPolicy | None:
    try:
        return load_policy(config_path)
    except (OSError, ValueError) as exc:
        print(f"Error: strategy policy config failed for {config_path}: {exc}", file=sys.stderr)
        return None


def _load_inventory(input_path: Path) -> Inventory | None:
    if not input_path.exists():
        print(f"Error: inventory file not found: {input_path}", file=sys.stderr)
        return None
    if not input_path.is_file():
        print(f"Error: inventory path is not a file: {input_path}", file=sys.stderr)
        return None
    try:
        return DomoMockConnector().load_inventory(input_path)
    except JSONDecodeError as exc:
        print(f"Error: invalid JSON in {input_path}: {exc.msg} at line {exc.lineno}, column {exc.colno}", file=sys.stderr)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Error: inventory validation failed for {input_path}: {exc}", file=sys.stderr)
    return None


def _format_analysis(inventory: Inventory, analysis: AnalysisResult, output_format: str, policy: StrategyPolicy | None = None) -> str:
    if output_format == "json":
        return json.dumps({"platform": inventory.platform, "generated_at": inventory.generated_at.isoformat(), "dataset_count": len(inventory.datasets), "dashboard_count": len(inventory.dashboards), "analysis": asdict(analysis)}, indent=2)
    return generate_markdown_report(inventory, analysis, policy)


def _print_summary(analysis: AnalysisResult) -> None:
    print("Health Scores:")
    for name, score in asdict(analysis.scores).items():
        print(f"- {name}: {score}/100")
    print("Top Risks:")
    for risk in analysis.top_risks or ["No top risks detected."]:
        print(f"- {risk}")


def _print_lint_results(analysis: AnalysisResult) -> int:
    findings = [*(f"Top risk: {risk}" for risk in analysis.top_risks), *(f"Risky dashboard: {dashboard}" for dashboard in analysis.risky_dashboards), *(f"Stale dataset: {dataset}" for dataset in analysis.stale_datasets), *(f"Duplicate metric candidate: {metric}" for metric in analysis.duplicate_metrics)]
    if not findings:
        print("Lint results: no findings detected.")
        return 0
    print("Lint results:")
    for finding in findings:
        print(f"- {finding}")
    return len(findings)


def _print_lint_summary(findings) -> None:
    severities = ("critical", "high", "medium", "low")
    print("Metadata lint summary:")
    print(f"- Total findings: {len(findings)}")
    for severity in severities:
        print(f"- {severity.title()}: {sum(1 for finding in findings if finding.severity == severity)}")
    for finding in findings[:5]:
        print(f"- {finding.severity.upper()} {finding.rule_id}: {finding.title} ({finding.affected_object_type} {finding.affected_object_id})")


if __name__ == "__main__":
    raise SystemExit(main())
