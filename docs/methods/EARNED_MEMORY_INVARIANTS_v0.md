# Earned Memory Invariants v0

**Status:** OPERABLE_V0 — pressure-earned invariant ledger  
**Scope:** relations demonstrated as consequential by MM-001 / MM-002 / MM-003  
**Adjacent method:** `docs/methods/MEMORY_COMPILATION_METHOD_v0.md`

## Purpose

Retain only conservation relations that became load-bearing under an actual
memory pressure.

This file is **not**:

- a universal ontology;
- an exhaustive model of memory;
- a schema registry;
- a semantic-similarity metric;
- permission to infer untested invariants.

Promotion rule:

```text
candidate relation
→ pressure
→ consequential failure or repeated reconstruction requirement
→ bounded qualification
→ ledger entry
```

No relation enters this ledger merely because it sounds useful.

---

## EMI-001 — Logical artifact identity is not historical artifact identity

```text
artifact path / logical role
!=
artifact version / immutable historical basis
```

**Earned by:** MM-001 Round 1 failure.

**Witness:** the later imported
`DME_Operational_Constitution_Seed_v0.md` ended at Article XX while immutable
historical source versions retained Article XXI and, later, Article XXII.

**Consequence:** when a compiled claim depends on historical content, memory
must retain or route through the immutable source coordinate that actually
carried that content.

---

## EMI-002 — Decision topology is not source-identity topology

```text
what survived / fractured / remained unresolved
!=
which exact historical artifacts carried the deliberation
```

**Earned by:** MM-002 Round 1 failure.

**Witness:** the Council checkpoint preserved the decision outcome but named its
four round sources only by repository-relative paths.

**Consequence:** a decision checkpoint can be semantically useful while still
failing historical source closure. Exact source identity must be conserved
separately when reconstruction depends on it.

---

## EMI-003 — Decision topology is not causal deliberation topology

```text
pooled decision outcome
!=
who introduced / attacked / replaced / accepted what, and when
```

**Earned by:** MM-002 Round 2 failure.

**Witness:** checkpoint + immutable basis envelope recovered exact round sources
but still could not reconstruct per-actor/per-round proposal transitions without
reopening the raw rounds.

**Consequence:** causal provenance is a distinct conservation dimension when the
warrant for a decision depends on the transformation path, not only the final
outcome.

---

## EMI-004 — Supersession is not falsification

```text
proposal not selected / superseded
!=
proposal experimentally disproved
```

**Earned by:** MM-002 Round 3 reconstruction pressure.

**Witness:** Codex-1 preserved the inspect-envelope A/B comparison as a valid
candidate; later rounds selected a narrower startup-boundary pressure instead.
The inspect comparison was not experimentally falsified.

**Consequence:** memory must preserve the difference between a branch losing
priority and a branch losing evidential validity.

---

## EMI-005 — Omission is not necessarily semantic loss

```text
exact wording omitted
!=
consequential information lost
```

when:

```text
required relation survives
+
standing / unresolvedness survives
+
exact immutable route back to omitted source survives
```

**Earned by:** successful MM-001 and MM-002 round trips after minimal repair.

**Witness:** both qualified carriers omitted substantial raw prose while
independent observers could reconstruct the consequential relations and return
to exact pinned sources for omitted detail.

**Consequence:** hot memory may stay small. Raw representation need not remain
inline when consequential structure and exact recovery coordinates are
preserved.

---

## EMI-006 — Primary carrier source closure is not operational dependency closure

```text
exact identity of the primary carrier and its immediate source artifacts
!=
exact historical identity of every consequential dependency the carrier relies on
```

**Earned by:** MM-003 cold audit 001, targeted repair verification, and cold
audit 002.

**Witness:** the MM-002 carrier correctly pinned the checkpoint and four Council
round artifacts, yet the historical `AGENT_CONTEXT.md` governing the
continuity dependency belonged to the frozen pre-handoff basis at blob
`416b2aaa6469d4e201860836399b8989c95dcaff`. The later transplant commit
contained a different blob at the same path:
`5b1102a7b619985fbbcff7034acc92e2800bd71f`.

