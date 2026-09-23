# CODEX — CELL 002 COMPOSED VISIBILITY REPAIR 001

OBJECT_TYPE:
IMPLEMENTATION_REPAIR_FRAME

TARGET:
EXISTING COMPOSED COCKPIT

USER-OBSERVED CURRENT STATE:

- Cockpit shell renders.
- Legacy / static observer renders.
- Perceptual instrument renders.
- CONSEQUENCE projection says:
  LIVE RUNTIME NOT CONNECTED · consequence objects unavailable.
- TOPOLOGY projection renders the older pressure / resolution map.
- CONTROL MEMBRANE is not configured.
- Cell-002 specimen exists as a separate standalone page.
- Cell-002 specimen is NOT visible / reachable inside the composed Cockpit.

VERIFIED CURRENT IMPLEMENTATION:

src/cockpit/observer/index.html
contains:
  instrument-root
  runtime-root
  control-root

src/cockpit/observer/app.mjs
creates perceptual instrument
starts runtime projection
starts control adapter

src/cockpit/observer/styles.css
currently includes:

body.instrument-active #runtime-root {
  display: none;
}

src/cockpit/observer/cell002.html
exists as a separate entrypoint.

# ==================================================
# REPAIR PURPOSE
# ==================================================

Make the already-implemented Cell-002 specimen
VISIBLE AND INTERACTIVE
from the existing composed Cockpit.

DO NOT:

- connect live runtime yet;
- redesign topology;
- redesign the perceptual instrument;
- invent a new dashboard;
- introduce a new state schema;
- merge authority/control semantics;
- make Cell 002 look live when it is recorded evidence.

# ==================================================
# PRIMARY USER-VISIBLE TARGET
# ==================================================

When the operator opens the existing Cockpit and selects:

CONSEQUENCE

they must have an obvious, visible way to open:

CELL 002 — AUTHORITY REPLAY SPECIMEN

without typing or reconstructing a separate URL.

Once opened inside the composed Cockpit, the user must see:

ACTIVE / remaining=1
→ RESERVATION
→ CONSUMING / remaining=0
→ INVOCATION BOUNDARY
→ CONSUMED / current_authority=NONE
→ REPLAY ATTEMPT
→ DENY / AUTHORITY_EXHAUSTED

and wrong-principal pressure.

Nodes / edges remain interactive.

# ==================================================
# COMPOSITION LAW
# ==================================================

CELL002 SPECIMEN
=
RECORDED SOURCE-BOUND EVIDENCE VIEW

LIVE CONSEQUENCE PROJECTION
=
CURRENT / STREAMING OPERATIVE VIEW

DO NOT COLLAPSE THEM.

The composed UI must visibly distinguish:

RECORDED SPECIMEN
vs
LIVE RUNTIME

If live runtime is unavailable:

show:
LIVE RUNTIME: NOT CONNECTED

but still permit:
RECORDED SPECIMEN: CELL 002
to be opened and inspected.

# ==================================================
# PREFERRED IMPLEMENTATION SHAPE
# ==================================================

Use the smallest composition seam that preserves the existing
Cell-002 source-bound renderer.

Preferred options, in order:

1. Refactor Cell-002 app into a reusable mount function and mount it
   into a dedicated composed Cockpit specimen root.

2. If that materially increases scope, embed the existing Cell-002
   page in a same-origin read-only iframe / panel reachable from the
   Consequence projection.

Do NOT duplicate Cell-002 semantic model / trace interpretation
inside app.mjs.

DO NOT rewrite Cell-002 into the legacy observer schema.

# ==================================================
# REQUIRED UI CHANGE
# ==================================================

Add one explicit specimen navigation affordance to the composed Cockpit.

Minimum acceptable form:

CONSEQUENCE
  [LIVE]
  [CELL 002 SPECIMEN]

or equivalent.

Selection of CELL 002 SPECIMEN must:

- remain inside the composed Cockpit page / shell;
- render the source-bound Cell-002 viewer;
- preserve all Cell-002 interaction;
- preserve source-unavailable failure behavior;
- not configure runtime or control adapters implicitly.

# ==================================================
# RUNTIME VISIBILITY WOUND
# ==================================================

Do not silently keep live-runtime state hidden merely because
the perceptual instrument is active.

Current CSS:

body.instrument-active #runtime-root {
  display: none;
}

must be reviewed.

For this repair:

either

A. keep runtime-root intentionally hidden but expose an explicit
   LIVE RUNTIME STATUS inside the Consequence surface,

or

B. stop hiding runtime-root and render its current unavailable /
   connected state visibly.

Whichever choice is made must preserve the distinction:

LIVE RUNTIME STATUS
!=
RECORDED CELL-002 SPECIMEN

# ==================================================
# SOURCE BOUNDARY
# ==================================================

Cell 002 continues loading only:

traces/authority_membrane_security_cell_002_installed_qualification_result.json

through read-only GET / cache:no-store
or equivalent existing source-bound mechanism.

If unavailable:

render:
SOURCE UNAVAILABLE / UNKNOWN_REGION

Never fabricate a trajectory.

# ==================================================
# ACCEPTANCE TEST — HUMAN
# ==================================================

From the same Cockpit page the operator currently opens:

1. click CONSEQUENCE;
2. click CELL 002 SPECIMEN;
3. see the Cell-002 trajectory;
4. click RESERVATION;
5. inspect BEFORE / TRANSFORMATION / WITNESS / AFTER;
6. click REPLAY;
7. see AUTHORITY_EXHAUSTED / invocation delta 0;
8. inspect claim ceiling / unknown region;
9. navigate back to LIVE consequence status;
10. see that LIVE remains NOT CONNECTED rather than being conflated
    with the recorded specimen.

No separate manually typed URL.

# ==================================================
# AUTOMATED TESTS
# ==================================================

Require tests proving:

- composed index exposes Cell-002 specimen navigation;
- Cell-002 viewer mounts / embeds from composed Cockpit;
- Cell-002 source remains read-only;
- Cell-002 source-unavailable remains fail-closed;
- existing observer tests remain green;
- existing perceptual-instrument tests remain green;
- existing control-adapter tests remain green;
- existing runtime tests remain green;
- no control endpoint is introduced;
- no authority effect is introduced;
- no runtime snapshot is synthesized from Cell-002 trace.

# ==================================================
# REQUIRED RETURN
# ==================================================

A. exact files modified;
B. exact composition mechanism chosen;
C. exact command / URL used to open Cockpit;
D. exact user click path to Cell 002;
E. deterministic visible post-state description;
F. whether runtime-root remains hidden or visible and why;
G. test counts;
H. screenshot if available;
I. explicit confirmation:

RECORDED SPECIMEN
!=
LIVE RUNTIME

J. explicit confirmation:

NO NEW AUTHORITY
NO NEW EXECUTION
NO NEW CONTROL PATH
NO SYNTHETIC LIVE STATE

STOP WHEN CELL 002 IS ACTUALLY VISIBLE
FROM THE COMPOSED COCKPIT.
