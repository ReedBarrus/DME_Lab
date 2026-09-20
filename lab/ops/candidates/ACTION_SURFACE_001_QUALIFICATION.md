# ACTION_SURFACE_001 — BOUNDED CANDIDATE QUALIFICATION

## Status

```text
CANDIDATE:
MATERIALIZED

BRANCH:
action-surface-v0

SOURCE MAIN:
759eca8c3f3c2d3e37d8031207742290f1fb8b6b

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE

MAIN ADOPTION:
NONE

PROMOTION:
NONE
```

## Bounded question

Can the Cockpit project the next declared Conductor routing operation from an
exact committed basis without inventing process liveness, creating authority,
selecting an action, replaying consequence, or advancing continuity state?

## Governing separations

```text
PROCESS SPEC EXISTS
!=
PROCESS REGISTERED

PROCESS REGISTERED
!=
PROCESS ACTIVE

ACTION VISIBLE
!=
ACTION SELECTED
!=
ACTION AUTHORIZED
!=
ACTION EXECUTED

ROUTING RECONSTRUCTION
!=
CONSEQUENCE REPLAY
```

## Exact candidate identities

```text
src/cockpit/action_surface.py
024bd22d343d60ad1598c3b395ee795c0ec70480

schemas/action_surface_v0.schema.json
c753f40a95e7145f364bd332e41d0dc56846ecf8

src/cockpit/projection_adapter.py
5efd0c5597ac78a234e1cd2478e389da4632b2a0

src/cockpit/observer/model.mjs
615f4b0e909414a18dbb82c9cfaf9e26648b28ca

src/cockpit/observer/render.mjs
841673d83bfcbb997cf18f5418b3725631deee56

src/cockpit/observer/app.mjs
a004b71464cc1fa651d56f77d98f7280a80e3602

tests/cockpit/test_action_surface.py
9471c688bd1ef4b76cea2b64bc7da5bf412e6246

tests/cockpit/test_observer.mjs
756155b000b7163d8a6f6b8ddfbce88a7c504656

tests/cockpit/test_projection_adapter.py
2f5f19b191f2b97cfeb8f87740812eda719855ca

docs/candidates/action_surface_v0/ACTION_SURFACE_CONTRACT_v0.md
f73a276117d7adbc8b371ff8c555805279f24429
```

## Observed focused qualification

The exact Action Surface Python implementation and exact focused test file were
reconstructed from their GitHub branch bytes into an isolated local test
directory.

Their local Git blob identities were checked with `git hash-object` and
matched the exact branch blobs listed above.

Executed:

```text
python -m unittest tests.cockpit.test_action_surface -v
```

Observed:

```text
3 / 3 PASS
```

The passing focused specimens cover:

```text
1. committed process specification
   != runtime registration

2. committed routing events reconstruct
   HUMAN_DECISION_REQUIRED
   without creating human authority

3. unknown routing event type
   fails legibly rather than becoming
   a plausible action surface
```

The generated synthetic action-surface object was also validated against:

```text
schemas/action_surface_v0.schema.json
```

Observed schema errors:

```text
0
```

## Exact Cockpit model / render qualification

The exact branch bytes for:

```text
src/cockpit/observer/model.mjs
src/cockpit/observer/render.mjs
src/cockpit/observer/app.mjs
tests/cockpit/test_observer.mjs
```

were syntax-checked in an isolated JavaScript evaluation after removing only
ESM import/export wrappers required by that evaluator.

Observed:

```text
model.mjs:
PARSE_OK

render.mjs:
PARSE_OK

app.mjs:
PARSE_OK

test_observer.mjs:
PARSE_OK
```

The exact model + render implementation was then exercised with a synthetic
`action_surface_v0` object through:

```text
buildObserverModel
→ selectView(ACTIONS)
→ selectAction
→ renderActiveView
```

Observed checks:

```text
selected process identity:
PASS

ACTIONS view selected:
PASS

SPEC_ONLY_UNREGISTERED retained:
PASS

visible/selected/authorized/executed boundary rendered:
PASS

NONE_BY_ACTION_SURFACE rendered:
PASS

Run control absent:
PASS

Execute control absent:
PASS
```

## Rakes caught before this receipt

### Exact committed provenance

Initial standalone Action Surface projection retained the caller's symbolic
`HEAD` in provenance.

Repair:

```text
SOURCE REF
→ resolve exact commit
→ read every process/event from that exact commit
→ retain exact 40-hex source commit
```

Scar:

```text
SOURCE REF
!=
SOURCE COMMIT
```

### Literal Git commit peel

The first exact-ref repair accidentally formed an invalid Python interpolation
for Git's `^{commit}` peel syntax. Static inspection caught it before this
qualification and the implementation was repaired to pass the literal Git peel
to `rev-parse`.

### Projection-status ordering

The first adapter splice derived `projection_status` before Action Surface
diagnostics were appended.

That admitted the possibility:

```text
ACTION SURFACE PROJECTION FAILURE
+
COCKPIT projection_status = complete
```

Repair moved Action Surface projection before operational-status adjudication.

A focused adapter regression test now requires:

```text
ActionSurfaceError
→ action_surfaces = []
→ visible action_surface_projection_failure diagnostic
→ projection_status = partial
```

### Process identity ambiguity

The candidate now rejects:

```text
duplicate process_id specifications

routing events referring to
a process with no unique committed specification

routing events preceding PROCESS_REGISTERED
```

rather than silently selecting or dropping a routing basis.

## Current main specimen

On the source main from which this branch was cut:

```text
lab/processes/LP001_CONDUCTOR_FIXTURE_v0.json:
PRESENT

lab/events/events.jsonl:
EMPTY
```

Therefore the expected first projected action posture is:

```text
process:
LP-001-CONDUCTOR-FIXTURE

runtime_registration:
ABSENT

phase:
SEEDED

routing_status:
UNREGISTERED

declared transition:
LOAD_FROZEN_CONTRACT

transition kind:
MECHANICAL

eligibility:
SPEC_ONLY_UNREGISTERED
```

This is intentionally a test of:

```text
DECLARED PROCESS GEOMETRY
!=
LIVE PROCESS EVENT
```

## Qualification ceiling

The following were not observed by this qualification:

```text
full repository test suite
GitHub CI workflow execution
deployed Cockpit browser session
human usability pressure
scheduled invocation
shared-room delivery
automatic continuity consumption
action request transport
authority transport
role invocation
capability availability
external execution
main integration
production reliability
scientific standing change
```

GitHub reported no workflow runs or commit statuses for the candidate head at
the time of inspection.

Therefore:

```text
FOCUSED QUALIFICATION:
OBSERVED

FULL-SUITE QUALIFICATION:
NOT OBSERVED

CANDIDATE REVIEW:
AVAILABLE

MAIN ADOPTION:
NOT AUTHORIZED BY THIS RECEIPT
```

## Next bounded operation

```text
ACTION_SURFACE_v0
→ independent candidate review / pressure
```

The candidate is suitable for review as a read-only action-legibility surface.
This receipt does not authorize merge or later executable action coupling.
