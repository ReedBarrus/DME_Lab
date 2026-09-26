# COCKPIT CELL 002 — PRESSURE SPECIMEN FRAME

OBJECT_TYPE:
COCKPIT_SPECIMEN_IMPLEMENTATION_FRAME

STATUS:
IMPLEMENTATION TARGET

PRIMARY TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

PURPOSE:

Render one real pressure specimen end-to-end at
object / transformation / witness / standing level.

DO NOT BUILD:
- a generic dashboard;
- a new authority schema;
- a new seat schema;
- a new cursor schema;
- a new Atlas schema;
- synthetic trajectories not present in evidence.

USE EXISTING SOURCE OBJECTS.

# ==================================================
# 1. VISUAL GRAMMAR
# ==================================================

The first viewer may use only these semantic primitives:

OBJECT
STATE
RELATION
TRANSFORMATION
WITNESS
STANDING
UNKNOWN_REGION

Any richer visual element must compile down to these.

# ==================================================
# 2. CELL 002 CONTROL TRAJECTORY
# ==================================================

Render the exact authority lifecycle as:

t0
OBJECT:
authority envelope / capability

STATE:
status = ACTIVE
remaining_uses = 1

TRANSFORMATION:
reserve one use

WITNESS:
reservation record

t1
STATE:
status = CONSUMING
remaining_uses = 0

TRANSFORMATION:
governed invocation boundary crossing

WITNESS:
invocation witness / test harness boundary witness

t2
OBJECT:
model invocation occurrence

STATE:
invocation_count_delta = 1

TRANSFORMATION:
finalize authority consumption

WITNESS:
consumption receipt

t3
STATE:
status = CONSUMED
remaining_uses = 0
current_authority = NONE

# ==================================================
# 3. CELL 002 PRESSURE TRAJECTORY
# ==================================================

From the exact same consumed capability instance:

t4
TRANSFORMATION:
replay attempt

HELD FIXED:
principal
capability_id
approval_id
request identity
input identity
model
endpoint
executor
policy

EXPECTED MATERIAL INTERVENTION:
attempt reuse of consumed authority

POST-STATE:

decision = DENY
reason = AUTHORITY_EXHAUSTED
invocation_count_delta = 0
current_authority = NONE

WITNESS:
replay-denial receipt

# ==================================================
# 4. WRONG-PRINCIPAL PRESSURE
# ==================================================

CONTROL OBJECT:
fresh active P-bound capability

MATERIAL INTERVENTION:
attempting_principal_id:
P -> Q

HELD FIXED:
capability
approval
request
input
model
endpoint
executor
policy
remaining_uses = 1
status = ACTIVE

EXPECTED POST-STATE:

decision = DENY
reason = PRINCIPAL_MISMATCH
reservation_count_delta = 0
invocation_count_delta = 0
remaining_uses = 1
status = ACTIVE

STANDING:

DECLARED PRINCIPAL CORRESPONDENCE:
ENFORCED

PRINCIPAL AUTHENTICATION:
NOT ESTABLISHED

# ==================================================
# 5. EDGE INSPECTOR
# ==================================================

Every transition edge must be clickable and show:

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
# 6. CONTROL / PRESSURE DIFF VIEW
# ==================================================

Render matched control and pressure side-by-side.

For replay:

CONTROL:
fresh current authority
-> invocation count = 1

PRESSURE:
same consumed capability
-> invocation count = 0
-> DENY

For principal mismatch:

CONTROL:
attempting principal P
-> eligible for reservation

PRESSURE:
attempting principal Q
-> no reservation
-> no invocation

The viewer must explicitly separate:

CHANGED
HELD_FIXED
OBSERVED_EFFECT

# ==================================================
# 7. STANDING BADGES
# ==================================================

Allowed standing labels for this specimen:

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

Standing labels must come from or be derivable from existing evidence.

Do not use PASS as the primary scientific rendering.

PASS may remain as test-run metadata.

# ==================================================
# 8. PROVENANCE TRAVERSAL
# ==================================================

Every rendered state / edge must support:

WHY IS THIS HERE?
-> backward provenance

WHAT DID THIS CAUSE?
-> forward consequence lineage

Backward traversal may include:

receipt
<- reservation
<- issued authority envelope
<- approval
<- request / input
<- policy / executor coordinates

Forward traversal may include only witnessed or explicitly projected edges.

Do not manufacture downstream effects.

# ==================================================
# 9. CURRENTNESS
# ==================================================

Viewer must show:

SOURCE CURRENTNESS
CURRENT AUTHORITY
HISTORICAL AUTHORITY
CURRENT STANDING
HISTORICAL STANDING

Do not collapse:

RECORDED
!=
CURRENT

HISTORICAL APPROVAL
!=
CURRENT AUTHORITY

# ==================================================
# 10. ACCEPTANCE CRITERION
# ==================================================

CELL 002 IS VISUALLY OBSERVABLE IN COCKPIT
ONLY IF A HUMAN CAN INSPECT:

1. exact objects involved;
2. pre-state;
3. material intervention;
4. transformation edge;
5. witnessed post-state;
6. standing / claim ceiling;
7. unresolved regions;
8. provenance to exact source artifacts.

# ==================================================
# 11. IMPLEMENTATION ORDER
# ==================================================

1. READ existing Cell-002 traces / state.
2. MATERIALIZE one source-bound specimen view.
3. RENDER object / edge / witness structure.
4. ADD control-pressure diff.
5. ADD backward / forward traversal.
6. PRESERVE unresolved / unqualified regions visibly.
7. STOP before generic dashboard expansion.

FIRST SUCCESS:

One real Cell-002 pressure can be understood visually
without reading the raw JSON or test source,
while every visual assertion remains source-challengeable.
