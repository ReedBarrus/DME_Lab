# COCKPIT EXISTING STATE PROJECTION AUDIT V0

OBJECT_TYPE:
EXISTING_STATE_PROJECTION_AUDIT

STATUS:
INITIAL / SOURCE-BOUND / NO NEW ONTOLOGY

PRIMARY LAW:

THE SYSTEM ALREADY HAS STATE.

COCKPIT MUST NOT MODEL IT AGAIN.

COCKPIT SHOULD PROJECT EXISTING DURABLE STATE
WITH CURRENTNESS, SOURCE, EFFECT, AND CLAIM CEILINGS PRESERVED.

# ==================================================
# 1. SEAT STATE
# ==================================================

VERIFIED SOURCE:

continuity/seats/labboib.json

CURRENT DURABLE FIELDS INCLUDE:

seat_id
consumer_id
seat_class
role
cursor_ref
working_state_ref
inbox_ref
outbox_ref
trigger.state
occupant.binding
allowed_wake_effects
forbidden_wake_effects
noncollapses
authority_effect
execution_effect

VERIFIED CURRENT RELATIONS:

seat_id:
LABBOIB

consumer_id:
labboib

cursor_ref:
continuity/cursors/labboib.json

working_state_ref:
continuity/current_state/labboib_working_state_v0.json

trigger.state:
UNBOUND

occupant.binding:
UNBOUND

authority_effect:
NONE_BY_MANIFEST

execution_effect:
NONE_BY_MANIFEST

CAUSAL / CONSEQUENTIAL EFFECT:

The seat manifest constrains:
- which durable state is referenced;
- which cursor is consumed;
- which inbox/outbox surfaces are associated;
- which wake effects are allowed;
- which effects are forbidden;
- what may be requested / emitted;
- what may NOT be inferred as authority or execution.

FORBIDDEN COLLAPSES ALREADY PRESENT:

SEAT_CONTINUITY != MODEL_CONTINUITY
MODEL_INSTANCE != SEAT
SCHEDULED_REENTRY != CONTINUOUS_PROCESS_IDENTITY
PERSISTENT_ATTENTION != PERSISTENT_EXECUTION_AUTHORITY
MESSAGE_DELIVERED != MESSAGE_ACCEPTED
ACTION_REQUESTED != ACTION_AUTHORIZED != ACTION_EXECUTED

SAFE COCKPIT PROJECTION:

seat identity
consumer identity
seat class
role
cursor ref
working-state ref
trigger standing
occupant standing
allowed / forbidden wake effects
authority effect
execution effect

COCKPIT MUST NOT INFER:

live occupant
current execution authority
continuous process identity
authorization from seat existence

# ==================================================
# 2. SEAT WORKING STATE
# ==================================================

VERIFIED SOURCE:

continuity/current_state/labboib_working_state_v0.json

VERIFIED FIELDS:

seat_id
state_id
campaign
continuity
injection_coordinate
current_frontier
unresolved
authority
last_wake_receipt_ref
standing_effect
authority_effect

VERIFIED CURRENT STANDING:

campaign.status:
ACTIVE_CANDIDATE_CONSTRUCTION

continuity.synchronized_through:
CE-000033

current_frontier:
materialize seat manifest, deterministic wake packet, and bounded qualification

authority.standing:
NONE

standing_effect:
NONE_BY_WORKING_STATE

authority_effect:
NONE_BY_WORKING_STATE

CAUSAL / CONSEQUENTIAL EFFECT:

This state constrains the seat's reconstructable working orientation,
campaign frontier, synchronized continuity position, and unresolveds.

SAFE COCKPIT PROJECTION:

current frontier
campaign association
synchronized-through event
unresolveds
authority standing
last wake receipt
state identity

COCKPIT MUST NOT TREAT WORKING STATE AS:

authority grant
scientific promotion
execution result
live occupant proof

# ==================================================
# 3. CURSOR STATE
# ==================================================

VERIFIED SOURCES:

continuity/cursors/sol.json
continuity/cursors/labboib.json
continuity/cursors/codex.json

VERIFIED CORE FIELDS:

