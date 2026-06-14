"""Optional Streamlit UI for uploading and analyzing inventory JSON."""

from __future__ import annotations

import json
from typing import Any

from enterprise_data_strategy_agent.analyzer import AnalysisResult, analyze_inventory
from enterprise_data_strategy_agent.models import Inventory, validate_inventory_payload
from enterprise_data_strategy_agent.report import generate_markdown_report

SCORE_LABELS = {
    "overall": "Overall",
    "governance": "Governance",
    "trust": "Trust",
    "freshness": "Freshness",
    "ownership": "Ownership",
    "executive_reporting_risk": "Executive reporting risk",
}


def parse_inventory_json(raw_json: str | bytes) -> Inventory:
    """Parse raw inventory JSON text and validate it into an Inventory."""

    if isinstance(raw_json, bytes):
        raw_json = raw_json.decode("utf-8")
    payload = json.loads(raw_json)
    if not isinstance(payload, dict):
        raise ValueError("Inventory JSON must be an object at the top level")
    return validate_inventory_payload(payload)


def build_report_bundle(inventory: Inventory) -> tuple[AnalysisResult, str]:
    """Run analysis and generate the markdown report for a validated inventory."""

    analysis = analyze_inventory(inventory)
    return analysis, generate_markdown_report(inventory, analysis)


def format_score_rows(analysis: AnalysisResult) -> list[dict[str, Any]]:
    """Return health scores in a table-friendly shape for UI rendering."""

    rows: list[dict[str, Any]] = []
    for key, label in SCORE_LABELS.items():
        explanation = analysis.score_explanations.get(key)
        rows.append(
            {
                "Score": label,
                "Value": getattr(analysis.scores, key),
                "Why": explanation.rationale if explanation else "No explanation available.",
            }
        )
    return rows


def summarize_inventory(inventory: Inventory) -> dict[str, Any]:
    """Return compact inventory metadata for display."""

    return {
        "Platform": inventory.platform,
        "Generated at": inventory.generated_at.isoformat(),
        "Datasets": len(inventory.datasets),
        "Dashboards/cards": len(inventory.dashboards),
    }


def _display_list(st: Any, title: str, items: list[str], empty_message: str) -> None:
    st.subheader(title)
    if items:
        for item in items:
            st.markdown(f"- {item}")
    else:
        st.caption(empty_message)


def run() -> None:
    """Launch the optional Streamlit app."""

    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover - exercised by Streamlit runtime expectations
        raise SystemExit("Streamlit is not installed. Install the UI extra with: pip install -e '.[ui]'") from exc

    st.set_page_config(page_title="Enterprise Data Strategy Agent", layout="wide")
    st.title("Enterprise Data Strategy Agent")
    st.caption("Upload inventory JSON, run the analyzer, and download a markdown strategy brief.")

    uploaded = st.file_uploader("Inventory JSON", type=["json"])
    if uploaded is None:
        st.info("Upload a JSON inventory file to begin. Try data/sample_domo_inventory.json from the repository.")
        return

    try:
        inventory = parse_inventory_json(uploaded.getvalue())
        analysis, markdown_report = build_report_bundle(inventory)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        st.error(f"Could not analyze inventory: {exc}")
        return

    st.success("Inventory validated and analyzed.")
    st.json(summarize_inventory(inventory), expanded=False)

    st.header("Health scores")
    cols = st.columns(len(SCORE_LABELS))
    for col, (key, label) in zip(cols, SCORE_LABELS.items(), strict=True):
        col.metric(label, f"{getattr(analysis.scores, key)}/100")
    st.dataframe(format_score_rows(analysis), hide_index=True, use_container_width=True)

    left, right = st.columns(2)
    with left:
        _display_list(st, "Top risks", analysis.top_risks, "No top risks detected.")
        _display_list(st, "Risky dashboards", analysis.risky_dashboards, "No risky critical dashboards detected.")
        _display_list(st, "Trusted data product opportunities", analysis.trusted_data_products, "No opportunities generated.")
    with right:
        _display_list(st, "Quick wins", analysis.quick_wins, "No quick wins generated.")
        _display_list(st, "Stale datasets", analysis.stale_datasets, "No stale datasets detected.")

    st.header("Markdown report")
    st.download_button(
        "Download markdown report",
        data=markdown_report,
        file_name="enterprise_data_strategy_brief.md",
        mime="text/markdown",
    )
    st.markdown(markdown_report)


def main() -> None:
    """Entry point for `streamlit run` or `python -m` execution."""

    run()


if __name__ == "__main__":
    main()
