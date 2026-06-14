"""Streamlit application for the Enterprise Data Strategy Agent."""

from __future__ import annotations

import json
from typing import Any

from enterprise_data_strategy_agent.policy import DEFAULT_POLICY
from enterprise_data_strategy_agent.ui import (
    backlog_summary,
    count_by_severity,
    finding_rows,
    generate_report_artifacts,
    load_bundled_sample_inventory,
    load_bundled_sample_policy,
    parse_inventory_json,
    parse_policy_yaml,
    remediation_rows,
    summarize_inventory,
    summarize_policy,
)


def run() -> None:
    """Render the Streamlit UI."""

    try:
        import streamlit as st
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Streamlit is not installed. Install dependencies with: pip install -r requirements.txt") from exc

    st.set_page_config(page_title="Enterprise Data Strategy Agent", layout="wide")
    st.title("Enterprise Data Strategy Agent")
    st.caption("Open-source strategy assistant for metadata governance, reporting trust, and enterprise data remediation planning.")
    st.info("Domo-style metadata is the first reference implementation. No real Domo credentials are required, and this app does not modify any source platform.")

    inventory = _inventory_selector(st)
    policy = _policy_selector(st)
    artifacts = None
    if inventory is not None and policy is not None:
        try:
            artifacts = generate_report_artifacts(inventory, policy)
        except Exception as exc:  # pragma: no cover - UI guardrail
            st.error(f"Could not generate reports: {exc}")

    tabs = st.tabs(["Overview", "Metadata Input", "Strategy Policy", "Lint Results", "Strategy Brief", "Remediation Plan", "Downloads", "About / Disclaimer"])
    with tabs[0]:
        _overview(st)
    with tabs[1]:
        st.subheader("Loaded metadata summary")
        if inventory:
            st.json(summarize_inventory(inventory), expanded=False)
        else:
            st.warning("Load bundled sample metadata or upload a valid inventory JSON file from the sidebar.")
    with tabs[2]:
        st.subheader("Strategy policy context")
        if policy:
            st.json(summarize_policy(policy), expanded=False)
        st.markdown("Policy context tunes severity, freshness, scoring, stakeholder, and ownership assumptions so recommendations match the organization rather than a generic checklist.")
    with tabs[3]:
        _lint_tab(st, artifacts)
    with tabs[4]:
        _brief_tab(st, artifacts)
    with tabs[5]:
        _plan_tab(st, artifacts)
    with tabs[6]:
        _downloads_tab(st, artifacts)
    with tabs[7]:
        _about(st)


def _inventory_selector(st: Any):
    st.sidebar.header("Metadata input")
    mode = st.sidebar.radio("Inventory source", ["Bundled sample inventory", "Upload custom JSON inventory"], index=0)
    try:
        if mode == "Bundled sample inventory":
            return load_bundled_sample_inventory()
        uploaded = st.sidebar.file_uploader("Custom inventory JSON", type=["json"])
        if uploaded is None:
            return None
        return parse_inventory_json(uploaded.getvalue())
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        st.sidebar.error(f"Could not load inventory: {exc}")
        return None


def _policy_selector(st: Any):
    st.sidebar.header("Strategy policy")
    mode = st.sidebar.radio("Policy source", ["Default policy", "Bundled sample policy", "Upload custom YAML policy"], index=0)
    try:
        if mode == "Default policy":
            return DEFAULT_POLICY
        if mode == "Bundled sample policy":
            return load_bundled_sample_policy()
        uploaded = st.sidebar.file_uploader("Custom policy YAML", type=["yml", "yaml"])
        if uploaded is None:
            return DEFAULT_POLICY
        return parse_policy_yaml(uploaded.getvalue(), uploaded.name)
    except (OSError, TypeError, ValueError) as exc:
        st.sidebar.error(f"Could not load policy: {exc}")
        return DEFAULT_POLICY


