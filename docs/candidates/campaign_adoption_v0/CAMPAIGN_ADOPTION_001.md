# CAMPAIGN_ADOPTION_001

## STATUS

```text
FROZEN SEMANTIC CONTRACT — CORRECTED CONTINUITY SEMANTICS
IMPLEMENTATION:
AUTHORIZED BY HUMAN GESTURE, BUT MUST QUALIFY BEFORE USE

DOGFOOD_001 RETRY:
HELD UNTIL ADOPTION IS DURABLY MATERIALIZED

COS-R2:
UNCHANGED
```

## Qualified prerequisites

This contract sits after:

```text
CAMPAIGN_BASIS_REVALIDATION_001
→ basis-relative warrant

CAMPAIGN_APPLICABILITY_PROJECTION_001
→ operationally visible current applicability
```

The adoption membrane does not revalidate, reinterpret, or weaken either relation.

## Sole question

```text
CAN REED EXPLICITLY DECLARE
ONE EXACT CAMPAIGN ADOPTED

AS AN UNRELEASED DEVELOPMENTAL COMMITMENT

SUCH THAT CURRENT LIVE STATUS IS DERIVED FROM:

UNRELEASED ADOPTION
×
CURRENT EFFECTIVE APPLICABILITY

WITHOUT:

REWRITING CAMPAIGN HISTORY
REVALIDATING THE CAMPAIGN
SELECTING ANY REQUEST
ASSIGNING ANY SEAT
CREATING PRIORITY
GRANTING AUTHORITY
CHANGING SCIENTIFIC STANDING
SCHEDULING
WAKING
OR EXECUTING ANYTHING?
```

## Governing distinctions

```text
ADOPTION
!=
A BOOLEAN ON THE CAMPAIGN

APPLICABLE
!=
ADOPTED

ADOPTED
!=
CURRENTLY LIVE

UNRELEASED ADOPTION
!=
CURRENT INTERNAL HUMAN DESIRE

HISTORICAL HUMAN DECLARATION
!=
MODEL INFERENCE ABOUT PRESENT INTENT

ADOPTED
!=
EXCLUSIVE

ADOPTED
!=
PRIORITIZED

ADOPTED
!=
SELECTED REQUEST

ADOPTED
!=
EXECUTION AUTHORITY

ADOPTION HISTORY
!=
CURRENT ADOPTION STATE

ADOPTION_RELEASED
!=
CAMPAIGN FRACTURED

ADOPTION_RELEASED
!=
CAMPAIGN OBSOLETE

CAMPAIGN CURRENTLY APPLICABLE
!=
CAMPAIGN CURRENTLY LIVE

MULTIPLE LIVE CAMPAIGNS
!=
PRIORITY ORDER

ADOPTION ORDER
!=
DEVELOPMENTAL PRIORITY

CURRENT APPLICABILITY LOST
!=
ADOPTION RELEASED

CURRENT APPLICABILITY RESTORED
!=
NEW ADOPTION REQUIRED
```

## Adoption is a durable human declaration

The historical campaign object remains immutable.

The adoption relation records only:

```text
REED DECLARED:
this exact campaign is adopted

UNTIL:
an exact release event ends that declaration
```

Conceptual target object:

```text
CAMPAIGN_ADOPTION_v0

adoption_id

campaign_id
campaign_sha256

actor_id = REED

adoption_kind:
    ADOPTED
    ADOPTION_RELEASED

target_adoption_id
target_adoption_sha256

gesture_ref
reason

adoption_effect:
    DECLARES_DEVELOPMENTAL_COMMITMENT
    or
    RELEASES_DEVELOPMENTAL_COMMITMENT

selection_effect = NONE
assignment_effect = NONE
priority_effect = NONE
standing_effect = NONE
authority_effect = NONE
scheduler_effect = NONE
wake_effect = NONE
execution_effect = NONE
```

For `ADOPTED`:

```text
target_adoption_id = null
target_adoption_sha256 = null
```

For `ADOPTION_RELEASED`:

```text
target_adoption_id
target_adoption_sha256

MUST bind one exact prior ADOPTED event
for the same exact campaign identity.
```

Scar:

```text
RELEASE CAMPAIGN LABEL
!=
RELEASE EXACT ADOPTION RELATION
```

## Adoption does not contain applicability

The adoption event MUST NOT embed or freeze:

```text
revalidation_id
revalidation_sha256
current_basis_refs
current_basis_sha256
effective_applicability
```

as the condition that defines continuing human commitment.

Those belong to the applicability membrane.

Scar:

```text
ADOPTION DECLARATION
!=
APPLICABILITY WARRANT
```

