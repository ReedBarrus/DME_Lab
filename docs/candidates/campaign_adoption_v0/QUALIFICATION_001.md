# CAMPAIGN_ADOPTION_001 — QUALIFICATION_001

## Status

```text
BOUNDED MECHANICAL QUALIFICATION
QUALIFIED AT RECORDED IMPLEMENTATION HEAD

REAL COCKPIT_OPERATING_SPACE_001 ADOPTION:
NOT YET MATERIALIZED BY THIS RECEIPT

DOGFOOD RETRY:
NO

MERGE:
NO
```

## Contract basis

Corrected semantic contract:

```text
campaign-adoption-contract-v0
contract correction head:
61f695b5691330e39ca1ec6c335dba8fdb3a7152
```

Implementation stack base:

```text
CAMPAIGN_APPLICABILITY_PROJECTION_001

campaign-applicability-projection-v0
e168f4f10336d5805bc48ccfda2bb59d8898e465
```

## Executed implementation basis

```text
branch:
campaign-adoption-v0

executed implementation head:
ed0888b1a485d3c298f54e8489ab01a438315d9b

PR:
#53
OPEN
DRAFT
UNMERGED
```

## Exact apparatus identities

```text
tools/campaign_adoption_v0.py
75a23fa6228b823239cabbc72dcbcd59cb550ed3

tests/runtime/test_campaign_adoption.py
c3d305883b91ffa2b53e8a5e9e98fec6b3b0ea06

.github/workflows/campaign-adoption-001.yml
66dae312537b0d9c4913e388fbdd69a5d8e6f37b
```

## Executed workflow evidence

```text
workflow:
CAMPAIGN_ADOPTION_001

run:
35514288278

job:
106087484701

head:
ed0888b1a485d3c298f54e8489ab01a438315d9b

result:
SUCCESS
```

Focused pressure:

```text
python -m unittest tests.runtime.test_campaign_adoption -v

Ran 24 tests
OK
```

## Required pressure results

```text
A1  current applicability + explicit Reed adoption
    → ADOPTED + LIVE
    PASS

A2  applicable without adoption
    → NOT_ADOPTED + NOT_LIVE
    PASS

A3  adoption while NOT_CURRENT
    → REJECT / no write
    PASS

A4  wrong campaign identity
    → REJECT
    PASS

A5  missing explicit gesture provenance
    → REJECT
    PASS

A6  same adoption ID + same bytes
    → IDEMPOTENT
    PASS

A7  same adoption ID + changed bytes
    → REJECT
    PASS

A8  adoption neighboring effects
    → all NONE
    PASS

A9  exact release
    → adoption history retained / current adoption ends
    PASS

A10 basis moves after adoption
    → adoption remains ADOPTED
    → live becomes BLOCKED_NOT_CURRENT
    PASS

A11 applicability restored
    → live returns
    → no new adoption event
    PASS

A12 two campaigns adopted
    → both coexist
    → priority NONE
    PASS
```

## Adversarial results

```text
X1  release wrong adoption SHA
    → REJECT
    PASS

X2  release without exact target
    → REJECT
    PASS

X3  second independent release of already released adoption
    → REJECT
    PASS

X4  storage metadata excluded from durable identity
    PASS

X5  downstream-state smuggling
    → REJECT
    PASS

X6  caller-supplied applicability verdict
    → REJECT
    PASS

X7  activity / applicability without adoption
    → NOT_ADOPTED
    PASS

X8  active-adoption ordering
    → deterministic non-semantic order / priority NONE
    PASS

X9  missing applicability source
    → FAIL CLOSED
    PASS

X10 release leaves applicability projection unchanged
    PASS

X11 adoption write leaves campaign + revalidation stores unchanged
    PASS

X12 applicability restoration emits no adoption event
    PASS
```

## Inherited regressions

Same workflow run:

```text
CAMPAIGN_APPLICABILITY_PROJECTION_001
20 / 20 PASS

CAMPAIGN_BASIS_REVALIDATION_001
17 / 17 PASS

ENVELOPE_SELECTION_001
PASS

PREPARATION_001
PASS

PREPARATION_ASSIGNMENT_001
PASS

WAKE_SOURCE_001
PASS

BOUNDED_REENTRY_001
PASS

COCKPIT_CONTROL_ADAPTER_001
PASS
```

## Mechanically conserved distinctions

```text
ADOPTION
!=
APPLICABILITY

UNRELEASED ADOPTION
!=
CURRENT INTERNAL HUMAN DESIRE

CURRENT APPLICABILITY LOST
!=
ADOPTION RELEASED

CURRENT APPLICABILITY RESTORED
!=
NEW ADOPTION REQUIRED

ADOPTION
!=
SELECTION
!=
ASSIGNMENT
!=
PRIORITY
!=
STANDING
!=
AUTHORITY
!=
SCHEDULER
!=
WAKE
!=
EXECUTION

RELEASE CAMPAIGN LABEL
!=
RELEASE EXACT ADOPTION RELATION

STORAGE METADATA
!=
DURABLE ADOPTION IDENTITY
```

## Claim ceiling

This qualification supports only:

```text
ONE EXACT CURRENTLY-APPLICABLE CAMPAIGN

CAN RECEIVE ONE EXPLICIT,
DURABLE REED ADOPTION DECLARATION

WHOSE UNRELEASED STATE PERSISTS
INDEPENDENTLY OF LATER BASIS DRIFT,

WHILE LIVE DEVELOPMENTAL STATUS IS DERIVED FROM:

UNRELEASED ADOPTION
×
CURRENT EFFECTIVE APPLICABILITY

WITHOUT CREATING:

SELECTION
ASSIGNMENT
PRIORITY
STANDING
AUTHORITY
SCHEDULER
WAKE
OR EXECUTION.
```

## Effect boundary

```text
CAMPAIGN MUTATION:
NO

REVALIDATION CREATION:
NO

REAL CAMPAIGN ADOPTION:
NO — qualification fixture only

SELECTION CREATION:
NONE

ASSIGNMENT:
NONE

PRIORITY:
NONE

STANDING EFFECT:
NONE

AUTHORITY EFFECT:
NONE

SCHEDULER EFFECT:
NONE

WAKE:
NONE

EXECUTION:
NONE

DOGFOOD RETRY:
NO

MERGE:
NO
```
