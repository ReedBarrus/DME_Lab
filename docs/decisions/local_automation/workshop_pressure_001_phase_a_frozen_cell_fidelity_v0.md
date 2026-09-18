# Workshop Pressure 001 — Phase A Frozen Cell Fidelity Evidence Return

**Status:** PHASE A ADVERSARIAL MATRIX PASSED IN TESTED MOCK SCOPE  
**Pressure:** Workshop Pressure 001 — Frozen Cell Fidelity  
**Execution basis:** `f4d40cda4b7f9d9658b59ea0bd444bd7f6809997`  
**Live provider:** NOT USED  
**LP-001 cell executed:** NO  
**Standing change authorized by this record:** NO

## Question

Can one frozen authorized cell either execute exactly once as declared or halt
legibly before crossing the violated boundary, using only a deterministic mock
invocation surface?

The bounded target is:

```text
one authorized cell
→ exact execution
OR
→ legible halt
```

This pass pressures only the Phase A bench implementation. It does not qualify a
real provider boundary, multi-cell orchestration, scoring, or LP-001 execution.

## Exact implementation basis

Committed implementation:

`src/runtime/workshop_frozen_cell.py`

Git blob:

`746ed0f087a9614b4b76387e2a2dd37b3bb90d7c`

Committed adversarial tests:

`tests/runtime/test_workshop_frozen_cell.py`

Git blob:

`d484600d9a2fefb842d27e8b853b7bd6e8764d39`

Supporting schemas:

- `schemas/workshop_frozen_cell_manifest_v0.schema.json`
  → blob `079db925f1b83d11a6b682b938e4db420a6b7a88`
- `schemas/workshop_fault_v0.schema.json`
  → blob `d19fae60e51590332bea40a89fec7df0bffa8d24`
- `schemas/workshop_cell_receipt_v0.schema.json`
  → blob `ed5c9193166bd4b852d21b2afbe4a703b6b2b79b`

Phase A contract:

`docs/methods/local_automation/Workshop_Frozen_Cell_Fidelity_v0.md`

→ blob `1ea379653a6a53c0cbb0fef36c8598cc8d81325f`

Before execution, the locally materialized source and test files were checked
using the Git blob identity rule:

```text
sha1("blob " + byte_length + NUL + bytes)
```

and matched the committed source/test blobs exactly.

## Execution

Command:

```text
python -m unittest tests.runtime.test_workshop_frozen_cell -v
```

Observed result:

```text
Ran 7 tests
OK
```

All seven predeclared Phase A cases passed.

## Matrix result

| Case | Injected condition | Expected boundary | Observed result |
| --- | --- | --- | --- |
| T00 | clean control | one invocation + success receipt | PASS — exactly one invocation; terminal state `RECEIPT_COMMITTED` |
| T01 | corrupted condition packet | halt before invocation | PASS — `E003_CONDITION_PACKET_MISMATCH`; invocation count 0 |
| T02 | corrupted specimen | halt before invocation | PASS — `E004_SPECIMEN_MISMATCH`; invocation count 0 |
| T03 | expected payload hash drift | halt before invocation | PASS — `E005_PAYLOAD_ASSEMBLY_MISMATCH`; invocation count 0 |
| T04 | required observable invocation-surface drift | halt before invocation | PASS — `E006_INVOCATION_SURFACE_MISMATCH`; invocation count 0 |
| T05 | output sink fails after invocation | retain execution fact; no success receipt | PASS — `E011_OUTPUT_CAPTURE_FAILURE`; invocation count 1; `INVOKED` and `OUTPUT_CAPTURED` retained; `RECEIPT_COMMITTED` absent |
| T06 | unclassified surface-observation exception | `E017`; halt; no improvisation | PASS — `E017_UNSPECIFIED_DEVIATION`; invocation count 0 |

## Invocation-observability result

T00 also preserved the declared invocation epistemic classes:

```text
model_label
→ VERIFIABLE_REQUIRED
→ independently observed and matched

tools_allowed
→ VERIFIABLE_REQUIRED
→ independently observed and matched

reasoning_mode
→ DECLARED_ONLY
→ retained under unverified

provider_backend_revision
→ UNOBSERVABLE
→ retained under unobservable
```

Therefore this pass does not promote requested/configured values into observed
facts merely because they were declared.

## Fault atomicity evidence

The tested pre-invocation failures all ended in `HALTED` with invocation count
zero.

The tested post-invocation failure T05 retained that invocation had occurred
while refusing to represent the cell as successfully completed.

Within this matrix:

```text
failure detected
!=
failure contained
```

was pressured by requiring the blocked downstream transition to remain
unexecuted, not merely by requiring an error message.

T05 additionally supports the bounded operational distinction:

```text
execution occurred
!=
successful cell completion
```

because the invocation happened exactly once while no successful completion
receipt was emitted.

T06 supports:

```text
unclassified deviation
!=
permission to improvise
```

within the tested mock surface.

## What this pass does not establish

This evidence does not establish:

- that every defined E001–E017 path is correct;
- a qualified real-provider invocation adapter;
- provider model identity or hidden provider-state observability;
- account-memory or conversation-inheritance isolation;
- anonymization behavior;
- persistent on-disk receipt/fault atomicity;
- multi-cell sequencing;
- blind scorer handoff;
- reveal/reducer correctness;
- LP-001 execution readiness;
- autonomous experimentation;
- generalized Workshop architecture;
- project scientific standing.

The implementation currently defines more fault codes than the T00–T06 matrix
pressures. Untested codes remain unqualified.

## Bounded result

The exact committed Phase A implementation and exact committed T00–T06 test
surface produced seven passing adversarial cases under deterministic local mock
execution.

The strongest warranted result is:

> Within the tested Phase A mock scope, the frozen-cell primitive executed the
> clean cell exactly once, halted before invocation for the declared
> pre-invocation mismatches, preserved execution occurrence without successful
> completion for the tested post-invocation retention failure, and defaulted an
> unclassified pre-invocation deviation to terminal E017 rather than
> improvisation.

This is evidence for the first bolt only.

## Next pressure

Do not connect LP-001 yet.

The next candidate pressure is Phase B:

```text
real invocation boundary
→ declared / observed / unverified / unobservable coordinates
→ same one-cell authority membrane
```

Phase B requires a separately selected and authorized provider adapter. This
record does not authorize it.