A human may adopt only when the campaign is currently applicable at the time of
the adoption gesture, but the durable declaration itself remains a separate
historical relation after the world moves.

## Admission rule for a new ADOPTED event

A new adoption event is admitted only when the operating projection establishes:

```text
exact campaign identity

AND

effective_applicability ∈ {
    CURRENT_BY_HISTORICAL_BASIS,
    CURRENT_BY_REVALIDATION
}
```

at the exact gesture-time basis.

This is an admission precondition, not a field that turns adoption into a
basis-bound object.

The admission receipt SHOULD retain a raw reference to the applicability
projection/evidence inspected for audit, but that reference does not redefine
the identity or lifetime of the human declaration.

## Current live developmental contract is derived

No campaign field such as:

```text
campaign["adopted"] = true
campaign["live"] = true
```

is permitted.

Two projections remain independent:

```text
CURRENT_ADOPTION_STATE(C)

requires:

one or more valid ADOPTED events for exact C
minus exact valid releases
```

and:

```text
LIVE_DEVELOPMENTAL_CONTRACT(C, B)

requires:

CURRENT_ADOPTION_STATE(C) = ADOPTED
+
EFFECTIVE_APPLICABILITY(C, B) is current
```

Therefore:

```text
B2:
campaign applicable
A1 unreleased
→ LIVE
```

If world moves to B3 and applicability is not established:

```text
A1:
STILL UNRELEASED ADOPTION

effective applicability:
NOT_CURRENT

→ NOT LIVE / BLOCKED
```

If a later revalidation establishes current applicability at B3:

```text
A1:
STILL UNRELEASED

effective applicability:
CURRENT_BY_REVALIDATION

→ LIVE AGAIN
```

without inventing a second human declaration.

This preserves:

```text
CURRENT APPLICABILITY LOST
!=
HUMAN WITHDREW COMMITMENT
```

and:

```text
CURRENT APPLICABILITY RESTORED
!=
HUMAN RE-ADOPTED
```

## Explicit human gesture

The first tested actor is:

```text
REED
```

This contract does not establish general human identity authentication.

The apparatus must preserve enough raw gesture provenance to distinguish:

```text
EXPLICIT HUMAN ADOPTION GESTURE
!=
SYSTEM INFERENCE THAT REED PROBABLY WANTS IT
```

No scheduler, model, seat, campaign, revalidation result, projection, or UI order
may self-adopt.

The user statement authorizing:

```text
COCKPIT_OPERATING_SPACE_001
```

is sufficient human intent to attempt materialization once this membrane is
mechanically qualified and exact current applicability is established.

## Coexisting campaigns

More than one exact campaign may be adopted/live simultaneously.

Projection order, insertion order, event order, row order, and UI order must
not create priority.

```text
C1 ADOPTED
+
C2 ADOPTED

!=
C1 > C2
!=
C2 > C1
```

## Claim ceiling

A passing implementation may establish only:

```text
ONE EXACT CURRENTLY-APPLICABLE CAMPAIGN

CAN RECEIVE ONE EXPLICIT,
DURABLE HUMAN ADOPTION DECLARATION

WHOSE UNRELEASED STATE PERSISTS
INDEPENDENTLY OF LATER BASIS DRIFT,

WHILE CURRENT LIVE STATUS REMAINS
THE PRODUCT OF:

UNRELEASED ADOPTION
×
CURRENT EFFECTIVE APPLICABILITY

WITHOUT CREATING:

REQUEST SELECTION
ASSIGNMENT
PRIORITY
STANDING CHANGE
AUTHORITY
SCHEDULER ACTION
WAKE
OR EXECUTION
```

## Nonclaims

This contract does not establish:

```text
automatic campaign activation without human adoption
automatic applicability
priority among live campaigns
exclusive campaign ownership
request selection
assignment
wake policy
scheduler safety
execution authority
scientific standing
semantic equivalence
general human identity authentication
DOGFOOD_001 completion
```

## Experimental discipline

Dogfood target remains:

```text
COCKPIT_OPERATING_SPACE_001
COS-R2
HUMAN_READABLE_ASSIGNMENT_DISPLAY != QUEUE_SEMANTICS
```

Only the missing human-intent relation is repaired here.

## Continuity stack retained

```text
HISTORY
→ what existed

REVALIDATION
→ does it still apply here?

APPLICABILITY PROJECTION
→ is that warrant current here?

ADOPTION
→ has Reed declared this campaign adopted and not released it?

SELECTION
→ what is Reed focusing on?

ASSIGNMENT
→ who holds one bounded unit?

WAKE
→ who gets one opportunity now?

EXECUTION
→ what actually happened?
```

None may impersonate its neighbor.
