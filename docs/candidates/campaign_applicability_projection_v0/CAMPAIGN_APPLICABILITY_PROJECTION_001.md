# CAMPAIGN_APPLICABILITY_PROJECTION_001

## STATUS

```text
FROZEN SEMANTIC CONTRACT
PRESSURE-DESIGN AUTHORIZED
IMPLEMENTATION:
NOT AUTHORIZED BY THIS CONTRACT

CAMPAIGN_ADOPTION_001:
FROZEN NEIGHBOR
IMPLEMENTATION HELD

DOGFOOD_001 RETRY:
HELD

COS-R2:
UNCHANGED
```

## Origin

The first real Cockpit dogfood attempt stopped because:

```text
CampaignStore.snapshot()
→ basis_status = STALE

SelectionStore.projection()
→ request_applicability = STALE
→ preparation = BLOCKED_PENDING_REVALIDATION
```

CAMPAIGN_BASIS_REVALIDATION_001 subsequently qualified one separate durable,
basis-relative warrant:

```text
historical campaign
+
traceably grounded requirements
+
raw current evidence
→
CURRENTLY_APPLICABLE @ exact basis B
```

However the existing operational applicability path still reads only the
historical campaign basis status.

Observed seam:

```text
REVALIDATION WARRANT EXISTS
!=
OPERATING PATH CONSUMES REVALIDATION WARRANT
```

## Sole question

```text
CAN ONE VALID BASIS-RELATIVE
CAMPAIGN REVALIDATION

BE CONSUMED BY THE EXISTING
OPERATIONAL APPLICABILITY PATH

SO THAT THE EXACT CAMPAIGN
IS TREATED AS CURRENTLY APPLICABLE
AT THE EXACT CURRENT BASIS

WITHOUT:

REWRITING CAMPAIGN HISTORY
WEAKENING HISTORICAL BASIS STATUS
ADOPTING THE CAMPAIGN
SELECTING ANYTHING
ASSIGNING ANY SEAT
CREATING PRIORITY
CHANGING STANDING
GRANTING AUTHORITY
SCHEDULING
WAKING
OR EXECUTING ANYTHING?
```

## Governing distinctions

```text
HISTORICAL BASIS STATUS
!=
EFFECTIVE CURRENT APPLICABILITY

REVALIDATION WARRANT EXISTS
!=
THIS OPERATING PATH CONSUMES IT

REVALIDATION STORE CONTAINS WARRANT
!=
THIS EXACT WARRANT APPLIES HERE NOW

HISTORY DID NOT BECOME CURRENT
!=
A CURRENT-WORLD RELATION BECAME WARRANTED

STALE HISTORICAL BASIS
!=
CURRENTLY INAPPLICABLE FOREVER

CURRENT_BY_REVALIDATION
!=
HISTORICAL BASIS CURRENT

CURRENTLY APPLICABLE
!=
ADOPTED

CURRENTLY APPLICABLE
!=
SELECTED

CURRENTLY APPLICABLE
!=
AUTHORIZED

CURRENTLY APPLICABLE
!=
LIVE DEVELOPMENTAL CONTRACT
```

## Historical truth remains unchanged

The existing historical projection remains authoritative about the campaign's
recorded basis relation:

```text
CampaignStore.snapshot(...)

basis_status:
CURRENT | STALE
```

If:

```text
current_basis_refs != campaign["basis_refs"]
```

then:

```text
historical basis_status:
STALE
```

must remain true.

This membrane MUST NOT repair applicability by changing that result to CURRENT.

Scar:

```text
HISTORY DID NOT BECOME CURRENT.

A WARRANTED CURRENT-WORLD RELATION
BECAME OPERATIONALLY VISIBLE.
```

## Projection target

The bounded projection should expose three independent coordinates:

```text
CAMPAIGN_APPLICABILITY_PROJECTION_v0

campaign_id
campaign_sha256

queried_current_basis_refs
queried_current_basis_sha256

historical_basis_status:
    CURRENT
    STALE

revalidation_status:
    NONE
    CURRENTLY_APPLICABLE
    NOT_APPLICABLE
    INSUFFICIENT_BASIS
    STALE_REVALIDATION

effective_applicability:
    CURRENT_BY_HISTORICAL_BASIS
    CURRENT_BY_REVALIDATION
    NOT_CURRENT

revalidation_id
revalidation_sha256

authority_effect = NONE
adoption_effect = NONE
selection_effect = NONE
assignment_effect = NONE
priority_effect = NONE
standing_effect = NONE
scheduler_effect = NONE
wake_effect = NONE
execution_effect = NONE
```

This is a semantic target, not implementation authorization.

## Effective applicability derivation

The projection must derive:

```text
CURRENT_BY_HISTORICAL_BASIS
```

only when:

