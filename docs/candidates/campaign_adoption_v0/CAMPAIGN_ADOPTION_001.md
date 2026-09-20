# CAMPAIGN_ADOPTION_001

## STATUS

```text
FROZEN SEMANTIC CONTRACT
PRESSURE-DESIGN AUTHORIZED
IMPLEMENTATION:
NOT AUTHORIZED BY THIS CONTRACT

DOGFOOD_001 RETRY:
HELD

COS-R2:
UNCHANGED

SYMBOLIC MEMORY:
OUTSIDE THIS MEMBRANE
```

## Qualified prerequisite

This contract is stacked on the reported qualified result of:

```text
CAMPAIGN_BASIS_REVALIDATION_001
```

at:

```text
campaign-basis-revalidation-v0
85414790834bf25446477514165403e7d34829e4
```

The prerequisite relation is:

```text
ONE EXACT HISTORICAL CAMPAIGN
CAN RECEIVE ONE BASIS-RELATIVE
CURRENTLY_APPLICABLE JUDGMENT
AGAINST ONE EXACT CURRENT BASIS

WITHOUT ADOPTION OR OTHER DOWNSTREAM CONTROL EFFECTS
```

This contract does not broaden that claim.

## Sole question

```text
CAN REED EXPLICITLY ADOPT
ONE EXACT CURRENTLY-APPLICABLE CAMPAIGN

AS A LIVE DEVELOPMENTAL CONTRACT

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

HISTORICAL HUMAN INTENT
!=
CURRENT HUMAN INTENT

ADOPTED AT B2
!=
HUMAN INTENT AUTOMATICALLY VALID AT B3

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
```

## Adoption is a durable relation

The historical campaign object remains immutable.

A valid adoption binds:

```text
exact campaign identity
+
exact successful applicability judgment
+
exact basis on which that judgment is current
+
explicit human adoption gesture
```

It must not mutate the historical campaign or the revalidation result.

Conceptual target object:

```text
CAMPAIGN_ADOPTION_v0

adoption_id

campaign_id
campaign_sha256

revalidation_id
revalidation_sha256

actor_id = REED

adoption_basis_refs
adoption_basis_sha256

adoption_kind:
    ADOPTED
    ADOPTION_RELEASED

target_adoption_id
target_adoption_sha256

reason

adoption_effect:
    LIVE_DEVELOPMENTAL_CONTRACT
    or
    RELEASES_LIVE_DEVELOPMENTAL_CONTRACT

selection_effect = NONE
assignment_effect = NONE
priority_effect = NONE
standing_effect = NONE
authority_effect = NONE
scheduler_effect = NONE
wake_effect = NONE
execution_effect = NONE
```

This shape is a semantic contract target, not implementation authorization.

For `ADOPTED` events:

```text
target_adoption_id = null
target_adoption_sha256 = null
```

For `ADOPTION_RELEASED` events:

```text
target_adoption_id
target_adoption_sha256

MUST bind one exact prior ADOPTED event
```

Scar:

```text
RELEASE CAMPAIGN LABEL
!=
RELEASE EXACT ADOPTION RELATION
```

## Exact applicability binding

Adoption must bind the exact durable revalidation object, not merely the campaign label.

A valid adoption requires:

```text
adoption.campaign_sha256
=
revalidation.campaign_sha256

AND

adoption.revalidation_sha256
=
exact durable revalidation object identity

AND

revalidation.disposition
=
CURRENTLY_APPLICABLE

AND

adoption.adoption_basis_sha256
=
revalidation.candidate_current_basis_sha256
```

No adoption is admitted against:

```text
NOT_APPLICABLE
INSUFFICIENT_BASIS
NOT_ESTABLISHED
stale / non-current revalidation basis
wrong campaign identity
wrong revalidation identity
```

## Current live developmental contract is derived

No campaign field such as:

```text
campaign["adopted"] = true
campaign["live"] = true
```

is permitted.

Current live state is a projection over preserved history.

At minimum:

```text
LIVE_DEVELOPMENTAL_CONTRACT(C, B)

requires:

valid exact campaign C
+
valid CURRENTLY_APPLICABLE revalidation R for exact basis B
+
valid ADOPTED event A bound to C + R + B
+
no valid ADOPTION_RELEASED event targeting A
```

Therefore:

```text
WORLD B2
+
R1 CURRENTLY_APPLICABLE @ B2
+
A1 ADOPTED against R1

→ LIVE @ B2
```

but:

```text
WORLD MOVES TO B3

R1:
historical applicability at B2

A1:
historical adoption at B2

CURRENT LIVE CONTRACT @ B3:
NOT_ESTABLISHED
```

A later:

```text
R2 CURRENTLY_APPLICABLE @ B3
```

does not transfer A1.

Scar:

```text
NEW REVALIDATION
!=
RENEWED HUMAN INTENT
```

## Explicit human gesture

The v0 question is scoped only to an explicit human adoption by:

```text
REED
```

This contract does not claim a general identity-authentication system.

The apparatus must preserve enough raw adoption input / confirmation evidence to distinguish:

```text
EXPLICIT HUMAN ADOPTION GESTURE
!=
SYSTEM INFERENCE THAT REED PROBABLY STILL WANTS IT
```

No scheduler, model, seat, campaign object, or revalidation result may self-adopt.

## Coexisting live campaigns

More than one exact campaign may be live simultaneously.

Projection order, insertion order, event order, row order, and UI order must not create priority.

```text
C1 LIVE
+
C2 LIVE

!=
C1 > C2
!=
C2 > C1
```

Any future prioritization relation is outside this membrane.

## Claim ceiling

A passing implementation may establish only:

```text
ONE EXACT CURRENTLY-APPLICABLE CAMPAIGN

CAN BE EXPLICITLY ADOPTED BY REED

AS ONE BASIS-RELATIVE LIVE DEVELOPMENTAL CONTRACT

WITH DURABLE ADOPTION / RELEASE HISTORY

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
automatic campaign activation
automatic re-adoption after revalidation
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

The dogfood target remains unchanged:

```text
COCKPIT_OPERATING_SPACE_001
COS-R2
HUMAN_READABLE_ASSIGNMENT_DISPLAY != QUEUE_SEMANTICS
```

The intended causal sequence remains:

```text
DOGFOOD_001
↓
BLOCKED AT APPLICABILITY

CAMPAIGN_BASIS_REVALIDATION_001
↓
QUALIFIED CURRENT APPLICABILITY

CAMPAIGN_ADOPTION_001
↓
EXPLICIT CURRENT HUMAN INTENT

DOGFOOD_001 RETRY
↓
SAME COS-R2 TARGET
```

No change to COS-R2 is authorized by this contract.

## Continuity stack retained

```text
HISTORY
→ what existed

REVALIDATION
→ does it still apply here?

ADOPTION
→ does Reed still want it live here?

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
