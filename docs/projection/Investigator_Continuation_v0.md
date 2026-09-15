# Investigator Continuation v0

**Status:** PROJECTION  
**Scientific standing:** NONE  
**Architecture authority:** NONE  
**Implementation authority:** NONE

Repository evidence outranks this projection.

This note preserves a candidate continuation surface for replacing one bounded investigator episode with another without requiring full reconstruction of the project and without converting prior interpretation into current authority.

It is motivated by two concrete pressures already present in the Lab:

1. repeated frontier-model reconstruction cost before useful work can begin;
2. observed client interruption during a consequential model invocation, where execution crossed an external boundary even though the coordinating investigator did not retain a complete result.

This projection does **not** authorize a scheduler, daemon, autonomous research loop, persistent subjective agent, unrestricted retry system, self-selecting research program, or generalized worker router.

---

## 1. Core Question

Can a fresh investigator recover enough current footing to continue legitimate work without:

- replaying the full project history;
- silently inheriting stale assumptions;
- treating prior interpretation as current authority;
- duplicating a consequence that may already have occurred;
- losing explicit missingness or unresolved residue;
- silently expanding worker authority;
- or hiding reconstruction cost upstream in packet production?

The projected target is:

```text
investigator episode N
        ↓
retained continuation packet
        ↓
interruption / replacement
        ↓
packet integrity check
        ↓
current-basis admission
        ↓
selective reconstruction
        ↓
investigator episode N+1
```

The continuity belongs to retained consequence lineage, not to one uninterrupted model context.

---

## 2. Governing Rules

> **The continuation packet is a navigation projection over authoritative state, not a replacement authority for that state.**

```text
prior continuation claim
!=
current admissible state
```

> **Continuation preserves addressability to prior consequence; it does not convert prior interpretation into current authority.**

> **Replacement of the investigator must not imply replacement, repetition, or completion of the consequence.**

> **Observed attempt facts should survive replacement more strongly than the predecessor's interpretation of those facts.**

A fresh investigator must admit the packet against current repository and relevant runtime evidence before relying on it.

---

## 3. Three Continuation Surfaces

The first projection used a broad mechanical/semantic split. Pressure revealed that this was too coarse because exact references can be mechanical while the meaning attached to them remains prior interpretation.

The sharper candidate split is:

### 3.1 Mechanical basis

Exact reproducible coordinates already available to the apparatus.

Candidate examples:

```text
repository identity
basis commit
branch
packet identity
packet digest
source path + Git blob identity
attempt identifier
retained request / operation evidence references
```

These coordinates should not be probabilistically regenerated when they are already mechanically available.

### 3.2 Prior projected standing

What investigator N believed, concluded, or relied upon at packet generation time.

Candidate examples:

```text
prior objective projection
prior established conclusions
unresolved residue
prior pressure references
prior authority-source references
prior retry interpretation
coordinates believed to require revalidation
```

These are retained claims, not current authority.

### 3.3 Current admission

What investigator N+1 verifies now.

Candidate checks include:

```text
current HEAD / branch / worktree condition
cited source identity
whether prior authority still applies
whether a prior objective remains current
whether external or runtime coordinates changed
whether in-flight consequence needs reconciliation
```

Current admission is performed by the replacement investigator or deterministic apparatus. It is not inherited from packet prose.

---

## 4. Minimal v0 Continuation Surface

The first executable pressure should remain smaller than the original candidate schema.

### 4.1 Packet identity and integrity

The packet needs enough structure to distinguish a complete continuation artifact from an interrupted or stale write.

Candidate coordinates:

```text
schema/version
continuation_id
predecessor_id (optional)
packet_status = COMPLETE
packet_digest
generated_at (diagnostic only)
```

`generated_at` is provenance, not freshness.

A packet lacking valid finalization or integrity should not be admitted.

Where feasible, implementation should use atomic finalize/rename or an equivalent write boundary so partial generation does not masquerade as a complete packet.

### 4.2 Repository basis

For the first pressure, prefer a deliberately constrained basis:

```text
repository
basis_commit
branch
clean_worktree_required = true
```

A dirty worktree is not solved in v0. It should force packet rejection or explicit reconstruction.

This avoids prematurely designing a generalized worktree fingerprint.

### 4.3 Exact source identity

Continuation claims should point to exact committed source identities:

```text
source_id
path
git_blob
```

For v0, if a cited source is dirty, the packet should not pretend the committed blob identifies the observed bytes. The source must be treated as stale or outside the first pressure.

Descriptive source roles may be retained for presentation later, but they do not determine authority.

### 4.4 Prior projected standing

The packet may retain:

```text
prior_objective_projection
prior_established[]
unresolved[]
must_revalidate[]
```

