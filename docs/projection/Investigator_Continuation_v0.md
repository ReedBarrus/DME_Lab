# Investigator Continuation v0

**Status:** PROJECTION
**Scientific standing:** NONE
**Architecture authority:** NONE
**Implementation authority:** NONE

Repository evidence outranks this projection.

This note preserves a candidate continuation surface for replacing one bounded investigator episode with another without requiring full reconstruction of the project and without converting prior interpretation into current authority.

It is motivated by two concrete pressures already present in the Lab:

1. repeated frontier-model reconstruction cost before useful work can begin;
2. observed client interruption during a consequential model invocation, where an authorized attempt may have occurred even though the coordinating investigator did not retain a complete result.

This projection does **not** authorize a scheduler, daemon, autonomous research loop, persistent subjective agent, unrestricted retry system, or self-selecting research program.

---

## 1. Core Question

Can a fresh investigator recover enough current footing to continue legitimate work without:

- replaying the full project history;
- silently inheriting stale assumptions;
- treating a prior interpretation as current authority;
- duplicating a consequence that may already have occurred;
- losing explicit missingness or unresolved residue;
- silently expanding worker authority;
- or reconstructing all available evidence when only a bounded subset changed?

The projected target is:

```text
investigator episode N
        ↓
retained continuation surface
        ↓
interruption / replacement
        ↓
current-basis verification
        ↓
selective reconstruction
        ↓
investigator episode N+1
```

The continuity belongs to the retained consequence lineage, not to one uninterrupted model context.

---

## 2. Governing Rule

> **The continuation packet is a navigation projection over authoritative state, not a replacement authority for that state.**

A continuation claim is therefore not accepted merely because the previous investigator emitted it.

```text
prior continuation claim
!=
current admissible state
```

A fresh investigator must compare the packet against current repository and runtime evidence before relying on it.

Two additional candidate invariants are load-bearing:

> **Continuation preserves addressability to prior consequence; it does not convert prior interpretation into current authority.**

> **Replacement of the investigator must not imply replacement, repetition, or completion of the consequence.**

---

## 3. Mechanical and Semantic Continuity

The current Repo Scout pressure suggests a useful separation.

### Mechanical continuity

Exact coordinates already available deterministically should remain mechanically owned.

Candidate examples:

```text
repository identity
basis commit
branch
worktree fingerprint
source paths / blobs
attempt identities
operation records
worker contract references
```

These coordinates should not be probabilistically regenerated when the runtime already knows them exactly.

### Semantic continuity

The previous investigator may project bounded semantic state over the mechanical basis.

Candidate examples:

```text
active objective
established bounded conclusions
unresolved residue
missing basis
currently warranted next pressure
coordinates requiring revalidation
```

These remain claims linked to evidence, not mechanically authoritative facts.

The fresh investigator verifies the mechanical basis first, then consumes only the semantic projection that remains admissible under the current state.

---

## 4. Candidate Continuation Surfaces

A minimal continuation packet should preserve five surfaces.

### 4.1 BASIS

Where exactly did the previous episode stop?

Candidate coordinates:

- repository;
- branch;
- basis commit;
- worktree fingerprint;
- generation time;
- source manifest;
- authority references;
- active pressure references.

### 4.2 STANDING

What has actually been established or completed?

Each retained statement should remain linked to authoritative repository evidence and preserve its standing.

### 4.3 RESIDUE

What remains unresolved, missing, stale, unacknowledged, or blocked?

Residue should not be converted into closure for convenience.

### 4.4 REACHABILITY

What is the next currently warranted pressure, if any?

A candidate next pressure does not become active merely because it is recorded.

```text
reachable pressure
!=
selected pressure
!=
authorized pressure
```

### 4.5 CAPABILITY SURFACE

What bounded workers or realized tools are currently addressable, and under what existing contracts?

The packet may reference worker capability and known task-family evidence, but it must not mint new authority or qualification.

```text
worker exists
!=
worker qualified
!=
worker authorized
```

---