**Consequence:** provenance closure is instance- and dependency-relative.
Closing one sibling reference set does not license assuming that other
consequential references are closed. When a carrier's meaning or legitimate use
depends on another artifact, resolve that dependency against the basis that
actually governed it.

---

## EMI-007 — Horizon-scoped operative retention is not full inline retention

```text
load-bearing distinction required by one declared horizon
!=
full generating evidence required inline in hot memory
```

when:

```text
the operative relation reconstructs exactly
+
unresolved boundaries survive
+
exact immutable routes to richer evidence survive
+
cold retention remains undeleted
```

**Earned by:** G7 / `DISTINCTION_RETENTION_MODE_V0_PRESSURE_001`.

**Witness:** the exact
`COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0` outcomes for
`WORLD_CHANGE != METHOD_CHANGE` reconstructed from a minimal carrier containing
the distinction id, horizon id, method-axis applicability law, unresolved
boundaries, and exact source handles, while the richer G4/G5/G6 case and
pressure structures remained non-inline.

Frozen adjudication result:
`docs/campaigns/distinction_retention_mode_001/pressure_runs/DISTINCTION_RETENTION_MODE_V0_PRESSURE_RESULT_001.md`
(blob `7d037362dd0e438ae7c1fb2553d452a9ae2fd233`).

Runtime witness:
`distinction_retention_mode_v0_observation.json`
(blob `1ff52354096371710ccdcdd77dfb9a6b2c1ada3b`).

**Consequence:** hot memory may retain the smallest carrier required to preserve
an exact horizon-scoped operative relation while richer pressure evidence moves
out of line but remains exactly cold-routable. This does not authorize raw-source
deletion, establish a quantitative carrying-cost optimum, establish global
ecology retention, or imply method improvement, capitalization, planning
authority, execution authority, or scientific standing.

---

## EMI-008 — Horizon-scoped hot retention is currentness-conditioned

```text
retention required for one declared horizon
!=
retention required regardless of that horizon's currentness
```

For the exact tested horizon:

```text
CURRENT
→ hot requirement remains REQUIRED

NONCURRENT
→ hot requirement becomes NOT_REQUIRED_FOR_DECLARED_HORIZON

UNRESOLVED
→ hot requirement remains UNRESOLVED
```

while:

```text
GLOBAL_HOT_REQUIREMENT = UNRESOLVED
EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

**Earned by:** G8 / `DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_001`.

**Witness:** externally supplied currentness of
`COGNITIVE_METHOD_APPLICABILITY_HORIZON_V0` conditioned the G7
hot-retention requirement for `WORLD_CHANGE != METHOD_CHANGE` exactly as
declared, without executing a retention transition.

Frozen adjudication result:
`docs/campaigns/distinction_retention_currentness_001/pressure_runs/DISTINCTION_RETENTION_CURRENTNESS_V0_PRESSURE_RESULT_001.md`
(blob `e5f603fbea6ef05193f092245252cd26d6eae66a`).

Runtime witness:
`distinction_retention_currentness_v0_observation.json`
(blob `949ff2b9333146ca16e68981123f338f6e4dfd15`).

**Consequence:** horizon-scoped hot residency must not silently outlive the
currentness of the exact horizon that required it. NONCURRENT removes only that
horizon's hot requirement; it does not establish global irrelevance, global
cooling authority, deletion permission, depreciation, retirement, or a
quantitative carrying-cost optimum.

---

## EMI-009 — Declared-scope retention aggregation is not global ecology retention

```text
deterministic aggregation over one exact declared horizon set
!=
global ecology hot-requirement standing
```

For one exact supplied set of horizon-local retention postures:

```text
ANY REQUIRED
→ DECLARED_SCOPE_HOT_REQUIREMENT = REQUIRED

else ANY UNRESOLVED
→ DECLARED_SCOPE_HOT_REQUIREMENT = UNRESOLVED

