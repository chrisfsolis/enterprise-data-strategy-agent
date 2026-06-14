from dataclasses import replace

from enterprise_data_strategy_agent.models import Dashboard, Dataset, validate_inventory_payload
from enterprise_data_strategy_agent.sample_loader import load_sample_inventory
from enterprise_data_strategy_agent.validation import lint_inventory


def _valid_inventory_payload(certified_dataset=True, certified_dashboard=False):
    return {
        "platform": "test",
        "generated_at": "2026-06-14",
        "datasets": [
            {
                "id": "ds_bool",
                "name": "Boolean Dataset",
                "business_domain": "Finance",
                "owner": "Owner",
                "department": "Finance",
                "refresh_cadence": "daily",
                "last_refreshed": "2026-06-14",
                "certified": certified_dataset,
                "row_count": 10,
                "sensitivity_level": "internal",
                "usage_level": "low",
                "business_criticality": "medium",
            }
        ],
        "dashboards": [
            {
                "id": "dash_bool",
                "title": "Boolean Dashboard",
                "type": "dashboard",
                "business_domain": "Finance",
                "owner": "Owner",
                "department": "Finance",
                "certified": certified_dashboard,
                "usage_level": "low",
                "business_criticality": "medium",
                "dataset_ids": ["ds_bool"],
                "audience": "Finance",
            }
        ],
    }


def test_lint_inventory_reports_metadata_quality_findings():
    inventory = load_sample_inventory("data/sample_domo_inventory.json")
    generated = inventory.generated_at
    broken_dataset = Dataset(
        id="ds_fin_rev",
        name="Broken Duplicate Finance",
        business_domain="Finance",
        owner="Analyst",
        department="Finance",
        refresh_cadence="sometimes",
        last_refreshed=generated.replace(year=generated.year + 1),
        certified=False,
        row_count=-5,
        sensitivity_level="secret",
        usage_level="popular",
        business_criticality="urgent",
    )
    orphan_dataset = Dataset(
        id="ds_orphan",
        name="Orphan Dataset",
        business_domain="Operations",
        owner="Analyst",
        department="Operations",
        refresh_cadence="daily",
        last_refreshed=generated,
        certified=True,
        row_count=None,
        sensitivity_level="restricted",
        usage_level="low",
        business_criticality="medium",
    )
    empty_dashboard = Dashboard(
        id="dash_fin_close",
        title="Duplicate Empty Dashboard",
        type="workbook",
        business_domain="Finance",
        owner="Analyst",
        department="Finance",
        certified=True,
        usage_level="viral",
        business_criticality="urgent",
        dataset_ids=[],
        audience="Finance",
    )
    certified_on_uncertified = Dashboard(
        id="dash_certified_bad_upstream",
        title="Certified Bad Upstream",
        type="dashboard",
        business_domain="Finance",
        owner="Analyst",
        department="Finance",
        certified=True,
        usage_level="high",
        business_criticality="critical",
        dataset_ids=["ds_sales_bookings"],
        audience="Finance",
    )
    linted = replace(
        inventory,
        datasets=[*inventory.datasets, broken_dataset, orphan_dataset],
        dashboards=[*inventory.dashboards, empty_dashboard, certified_on_uncertified],
    )

    findings = lint_inventory(linted)
    messages = [finding.message for finding in findings]

    assert any("Dataset ID appears" in message for message in messages)
    assert any("Dashboard ID appears" in message for message in messages)
    assert any("Invalid sensitivity" in message for message in messages)
    assert any("Invalid usage" in message for message in messages)
    assert any("Invalid criticality" in message for message in messages)
    assert any("Invalid refresh cadence" in message for message in messages)
    assert any("Invalid dashboard type" in message for message in messages)
    assert any("row count is negative" in message for message in messages)
    assert any("row count is missing" in message for message in messages)
    assert any("no downstream dashboards" in message for message in messages)
    assert any("no dataset_ids" in message for message in messages)
    assert any("last_refreshed is after" in message for message in messages)
    assert any("no named steward" in message for message in messages)
    assert any("backed by uncertified datasets" in message for message in messages)
    assert all(finding.recommended_action for finding in findings)


def test_structural_parser_allows_missing_row_count_for_linting():
    payload = {
        "platform": "test",
        "generated_at": "2026-06-14",
        "datasets": [
            {
                "id": "ds_missing_rows",
                "name": "Missing Rows",
                "business_domain": "Finance",
                "owner": "Owner",
                "department": "Finance",
                "refresh_cadence": "daily",
                "last_refreshed": "2026-06-14",
                "certified": True,
                "sensitivity_level": "internal",
                "usage_level": "low",
                "business_criticality": "medium",
            }
        ],
        "dashboards": [],
    }

    inventory = validate_inventory_payload(payload)

    assert inventory.datasets[0].row_count is None
    assert any("row count is missing" in finding.message for finding in lint_inventory(inventory))


def test_validate_inventory_payload_accepts_json_boolean_certified_values():
    inventory = validate_inventory_payload(_valid_inventory_payload(True, False))

    assert inventory.datasets[0].certified is True
    assert inventory.dashboards[0].certified is False

    inventory = validate_inventory_payload(_valid_inventory_payload(False, True))

    assert inventory.datasets[0].certified is False
    assert inventory.dashboards[0].certified is True


def test_validate_inventory_payload_rejects_non_boolean_dataset_certified_values():
    for certified in ("false", "true", 0, 1):
        payload = _valid_inventory_payload(certified_dataset=certified)

        try:
            validate_inventory_payload(payload)
        except ValueError as exc:
            assert "Dataset ds_bool certified must be a boolean" in str(exc)
        else:
            raise AssertionError(f"Expected ValueError for dataset certified={certified!r}")


def test_validate_inventory_payload_rejects_non_boolean_dashboard_certified_values():
    for certified in ("false", "true", 0, 1):
        payload = _valid_inventory_payload(certified_dashboard=certified)

        try:
            validate_inventory_payload(payload)
        except ValueError as exc:
            assert "Dashboard dash_bool certified must be a boolean" in str(exc)
        else:
            raise AssertionError(f"Expected ValueError for dashboard certified={certified!r}")
