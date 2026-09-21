# COCKPIT_ONLINE_INTEGRATION_PRESSURE_001

## Status

```text
INTEGRATION PRESSURE:
FROZEN

IMPLEMENTATION:
NOT YET MATERIALIZED ON THIS BRANCH

DEPLOYMENT:
NONE

CONTROL AUTHORITY:
NONE

MERGE / REBASE:
NONE
```

## Question

What is the smallest composition that can bring the perceptual Cockpit online
on the current default-branch lineage while preserving newer `main` behavior
and without treating independently good branches as automatically composable?

The governing cut is:

```text
INTEGRATION
!=
UNION OF GOOD BRANCHES
```

and:

```text
BRANCH COORDINATE
IS PART OF BASIS
```

## Exact coordinates

```text
COMMON ANCESTOR:
35d1f13396afde04e4fbad8d3c3de60136926736

CURRENT MAIN:
00b3783683ad9009d6152cc861b9383087aece7f

CURRENT PERCEPTUAL CAMPAIGN:
0fd6f3d81393eb81e4f8d3df86e6b6d411d2c0f9

CURRENT DEVELOPMENT CAMPAIGN:
7cd6ffd9b03c1d7638f2fffb38448f47a1e78d95
```

## Lineage geometry

Current comparisons:

```text
main vs perceptual:
DIVERGED
199 perceptual-side commits after merge base
111 main-side commits after merge base
137 changed files

main vs development:
DIVERGED
72 development-side commits after merge base
111 main-side commits after merge base
54 changed files
```

Therefore:

```text
PERCEPTUAL HEAD
!=
MAIN + PERCEPTUAL DELTA

DEVELOPMENT HEAD
!=
MAIN + DEVELOPMENT DELTA
```

No whole-branch merge is authorized by this pressure.

## Changed-surface classification

Relative to the common ancestor, `main` and the perceptual campaign both
changed only two existing Cockpit observer files:

```text
src/cockpit/observer/app.mjs
src/cockpit/observer/styles.css
```

The current perceptual instrument also modifies `index.html` relative to the
ancestor, while current `main` leaves that file at the earlier observer shape.

### Main-only Cockpit evolution

Current `main` contains newer observer / Action Surface work including:

```text
src/cockpit/action_surface.py
src/cockpit/generate_projection.py
src/cockpit/projection_adapter.py
src/cockpit/observer/model.mjs
src/cockpit/observer/render.mjs
tests/cockpit/test_action_surface.py
tests/cockpit/test_observer.mjs
tests/cockpit/test_projection_adapter.py
```

This must not be deleted merely because the perceptual branch started from an
older observer composition point.

### Perceptual-only operating bundle

The current perceptual lineage contains the following candidate read-oriented
online bundle absent from `main`:

```text
src/cockpit/observer/perceptual_instrument.mjs
src/cockpit/observer/runtime_live.mjs
src/cockpit/observer/control_live.mjs
src/cockpit/live_runtime_projection.py
src/cockpit/development_horizon_projection.py
tests/cockpit/test_perceptual_instrument.mjs
tests/runtime/test_live_runtime_projection.py
```

It also adds three UI roots in:

```text
src/cockpit/observer/index.html

instrument-root
runtime-root
control-root
```

### Control write membrane

The Python control adapter is deliberately not classified as part of the
minimal read-only integration bundle:

```text
src/cockpit/control_adapter.py
```

It depends on a wider qualified stack including campaign, selection,
revalidation, preparation, assignment, bounded reentry, and wake-source
machinery.

Therefore:

```text
PERCEPTUAL INSTRUMENT ONLINE
!=
CONTROL MEMBRANE ONLINE
```

The browser-side `control_live.mjs` may remain present while the adapter is
unconfigured, because its explicit unavailable state preserves:

```text
LIVE PROJECTION
!=
CONTROL PATH
```

No write-capable backend is imported merely to make the UI look complete.

## Overlap 1 — app.mjs

The two lineages changed `app.mjs` for different reasons.

### Current main adds

```text
selectAction
[data-action-key]
Action Surface selection
```

### Perceptual lineage adds

```text
createPerceptualInstrument
startRuntimeProjection
startControlAdapter
semantic selection -> exact instrument address
runtime snapshot -> instrument consequence graph
observer model -> instrument topology basis
```

The composition requirement is:

```text
MAIN ACTION-SURFACE NAVIGATION
+
PERCEPTUAL ADDRESS CONTINUITY
+
RUNTIME / CONTROL STARTUP
```

No side may overwrite the other.

## Overlap 2 — styles.css

The common ancestor contains 1158 lines.

Current `main` is exactly that shared prefix plus an appended Action Surface
style block.