consumer
cursor_state
last_seen_event_id
bootstrap_mode

LABBOIB additionally preserves:

bootstrap_basis.stream_head_at_materialization
bootstrap_basis.purpose
bootstrap_basis.historical_chat_imported

CURRENT VERIFIED POSITIONS:

sol:
POSITIONED @ CE-000029

labboib:
POSITIONED @ CE-000033

codex:
POSITIONED @ CE-000010

CAUSAL / CONSEQUENTIAL EFFECT:

Cursor state changes what a consumer treats as already seen versus unseen
and therefore changes the reconstruction / continuation boundary.

SAFE COCKPIT PROJECTION:

consumer
cursor state
last seen event
bootstrap mode
bootstrap basis where present

COCKPIT MAY DERIVE:

relative continuity position
candidate unseen interval only when the event stream basis is also resolved

COCKPIT MUST NOT INFER:

authority
execution
knowledge of event content merely from cursor position
successful consumption of any event not independently witnessed

# ==================================================
# 4. ATLAS / LOCAL-FRAME PROJECTION
# ==================================================

VERIFIED SOURCE:

src/projection/draci_local_frame_v0.py

VERIFIED DESIGN POSTURE:

The projector explicitly describes itself as:
- bounded;
- derived;
- source-bound;
- append-free;
- not a frame/event schema;
- not a source of authority.

The projection retains:
- exact source refs;
- exact basis refs;
- content identities;
- temporal PRE / OPERATIVE / POST relations;
- unresolved coordinates;
- currentness ceilings;
- authority ceilings;
- consequence closure ceilings.

CAUSAL / CONSEQUENTIAL EFFECT:

Atlas / local-frame projections affect:
- navigation;
- reconstruction;
- interpretation;
- which relations remain visible;
- which unknowns remain explicit;
- which downstream requests or pressures may be formulated.

REPRESENTATION CAN THEREFORE BE CONSEQUENTIAL
WITHOUT ITSELF BEING EXECUTION AUTHORITY.

SAFE COCKPIT PROJECTION:

exact projection identity
projection question / orientation
source refs
basis refs
temporal relations
known invariants
unresolved coordinates
currentness standing
authority standing
consequence-closure standing

COCKPIT MUST PRESERVE:

DERIVED_VIEW_ONLY
where supplied by the projector.

COCKPIT MUST NOT CONVERT:

derived projection
→ source event

projection relation
→ execution fact

navigation surface
→ authority

# ==================================================
# 5. CAMPAIGN / SCIENTIFIC STATE
# ==================================================

VERIFIED SOURCES INCLUDE:

docs/campaigns/authority_membrane_security_001/
CELL_002_FINAL_CANDIDATE_ADJUDICATION_001.md

docs/campaigns/authority_membrane_security_001/
CELL002_INSTALLED_QUALIFICATION_FRAME.md

NOTE:

CURRENT_BUNDLE.md is retained campaign history but is stale relative
to the present Cell-002 installed state. Cockpit must therefore not
treat filename or existence as proof of current campaign standing.

CURRENT VERIFIED SECURITY CAMPAIGN RELATION:

CELL_002_CANDIDATE_APPARATUS:
BOUNDEDLY_QUALIFIED

CELL_002_INSTALLED:
YES

CELL_002_INSTALLED_QUALIFIED:
NO

Installed qualification requires matched:
- control;
- exact replay;
- wrong declared principal;
- Cell-001 regression.

SAFE COCKPIT PROJECTION:

campaign identity
current cell / pressure object when currentness basis is explicit
candidate standing
installed standing
claim ceiling
next lawful pressure
required witnesses
unresolved limits
dependency references

COCKPIT MUST NOT INFER CURRENTNESS FROM:

filename
directory membership
historical bundle
latest-looking prose

CURRENTNESS NEEDS AN EXPLICIT BASIS.

# ==================================================
# 6. AUTHORITY STATE
# ==================================================

OPERATIVE SOURCE:

LOCAL TRUST ROOT
NOT REPOSITORY
NOT COCKPIT

INSTALLED COORDINATES:

