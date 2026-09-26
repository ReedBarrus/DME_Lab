# CODEX — COCKPIT CELL 002 SPECIMEN VIEWER IMPLEMENTATION FRAME

OBJECT_TYPE:
IMPLEMENTATION_FRAME

TARGET:
FIRST REAL COCKPIT PRESSURE SPECIMEN

PRIMARY SPECIMEN:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

MODE:
SOURCE-BOUND OBSERVABILITY IMPLEMENTATION

# ==================================================
# PURPOSE
# ==================================================

Implement one real Cell-002 pressure specimen end-to-end
at object / transformation / witness / standing level.

This is NOT a generic dashboard task.

This is NOT a new ontology task.

This is NOT a normalization task.

# ==================================================
# REQUIRED SOURCE BASIS
# ==================================================

Use existing concrete state and evidence only.

Primary sources include:

tests/security/run_installed_authority_membrane_cell002.py

traces/authority_membrane_security_cell_002_installed_qualification_result.json

docs/campaigns/authority_membrane_security_001/
CELL_002_INSTALLED_QUALIFICATION_RESULT.md

docs/campaigns/authority_membrane_security_001/
COCKPIT_CELL002_PRESSURE_SPECIMEN_FRAME.md

docs/campaigns/authority_membrane_security_001/
COCKPIT_EXISTING_STATE_PROJECTION_AUDIT_V0.md

Do not invent replacement schemas for:

seat
cursor
authority
campaign
Atlas

# ==================================================
# VISUAL GRAMMAR
# ==================================================

The implementation may rely only on these semantic primitives:

OBJECT
STATE
RELATION
TRANSFORMATION
WITNESS
STANDING
UNKNOWN_REGION

Any UI element must resolve to one or more of these.

# ==================================================
# FIRST REQUIRED SPECIMEN
# ==================================================

Render the installed Cell-002 control path:

ACTIVE / remaining=1
→ reservation
→ CONSUMING / remaining=0
→ invocation boundary
→ CONSUMED / current_authority=NONE

Then render exact replay:

same consumed capability
→ replay attempt
→ DENY
→ AUTHORITY_EXHAUSTED
→ invocation delta=0

Then render wrong-principal pressure:

fresh P-bound capability
attempting principal P → Q
→ DENY
→ PRINCIPAL_MISMATCH
→ no reservation
→ no invocation
→ ACTIVE / remaining=1 preserved

# ==================================================
# EDGE INSPECTOR
# ==================================================

Every node / edge must be inspectable for:

BEFORE_OBJECT
BEFORE_STATE

TRANSFORMATION / OPERATOR

BASIS

WITNESS

AFTER_OBJECT
AFTER_STATE

WHAT_CHANGED

WHAT_DID_NOT_CHANGE

STANDING_EARNED

CLAIM_CEILING

UNRESOLVED

SOURCE_ARTIFACTS

# ==================================================
# CONTROL / PRESSURE DIFF
# ==================================================

The viewer must explicitly show:

CHANGED
HELD_FIXED
OBSERVED_EFFECT

For replay:

CHANGED:
current authority standing from fresh to consumed
plus replay attempt occurrence

HELD_FIXED:
capability instance
approval
principal
request
input
model
endpoint
executor
policy

OBSERVED_EFFECT:
second invocation delta = 0
DENY / AUTHORITY_EXHAUSTED

For wrong principal:

CHANGED:
attempting_principal_id P → Q

HELD_FIXED:
capability
approval
request
input
model
endpoint
executor
policy
remaining_uses=1
status=ACTIVE

OBSERVED_EFFECT:
no reservation
no invocation
authority preserved

# ==================================================
# SOURCE-BOUNDARY LAW
# ==================================================

THE VIEWER MAY PROJECT
ONLY WHAT THE SOURCE ARTIFACT ESTABLISHES.

If a relation is not present in admitted evidence:

render:
UNKNOWN / UNRESOLVED / NOT_DERIVED

Do NOT:
- interpolate;
- infer hidden transitions;
- invent causal edges;
- infer currentness from filename;
- silently collapse projected standing into realized standing.

# ==================================================
# CURRENTNESS
# ==================================================

Every rendered object must expose:

SOURCE CURRENTNESS
HISTORICAL STANDING
CURRENT STANDING
CURRENT AUTHORITY
CLAIM CEILING

If currentness cannot be established from the source basis:

CURRENTNESS:
UNRESOLVED

# ==================================================
# PROVENANCE TRAVERSAL
# ==================================================

Required interactions:

WHY IS THIS STATE HERE?

and:

WHAT DID THIS TRANSFORMATION CAUSE?

Backward traversal may walk:

receipt
<- reservation
<- authority envelope
<- approval
<- request / input
<- executor / policy coordinates

Forward traversal may walk only witnessed or explicitly projected edges.

# ==================================================
# STANDING DISPLAY
# ==================================================

Allowed labels:

OBSERVED
ADJUDICATED
PROJECTED
REALIZED
UNRESOLVED
NOT_DERIVED
QUALIFIED
PARTIAL
UNTESTED
NOT_ESTABLISHED

PASS may appear only as test-run metadata.

PASS must not be the primary scientific rendering.

# ==================================================
# ACCEPTANCE CRITERION
# ==================================================

A human can inspect, from one rendered Cell-002 specimen:

1. exact objects involved;
2. pre-state;
3. material intervention;
4. transformation edge;
5. witnessed post-state;
6. standing / claim ceiling;
7. unresolved regions;
8. provenance to exact source artifacts.

AND:

the rendered output does not require reading raw JSON
to understand the tested consequential relation.

# ==================================================
# SECONDARY CONSTRAINT
# ==================================================

Design the renderer so that UNKNOWN_REGION is a first-class
visual possibility.

Do NOT implement the sparse round-trip specimen yet.

But the Cell-002 viewer must not make assumptions that would
prevent a later specimen from rendering:

FRAME 0
→ UNKNOWN_REGION
→ FRAME 1

without inventing an intermediate trajectory.

# ==================================================
# DO NOT
# ==================================================

DO NOT:

build a generic dashboard
create a new state ontology
create a new event ontology
normalize all repo state
implement seat spawning
implement cursor spawning
add authority controls
add revocation
add freeze
add network monitoring
add external membrane
add generic 3D visualization
add a new Atlas representation

# ==================================================
# REQUIRED RETURN
# ==================================================

A. exact files added / modified;
B. exact source artifacts consumed;
C. screenshot or deterministic rendered output description;
D. control trajectory rendering;
E. replay-pressure rendering;
F. wrong-principal rendering;
G. edge-inspector fields;
H. provenance traversal behavior;
I. unresolved / claim-ceiling rendering;
J. tests;
K. explicit statement of what remains hardcoded to Cell 002;
L. explicit statement of what is generic only because the source relation already supports it.

STOP AFTER ONE SOURCE-BOUND CELL-002 SPECIMEN VIEWER.