```text
CampaignStore.snapshot(...).basis_status == CURRENT
```

It may derive:

```text
CURRENT_BY_REVALIDATION
```

only when an exact durable revalidation exists such that:

```text
revalidation.campaign_sha256
=
exact campaign identity

AND

revalidation.candidate_current_basis_sha256
=
exact queried current basis identity

AND

revalidation.disposition
=
CURRENTLY_APPLICABLE
```

Otherwise:

```text
effective_applicability:
NOT_CURRENT
```

A revalidation against B2 MUST NOT make the campaign effectively current at B3.

## Exact warrant identity

The revalidation store already exposes basis-relative current applicability.

The operational projection must nevertheless remain able to identify the exact
durable warrant it consumed.

At minimum it must expose:

```text
revalidation_id
revalidation_sha256
```

for the warrant used to derive CURRENT_BY_REVALIDATION.

Scar:

```text
REVALIDATION LABEL
!=
DURABLE REVALIDATION IDENTITY
```

Storage metadata such as `_seq` must not enter the warrant identity.

If more than one exact CURRENTLY_APPLICABLE warrant exists for the same campaign
and exact basis, projection order MUST NOT create priority. The projection may
expose all matching warrants or deterministically select one by a declared
non-semantic rule, but that choice must not create authority, recency preference,
or developmental priority.

## Operational consumption

The existing selection projection currently overloads historical basis status:

```text
basis_status == CURRENT
→ request_applicability CURRENT

basis_status == STALE
→ request_applicability STALE
→ BLOCKED_PENDING_REVALIDATION
```

The smallest intended integration is:

```text
SelectionStore.projection(...)
consumes effective_applicability

NOT merely historical basis_status
```

Thus:

```text
historical basis:
STALE

valid exact revalidation:
CURRENTLY_APPLICABLE @ B2

effective applicability:
CURRENT_BY_REVALIDATION

existing selected OPEN request:
request_applicability:
CURRENT_BY_REVALIDATION

preparation:
ELIGIBLE_FOR_PACKET_PREPARATION
```

while:

```text
CampaignStore.snapshot(...).basis_status
remains:
STALE
```

This contract does NOT authorize creating a selection event. Qualification may
use fixture selection history only to test projection behavior.

## Revalidation failure states remain legible

If the latest or inspected revalidation evidence is:

```text
NOT_APPLICABLE
INSUFFICIENT_BASIS
or
for a different exact basis
```

the projection must not silently convert the campaign to current.

At minimum:

```text
effective_applicability:
NOT_CURRENT
```

and the exact reason must remain inspectable.

A historical CURRENTLY_APPLICABLE warrant for another basis is:

```text
STALE_REVALIDATION
```

relative to the queried basis.

## No adoption smuggling

This membrane stops at applicability.

A successful projection may establish:

```text
effective_applicability:
CURRENT_BY_REVALIDATION
```

while all of the following remain:

```text
adoption:
NONE

live developmental contract:
NOT_ESTABLISHED

selection creation:
NONE

assignment:
NONE

priority:
NONE

standing effect:
NONE

authority effect:
NONE

scheduler effect:
NONE

wake effect:
NONE

execution effect:
NONE
```

CAMPAIGN_ADOPTION_001 remains a separate neighboring membrane.

## Claim ceiling

A passing implementation may establish only:

```text
ONE EXACT BASIS-RELATIVE
CURRENTLY_APPLICABLE REVALIDATION

CAN BE MADE OPERATIONALLY LEGIBLE
TO THE EXISTING CAMPAIGN / REQUEST
APPLICABILITY PATH

FOR THE SAME EXACT CAMPAIGN
AND THE SAME EXACT CURRENT BASIS

WITHOUT REWRITING HISTORICAL
CAMPAIGN BASIS STATUS OR CREATING
DOWNSTREAM CONTROL EFFECTS.
```

## Nonclaims

This contract does not establish:

```text
campaign adoption
live developmental intent
automatic request selection
assignment
priority
authority
standing
scheduler behavior
wake policy
execution
semantic equivalence
general dependency analysis
automatic dogfood continuation
```

## Experimental discipline

The dogfood target remains:

```text
COCKPIT_OPERATING_SPACE_001
COS-R2
HUMAN_READABLE_ASSIGNMENT_DISPLAY != QUEUE_SEMANTICS
```

No change to COS-R2 is authorized.

The causal chain remains:

```text
DOGFOOD_001
↓
basis fracture

CAMPAIGN_BASIS_REVALIDATION_001
↓
warrant earned

CAMPAIGN_APPLICABILITY_PROJECTION_001
↓
warrant becomes operationally legible

CAMPAIGN_ADOPTION_001
↓
declared human commitment

SAME DOGFOOD_001
↓
next rake
```