## 5. In-Flight Consequence

The observed Qwen comparison interruption makes in-flight consequence a first-class continuation pressure.

A continuation mechanism that preserves only a "next task" but loses whether an external attempt already crossed its action boundary can create duplicate consequence.

Candidate attempt states include:

```text
NOT_INVOKED
INVOKED_UNACKNOWLEDGED
INVOKED_STILL_RUNNING
INVOKED_COMPLETED_RESPONSE_RECOVERABLE
INVOKED_COMPLETED_RESPONSE_LOST
INVOCATION_STATE_UNKNOWN
```

These names are provisional and do not establish a runtime taxonomy.

The important distinction is:

```text
attempt authorized
!=
attempt invoked
!=
provider accepted
!=
execution completed
!=
response acknowledged
!=
result retained
```

A replacement investigator must reconcile the strongest available attempt evidence before retry becomes admissible.

---

## 6. Candidate Schema

The following schema is a projection only. It is intentionally small enough to pressure directly before generalized persistence machinery is introduced.

```json
{
  "schema": "investigator_continuation_v0",
  "continuation_id": "...",
  "predecessor_id": null,

  "mechanical_envelope": {
    "repository": "ReedBarrus/DME_Lab",
    "basis_commit": "...",
    "branch": "main",
    "worktree_fingerprint": "...",
    "generated_at": "...",

    "authority_refs": [],
    "active_pressure_refs": [],

    "source_manifest": [
      {
        "source_id": "source-0001",
        "path": "...",
        "blob": "...",
        "role": "decision|method|projection|trace|contract"
      }
    ],

    "inflight_attempts": [
      {
        "attempt_id": "...",
        "operation": "...",
        "standing": "INVOKED_UNACKNOWLEDGED",
        "evidence_refs": [],
        "retry_admissibility": "RECONCILIATION_REQUIRED"
      }
    ],

    "worker_surface": [
      {
        "worker_id": "repo_scout_v0",
        "contract_ref": "...",
        "authority": "READ_ONLY",
        "task_family": "...",
        "standing": "...",
        "known_limits_refs": []
      }
    ]
  },

  "continuation_projection": {
    "active_objective": {
      "statement": "...",
      "source_refs": []
    },

    "established": [
      {
        "statement": "...",
        "standing": "...",
        "source_refs": []
      }
    ],

    "unresolved": [
      {
        "statement": "...",
        "source_refs": [],
        "missing_basis": [],
        "next_discriminator": "..."
      }
    ],

    "candidate_next_pressure": {
      "statement": "...",
      "basis_refs": [],
      "authorization": "REQUIRES_SELECTION|ALREADY_WARRANTED"
    },

    "must_revalidate": [
      {
        "coordinate": "...",
        "reason": "...",
        "evidence_refs": []
      }
    ],

    "known_omissions": []
  }
}
```

No field above is yet authoritative merely because it appears in this projection.

---

## 7. Admission of a Continuation Packet

A fresh investigator should not merely read the packet and trust it.

Candidate admission flow:

```text
load continuation packet
        ↓
resolve current repository state
        ↓
compare HEAD / branch / worktree
        ↓
resolve cited sources
        ↓
reconcile in-flight attempts
        ↓
check must-revalidate coordinates
        ↓
continuation admissible?
```

If admissible:

```text
consume bounded continuation projection
        ↓
inspect only consequential cited residue
        ↓
perform next legitimate work
```

If not admissible:

```text
identify changed coordinates
        ↓
reconstruct affected state
        ↓
replace or amend continuation projection
```

The intended optimization is selective reconstruction, not blind trust and not automatic full-project replay.

A generalized dependency graph is not required for v0. If one cited source changes, v0 may conservatively mark the dependent continuation claim for reinspection.

---

## 8. Worker Surface and Realization References

The continuation packet may make bounded capabilities addressable without granting them new power.

For example, it may retain that:

```text
Repo Scout v0
→ contract reference
→ READ_ONLY authority
→ retained failure / utility evidence
```

