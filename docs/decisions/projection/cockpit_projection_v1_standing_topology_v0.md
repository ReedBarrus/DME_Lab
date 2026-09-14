# Cockpit Projection v1 Standing Topology v0

## Scope and authority

This first Projection v1 human-use refinement changes only the read-only
Cockpit projection. After `git fetch origin main`, local `HEAD` and
`origin/main` were identical at:

```text
add0f280b77193a43bf7639e8b28478925eac0f8
```

That committed tree was the authority. This pass did not change the Projection
Adapter, projection contract, Pressure / Resolution Map scientific content,
constraints, evidence, Controller, or repository state through the UI.

## Human-use observations

The first observer session established bounded use evidence, not general
comprehension:

- the map exposed PR-006 and PR-018 as `OPEN` / reachable while the navigation
  strip retained explicit no-active-pressure state;
- normalized evidence references provided useful direct navigation to
  committed source evidence;
- PR-001 prompted a candidate missing-coordinate idea, but that idea is not
  repository evidence and caused no scientific or adapter change;
- the generic `wound` presentation conflated PR-009 scientific basis
  insufficiency with Cockpit malfunction;
- PR-017's `CANDIDATE_SURVIVED` token was vulnerable to an unsupported schema
  validation interpretation when separated from its pressure, missing
  discriminator, resolution, and residue.

These findings warrant projection refinement only.

## Generic biological-language adjudication

Generic `wound` / `wounded` language was removed from the current observer.
The projection now retains typed conditions from normalized fields and
diagnostics: missing discriminator, projection diagnostic kind, duplicate
identity, unknown standing, freshness state, projection status, broken
evidence status, and explicit field missingness. Shared alert styling does not
replace their visible text.

`BASIS_INSUFFICIENT` is rendered as a scientific standing with an interrupted
standing boundary. It does not acquire the projection-diagnostic corner mark,
diagnostic badge, or diagnostic-panel state unless a normalized diagnostic is
also associated with that occurrence.

No new universal condition taxonomy was created.

## Map compression

Each map occurrence remains limited to its normalized pressure ID, short
title, exact current standing, occurrence index, and compact indicators for
history, duplicate identity, projection diagnostics, unknown standing,
missing-discriminator presence or absence, residue presence, and explicit
activity. Longer pressure, discriminator, resolution, residue, relation,
history, evidence, provenance, and diagnostic material remains recoverable in
the inspector.

No node receives size, prominence, standing, or activity from relation degree.
Activity still requires an explicit normalized active-pressure value.

## Standing visual grammar

The smallest implemented form mapping is:

| Exact normalized standing | Projection form |
| --- | --- |
| `OPEN` | open dashed boundary |
| `PARTIAL_RESOLUTION` | stable boundary with an incomplete right edge |
| `BOUNDED_RESOLUTION` | solid stable boundary |
| `BASIS_INSUFFICIENT` | interrupted right boundary in the non-diagnostic standing color |
| `BLOCKER_REMOVED` | solid boundary with a heavier base |
| `CANDIDATE_SURVIVED` | double boundary |
| `EQUIVALENT_UNDER_CURRENT_PRESSURE` | inset paired boundary |
| `SHELVED` | reduced-prominence dotted boundary |

Unknown standing retains its exact normalized text and receives an explicit
unknown-standing presentation. `ACTIVE` is a separate overlay emitted only
for explicit normalized activity. None of these forms ranks another, and no
`fully resolved` category exists.

History count, missing-discriminator presence, residue presence, duplicate
identity, and projection-diagnostic presence remain separate typed indicators;
they do not rewrite current standing.

## Basis / scope audit

Audit result: **C. INSUFFICIENT**.

Current normalized pressure nodes expose `pressure`, `standing`,
`missing_discriminator`, `resolution_so_far`, `residue`, `blocked_by`,
`unlocks`, `resolution_history`, evidence references, and provenance. They do
not expose a structured basis or scope coordinate for the current standing.

The observer therefore displays the neutral limitation `basis not explicitly
projected` in the CURRENT inspector region. It does not parse decision prose,
Pressure / Resolution Map Markdown, evidence, or Git history to manufacture a
basis. Whether the contract and adapter should later project a bounded
basis/scope structure remains residue for a separate adapter-pressure pass;
this pass does not widen the adapter.

## PR-009 and PR-017 recovery boundary

For PR-009, the exact `BASIS_INSUFFICIENT` standing remains visible on the map.
Its normalized missing discriminator, resolution so far, residue, evidence,
history, provenance, and diagnostics are separated in the inspector. This
allows recovery of the public-association gap and recoverable-evidence residue
already present in normalized data without presenting insufficient basis as
false evidence or projection failure.

