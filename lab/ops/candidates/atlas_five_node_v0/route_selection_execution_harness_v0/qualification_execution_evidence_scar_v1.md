# ATLAS_ROUTE_SELECTION_EXECUTION_HARNESS_v0 — qualification execution-evidence scar

An earlier branch, `atlas-route-selection-execution-harness-v0`, contains:

- `qualification_output_v0.json`
- `qualification_receipt_v0.json`

Those artifacts were authored before an actual runtime execution of
`qualification.py` occurred in this administration.

Therefore they are retained only as non-promoting lineage.

```text
AUTHORED QUALIFICATION OUTPUT
!=
EXECUTED QUALIFICATION

QUALIFICATION RECEIPT
!=
QUALIFICATION EXECUTION EVIDENCE
WHEN IT CAN BE WRITTEN WITHOUT THE RUN
```

A fresh qualification run was then performed through GitHub Actions from the
implementation basis commit:

```text
9f43e02d2e4f01dceb227db34a8d5cb653e9f8fd
```

The workflow commit was:

```text
001ad4d86306564a3f4de4b46a12e3e8173862be
```

The hosted runner checked out that exact workflow commit, installed CPython
3.13.15, actually invoked:

```text
python -S lab/ops/candidates/atlas_five_node_v0/route_selection_execution_harness_v0/qualification.py
```

and the job completed successfully with all ten qualification cells reporting
PASS. The emitted qualification output SHA-256 was:

```text
1d0776d3cb49125d9c7642364119c37c7f44e5d4223ee3e3131759ce9575c25a
```

The scientific ATLAS_ROUTE_SELECTION_001 A/B cells were not invoked by this
qualification run.

This establishes only qualification execution evidence for the bounded harness.

```text
QUALIFIED HARNESS
!=
SCIENTIFIC REALIZATION

QUALIFIED HARNESS
!=
SCIENTIFIC PROMOTION
```
