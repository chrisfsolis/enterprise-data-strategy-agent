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
from enterprise_data_strategy_agent.linting import generate_markdown_lint_report, lint_inventory
from enterprise_data_strategy_agent.models import Inventory
from enterprise_data_strategy_agent.report import generate_markdown_report

DEFAULT_INPUT_PATH = Path("data/sample_domo_inventory.json")
DEFAULT_OUTPUT_PATH = Path("examples/generated_strategy_brief.md")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Analyze enterprise analytics metadata and generate a strategy brief.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Generate an enterprise data strategy brief")
    analyze.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to synthetic inventory JSON (default: {DEFAULT_INPUT_PATH})")
    analyze.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help=f"Path to write the analysis output (default: {DEFAULT_OUTPUT_PATH})")
    analyze.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Analysis output format (default: markdown)")
    analyze.add_argument("--print-summary", action="store_true", help="Print top risks and health scores to stdout")

    validate = subparsers.add_parser("validate", help="Validate and lint an inventory without generating a strategy brief")
    validate.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to synthetic inventory JSON (default: {DEFAULT_INPUT_PATH})")
    validate.add_argument("--print-summary", action="store_true", help="Print top risks and health scores to stdout")

    lint = subparsers.add_parser("lint", help="Run advisory metadata quality and governance lint checks")
    lint.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help=f"Path to synthetic inventory JSON (default: {DEFAULT_INPUT_PATH})")
    lint.add_argument("--output", help="Optional path to write a markdown lint report")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""

    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        inventory = _load_inventory(Path(args.input))
        if inventory is None:
            return 2

        analysis = analyze_inventory(inventory)
        output_path = Path(args.output)
        output = _format_analysis(inventory, analysis, args.format)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(f"Enterprise data strategy {args.format} output generated: {output_path}")
        if args.print_summary:
            _print_summary(analysis)
        return 0

    if args.command == "lint":
        inventory = _load_inventory(Path(args.input))
        if inventory is None:
            return 2

        findings = lint_inventory(inventory)
        print(f"Inventory structural validation passed: {args.input}")
        print(f"Datasets: {len(inventory.datasets)}")
        print(f"Dashboards/cards: {len(inventory.dashboards)}")
        _print_lint_summary(findings)
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(generate_markdown_lint_report(inventory, findings), encoding="utf-8")
            print(f"Metadata lint report generated: {output_path}")
        return 0

    if args.command == "validate":
        inventory = _load_inventory(Path(args.input))
        if inventory is None:
            return 2

        analysis = analyze_inventory(inventory)
        print(f"Inventory validation passed: {args.input}")
        print(f"Datasets: {len(inventory.datasets)}")
        print(f"Dashboards: {len(inventory.dashboards)}")
        lint_count = _print_lint_results(analysis)
        if args.print_summary:
            _print_summary(analysis)
        return 1 if lint_count else 0

    return 1


def _load_inventory(input_path: Path) -> Inventory | None:
    """Load an inventory and print friendly CLI errors for common failures."""

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


def _format_analysis(inventory: Inventory, analysis: AnalysisResult, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(
            {
                "platform": inventory.platform,
                "generated_at": inventory.generated_at.isoformat(),
                "dataset_count": len(inventory.datasets),
                "dashboard_count": len(inventory.dashboards),
                "analysis": asdict(analysis),
            },
            indent=2,
        )
    return generate_markdown_report(inventory, analysis)


def _print_summary(analysis: AnalysisResult) -> None:
    print("Health Scores:")
    for name, score in asdict(analysis.scores).items():
        print(f"- {name}: {score}/100")
    print("Top Risks:")
    for risk in analysis.top_risks or ["No top risks detected."]:
        print(f"- {risk}")


def _print_lint_results(analysis: AnalysisResult) -> int:
    findings = [
        *(f"Top risk: {risk}" for risk in analysis.top_risks),
        *(f"Risky dashboard: {dashboard}" for dashboard in analysis.risky_dashboards),
        *(f"Stale dataset: {dataset}" for dataset in analysis.stale_datasets),
        *(f"Duplicate metric candidate: {metric}" for metric in analysis.duplicate_metrics),
    ]
    if not findings:
        print("Lint results: no findings detected.")
        return 0

    print("Lint results:")
    for finding in findings:
        print(f"- {finding}")
    return len(findings)


def _print_lint_summary(findings):
    severities = ("critical", "high", "medium", "low")
    print("Metadata lint summary:")
    print(f"- Total findings: {len(findings)}")
    for severity in severities:
        print(f"- {severity.title()}: {sum(1 for finding in findings if finding.severity == severity)}")
    for finding in findings[:5]:
        print(f"- {finding.severity.upper()} {finding.rule_id}: {finding.title} ({finding.affected_object_type} {finding.affected_object_id})")


if __name__ == "__main__":
    raise SystemExit(main())