For PR-017, the exact `CANDIDATE_SURVIVED` standing remains adjacent to its
normalized pressure context only through selection and inspection. Missing
discriminator, resolution so far, residue, relations, and history are separate
regions. The UI does not add `schema valid`, `verified`, `proved`, `resolved`,
or `prediction succeeded` status.

## Relation geometry

Every semantic edge still originates in exactly one normalized
`pressure_relations` object. Uniquely resolved pressure-to-pressure relations
use orthogonal paths for legibility. `unlocks` is solid and `blocked_by` is
dashed, with both forms named in the legend. Selecting a pressure foregrounds
only its incident explicit relations.

Ambiguous or non-pressure endpoints remain listed as unresolved relation
residue and are not assigned invented graph endpoints. Node proximity, grid
position, edge count, or selected foreground do not establish relation,
importance, truth, confidence, priority, or causal centrality.

## Inspector and transitions

The inspector now separates these regions:

1. CURRENT;
2. CONTEXT / MISSING DISCRIMINATOR;
3. RESOLUTION SO FAR;
4. RESIDUE;
5. RELATIONS;
6. RESOLUTION HISTORY;
7. EVIDENCE;
8. PROVENANCE;
9. DIAGNOSTICS.

Current and historical standings remain separate. Missing discriminator and
residue remain separate. Evidence links remain navigation rather than proof
badges. Unique explicit pressure relations can be followed to another local
inspector selection.

The projection-only transition invariant is:

> A typed Cockpit transition changes only the foreground projection or lens.

Pressure-to-inspector, pressure-to-history, pressure-to-evidence, relation
follow, and evidence-to-source/provenance transitions may change what is
foregrounded or open a normalized reference. They must not invoke Controller,
change repository state, authorize pressure, start an experiment, modify
standing, or cause a repository or other external write.

## Test evidence

Focused observer tests passed 22/22. They cover exact standing forms, activity
separation, current/history separation, discriminator/residue separation,
typed projection diagnostics, relation-only edges, relation-degree invariance,
read-only evidence navigation, and absence of Controller/write actions.
Existing synthetic partial, failed, stale, conflict, duplicate,
broken-evidence, unknown-standing, and unsupported-structure fixtures remain in
use.

Generator tests passed 2/2. Existing Cockpit adapter, pressure, remediation,
and re-pressure tests passed 39/39. The full hardware-free Python suite passed
549/549. JavaScript syntax checks and `git diff --check` passed.

## Real-repository smoke boundary

The adapter generated the real model from exact commit
`add0f280b77193a43bf7639e8b28478925eac0f8`, current with `origin/main`. It
contained 19 pressure-node occurrences, 24 explicit pressure relations, 214
evidence references, and zero projection diagnostics. The smoke recovered:

- active pressure: explicit none;
- PR-006 `OPEN`;
- PR-018 `OPEN`;
- PR-009 `BASIS_INSUFFICIENT`;
- PR-017 `CANDIDATE_SURVIVED`;
- PR-019 current `BOUNDED_RESOLUTION`;
- PR-019 R0 `BASIS_INSUFFICIENT`;
- PR-019 R1 `BOUNDED_RESOLUTION`.

Direct real-model PR-009 and PR-017 renders retained exact standing, missing
discriminator, residue, evidence navigation, inactive state, and no associated
projection diagnostic. PR-017 history retained `BASIS_INSUFFICIENT`,
`BLOCKER_REMOVED`, and `CANDIDATE_SURVIVED` as separate entries.

A headless Chrome load reached projection state `complete` and rendered the
repository header, navigation, Pressure / Resolution Map, inspector regions,
evidence links, and the present-and-empty diagnostic surface. This is a
render/load and recoverability check only. It does not establish comprehension
success.

## Limitations and Projection v1 residue

- Basis and scope are not structured normalized fields.
- Standing forms are a bounded projection grammar, not a universal visual
  semantics result.
- The grid and orthogonal routing remain composition, not evidentiary geometry.
- Relation crossings and dense topology have not received general usability or
  accessibility pressure.
- Map title compression still depends on current normalized titles.
- No general comprehension, visual semantic safety, production readiness,
  observation-model correctness, observational geometry, or continuous atlas
  navigation is established.

Projection v1 remains in progress. The next expected pass is bounded
Constraints / Lineage / Horizon / Source views plus projection-only typed
transitions among those views. That next pass is not implemented here.

## Bounded adjudication

The strongest supported claim is:

> The refined projection preserves the named standing distinctions while
> reducing map prose and separating typed scientific state from projection
> diagnostics.

This pass stops before observational surfaces, event capture, clocks, boss
atlas, Controller, the next bounded view pass, or final Observatory aesthetic
refinement.