Each consequential projected claim should retain evidence/source references.

Names should preserve prior ownership. Avoid field names such as `active_objective` or `ALREADY_WARRANTED` that can look like transferable current authority.

### 4.5 Optional in-flight attempt evidence

If the selected continuation specimen contains an interrupted or externally consequential action, the packet should retain observed attempt coordinates rather than one synthesized lifecycle enum.

Candidate minimal evidence surface:

```text
attempt_id
operation / contract reference
realization reference, when consequential
request retained? + evidence ref
client invocation observed? + evidence ref
provider acceptance/start observed? + evidence ref
provider completion/stop observed? + evidence ref
complete response retained? + evidence ref
external consequence observed? + evidence ref, when applicable
```

The important distinction remains:

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
!=
external consequence observed
```

`retry_admissibility` is derived standing. It should not substitute for the retained observations from which retry standing is reconstructed.

---

## 5. Candidate Schema

The following schema is a projection only and is intentionally narrow.

```json
{
  "schema": "investigator_continuation_v0",
  "continuation_id": "...",
  "predecessor_id": null,

  "integrity": {
    "packet_status": "COMPLETE",
    "packet_digest": "...",
    "generated_at": "..."
  },

  "mechanical_basis": {
    "repository": "ReedBarrus/DME_Lab",
    "basis_commit": "...",
    "branch": "main",
    "clean_worktree_required": true,

    "source_manifest": [
      {
        "source_id": "source-0001",
        "path": "...",
        "git_blob": "..."
      }
    ]
  },

  "prior_projected_standing": {
    "prior_objective_projection": {
      "statement": "...",
      "source_refs": []
    },

    "prior_established": [
      {
        "statement": "...",
        "standing_at_generation": "...",
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

    "must_revalidate": [
      {
        "coordinate": "...",
        "reason": "...",
        "evidence_refs": []
      }
    ],

    "inflight_attempts": []
  }
}
```

No field becomes current authority merely because it is present in the packet.

---

## 6. Admission and Missingness

A fresh investigator should not merely read the packet and trust it.

Candidate admission flow:

```text
load packet
        ↓
verify schema + finalization + digest
        ↓
resolve current repository state
        ↓
require / verify clean worktree for v0
        ↓
compare HEAD + branch
        ↓
resolve cited source blobs
        ↓
revalidate explicitly named coordinates
        ↓
reconcile in-flight attempts when present
        ↓
packet admissible for bounded use?
```

For checks that can change the next legitimate action, v0 should preserve more than Boolean success/failure.

Candidate observation outcomes:

```text
MATCH / OBSERVED
MISMATCH
CHECKED_ABSENT / OBSERVED_ABSENT
CHECK_FAILED / OBSERVATION_FAILED
NOT_CHECKED / NOT_OBSERVED
```

Exact naming is not yet authoritative. The required distinction is that absence, failed observation, and unobserved state do not collapse into one another.

If admissible:

```text
consume bounded prior projection
        ↓
inspect only consequential cited residue
        ↓
reach next legitimate action or abstention
```

If not admissible:

```text
identify changed / failed coordinates
        ↓
reconstruct only affected state where possible
        ↓
replace or amend continuation standing
```

A generalized dependency graph is not required for v0. A changed cited source may conservatively invalidate the dependent continuation claim for reinspection.

---

## 7. Continuation Lineage

`predecessor_id` identifies the packet directly consumed when generating a successor packet.

For v0:

```text
multiple packets may share one predecessor_id
newer packet != authoritative packet
latest timestamp != winner
```

No branch machinery is earned yet. A continuation packet must be explicitly selected and admitted; lineage alone does not select authority.

---

## 8. Deferred Capability Surface

The original projection included `worker_surface` in the first schema. Audit pressure showed that this risks conflating:

```text
worker exists
!=
worker addressable
!=
worker operational
!=
worker qualified
!=
worker authorized
!=
worker currently admissible
```

Therefore generalized worker/capability routing is **deferred from the first continuation pressure** unless the selected test task concretely requires it.

If later pressure requires retained worker references, the minimal candidate surface should preserve exact worker, contract, realization, qualification-evidence, authorization-evidence, and known-limit references without asserting current admissibility.

Worker routing should be earned by a later delegated-continuation pressure rather than smuggled into v0.

---

## 9. Deliberate Omissions

Investigator Continuation v0 should not attempt to preserve or solve:

- hidden chain of thought;
- model subjective state;
- complete conversation history;
- every repository fact;
- dirty-worktree continuation;
- a generalized dependency graph;
- autonomous objective selection;
- unrestricted retry state;
- generalized worker routing;
- implicit worker qualification;
- a universal scheduler;
- a persistent daemon;
- broad architectural summaries not needed for continuation.

The continuation surface should remain smaller than the authoritative state it points into.

---

## 10. First Executable Pressure — Clean Continuation Efficiency

The first implementation pressure should answer only:

> Can a finalized, basis-checked continuation packet reduce fresh-investigator reconstruction burden on one bounded task without degrading competent continuation?

Use one frozen predecessor episode and one real bounded next task.

Create two equivalent fresh-start conditions from the same repository basis.

### Condition A — ordinary reconstruction

A fresh investigator receives normal repository access and the normal startup protocol.

### Condition B — continuation-assisted reconstruction

A fresh investigator receives the same repository access and task instruction plus one finalized continuation packet.

Neither condition receives inherited chat context or extra human hints.

The packet must be the only intended informational intervention.

### Correctness gate before efficiency

Do not compare cost until both conditions are independently adjudicated against authoritative repository evidence.

At minimum, a competent continuation should preserve:

```text
current basis identified correctly
no stale authority silently inherited
no consequential unresolved residue silently dropped
no missingness collapsed into certainty
same legitimate next action / abstention reached,
or an independently acceptable bounded equivalent
```

A faster wrong continuation is failure, not efficiency.

### Cost accounting

Do not hide continuation work upstream.

For Condition A:

```text
C_A = ordinary fresh reconstruction cost
```

For Condition B:

```text
C_B =
packet-production overhead attributable to continuation
+ packet admission / revalidation
+ selective reconstruction
```

The predecessor episode's substantive research work is not charged to B merely because it happened earlier. Additional summarization, source inspection, serialization, or adjudication performed specifically to produce the packet is continuation cost and must not be treated as free.

Measure separately where observable:

```text
wall time
frontier token / attention burden
files / source bytes examined
Git operations
tool calls
tests rerun only for orientation
human clarification
duplicate work
stale assumptions
```

Do not collapse these into one scalar.

A first positive result would support only the narrow claim that continuation changed reconstruction burden without degrading correctness under one frozen specimen.

---

## 11. Second Executable Pressure — Interrupted Consequence Recovery

Interrupted-consequence recovery should remain a separate pressure so failure can be localized.

Use an already-earned Qwen-shaped specimen or an equivalent no-model fixture where authoritative evidence preserves:

```text
attempt occurred
!=
complete result retained
!=
retry authorized
```

Condition A reconstructs that standing through ordinary authoritative evidence.

Condition B admits a continuation packet carrying the observed attempt coordinates and selectively revalidates them.

The pressure should require both conditions to determine the legitimate next action **without issuing another consequential model call**.

Primary discriminator:

```text
does replacement preserve the consequence boundary
without false closure or automatic retry?
```

Efficiency is secondary to correct reconciliation.

---

## 12. Candidate Success Threshold

A boundedly useful v0 continuation mechanism would allow a fresh investigator to:

1. verify packet integrity;
2. verify the current repository basis under the declared v0 constraints;
3. recover prior objective, established standing, and unresolved residue as prior projections rather than current authority;
4. selectively revalidate consequential coordinates;
5. preserve observation failure and missingness distinctions;
6. reach the next legitimate action or abstention without independently reconstructing the full prior episode;
7. reduce at least one meaningful continuation burden after packet-production cost is included.

Interrupted-consequence recovery is a distinct later success condition unless the chosen first specimen naturally contains it.

---

## 13. Relationship to Persistent Research Autonomy

This projection remains a narrow candidate mechanism beneath `Persistent_Research_Autonomy.md`.

It does not establish persistent autonomy.

It pressures only whether replaceable investigator episodes can conserve enough basis, residue, and consequence state to continue bounded work correctly and cheaply.

Only after continuation itself pays rent should later pressure consider delegated worker resumption, scheduling, or repeated autonomous invocation.

Projected later shape remains merely prospective:

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

The persistent identity, if useful to describe at all, belongs to recoverable work lineage rather than one uninterrupted context window.

---

## 14. Reopening and Promotion Conditions

Do not promote this projection into generalized infrastructure because the schema looks plausible.

Implementation is warranted only to test whether it reduces the already-observed reconstruction burden while preserving current consequence boundaries.

Further persistence machinery should be earned only by recurrence, including pressure such as:

- repeated successful continuation across investigator replacement;
- repeated in-flight consequence reconciliation;
- measured reconstruction cost remaining consequential;
- repeated bounded worker allocation from recovered state;
- dirty-worktree continuation becoming necessary;
- scheduling becoming the dominant remaining manual operation.

Until then:

```text
preserve the continuation question
implement only the smallest pressureable surface
measure total continuation cost
promote nothing that has not paid rent
```
