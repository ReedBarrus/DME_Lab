# CAMPAIGN_APPLICABILITY_PROJECTION_001 — QUALIFICATION 001

## Status

```text
MECHANICALLY QUALIFIED
IN THE TESTED SCOPE

DOGFOOD_001:
NOT RETRIED

CAMPAIGN_ADOPTION_001:
NOT IMPLEMENTED

MERGE:
NOT AUTHORIZED
```

## Frozen contract basis

```text
contract branch:
campaign-applicability-projection-contract-v0

contract head:
544f5409173a2bd16380cbe22d31c339b9587070

implementation branch:
campaign-applicability-projection-v0

qualification implementation head:
7f9c7a67a355a9eaa100e03249b5590bee6a4430
```

The frozen contract documents were not modified by the implementation work.

## Qualified artifact identities

```text
tools/campaign_applicability_projection_v0.py
blob:
b1463ada90ffff799166b03f81e83d2fdb760ed3

tools/envelope_selection_v0.py
blob:
17363e4915c96bcaf03ae3c721bc62e1271fe47f

src/cockpit/control_adapter.py
blob:
a10d41d488df85f94ee84ec80c6f28bb4d211e63

tests/runtime/test_campaign_applicability_projection.py
blob:
462fb11c1616bff50e7804cc1d635e2c1db697b7

.github/workflows/campaign-applicability-projection-001.yml
blob:
b1e13d95d85007eacdb2d865760646d3e5e70893
```

## Execution evidence

Dedicated workflow:

```text
CAMPAIGN_APPLICABILITY_PROJECTION_001

run:
35513699921

job:
106085939233

result:
SUCCESS
```

Independent PR-triggered neighboring workflows on the same implementation head:

```text
ENVELOPE_SELECTION_001
run 35513699925
SUCCESS

COCKPIT_CONTROL_ADAPTER_001
run 35513699919
SUCCESS
```

The dedicated run executed:

```text
compile:
SUCCESS

focused applicability pressure:
20 / 20 PASS

campaign basis revalidation regression:
17 / 17 PASS

envelope selection regression:
10 / 10 PASS

preparation regression:
10 / 10 PASS

preparation assignment regression:
12 / 12 PASS

wake source regression:
10 / 10 PASS

bounded reentry regression:
10 / 10 PASS

cockpit control adapter regression:
12 / 12 PASS
```

## Qualified composition

The qualified membrane composes:

```text
CampaignStore.snapshot()
historical basis truth

+

CampaignBasisRevalidationStore
durable basis-relative warrants

↓

CampaignApplicabilityProjector
read-only effective applicability

↓

SelectionStore.projection()
preparation gating
```

The existing historical snapshot remains unchanged.

For a campaign whose historical basis differs from the queried basis:

```text
CampaignStore.snapshot().basis_status
=
STALE
```

may coexist with:

```text
revalidation_status
=
CURRENTLY_APPLICABLE

effective_applicability
=
CURRENT_BY_REVALIDATION
```

Therefore:

```text
HISTORICAL BASIS STATUS
!=
EFFECTIVE CURRENT APPLICABILITY
```

## Focused pressure result

### P1

Exact historical basis, no revalidation:

```text
historical_basis_status = CURRENT
revalidation_status = NONE
effective_applicability = CURRENT_BY_HISTORICAL_BASIS

PASS
```

### P2

Historical basis stale plus exact valid revalidation:

```text
historical_basis_status = STALE
revalidation_status = CURRENTLY_APPLICABLE
effective_applicability = CURRENT_BY_REVALIDATION

CampaignStore basis_status remains STALE

PASS
```

### P3

Valid warrant at B2 queried at B3:

```text
revalidation_status = STALE_REVALIDATION
effective_applicability = NOT_CURRENT

PASS
```

### P4

Same campaign label with different exact campaign bytes:

```text
wrong campaign identity does not transfer
effective_applicability = NOT_CURRENT
invalid warrant identity remains diagnostic

PASS
```

### P5

Exact campaign/basis with revalidation disposition:

```text
INSUFFICIENT_BASIS
→ NOT_CURRENT

PASS
```

### P6

Exact campaign/basis with revalidation disposition:

```text
NOT_APPLICABLE
→ NOT_CURRENT

PASS
```

### P7

Existing selected OPEN request plus exact valid warrant:

```text
request_applicability
=
CURRENT_BY_REVALIDATION

preparation
=
ELIGIBLE_FOR_PACKET_PREPARATION

new selection event:
NONE

PASS
```

### P8

Existing selected request plus stale warrant:

```text
request_applicability
=
STALE

preparation
=
BLOCKED_PENDING_REVALIDATION

PASS
```

### P9

Projection is read-only:

