# TOWN SQUARE V0 — DURABLE ADDRESSED MESSAGE TRANSPORT FRAME

OBJECT_TYPE:
IMPLEMENTATION / PRESSURE FRAME

STATUS:
PROPOSED NEXT SURFACE AFTER CELL-002 COCKPIT INTEGRATION

PRIMARY LAW:

ADDRESS
!=
MESSAGE
!=
DURABLE TRANSPORT
!=
DELIVERY
!=
ACCEPTANCE
!=
WAKE
!=
AUTHORITY
!=
INVOCATION
!=
RESPONSE

# ==================================================
# EXISTING BASIS — DO NOT REPLACE
# ==================================================

Existing Cockpit function:

src/cockpit/observer/perceptual_instrument.mjs
buildAddressedChatPacket(...)

Existing packet:

schema:
cockpit_address_context_v0

fields:
addresses
runtime_state_sha256
repository_source_commit
repository_source_ref
authority_effect = NONE
semantic_claim_effect = NONE
transport_effect = NONE

This remains the addressing/context object.

DO NOT mutate it into a transport / authority object.

# ==================================================
# TOWN SQUARE ROLE
# ==================================================

TOWN SQUARE
=
DURABLE ADDRESSED MESSAGE DIRECTORY / TRANSPORT SURFACE

V0 lives in the repository / local runtime only.

It provides:

- immutable message identity;
- explicit source;
- one or more intended destination seats;
- creation timestamp;
- continuity / frame anchor when known;
- exact Cockpit address-context packet;
- message body;
- durable delivery records.

It does NOT:

- wake a seat by itself;
- authorize an invocation;
- advance a cursor;
- assert message acceptance;
- assert semantic integration;
- create execution authority.

# ==================================================
# MESSAGE OBJECT — MINIMUM V0
# ==================================================

A durable Town Square message should minimally preserve:

message_id

source:
  kind
  id

destinations:
  - kind: seat
    id: <seat_id>

created_at

frame_ref:
  optional continuity/event/frame anchor
  null when unresolved

address_context:
  exact cockpit_address_context_v0 packet

body:
  user / seat supplied message text or body ref

reply_to:
  optional message_id

authority_effect:
NONE_BY_MESSAGE

execution_effect:
NONE_BY_MESSAGE

wake_effect:
NONE_BY_MESSAGE

cursor_effect:
NONE_BY_MESSAGE

# ==================================================
# DESTINATION LAW
# ==================================================

V0 destinations are seats.

Cursor / campaign / request / artifact / pressure coordinates belong in:

address_context
and/or
frame_ref

They are contextual coordinates,
not independent chat recipients.

Therefore:

SEAT
=
recipient

CURSOR / CAMPAIGN / OBJECT COORDINATES
=
orientation / address context

# ==================================================
# DELIVERY RECEIPT — SEPARATE OBJECT
# ==================================================

For every destination seat, transport may append a distinct receipt:

delivery_id
message_id
destination_seat_id
delivered_at
delivery_state

Allowed V0 delivery states:

DELIVERED
DELIVERY_FAILED

Do NOT use delivery state to imply:

ACCEPTED
READ
INTEGRATED
WAKE_REQUESTED
WAKE_ADMITTED
INVOKED
RESPONDED

# ==================================================
# LATER DOWNSTREAM OBJECTS — NOT TOWN SQUARE V0
# ==================================================

Future distinct objects may include:

MESSAGE_ACCEPTANCE_RECEIPT

WAKE_REQUEST

WAKE_ADMISSION / DENIAL

AUTHORITY_ENVELOPE

INVOCATION_RECEIPT

RESPONSE_MESSAGE

These must remain separate transitions.

# ==================================================
# DIRECTORY VIEW
# ==================================================

Town Square Cockpit projection should show:

SOURCE
DESTINATION(S)
CREATED_AT
FRAME_REF
MESSAGE_ID
BODY / BODY_REF
ADDRESS CONTEXT
DELIVERY RECEIPTS

and visibly preserve:

SENT
!=
DELIVERED
!=
ACCEPTED
!=
WAKE
!=
INVOKED
!=
RESPONDED

# ==================================================
# CONCURRENCY PURPOSE
# ==================================================

Town Square should allow multiple seats to share one continuity surface
without requiring simultaneous model execution.

One immutable message may fan out into multiple destination-specific
delivery receipts.

Example:

MESSAGE M1
├── delivery -> SOLA
├── delivery -> LABBOIB
└── delivery -> CODEX

Each seat may later independently:

accept
defer
refuse
request wake
respond

No shared response or synchronized invocation is implied.

# ==================================================
# FIRST PRESSURES
# ==================================================

PRESSURE 1 — DELIVERY != WAKE

message delivered to seat
→ no wake object exists
→ invocation count remains zero

PRESSURE 2 — MULTI-DESTINATION INDEPENDENCE

one message
→ delivery succeeds for seat A
→ delivery fails for seat B

Viewer must preserve both independently.

PRESSURE 3 — CONTEXT DOES NOT GRANT AUTHORITY

address_context names an authority-bearing object
→ message authority_effect remains NONE_BY_MESSAGE
→ no authority envelope is created

PRESSURE 4 — CURSOR DOES NOT MOVE

message delivered with frame_ref / cursor context
→ destination cursor remains unchanged
until a separately admitted continuity-consumption transition occurs

# ==================================================
# FIRST COCKPIT VIEW
# ==================================================

Do not build a chat platform first.

First view:

one timeline / directory
of immutable messages + delivery receipts

with filters:

source
destination seat
frame / continuity anchor
campaign / addressed object

Clicking a message should reveal:

WHY WAS THIS ADDRESSED HERE?
WHAT WAS THE SOURCE FRAME?
WHO RECEIVED IT?
WHAT HAS NOT YET HAPPENED?

# ==================================================
# IMPLEMENTATION ORDER
# ==================================================

0. FINISH CELL-002 COMPOSED COCKPIT VISIBILITY.
1. MATERIALIZE one durable Town Square message object.
2. MATERIALIZE one destination-specific delivery receipt.
3. PROJECT both read-only in Cockpit.
4. PRESSURE DELIVERY != WAKE.
5. ONLY THEN add wake-request transport.
6. ONLY AFTER WAKE IS OBSERVABLE connect bounded invocation authority.

# ==================================================
# META-OBSERVABILITY TARGET
# ==================================================

Where a pressure is run, preserve enough witness that Cockpit can render:

TEST OBJECT
→ INTERVENTION
→ OBSERVATION
→ RESULTING STANDING

Test capture itself should be inspectable as an object with:

source
apparatus
intervention
witnesses
unobserved regions
claim ceiling

Do not infer that an unobserved internal transition occurred merely because
the test produced a terminal result.

PRESSURE OBSERVABILITY
SHOULD ITSELF BE PRESSUREABLE.