bridge:
C:\Users\Admin\.dme_lab_bridge\bridge.py

authority module:
C:\Users\Admin\.dme_lab_bridge\local_authority_consumption_v0.py

authority state:
C:\Users\Admin\.dme_lab_bridge\authority_state_v0\

policy:
C:\Users\Admin\.dme_lab_bridge\policy.json

CURRENT VERIFIED INSTALLED HASHES:

bridge:
0f86b8499c269ee42ed50285e4429c504ff5e6f93a6e65836128e98ef9d2bb21

authority module:
bfbbb929f0a0b55a745b5095fd2abd16541757b88f3151d69e7e7bb325e57303

policy:
65f2ce8c3ce1cd5147940ff851cb61a9f04b7db220dadb4c77e1d5352e28200b

SAFE COCKPIT PROJECTION:

capability_id
approval_id
principal_id
request / input / model / endpoint coordinates
remaining uses
status
history
receipts
denials
current authority
executor / policy hashes

COCKPIT MUST NOT:

mint authority
edit remaining_uses directly
convert historical approval into current authority
become the trust root

# ==================================================
# 7. EXISTING RELATIONAL CHAIN
# ==================================================

The existing concrete surfaces already support this projection chain:

SEAT
→ cursor_ref
→ CURSOR
→ continuity event boundary

SEAT
→ working_state_ref
→ WORKING STATE
→ campaign / frontier / unresolveds

ATLAS / LOCAL FRAME
→ exact source + basis refs
→ derived relational projection

CAMPAIGN
→ pressure / adjudication / claim ceiling
→ request / implementation / qualification state

REQUEST
→ HUMAN APPROVAL
→ LOCAL AUTHORITY ENVELOPE
→ INSTALLED BRIDGE
→ INVOCATION
→ RECEIPT / DENIAL
→ CURRENT STANDING

Cockpit's job is to traverse and display those references.

# ==================================================
# 8. FIRST COCKPIT IMPLEMENTATION TARGET
# ==================================================

DO NOT CREATE:

new seat schema
new cursor schema
new Atlas-state schema
generic agent-status schema
parallel campaign object model
parallel authority database

FIRST READ-ONLY PROJECTIONS:

A. SEAT CARD
- existing seat manifest
- working state
- cursor ref / cursor standing
- occupant / trigger standing
- explicit authority / execution effects
- unresolveds

B. CURSOR CARD
- consumer
- current cursor state
- last_seen_event_id
- bootstrap basis
- linked seat(s) where explicitly referenced

C. CAMPAIGN CARD
- exact currentness basis
- current pressure / cell
- standing
- claim ceiling
- next lawful pressure
- relevant artifact refs

D. AUTHORITY CARD
- local trust-root current state
- capability / approval / principal
- remaining use
- status
- latest receipt / denial
- installed executor / policy coordinates

E. ATLAS PROJECTION
- use existing local-frame projector outputs
- retain DERIVED_VIEW_ONLY standing
- show source / basis / unresolved coordinates

# ==================================================
# 9. MINIMUM CROSS-OBJECT QUESTIONS
# ==================================================

For any projected object, Cockpit should answer:

WHERE IS THE SOURCE STATE?

WHAT IS CURRENT?

WHAT IS HISTORICAL?

WHAT DOES THIS OBJECT CAUSALLY AFFECT?

WHAT AUTHORITY DOES IT NOT HAVE?

WHAT EXACT REFERENCES CONNECT IT TO OTHER OBJECTS?

WHY IS THIS PROJECTION CURRENT?

WHAT IS UNRESOLVED?

# ==================================================
# 10. IMPLEMENTATION LAW
# ==================================================

PROJECT FIRST.
DO NOT NORMALIZE FIRST.

READ EXISTING OBJECTS AT THEIR CURRENT SOURCES.

ONLY INTRODUCE A NEW ADAPTER OR INDEX
WHEN AN ACTUAL ACCESS / PERFORMANCE / JOIN FAILURE
IS OBSERVED AND PRESSURED.

SOURCE OBJECT
!=
COCKPIT VIEW

COCKPIT VIEW
!=
SOURCE OF TRUTH