else
→ DECLARED_SCOPE_HOT_REQUIREMENT = NOT_REQUIRED_FOR_DECLARED_SCOPE
```

while:

```text
DECLARED_SCOPE_COMPLETE_FOR_SUPPLIED_HORIZONS = YES
GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED
EXACT_COLD_SOURCE_RETENTION_REQUIRED = YES
```

**Earned by:** G9 / `RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_001`.

Frozen adjudication result:
`docs/campaigns/retention_scope_aggregation_001/pressure_runs/RETENTION_SCOPE_AGGREGATION_V0_PRESSURE_RESULT_001.md`
(blob `94152a26078c527cabfef7cd2cf1e7e3b4990df1`).

Runtime witness:
`retention_scope_aggregation_v0_observation.json`
(blob `212d7a9d4fb7bc982cb83b418ee6d5982008c574`).

**Consequence:** a bounded declared scope can be aggregated without pretending
that the scope exhausts the ecology. Scope-local closure is therefore usable
while the exterior remains explicitly unresolved. This does not establish global
cooling, retention-transition authority, deletion permission, depreciation,
retirement, quantitative carrying-cost optimization, method capitalization,
autonomous planning, authority, execution, or scientific standing.

---

## EMI-010 — Partial-basis extension is not prior-coordinate invalidation

```text
extend one exact declared basis
!=
mutate unchanged prior local coordinates
```

For the exact G10 specimen:

```text
B0:
H_A = REQUIRED
H_B = NOT_REQUIRED_FOR_DECLARED_HORIZON

B1 = B0 + H_C
H_C = UNRESOLVED

