# Cockpit Projection v1 Bounded Views v0

## Scope and authority

This Projection v1 P2 implementation extends the committed P1 standing
projection into discrete, read-only bounded views. After `git fetch origin
main`, local `HEAD` and `origin/main` were identical at:

```text
2207431b6ae6730327dbd8d9656f0360057921ca
```

That committed tree is the authority. The working tree was clean at entry.
This pass changes no Projection Adapter behavior, projection contract,
Pressure / Resolution Map scientific content, constraint record, evidence,
trace, standing, Controller document, or external state.

## Normalized data boundary

The browser still loads one serialized Projection Adapter result. P2 consumes:

| View or shell | Normalized surfaces |
| --- | --- |
| Persistent shell | `repository_state`, `projection_diagnostics` |
| MAP | `pressure_nodes`, `pressure_relations`, `evidence_refs` |
| CONSTRAINTS | `constraints`, `evidence_refs` |
| LINEAGE | selected `pressure_nodes` occurrence, its `resolution_history` and `evidence_ref_ids`, plus explicit `pressure_relations` |
| HORIZON | `projection_documents` |
| SOURCE | `evidence_refs` |

The frontend does not fetch or parse `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, constraint JSONL, decisions, projection document
bodies, traces, or Git history to construct these views. Opening a normalized
source link is human navigation and does not feed source content back into the
model.

No adapter widening was required. Every P2 view could legally render its
already-contracted normalized surface. Missing arrays render as unavailable;
the frontend does not repair them.

## View vocabulary and shell

The persistent shell now offers exactly:

```text
MAP | CONSTRAINTS | LINEAGE | HORIZON | SOURCE
```

The repository/projection header, current navigation, freshness, diagnostic
summary, current-lens selection, transition description, and global diagnostic
panel persist across lenses. These are discrete projection modes, not spatial
regions of a compositional atlas. Switching lenses establishes no relation
between objects displayed in different views.

SYSTEM remains unavailable because no earned-system structure is normalized.
No DISTINCTIONS, Distinction Atlas, observational surface, boss view, or
continuous atlas navigation was introduced.

## MAP preservation

MAP remains the default orientation surface and retains P1 behavior:

- exact standing topology and compressed nodes;
- explicit `blocked_by` / `unlocks` geometry only;
- occurrence-aware pressure selection;
- current standing separate from resolution history;
- missing discriminator separate from residue;
- explicit activity only;
- evidence navigation without proof semantics;
- basis limitation `basis not explicitly projected`;
- typed projection diagnostics distinct from scientific standing.

The pressure inspector now provides a discrete transition to that exact
occurrence's LINEAGE lens. Relation following is validated against one uniquely
drawable normalized relation before changing pressure foreground.

## CONSTRAINTS

Every normalized constraint record receives an occurrence key based on its
array position and retained identity. No records are merged. Cards keep
`left`, `relation`, and `right` visually distinct, with `scope`, `basis`, and
`standing` explicit. The inspector exposes optional note, record provenance,
adapter provenance, diagnostics, and only the evidence IDs emitted by that
constraint.

Read-only filtering searches the exact emitted ID, left, relation, right,
scope, basis, standing, and note strings. Filtering changes displayed
foreground only.

The view states its boundary:

```text
constraint != local distinction event
```

Constraint presence does not establish pressure relevance, causal direction,
research priority, confidence, universal truth, or activation. No normalized
pressure/constraint relation exists, so P2 implements no pressure-to-constraint
or constraint-to-pressure transition.

## LINEAGE

LINEAGE is selected-pressure-local. It contains only:

- the selected pressure occurrence and exact current standing;
- `resolution_history` in normalized array order;
- explicit incoming and outgoing `pressure_relations`;
- the pressure's emitted evidence IDs and normalized references;
- provenance and associated diagnostics.

The view explicitly states:

> Declared history order is shown. Visual continuity does not establish causal
> lineage.

No causal edges connect history entries. No global chronology or Git history
is reconstructed. No pressure-to-pressure edge exists unless supplied by
`pressure_relations`. PR-017's declared history does not imply prospective
prediction success, and current standing never collapses into history.

## HORIZON

HORIZON is populated only from `projection_documents`. It renders an explicit
earned/observed-territory versus projected-territory boundary, then shows each
document's emitted title, source path, source commit, classification, exact
standing, explicit non-authority declaration, provenance, and associated
diagnostics where available.

Projection document bodies are neither present in nor recovered by the view.
The normalized committed source path may be opened for human inspection, but
opening it does not change the model.

Controller remains exactly `PARKED` when emitted and visibly
`NON-AUTHORITATIVE`. P2 supplies no Controller action, capability, readiness,
availability, implementation, authorization, or invocation surface.

## SOURCE

Every normalized evidence reference receives an independent occurrence key.
The browser exposes exact ID, origin identity, original target, target kind,
resolution status, committed path checked, provenance, and associated
diagnostics where available. Read-only filtering covers those exact emitted
fields.

`resolved`, `broken`, `external_unchecked`, `unsupported`, unknown, and future
exact status text remain visible without nearest-status coercion. In
particular:

```text
resolved = target resolvable under the adapter's bounded rule
resolved != proved / verified / true / causal
```

Normalized safe source links remain directly navigable. Their contents are not
fetched into the projection.

## Typed projection transitions

P2 records three local transition classes:

| Type | Coordinates | Meaning |
| --- | --- | --- |
| `view_transition` | `projection_lens` | Change among MAP, CONSTRAINTS, LINEAGE, HORIZON, and SOURCE; asserts no object relation. |
| `object_selection` | pressure occurrence, constraint occurrence, evidence reference, or projection document occurrence | Change the inspected normalized occurrence inside its legal view. |
| `object_traversal` | `pressure_occurrence_to_declared_lineage`, `explicit_pressure_relation`, or `explicit_evidence_ref_id` | Follow a coordinate already present in normalized data. |

The implemented semantic traversal vocabulary is:

- pressure occurrence to its inspector;
- pressure occurrence to its declared LINEAGE;
- pressure occurrence across one explicit uniquely resolved pressure relation;
- pressure or constraint occurrence to an evidence reference named in its own
  `evidence_ref_ids`;
- evidence reference to normalized source navigation;
- projection document to its normalized committed source path.

An evidence traversal is rejected when the requested evidence ID is absent
from the owning pressure or constraint. Ambiguous pressure relations are not
followable to an invented occurrence. No evidence-to-pressure, document-to-
pressure, pressure-to-constraint, constraint-to-pressure, or causal-successor
traversal is synthesized.

Every transition changes only local foreground or browser navigation. It does
not mutate normalized input, activity, standing, repository state, or external
systems; authorize pressure; start experiments; invoke Controller; or write
through an API.

## Selected-object continuity

Selection is view-specific and occurrence-aware:

- MAP and LINEAGE share the exact selected pressure occurrence key, including
  array position and provenance-bearing occurrence identity;
- CONSTRAINTS, HORIZON, and SOURCE each retain their own selected normalized
  occurrence while the user switches away;
- switching to a view that cannot represent the previous object's type shows
  that view's own selection rather than manufacturing an equivalent object;
- an evidence traversal selects one exact evidence-reference occurrence in
  SOURCE;
- no selection is reduced to pressure ID alone, so duplicate pressure
  occurrences remain distinct through MAP / LINEAGE transitions.

The shell labels selection as `SELECTED IN THIS LENS` and labels transition
state as local foreground that asserts no new relation.

## Diagnostic behavior

The global diagnostic count and dedicated diagnostic panel remain mounted
outside the active view and therefore survive every lens change. Missing
diagnostic arrays remain unavailable rather than zero. Where a diagnostic has
an exact supported association to a displayed normalized occurrence, the
local inspector also exposes it; otherwise the diagnostic remains globally
visible.

Valid neighboring constraints, references, pressures, and projection
documents continue to render when another source structure is malformed.
Scientific standing remains separate from adapter-operational diagnostics.

## Test evidence

Focused observer tests protect:

- the exact five-view vocabulary and MAP default;
- independently addressable constraint and evidence occurrences;
- distinct constraint left / relation / right plus explicit scope and basis;
- the constraint/local-distinction boundary;
- evidence traversal gated by owner `evidence_ref_ids`;
- normalized history order and current/history separation;
- explicit pressure-relation traversal only;
- duplicate pressure occurrence continuity into LINEAGE;
- projection-document-only HORIZON population and body non-parsing;
- Controller `PARKED` and explicit non-authority;
- exact SOURCE status and origin identity;
- view switching without model, activity, or relation mutation;
- rejection of pressure-to-constraint synthesis;
- diagnostic persistence in all five lenses;
- preservation of every P1 standing and read-only invariant.

Validation passed with 34/34 focused observer tests, 32/32 Cockpit
adapter/generator pressure tests, and 549/549 repository tests. JavaScript
syntax checks and `git diff --check` also passed.

## Real-repository smoke boundary

The exact-current adapter specimen at
`2207431b6ae6730327dbd8d9656f0360057921ca` exercised all five rendered views
and representative transitions:

- MAP PR-019 to LINEAGE PR-019;
- MAP pressure to its emitted evidence and SOURCE;
- CONSTRAINT to its emitted evidence and SOURCE;
- HORIZON Controller to normalized source inspection.

The specimen contained 19 pressure occurrences, 24 explicit pressure
relations, 46 constraint occurrences, 214 evidence-reference occurrences,
three projection documents, and zero projection diagnostics. All 214 emitted
evidence references had the exact current status `resolved`; that status was
not promoted to proof. Controller rendered exactly `PARKED` and explicitly
non-authoritative. A headless Chrome load confirmed the exact commit, all five
persistent view controls, MAP default, current projection state, and visible
zero-diagnostic surface. Counts remain facts about that one source commit, not
UI constants. Browser load and transition smoke do not establish human
navigation success or general comprehension.

## Known limitations and remaining P3 pressure

- Pressure current-standing basis/scope remains unprojected and is not repaired
  in P2.
- LINEAGE is pressure-local and cannot establish a global causal account.
- SOURCE resolution status cannot adjudicate evidence sufficiency.
- Constraint filtering is literal substring filtering, not a query or
  inference engine.
- View-local selection history is not a repository history or semantic graph.
- The bounded geometry has not established general accessibility, usability,
  or unsupported-inference safety.
- No continuous atlas, observational geometry, event topology, agency model,
  Controller, earned SYSTEM view, or production deployment exists.

Projection v1 remains in progress. The next step is P3 adversarial human,
navigation, and unsupported-inference pressure over these bounded views and
typed transitions. P3 is not begun here.

## Bounded adjudication

The strongest permitted claim is:

> Projection v1 now exposes the currently normalized MAP, CONSTRAINTS,
> LINEAGE, HORIZON, and SOURCE structures as bounded read-only views connected
> by projection-only transitions without introducing new scientific relations.

This does not establish human navigation success, general comprehension,
visual semantic safety, continuous atlas navigation, observational geometry,
event topology, agency or decision geometry, Controller integration, or
production readiness.