The perceptual branch is exactly that shared prefix plus appended
runtime / control / perceptual-instrument style blocks.

This is a favorable composition geometry:

```text
COMMON STYLE BASIS
+
ACTION SURFACE APPEND
+
PERCEPTUAL / RUNTIME APPEND
```

The integration should preserve both tails rather than replacing either full
file.

## Exact source blobs for candidate bundle

```text
perceptual_instrument.mjs
bd22cdfd4505cb2ada4dc2b0f0fb850d1429f2aa

runtime_live.mjs
54f77aeb123ed80c846bdb540c32a9a54c78fedf

control_live.mjs
badd63646445263c9c293ec76ba18bc909156474

live_runtime_projection.py
c0fd7b0287b9910aa960e141d8734e2f7041ef92

development_horizon_projection.py
9f5efb36a526c9311e059cdfefca32a3f8b5d785

test_perceptual_instrument.mjs
1b7c95aea1d47d2ea0064f9178d4d9f8480d7b5b

test_live_runtime_projection.py
51604dfc35e6730467011354f512a49d622857c5
```

Overlap source blobs:

```text
app.mjs

main:
a004b71464cc1fa651d56f77d98f7280a80e3602

perceptual:
15a4ea879164eaa5bf6a53ec54d5212a86d17e69

styles.css

main:
6bf3dc692cb9dc1195884be665573e58f497431f

perceptual:
0d4c3f0489a0edbbaf2f2fc190a92b77c2f8d0c5

index.html

main:
226915668b120ba7e71dec3ff975e61d0a544f35

perceptual:
219c4cb82887a55469180f2ad64c65464b69ddc0
```

## Proposed smallest integration cells

### I1 — static observer regression

Compose the candidate UI bundle onto current `main`.

Require:

```text
existing observer tests pass
existing Action Surface tests pass
projection-adapter tests pass
```

This protects current-main behavior.

### I2 — perceptual instrument regression

Run the current perceptual tests on the composed lineage.

Require the already-earned cuts to survive:

```text
CONSEQUENCE != TOPOLOGY

ADDRESS RETAINED
!=
ADDRESS REPRESENTABLE

GEOMETRY != RELATION

SCREEN POSITION != PRIORITY

CONTROL PREFILL
!=
PREVIEW ADMISSIBILITY
```

### I3 — live runtime read path

Run the read-only runtime projection on the composed lineage.

Require:

```text
projection can expose configured durable runtime sources
missing configured source = PARTIAL / explicit
HTTP write methods rejected
polling does not create state
cross-store atomicity remains UNESTABLISHED
```

### I4 — control-unconfigured browser posture

Load the integrated Cockpit with no control adapter configured.

Require:

```text
perceptual instrument renders
legacy observer / science views remain reachable
runtime status is failure-legible
control surface says unavailable
no write path exists
```

### I5 — exact overlap composition

Verify the composed `app.mjs` retains both:

```text
[data-action-key] -> selectAction(...)
```

and:

```text
observer semantic selection
-> exact instrument address
```

Verify composed CSS contains both independent style families.

## Stop conditions

Stop integration if:

```text
- current-main Action Surface selection disappears;
- current observer/science navigation regresses;
- perceptual address switching becomes kind-relative again;
- control affordances regain an admissibility-sounding label;
- runtime projection gains a write effect;
- unconfigured control silently becomes available;
- whole campaign history must be imported merely to satisfy an incidental import;
- a missing durable runtime source is rendered as healthy empty state;
- composition requires inferring equivalence between different branch objects;
- tests from either side cannot be executed against the composed lineage.
```

## Claim ceiling

A clean pass may establish only:

```text
THE TESTED READ-ORIENTED PERCEPTUAL COCKPIT BUNDLE
COMPOSES WITH THE TESTED CURRENT-MAIN OBSERVER / ACTION SURFACE
WITHOUT THE TESTED REGRESSIONS.
```

It does not establish:

```text
deployment to Reed's machine
control membrane integration
authenticated human control
scheduler authority
wake authority
scientific standing
general branch integration safety
future model / occupant continuity
```

## Next step if pressure survives

Materialize the bounded read-oriented bundle on this integration branch,
execute I1-I5, and only then consider a separate control-stack composition.

The intended progression is:

```text
COCKPIT VISIBLE + LIVE-READABLE
↓
COCKPIT CONTROL MEMBRANE COMPOSED
↓
LOCAL DOGFOOD / USER OBSERVATION
↓
IDENTITY + SEMANTIC-DEBT CONSERVATION PRESSURES
```

not:

```text
MERGE THE CAMPAIGN
AND HOPE.
```