```text
campaign bytes:
UNCHANGED

historical snapshot:
UNCHANGED

historical basis_status:
STALE

PASS
```

### P10

Valid warrant has no neighboring effects:

```text
adoption NONE
selection effect NONE
assignment effect NONE
priority NONE
standing NONE
authority NONE
scheduler NONE
wake NONE
execution NONE

live developmental contract:
NOT_ESTABLISHED

PASS
```

### P11

Exact durable warrant identity is exposed:

```text
revalidation_id
+
revalidation_sha256

storage _seq:
excluded from durable identity

PASS
```

### P12

Multiple matching CURRENTLY_APPLICABLE warrants:

```text
effective applicability:
CURRENT_BY_REVALIDATION

all exact warrant identities exposed

representative selection rule:
LEXICOGRAPHIC_DURABLE_IDENTITY_NON_SEMANTIC

priority effect:
NONE

PASS
```

## Additional adversarial result

### X1

Caller attempts to supply an effective-applicability verdict:

```text
projection API does not admit the field

PASS
```

### X2

Stored result JSON is changed while the retained result SHA is not:

```text
warrant identity validation fails
effective applicability remains NOT_CURRENT

PASS
```

This mechanically preserves:

```text
REVALIDATION LABEL
!=
DURABLE REVALIDATION IDENTITY
```

### X3

Visually similar but different exact basis:

```text
no exact warrant match
NOT_CURRENT

PASS
```

### X4

Historical basis is CURRENT while stale old warrants exist:

```text
CURRENT_BY_HISTORICAL_BASIS

old warrants do not override historical truth

PASS
```

### X5

Revalidation source unavailable:

```text
revalidation_status = UNAVAILABLE
effective_applicability = NOT_CURRENT
diagnostic retained

PASS
```

### X6

Projection-side writes:

```text
campaign store:
UNCHANGED

revalidation store:
UNCHANGED

selection store:
UNCHANGED

preparation store:
UNCHANGED

assignment store:
UNCHANGED

wake store:
UNCHANGED

reentry store:
UNCHANGED

controller marker store:
UNCHANGED

PASS
```

### X7

Current applicability plus non-OPEN standing:

```text
FRACTURED
→ BLOCKED_OBSOLETE

EARNED
→ BLOCKED_RESOLVED

PASS
```

Therefore:

```text
APPLICABILITY
!=
DEVELOPMENTAL RELEVANCE
```

### X8

Effective current applicability:

```text
CURRENT_BY_REVALIDATION

live developmental contract:
NOT_ESTABLISHED

adoption effect:
NONE

PASS
```

## Operational wiring

The Cockpit control adapter now accepts an optional dedicated revalidation-store
source and, when configured, constructs the same read-only applicability
projector used by SelectionStore.

This adds no direct controller-store dependency and creates no selection,
assignment, bell, wake, standing, authority, scheduler, adoption, or execution
effect.

If no revalidation source is configured, existing historical-basis behavior
remains available.

## Failures encountered during qualification work

Two test-harness failures occurred before the successful qualification run.

### Failure 1

The revalidation request was initially given a decoded Python campaign object.

Observed apparatus response:

```text
campaign_bytes must be exact UTF-8 text
```

Scar retained:

```text
CAMPAIGN OBJECT
!=
CAMPAIGN BYTES
```

### Failure 2

The fixture then supplied the characters backslash+n after the JSON object
rather than an actual newline.

Observed apparatus response:

```text
JSONDecodeError:
Extra data
```

The fixture was repaired to provide actual valid UTF-8 JSON text.

No production semantic contract was changed to make either test pass.

## Claim ceiling

Qualification supports only:

```text
ONE EXACT BASIS-RELATIVE
CURRENTLY_APPLICABLE REVALIDATION

CAN BE MADE OPERATIONALLY LEGIBLE
TO THE EXISTING CAMPAIGN / REQUEST
APPLICABILITY PATH

FOR THE SAME EXACT CAMPAIGN
AND SAME EXACT CURRENT BASIS

WITHOUT FALSIFYING HISTORICAL
BASIS STATUS OR CREATING
DOWNSTREAM CONTROL EFFECTS.
```

It does not establish:

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
automatic DOGFOOD_001 continuation
```

## Residue

The qualified v0 intentionally does not establish semantic equivalence between
changed qualified surfaces.

It also does not make a revalidation against one basis transferable to another.

```text
VALID WARRANT EXISTS
!=
THIS WARRANT APPLIES AT EVERY BASIS

CURRENTLY APPLICABLE
!=
LIVE DEVELOPMENTAL CONTRACT
```

DOGFOOD_001 remains held.

CAMPAIGN_ADOPTION_001 remains separate.
