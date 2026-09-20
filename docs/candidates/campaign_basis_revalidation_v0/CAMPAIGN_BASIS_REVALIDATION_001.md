# CAMPAIGN_BASIS_REVALIDATION_001

## STATUS

```text
FROZEN SEMANTIC CONTRACT
PRESSURE-DESIGN AUTHORIZED
IMPLEMENTATION:
NOT AUTHORIZED BY THIS CONTRACT

CAMPAIGN_ADOPTION_001:
UNTOUCHED

DOGFOOD RETRY:
NOT YET AUTHORIZED BY THIS CONTRACT
```

## Origin

This membrane is grounded in the first real Cockpit dogfood stop:

```text
COCKPIT_OPERATING_SPACE_001
DOGFOOD_001

observed:
historical campaign basis != current repository basis

result:
DOGFOOD_BLOCKED_BASIS

downstream objects:
request NONE
selection NONE
assignment NONE
bell NONE
wake NONE
work units 0
```

The observed missing relation is:

```text
HISTORICAL CAMPAIGN BASIS
→
CURRENTLY ADMISSIBLE CAMPAIGN BASIS
```

The smallest retained distinction is:

```text
CAMPAIGN_BASIS_REVALIDATED
!=
CAMPAIGN_BASIS_REWRITTEN
```

## Sole question

```text
CAN ONE EXACT HISTORICAL CAMPAIGN

BE JUDGED CURRENTLY APPLICABLE
AGAINST ONE EXACT PROPOSED CURRENT BASIS

WITHOUT:

REWRITING CAMPAIGN BYTES
CHANGING HISTORICAL CAMPAIGN IDENTITY
ADOPTING THE CAMPAIGN
SELECTING WORK
ASSIGNING A SEAT
CREATING PRIORITY
CHANGING STANDING
GRANTING AUTHORITY
OR EXECUTING ANY CONSEQUENCE?
```

## Governing distinctions

```text
HISTORICAL CAMPAIGN IDENTITY
!=
CURRENT CAMPAIGN APPLICABILITY

CAMPAIGN CONTINUITY REQUIREMENT
!=
EVIDENCE USED TO TEST REQUIREMENT
!=
RESULT OF TESTING REQUIREMENT

BASIS REVALIDATED
!=
CAMPAIGN ADOPTED

CAMPAIGN ADOPTED
!=
REQUEST SELECTED

BASIS REVALIDATION
!=
STANDING CHANGE

BASIS REVALIDATION
!=
AUTHORITY GRANT

REVALIDATION EVIDENCE EXISTS
!=
REVALIDATION PASSED

REVALIDATED AT BASIS B2
!=
APPLICABLE AT BASIS B3

GIT DESCENDANT
!=
SEMANTICALLY VALID SUCCESSOR BASIS

WHOLE WORLD CHANGED
!=
CAMPAIGN-RELEVANT WORLD CHANGED

"I THINK THIS CHANGE IS IRRELEVANT"
!=
MECHANICALLY IRRELEVANT TO THIS CAMPAIGN
```

## Historical object immutability

The exact historical `development_campaign_v0` object remains immutable.

A revalidation may not mutate:

```text
campaign_id
campaign_sha256
campaign basis_refs
campaign objective
claim ceiling
unresolved relations
dependency edges
status
or any historical campaign bytes
```

Therefore:

```text
CURRENT APPLICABILITY
MUST NOT BE STORED
AS A MUTATED CAMPAIGN FIELD
```

## Requirement provenance

The revalidation caller may not freely choose a reduced requirement set at
execution time.

```text
REVALIDATION REQUIREMENTS
MUST BE TRACEABLY GROUNDED

IN:

the exact historical campaign
and/or
the exact qualified surfaces
that campaign actually relies upon
```

The caller may supply raw evidence needed to inspect those requirements.

The caller may not supply pre-adjudicated answers such as:

```text
surface_compatible = true
dependency_still_valid = true
campaign_still_applies = true
```

Scar:

```text
RAW CONTINUITY BASIS
!=
PRE-ADJUDICATED COMPATIBILITY VERDICT
```

The apparatus must expose the requirements it derived so omission is visible.

```text
REQUIREMENT DERIVED
!=
REQUIREMENT LEGITIMATELY GROUNDED
```

If pressure later shows that campaign bytes cannot supply an adequate
requirement basis, that may motivate a separate continuity-contract object.
This contract does not introduce one.

## Candidate result object

The first apparatus may materialize a separate durable result shaped
conceptually as:

```text
CAMPAIGN_BASIS_REVALIDATION_v0

revalidation_id

campaign_id
campaign_sha256

historical_basis_refs
historical_basis_sha256

candidate_current_basis_refs
candidate_current_basis_sha256

derived_continuity_requirements[]
evidence_refs[]

disposition:
    CURRENTLY_APPLICABLE
    NOT_APPLICABLE
    INSUFFICIENT_BASIS

adjudication_ref

authority_effect = NONE
adoption_effect = NONE
selection_effect = NONE
standing_effect = NONE
execution_effect = NONE
priority_effect = NONE
scheduler_effect = NONE
```

This shape is a contract target, not implementation authorization.

## Derived continuity requirement record

Each derived requirement should make visible at least:

```text
requirement_id
campaign_relevance_basis
historical_identity_or_relation
raw_current_evidence_inspected
test_relation
observed_result
```

The result must remain inspection-friendly enough for an adversarial reviewer to
detect omitted or weakened requirements.

## Current applicability projection

Current applicability is derived; it is not a permanent flag.

At minimum:

```text
CURRENTLY_APPLICABLE(campaign, current_basis)

requires a valid revalidation R such that:

R.campaign_sha256
=
exact historical campaign identity

AND

R.candidate_current_basis_sha256
=
exact current basis identity

AND

R.disposition
=
CURRENTLY_APPLICABLE
```

Therefore:

```text
REVALIDATION RESULT
!=
CURRENT APPLICABILITY FOREVER
```

If the world moves from B2 to B3, a B2 revalidation remains historical evidence
only.

## Applicability is not adoption

A successful endpoint is intentionally anticlimactic:

```text
COCKPIT_OPERATING_SPACE_001

historical identity:
UNCHANGED

candidate current basis:
B2

revalidation:
CURRENTLY_APPLICABLE

adoption:
NONE

selection:
NONE

assignment:
NONE

wake:
NONE

authority:
NONE
```

No field or disposition in this membrane may activate the campaign as a live
developmental contract.

## Exact-basis conservatism

The current v0 rule remains the conservative baseline:

```text
current_basis_refs != campaign.basis_refs
→
STALE
```

CAMPAIGN_BASIS_REVALIDATION_001 does not presume that rule is too strict.

It asks whether campaign-relevant semantic continuity can be mechanically
established under basis drift.

If irrelevance cannot be mechanically established from grounded campaign
requirements and qualified evidence, exact-basis staleness remains the correct
result.

## Claim ceiling

A passing implementation may establish only:

```text
ONE EXACT HISTORICAL CAMPAIGN

CAN RECEIVE ONE BASIS-RELATIVE
CURRENT APPLICABILITY JUDGMENT

AGAINST ONE EXACT CURRENT BASIS

WITHOUT REWRITING HISTORY
OR CREATING ADOPTION,
SELECTION,
ASSIGNMENT,
PRIORITY,
STANDING,
AUTHORITY,
SCHEDULER,
OR EXECUTION EFFECTS.
```

## Nonclaims

This contract does not establish:

```text
campaign adoption
automatic campaign activation
request selection
assignment
wake policy
scheduler behavior
standing promotion
authority
execution
general semantic-equivalence checking
general code-impact analysis
general proof that Git ancestry preserves campaign semantics
```

## Continuity principle retained

```text
DURABILITY PRESERVES HISTORY.

CONTINUITY RELATES
PRESERVED HISTORY
TO A CHANGING WORLD.

CONTINUITY
!=
EDIT HISTORY UNTIL IT LOOKS CURRENT
```