def _overview(st: Any) -> None:
    st.markdown("""
### What this tool does
- Profiles Domo-style enterprise metadata for governance, freshness, ownership, reporting trust, and remediation opportunities.
- Helps enterprise data managers, analytics leaders, Domo admins, and non-technical stakeholders discuss priorities from a shared evidence base.
- Uses Domo-style metadata first because it is a familiar BI reference pattern for datasets, cards, dashboards, owners, certification, and freshness.
- Runs lint checks, then analysis/scoring, then planning so raw metadata findings become an executive strategy brief and actionable backlog.
- Provides advisory outputs only; it does not call Domo APIs, require credentials, or modify Domo or any other platform.
""")


def _lint_tab(st: Any, artifacts: Any) -> None:
    if artifacts is None:
        st.warning("Load valid metadata to run lint results.")
        return
    st.subheader("Findings by severity")
    counts = count_by_severity(artifacts.lint_findings)
    cols = st.columns(4)
    for col, severity in zip(cols, counts, strict=True):
        col.metric(severity.title(), counts[severity])
    selected = st.multiselect("Filter by severity", list(counts), default=list(counts))
    rows = [row for row in finding_rows(artifacts.lint_findings) if row["severity"] in selected]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.subheader("Markdown lint report preview")
    st.markdown(artifacts.lint_report_markdown)


def _brief_tab(st: Any, artifacts: Any) -> None:
    if artifacts is None:
        st.warning("Load valid metadata to generate a strategy brief.")
        return
    scores = artifacts.analysis.scores
    cols = st.columns(6)
    metrics = [("Overall", scores.overall), ("Governance", scores.governance), ("Trust", scores.trust), ("Freshness", scores.freshness), ("Ownership", scores.ownership), ("Executive risk", scores.executive_reporting_risk)]
    for col, (label, value) in zip(cols, metrics, strict=True):
        col.metric(label, f"{value}/100")
    st.subheader("Top findings")
    for finding in artifacts.analysis.top_risks[:8] or ["No top risks detected."]:
        st.markdown(f"- {finding}")
    st.subheader("Markdown strategy brief preview")
    st.markdown(artifacts.strategy_brief_markdown)


def _plan_tab(st: Any, artifacts: Any) -> None:
    if artifacts is None:
        st.warning("Load valid metadata to generate a remediation plan.")
        return
    summary = backlog_summary(artifacts.remediation_items)
    for label in ("by_priority", "by_severity", "by_effort", "by_time_horizon"):
        st.subheader(label.replace("_", " ").title())
        st.json(summary[label], expanded=False)
    st.dataframe(remediation_rows(artifacts.remediation_items), hide_index=True, use_container_width=True)
    st.subheader("Markdown remediation plan preview")
    st.markdown(artifacts.remediation_plan_markdown)


def _downloads_tab(st: Any, artifacts: Any) -> None:
    if artifacts is None:
        st.warning("Load valid metadata to enable downloads.")
        return
    st.download_button("Enterprise Data Strategy Brief markdown", artifacts.strategy_brief_markdown, "enterprise_data_strategy_brief.md", "text/markdown")
    st.download_button("Metadata Lint Report markdown", artifacts.lint_report_markdown, "metadata_lint_report.md", "text/markdown")
    st.download_button("Remediation Plan markdown", artifacts.remediation_plan_markdown, "remediation_plan.md", "text/markdown")
    st.download_button("Remediation Backlog JSON", artifacts.remediation_backlog_json, "remediation_backlog.json", "application/json")


def _about(st: Any) -> None:
    st.markdown("""
- This project is independent and unofficial.
- Domo-style metadata is the first reference implementation.
- No real Domo API calls are made in this version.
- No source platform is modified.
- Sample data is synthetic.
- The project is MIT licensed.
- Future connectors may support Domo, Snowflake, Power BI, Tableau, Looker, dbt, Collibra, Alation, Atlan, or other platforms.
""")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
