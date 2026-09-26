# COCKPIT AUTHORITY CONTROLS V0

OBJECT_TYPE:
COCKPIT_AUTHORITY_CONTROL_SURFACE_SPEC

STATUS:
INITIAL IMPLEMENTATION TARGET

PRIMARY PURPOSE:

Make authority state legible and operator-manageable without
making Cockpit the trust root.

## Core projection

Cockpit must show, for each capability:

SUBJECT:
principal / seat / cursor / task owner

OBJECT:
capability / request / artifact / task association

AUTHORIZATION:
approval identity
operation / scope
use_limit
remaining_uses
status
executor / policy coordinates
expiry when later supported

HISTORY:
issuance
reservation
consumption receipts
denials
failures
current standing

CORRECTIVE:
corrective owner
available corrective requests
qualified / unqualified control dimensions

## Initial read-only card

CAPABILITY CARD:

capability_id
principal_id
task_id / campaign_id when present
operation
scope
granted uses
consumed uses
remaining uses
status

latest event
latest receipt
latest denial
current authority

executor hash
policy hash

ATOMICITY
PRINCIPAL_BINDING
REPLAY
CRASH_RECOVERY
CONCURRENCY
REVOCATION
CONTAINMENT

Each standing must be explicit:
QUALIFIED / PARTIAL / UNTESTED / NOT_ESTABLISHED

## Initial operator requests

Cockpit MAY submit typed requests for:

GRANT_ONE_SHOT
DENY_REQUEST
FREEZE_CAPABILITY
REVOKE_CAPABILITY
REDUCE_REMAINING_USES
REQUEST_FRESH_REVIEW
STOP_AFTER_CURRENT_STEP

But the trusted local authority membrane decides and records
the authoritative state transition.

COCKPIT BUTTON
!=
AUTHORITY STATE MUTATION

## Operator-only issuance rule V0

For now:

EVERY NEW AUTHORITY ENVELOPE
REQUIRES EXPLICIT HUMAN OPERATOR APPROVAL.

No non-human role / seat may self-authorize a fresh envelope.

Agents / seats / cursors MAY:

- formulate requests;
- create proposed authorization objects;
- attach requested scope / use count;
- attach task / campaign context;
- refuse work;
- request reduction / termination.

They MAY NOT:

- mint active authority;
- increase their own remaining authority;
- bypass the membrane;
- use Cockpit control endpoints.

## Future subject-object modulation

Cockpit is expected to become a subject-object authorization
requester / modulator / viewer.

Future objects MAY include:

task
campaign
artifact
request
capability
seat
cursor
result
receipt
warrant

Objects may be selected, paired, moved, attached, or related.

This is not required for V0 implementation.

## STOP semantics target

STOP_AFTER_CURRENT_STEP means:

- no new consequence admission;
- currently admitted indivisible step may finish if safe;
- emit early-termination / closure receipt;
- remaining authority becomes inactive / frozen or revoked
  according to the governing corrective rule;
- principal returns to inactive / sleeping standing when managed.

This behavior is NOT YET QUALIFIED.

## Legibility law

Cockpit must make visible:

WHAT MAY HAPPEN NOW?
WHAT JUST HAPPENED?
WHY WAS IT ALLOWED OR DENIED?
WHO / WHAT HELD THE AUTHORITY?
WHAT AUTHORITY REMAINS?
WHAT CAN STOP FURTHER PROPAGATION?
WHAT CONTROL DIMENSIONS ARE STILL UNPROVEN?
