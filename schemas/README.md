# Schemas

This directory is reserved for schemas once runtime pressure requires them.

Schema files should remain provisional until checked against real observations, ingest envelopes, ledger entries, and replay behavior.

Current rule: schema != reality.

## Current Schema Hypotheses

- `ledger_record_v0.schema.json`: descriptive, shadow-only JSON Schema for the tested v0 ledger record boundary.
- `investigator_continuation_v0.schema.json`: implementation schema for the
  bounded clean-basis continuation packet. It structures mechanical basis and
  caller-supplied prior projected standing; it does not confer current authority.

This schema is a comparison surface. It does not regulate ledger append or establish truth, semantic meaning, or ledger-wide invariants.
