"""Command line interface for the Enterprise Data Strategy Agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from enterprise_data_strategy_agent.analyzer import analyze_inventory
from enterprise_data_strategy_agent.connectors.domo_mock import DomoMockConnector
from enterprise_data_strategy_agent.report import generate_markdown_report


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Analyze enterprise analytics metadata and generate a strategy brief.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="Generate an enterprise data strategy brief")
    analyze.add_argument("--input", required=True, help="Path to synthetic inventory JSON")
    analyze.add_argument("--output", required=True, help="Path to write the markdown report")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""

    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        input_path = Path(args.input)
        output_path = Path(args.output)
        inventory = DomoMockConnector().load_inventory(input_path)
        analysis = analyze_inventory(inventory)
        report = generate_markdown_report(inventory, analysis)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Enterprise data strategy brief generated: {output_path}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
