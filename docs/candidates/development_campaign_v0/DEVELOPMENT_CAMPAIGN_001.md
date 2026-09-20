# DEVELOPMENT_CAMPAIGN_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

CAMPAIGN OUTPUT:
PROPOSAL / HORIZON ONLY

EXECUTION PACKET:
NOT CREATED

EXECUTION AUTHORITY:
NONE

SCHEDULING:
NONE

AUTOMATIC ADOPTION:
NONE
```

## Sole question

```text
CAN A DURABLE DEVELOPMENTAL HORIZON
GENERATE AND ACCUMULATE
BOUNDED EXECUTION-ENVELOPE REQUESTS

WITHOUT THE CAMPAIGN ITSELF
ACQUIRING EXECUTION AUTHORITY?
```

## Existing protocol relation

DME_Lab already has an `EXECUTION_PACKET_v0` handoff in
`docs/methods/TWINNING_PROTOCOL_v0.md`.

This candidate does not replace it.

```text
EXECUTION_ENVELOPE_REQUEST_v0
!=
EXECUTION_PACKET_v0
```

An envelope request is only a bounded proposal asking for a future executable
packet to be reviewed, selected, and explicitly authorized.

## Developmental horizon

A campaign retains:

```text
campaign_id
basis_refs
objective
claim_ceiling

target_objects[]
unresolved_relations[]
pressure_points[]
dependency_edges[]

proposal_allowance

completion_criteria[]
stop_conditions[]
explicit_non_authorizations[]
```

and is always emitted by `build_campaign()` as:

```text
status = CANDIDATE
authority_effect = NONE
execution_effect = NONE
adoption_effect = NONE
```

## Envelope-draft allowance

The campaign may describe a bounded proposal allowance:

```text
max_candidates
max_model_calls
allowed_resource_classes

external_effects = NONE
authority_effect = NONE
```

This answers:

```text
NO EXECUTION ENVELOPE
!=
NO MOVEMENT
```

because a seat may still produce a small number of candidate ways to ask for
future authority.

But:

```text
ENVELOPE REQUEST
!=
EXECUTION ENVELOPE

CANDIDATE REQUEST
!=
AUTHORIZED EXECUTION PACKET

HUMAN SELECTION
!=
EXECUTION AUTHORIZATION

EXECUTION AUTHORIZATION
!=
EXECUTION OCCURRED
```

## Required request coordinates

Each `EXECUTION_ENVELOPE_REQUEST_v0` names:

```text
object / claim under pressure
unresolved relation
smallest proposed intervention
expected observable
allowed effect surface
forbidden effects
required authority
resource cost
expected information gain
stop conditions
```

The request carries:

```text
packet_status = CANDIDATE_REQUEST
authorization_effect = NONE
execution_effect = NONE
```

## Chipping away

Campaign progress is not inferred from task completion.

The campaign store accepts only explicit
`CAMPAIGN_STANDING_UPDATE_v0` records with an external `adjudication_ref`.

```text
TASK EXECUTED
!=
CAMPAIGN RELATION RESOLVED

ALL PLANNED TASKS DONE
!=
CAMPAIGN COMPLETE

CAMPAIGN RELATION RESOLVED
!=
EVERY PLANNED TASK EXECUTED
```

A campaign snapshot is a derived projection over:

```text
fixed campaign packet
+
explicit standing updates
+
lodged candidate envelope requests
+
non-standing execution receipts
```

The campaign store does not adjudicate evidence itself.

## Pressure cells

```text
C1 BUILD / POST
   build_campaign() creates fixed CANDIDATE horizon
   post_campaign() retains exact bytes
   → no authority / execution / adoption effect

C2 MULTI-SEAT REQUESTS
   LABBOIB and COMMANDER lodge different requests
   against one unresolved relation
   → both survive
   → one object does not imply one next experiment

C3 DRAFT ALLOWANCE
   no request exists for an open relation
   deterministic draft generation may create <= max_candidates
   → generated requests remain candidate-only
   → no execution packet produced

C4 REQUEST IS NOT PACKET
   candidate request includes required_authority
   → authorization_effect NONE
   → no EXECUTION_PACKET_v0 materialized

C5 TASK RECEIPT DOES NOT CLOSE RELATION
   execution receipt says COMPLETED
   → relation remains OPEN
   until external standing update exists

C6 RESOLUTION CAN INVALIDATE PLANNED WORK
   external adjudication marks relation FRACTURED
   → relation leaves open frontier
   → previously drafted requests remain historical proposals
   → no need to execute all planned requests

C7 CAMPAIGN RESOLUTION IS CLAIM-DRIVEN
   all relations externally EARNED/FRACTURED
   → derived campaign frontier RESOLVED
   even if some candidate requests were never executed

C8 BASIS DRIFT
   campaign packet basis remains fixed
   current basis differs
   → snapshot = STALE
   → campaign bytes unchanged

C9 IDEMPOTENT REQUEST IDENTITY
   same request_id + same bytes replay
   → one durable request
   same request_id + different bytes
   → reject
```

## Claim ceiling

A passing candidate may support only that the tested campaign store can retain
one fixed developmental horizon, accept multiple proposal-only execution
envelope requests under a bounded allowance, derive an open frontier from
explicit standing updates, and avoid converting requests, task receipts, or
campaign completion into execution authority.

It does not establish:

```text
general autonomous research planning
automatic campaign adoption
automatic pressure selection
automatic execution authorization
scheduler correctness
general priority optimization
general model-routing policy
scientific adjudication by the campaign store
```