or that a realized local model has retained evidence under one transformation regime.

The packet must not infer:

```text
available worker
→ qualified worker

known realization
→ generally suitable realization

prior authorization
→ current authorization
```

Any worker invocation remains governed by its own current contract, authority boundary, and realized basis.

---

## 9. Deliberate Omissions

Investigator Continuation v0 should not attempt to preserve:

- hidden chain of thought;
- model weights or subjective state;
- complete conversation history;
- every repository fact;
- a generalized dependency graph;
- autonomous objective selection;
- unrestricted retry state;
- implicit worker qualification;
- a universal scheduler;
- a persistent daemon;
- broad architectural summaries not needed for continuation.

The continuation surface should remain smaller than the authoritative state it points into.

---

## 10. First Executable Pressure

The first legitimate implementation pressure should compare a normal fresh-start investigator against a continuation-assisted fresh investigator on the same bounded next task.

### Condition A — ordinary reconstruction

A fresh investigator receives normal repository access and must orient using the current startup protocol.

### Condition B — continuation-assisted reconstruction

A fresh investigator receives normal repository access plus one committed `investigator_continuation_v0` packet and is instructed to verify and use it rather than independently reconstruct the entire project unless packet admission fails.

The task should be real, bounded, and already reachable from current repository standing.

Measure where observable:

```text
wall time before first legitimate action
files opened
Git operations
tests rerun only for orientation
human clarification required
duplicate work
stale assumptions reused
unreconciled prior attempts
frontier token / attention burden
```

Do not collapse these into a scalar score.

---

## 11. Required Failure Pressures

A continuation apparatus should eventually survive at least the following bounded cases:

```text
HEAD unchanged
→ cheap successful continuation

HEAD changed after packet
→ stale basis detected

one cited source changed
→ affected projection not silently reused

prior action unacknowledged
→ retry not automatically admitted

worker contract changed
→ old authority not inherited

missing interval
→ missingness retained explicitly
```

These are candidate pressures, not a mandate to implement all cases in one pass.

---

## 12. Candidate Success Threshold

A boundedly useful continuation mechanism would allow a fresh investigator to:

1. verify the current basis;
2. recover the active objective;
3. recover established standing and unresolved residue;
4. detect or reconcile any in-flight consequence relevant to retry;
5. discover currently addressable bounded workers without expanding their authority;
6. reach the next legitimate action without independently reconstructing the full prior episode.

The mechanism should also measurably reduce at least one meaningful reconstruction burden without increasing stale-state or duplicate-action risk.

---

## 13. Relationship to Persistent Research Autonomy

This projection is a narrower candidate mechanism beneath `Persistent_Research_Autonomy.md`.

It does not establish persistent autonomy.

It pressures only whether replaceable investigator episodes can conserve enough basis, residue, and consequence state to continue bounded work correctly and cheaply.

If successful, later scheduling could invoke fresh episodes over retained continuation state.

That later possibility does not authorize a scheduler now.

Projected later shape:

```text
tick / meaningful state change
        ↓
is admissible unresolved work present?
        ↓
NO → STOP
YES → instantiate bounded investigator
        ↓
admit continuation state
        ↓
changed-world check
        ↓
bounded work
        ↓
retain consequence + new continuation
        ↓
episode ends
```

The persistent identity, if useful to describe at all, belongs to the recoverable work lineage rather than one uninterrupted context window.

---

## 14. Reopening and Promotion Conditions

Do not promote this projection into generalized infrastructure because the schema looks plausible.

Implementation is warranted only to test whether it reduces the already-observed reconstruction burden while preserving current consequence boundaries.

Further persistence machinery should be earned only by recurrence, including pressure such as:

- repeated continuation across investigator replacement;
- repeated in-flight consequence reconciliation;
- measured reconstruction cost remaining consequential;
- repeated bounded worker allocation from recovered state;
- scheduling becoming the dominant remaining manual operation.

Until then:

```text
preserve the continuation question
implement only the smallest pressureable surface
measure whether it pays rent
```
