# CODEX — CELL 002 COMPOSED COCKPIT INTEGRATION FRAME

OBJECT_TYPE:
IMPLEMENTATION_FRAME

PURPOSE:
Make the already-implemented Cell-002 specimen viewer
actually accessible inside the existing composed local Cockpit.

DO NOT redesign the specimen viewer.
DO NOT create a second Cockpit.
DO NOT introduce a new state model.

# ==================================================
# SOURCE OBJECT A — EXISTING COMPOSED COCKPIT
# ==================================================

Existing entrypoint:

src/cockpit/observer/index.html
src/cockpit/observer/app.mjs
src/cockpit/observer/styles.css

Existing composed surfaces include:

instrument-root
runtime-root
control-root

Existing observer / perceptual machinery includes:

src/cockpit/observer/model.mjs
src/cockpit/observer/render.mjs
src/cockpit/observer/perceptual_instrument.mjs
src/cockpit/observer/runtime_live.mjs
src/cockpit/observer/control_live.mjs

# ==================================================
# SOURCE OBJECT B — CELL 002 SPECIMEN VIEWER
# ==================================================

Expected local candidate artifacts:

src/cockpit/observer/cell002.html
src/cockpit/observer/cell002.css
src/cockpit/observer/cell002_app.mjs
src/cockpit/observer/cell002_model.mjs
src/cockpit/observer/cell002_render.mjs

test:

tests/cockpit/test_cell002_specimen.mjs

Primary source:

traces/authority_membrane_security_cell_002_installed_qualification_result.json

# ==================================================
# REQUIRED TRANSFORMATION
# ==================================================

COMPOSE:

existing local Cockpit
+
existing Cell-002 source-bound specimen viewer

INTO:

one local Cockpit entrypoint from which the operator
can visibly open / select the Cell-002 specimen.

The Cell-002 specimen must remain read-only.

Do not merge authority controls into the specimen.

Do not duplicate the specimen semantic model inside app.mjs.

Prefer a thin composition / navigation seam.

# ==================================================
# REQUIRED USER-VISIBLE POST-STATE
# ==================================================

From the actual local Cockpit entrypoint, a human must be able to:

1. open Cockpit;
2. select / open Cell 002;
3. see the control trajectory;
4. see replay pressure;
5. see wrong-principal pressure;
6. click a node / edge;
7. inspect BEFORE / TRANSFORMATION / WITNESS / AFTER;
8. inspect CHANGED / HELD FIXED / OBSERVED EFFECT;
9. inspect claim ceiling / unresolved region;
10. traverse backward / forward provenance.

No manual URL reconstruction should be required after Cockpit is opened.

# ==================================================
# SOURCE-BOUNDARY REQUIREMENT
# ==================================================

The integrated specimen must still load only the fixed
Cell-002 qualification trace by read-only GET with cache:no-store,
or an equivalently source-bound existing path.

Integration must NOT turn source-unavailable into synthetic success.

If the trace is unavailable:

render source unavailable / unresolved.

# ==================================================
# CHAT / ADDRESSING NON-COLLAPSE
# ==================================================

Preserve existing perceptual-instrument law:

ADDRESSED CHAT PACKET
!=
TRANSPORT
!=
AUTHORITY
!=
INVOCATION

Do not wire Cell-002 integration to chat execution.

Existing addressed-chat behavior must remain non-consequential
unless a separate transport / wake / authority path is later added.

# ==================================================
# REQUIRED TESTS
# ==================================================

Add / update tests proving:

A. composed Cockpit exposes a visible Cell-002 entry;
B. entry resolves to the specimen viewer without a second standalone app launch;
C. specimen remains read-only;
D. existing observer, perceptual instrument, runtime, and control tests remain green;
E. source-unavailable Cell-002 remains visibly unavailable;
F. existing addressed-chat packet remains authority_effect=NONE and transport_effect=NONE.

# ==================================================
# REQUIRED RETURN
# ==================================================

A. files changed;
B. exact local command / URL used to open Cockpit;
C. exact clicks / navigation to reach Cell 002;
D. whether Cell 002 is embedded, routed, or linked and why;
E. screenshot or deterministic DOM description of visible integration;
F. test counts;
G. source-unavailable behavior;
H. explicit statement that no authority / execution path was added.

STOP WHEN CELL 002 IS ACTUALLY VISIBLE AND INTERACTIVE
FROM THE EXISTING LOCAL COCKPIT ENTRYPOINT.