PRIOR_LOCAL_COORDINATES_PRESERVED = YES
```

while:

```text
EXTERIOR_POSTURE = UNRESOLVED
GLOBAL_ECOLOGY_HOT_REQUIREMENT = UNRESOLVED
SCALAR_HOTNESS = NOT_ESTABLISHED
```

**Earned by:** G10 / `PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_001`.

Frozen adjudication result:
`docs/campaigns/partial_basis_retention_profile_001/pressure_runs/PARTIAL_BASIS_RETENTION_PROFILE_V0_PRESSURE_RESULT_001.md`
(blob `e0c27dd06b68ac7e3dc08d20093e60eee35509eb`).

Runtime witness:
`partial_basis_retention_profile_v0_observation.json`
(blob `4f4c7efef184c1f60ab362420d7ef09a1c43dab1`).

**Consequence:** a partial declared relational basis may grow by adding a new
coordinate without silently rewriting unchanged prior local coordinates.
Unresolved interior and exterior residue remain explicit. This does not
establish global coverage, load weighting, scalar hotness, global invariance,
economic optimality, cooling authority, retention transition, planning
authority, execution authority, or scientific standing.

---

## EMI-011 — Unresolved membership is not conserved residual posture

```text
interior unresolved membership + unresolved exterior posture
!=
exact conserved residual classification / non-promotion posture
```

for the tested hot-memory reconstruction class.

For the exact G11/G12 specimen:

```text
INTERIOR_UNRESOLVED_MEMBERS = {H_C}
EXTERIOR_POSTURE = UNRESOLVED
```

alone did not reconstruct:

```text
NONRESIDUAL_MEMBERS = {H_A, H_B}
RESIDUAL_CONSERVED = YES
RESIDUAL_GAP_STATUS = NOT_ESTABLISHED
RESIDUAL_WORK_ELIGIBILITY = NOT_ESTABLISHED
ARCHITECTURE_REQUIREMENT = NOT_ESTABLISHED
```

when the G11 residual-conservation relation was ablated from the bounded hot
carrier and cold sources remained routable but unread.

**Earned by:** G11 /
`PARTIAL_BASIS_RESIDUAL_CONSERVATION_V0_PRESSURE_001`
and G12 /
`RESIDUAL_CONSERVATION_RECONSTRUCTION_LOAD_V0_PRESSURE_001`.

**Witness:** G11 established the exact typed residual posture without promoting
the residual into a gap, work eligibility, or architecture requirement. G12 then
ablated that relation while preserving the same G10 membership/exterior basis
and exact cold-source handles. The control reconstructed all seven requested
G11 coordinates; the ablation left five coordinates unresolved.

Frozen G11 adjudication result:
`docs/campaigns/partial_basis_residual_conservation_001/pressure_runs/PARTIAL_BASIS_RESIDUAL_CONSERVATION_V0_PRESSURE_RESULT_001.md`
(blob `c31eefa748213c70a39713e2137343638ee4fb15`).

Runtime G11 witness:
`partial_basis_residual_conservation_v0_observation.json`
(blob `1736d63c13c27d37641f3a6f78825c9288428a50`).

Frozen G12 adjudication result:
`docs/campaigns/residual_conservation_reconstruction_load_001/pressure_runs/RESIDUAL_CONSERVATION_RECONSTRUCTION_LOAD_V0_PRESSURE_RESULT_001.md`
(blob `298e0449faee65c7c1ae615ea00363d0e0e52675`).

Runtime G12 witness:
`docs/campaigns/residual_conservation_reconstruction_load_001/pressure_runs/RESIDUAL_CONSERVATION_RECONSTRUCTION_LOAD_V0_PRESSURE_OBSERVATION_002.json`
(blob `c49f9dbc70be84fd61a02bf63dd7cba03c415e4d`).

**Consequence:** when a bounded hot-memory handoff must reconstruct this class of
residual posture without reopening cold evidence, unresolved membership and
exterior posture alone are insufficient. The carrier must preserve enough
qualified residual relation to recover explicit residual classification and
non-promotion standing. This does not require all richer source evidence inline
when exact cold routes remain available.

This entry does not establish that a conserved residual is a declared gap,
work-eligible, actionable, architecturally mandatory, globally invariant,
globally complete, economically weighted, or authorized for planning,
execution, or scientific promotion.

---

## EMI-012 — Descriptive content is not explicit declaration standing

```text
descriptive / repair coordinates
!=
explicit declaration standing
```

for the tested externally supplied declaration-reconstruction class.

For the exact G13 specimen, both carriers preserved:

```text
HORIZON_ID = H1_POST_CONSEQUENCE_PHASE_HANDOFF
ITEM_ID = G1_STALE_SUCCESSOR_3_HANDOFF
RELATION_TARGETS = {
  CONTROL_KERNEL_ACTIVATION,
  CAMPAIGN_HANDOFF,
  RECONSTRUCTION
}
POST_REPAIR_HORIZON_POSTURE = HORIZON_SATISFIED
```

while only the control preserved:

```text
DECLARATION_STANDING = EXTERNALLY_SUPPLIED_LIVE_GAP
```

When that standing coordinate was ablated, an independent reconstructor returned:

```text
DECLARATION_STANDING = UNRESOLVED_FROM_CARRIER
```

despite retaining the same descriptive and repair coordinates.

**Earned by:** G13 /
`DECLARATION_STANDING_RECONSTRUCTION_V0_PRESSURE_001`.

Frozen G13 result:
`docs/campaigns/declaration_standing_reconstruction_001/pressure_runs/DECLARATION_STANDING_RECONSTRUCTION_V0_PRESSURE_RESULT_001.md`
(blob `396604a594370b9d991fa30e18ec44c27a96c76e`).

Runtime G13 witness:
`docs/campaigns/declaration_standing_reconstruction_001/pressure_runs/DECLARATION_STANDING_RECONSTRUCTION_V0_PRESSURE_OBSERVATION_001.json`
(blob `14e915cbc351447688ba8d22362496be35977893`).

**Consequence:** when this class of bounded carrier must reconstruct exact
externally supplied declaration standing without reopening cold evidence,
descriptive content and matched repair correspondence alone are insufficient.
Enough explicit declaration standing must be preserved to recover that coordinate.

This does not establish a general definition of gap, automatic gap discovery,
residual-to-gap transition law, downstream work eligibility, architecture
requirement, global invariance, global ecology coverage, economic weighting,
planning, authority, execution, or scientific standing.

---

## EMI-013 — Declaration standing is not work eligibility

```text
declared gap presence
!=
work eligibility
```

for the tested relational-horizon selector class.

For the exact G14 specimen, both control and intervention preserve:

```text
HORIZON_ID = H1_POST_CONSEQUENCE_PHASE_HANDOFF
GAP_ID = G1_STALE_SUCCESSOR_3_HANDOFF
STATEMENT = declared eligible gap
BLOCKS = {CONTROL_KERNEL_ACTIVATION}
DECLARED_GAP_PRESENT = YES
```

while changing only:

```text
WORK_ELIGIBLE = true
```

to:

```text
WORK_ELIGIBLE = false
```

changes selector posture from:

```text
EXACT_ELIGIBLE_GAP
```

to:

```text
NO_JUSTIFIED_WORK
```

with the declared gap still represented.

**Earned by:** G14 /
`DECLARATION_WORK_ELIGIBILITY_SELECTION_LOAD_V0_PRESSURE_001`.

Frozen G14 result:
`docs/campaigns/declaration_work_eligibility_selection_load_001/pressure_runs/DECLARATION_WORK_ELIGIBILITY_SELECTION_LOAD_V0_PRESSURE_RESULT_001.md`
(blob `329124a845fe1e935cd17bb87919ccb340199fe0`).

Runtime G14 witness:
`declaration_work_eligibility_selection_load_v0_observation.json`
(blob `54ab5157ec936474c6189f2d956127fc5cb1e0c0`).

**Consequence:** in this tested selector class, declared-gap presence alone is
insufficient for selection. The separate work-eligibility coordinate carries
bounded selection load.

This does not establish criteria for granting eligibility, gap discovery,
residual-to-gap transition, work admission, planning, authority, execution,
global invariance, global ecology coverage, economic weighting, or scientific standing.

---

## EMI-014 — Non-authoritative planning/task artifacts are not operative currentness

```text
non-authoritative planning / task artifacts
!=
operative current state
```

for the tested WORKCYCLE_STABILIZATION_001 currentness-reconstruction class.

For the exact G15 specimen, the control carrier explicitly preserved:

```text
CAMPAIGN_POSTURE = CLOSED
CURRENT_HORIZON_POSTURE = CLOSED
NEXT_PRESSURE = null
SUCCESSOR_POSTURE = NO_SUCCESSOR
NEXT_PRESSURE_ALLOWED = false
```

while both control and ablation preserved the same non-authoritative planning/task
surfaces, including an ACTIVE_CANDIDATE_SEQUENCE planning seed and a
READY_TO_SEND_WORK_PACKET.

When the authoritative current-state coordinate was ablated, an independent
reconstructor returned:

```text
CAMPAIGN_POSTURE = UNRESOLVED_FROM_CARRIER
CURRENT_HORIZON_POSTURE = UNRESOLVED_FROM_CARRIER
NEXT_PRESSURE = UNRESOLVED_FROM_CARRIER
SUCCESSOR_POSTURE = UNRESOLVED_FROM_CARRIER
NEXT_PRESSURE_ALLOWED = UNRESOLVED_FROM_CARRIER
```

rather than inferring operative standing from those planning/task artifacts.

**Earned by:** G15 /
`OPERATIVE_CURRENTNESS_RECONSTRUCTION_V0_PRESSURE_001`.

Frozen G15 result:
`docs/campaigns/operative_currentness_reconstruction_001/pressure_runs/OPERATIVE_CURRENTNESS_RECONSTRUCTION_V0_PRESSURE_RESULT_001.md`
(blob `dc39156956cd08df6fef7970fcd88d69dbb6b378`).

Runtime G15 witness:
`docs/campaigns/operative_currentness_reconstruction_001/pressure_runs/OPERATIVE_CURRENTNESS_RECONSTRUCTION_V0_PRESSURE_OBSERVATION_001.json`
(blob `f0f4136772c0440491e6a87631b6301cc67bef94`).

**Consequence:** for this bounded reconstruction class, visible planning/task
artifacts are insufficient to recover exact operative campaign currentness when
the authoritative current-state coordinate is absent. A currentness-bearing
coordinate must remain explicitly recoverable rather than being inferred from
artifact labels, readiness, or existence.

This does not establish a generic currentness resolver, cross-campaign precedence,
task ranking, planning activation, work selection, authority, execution, global
invariance, global ecology coverage, economic weighting, scientific standing,
or path-relocation semantics.

---

## Current nonclaim

These fourteen entries are the current bounded invariant bank.

```text
fourteen earned invariants
!=
complete coordinate system of semantic memory
```

Future specimens may:

- add a new invariant;
- narrow an existing invariant;
- show two entries are factorable;
- expose a false distinction;
- reveal a licensed transition that changes what must be conserved.

Amend this ledger only through retained pressure evidence.
