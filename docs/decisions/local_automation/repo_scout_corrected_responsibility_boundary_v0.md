# Repo Scout Corrected Responsibility Boundary v0

**Status:** IMPLEMENTED BOUNDED APPARATUS CHANGE

**Starting apparatus basis:** `7dc0174c88fac0dd14dd032af538c7fd8ca84f5d`

**Repo Scout apparatus version:** `repo_scout_v0.1`

**Live model calls:** `0`

**Realization qualification or promotion:** `NONE`

**Scientific standing:** `NONE`

## Evidence boundary

Two retained live pressures exposed a contract-design wound:

- the first packet regenerated an unsupported execution basis even though the
  apparatus already held the exact basis mechanically;
- the single-source packet copied descriptive contract placeholders into result
  value positions and returned inconsistent escalation/terminal state.

The apparatus rejected both packets. Therefore:

```text
apparatus defect
!=
contract-design pressure
!=
realization failure
```

This change addresses only the demonstrated responsibility overlap. It does not
reinterpret either live result and does not establish Hermes capability or
incapability.

## Corrected ownership

The model proposal now contains exactly:

```text
evidence[].source_id
evidence[].location
evidence[].observation
bounded_interpretation
unresolved
escalation.required
escalation.reason
```

The apparatus attaches these already-known fields to the final retained result:

```text
task_id
execution_basis
scope_used
operations_used
```

It derives `terminal_action` from `escalation.required`. It issues deterministic
bounded source identities, requires evidence claims to select an issued identity,
and resolves that identity to final `evidence[].source_path` mechanically.

Thus:

```text
select provenance relation
!=
reconstruct provenance coordinate
```

The external `repo_scout_result` v0 shape remains unchanged. Descriptive
placeholder values are absent from the model proposal schema. `unresolved`
remains unchanged and intentionally undecomposed.

## Authority and rejection continuity

The caller still freezes the complete inspection plan, exact repository basis,
path/operation scope, realization basis, and budgets. The apparatus still permits
one injected model call, no retry, no model-directed tool planning, no repository
write surface, and no acceptance authority.

Malformed or extra model-owned fields, inconsistent escalation content, unknown
source identities, budget violations, out-of-scope operations, and repository
mutation remain mechanical failures.

## Retained A specimen

The A side of the forthcoming comparison remains immutable:

- retained result:
  [`repo_scout_single_source_coordinate_conservation_result_v0.md`](repo_scout_single_source_coordinate_conservation_result_v0.md)
- A execution basis: `5d08eee91add15ac9e7453226cf61b3a522c8707`
- source artifact:
  `docs/decisions/local_automation/turbo_t1_q1_completion_budget_pressure_result_v0.md`
- A result: mechanical `FAIL`; coordinate fidelity `FAIL`; requested coordinates
  recovered `0 / 6`

The exact source artifact remains content-equivalent at the corrected apparatus
basis:

| Coordinate | A basis | Corrected starting basis |
| --- | --- | --- |
| Commit | `5d08eee91add15ac9e7453226cf61b3a522c8707` | `7dc0174c88fac0dd14dd032af538c7fd8ca84f5d` |
| Git blob | `865b73e0c0703831132cccb8478bf76a68d8b004` | `865b73e0c0703831132cccb8478bf76a68d8b004` |
| Blob bytes | `3670` | `3670` |
| SHA-256 | `437df0d5fbc2435e1de3769193a6c338b6fa98b80da4292d30e825d811f9c621` | `437df0d5fbc2435e1de3769193a6c338b6fa98b80da4292d30e825d811f9c621` |

Equal Git object identity proves byte equality; the independent byte digest and
size make that equality explicit. No source-content drift confounds A/B.

## Smallest executable B pressure

After this apparatus change is committed, a separately authorized B pressure may
freeze its exact then-current commit and reuse:

```text
source: docs/decisions/local_automation/turbo_t1_q1_completion_budget_pressure_result_v0.md
inspection plan: one git_show, lines 1-94
question: the exact six-coordinate conservation question retained in A
realization/settings: the exact Hermes realization/settings retained in A
model calls: 1
automatic retries: 0
tools/write authority: none
```

The only intended intervention is the corrected model/runtime responsibility
boundary. The model returns only its proposal fields; the apparatus attaches the
authoritative envelope, resolves selected source IDs, and derives terminal action.

Evaluation remains separate for mechanical validity, coordinate fidelity,
missingness, unsupported additions/substitutions, source-location fidelity, and
utility relative to direct source inspection.

```text
B conserves the model-owned coordinates
→ bounded evidence that the old competing answer surface materially contributed

B still loses the model-owned coordinates
→ removing the contract ambiguity was insufficient under this realization/task
```

Neither branch grants general qualification.

STOP. B was not executed.
