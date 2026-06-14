# Architecture

## Data input layer
The starter project reads a local JSON inventory with synthetic Domo-style metadata. This keeps demos credential-free while preserving realistic enterprise metadata fields.

## Connector abstraction
`MetadataConnector` defines a read-only loading contract so future platforms can provide their own metadata inventories without changing the analyzer.

## Domo mock connector
`DomoMockConnector` loads and validates the sample inventory. It does not call Domo APIs and does not require credentials.

## Analysis engine
The analyzer reviews freshness, certification, ownership, sensitivity, stewardship, usage, criticality, dashboard dependencies, and duplicate metric candidates.

## Scoring engine
The scoring engine returns health scores from 0 to 100 for overall strategy health, governance, trust, freshness, ownership, and executive reporting risk.

## Report generator
The report generator produces a consultant-style markdown strategy brief for enterprise data managers.

## Future real Domo API connector
A future connector should use read-only credentials, least privilege scopes, explicit tenant configuration, rate-limit handling, and safe local export controls.

## Future UI layer
A lightweight Streamlit or web UI could let users upload inventory files, review findings interactively, and export briefs.

## Future AI assistant layer
An AI layer could help users ask natural-language questions about risks, definitions, and remediation plans while grounding answers in metadata findings.
