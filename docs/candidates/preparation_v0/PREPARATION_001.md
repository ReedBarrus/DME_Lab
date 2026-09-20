# PREPARATION_001

## Status

```text
BOUNDED EXECUTABLE CANDIDATE

PREPARATION HISTORY:
APPEND-ONLY RECEIPTS

CURRENT PREPARATION READINESS:
DERIVED PROJECTION

PACKET DRAFT:
REPRESENTED EXECUTION_PACKET_v0
WITH AUTHORIZATION = NOT_AUTHORIZED

CANONICAL MUTATION:
NONE

EXECUTION AUTHORITY:
NONE

STANDING EFFECT:
NONE
```

## Sole question

```text
CAN A SELECTED + CURRENTLY PREPARATION-ELIGIBLE
EXECUTION-ENVELOPE REQUEST

ACCUMULATE BOUNDED PREPARATORY WORK

WITHOUT THAT WORK ITSELF
ACQUIRING:

execution authority
standing effect
canonical mutation
priority
or packet self-authorization?
```

## Historical / current split

Preparation is append-only history.

Current readiness is a projection.

```text
PREPARATION ELIGIBLE
!=
PREPARATION STARTED

PREPARATION STARTED
!=
PREPARATION ARTIFACT EXISTS

PREPARATION ARTIFACT EXISTS
!=
PACKET READY

PACKET READY
!=
EXECUTION AUTHORIZED
```

Each `PREPARATION_RECEIPT_v0` binds exact campaign, request, selection, and
preparation-basis identities.

Current preparation status is derived from those receipts plus the present
selection/campaign projection.

## Preparation kinds

```text
RESOLVE_REFS
REVALIDATE_BASIS
ASSEMBLE_EVIDENCE
DRAFT_PACKET
REQUEST_REVIEW
REVIEW_RESULT
ESTIMATE_RESOURCES
DETECT_CONFLICTS
DERIVE_STOP_CONDITIONS
```

The list is an allowed receipt vocabulary.

It does not imply that every selected request requires every kind.

## Receipt effects

Every retained preparation receipt carries:

```text
preparation_effect = PREPARATION_ONLY
canonical_mutation_effect = NONE
authorization_effect = NONE
execution_effect = NONE
standing_effect = NONE
priority_effect = NONE
```

Therefore:

```text
PREPARATION RECEIPT
!=
EXECUTION AUTHORITY
```

## Packet drafting

Preparation may retain a represented `EXECUTION_PACKET_v0` artifact using the
required fields already defined by `docs/methods/TWINNING_PROTOCOL_v0.md`.

The packet draft must carry:

```text
AUTHORIZATION = NOT_AUTHORIZED
```

This uses the existing Twinning distinction:

```text
represented packet
!=
authorized packet
```

Preparation does not introduce a second execution-packet species.

## Current readiness projection

The v0 projection derives one of:

```text
PREP_INCOMPLETE

PREP_INCOMPLETE_REVIEW_OBJECTION

PREP_INCOMPLETE_REVIEW_CONFLICT

PREP_BLOCKED_STALE

PREP_BLOCKED_RESOLVED

PREP_BLOCKED_OBSOLETE

PREP_READY_FOR_AUTHORITY_REVIEW
```

A request may be selected while preparation is blocked.

A packet draft may exist while the request is stale.

A resource estimate may exist while execution authority is absent.

No historical receipt is rewritten when current readiness changes.

## Basis rule

v0 is deliberately conservative.

A preparation receipt is current only when:

```text
preparation_basis_refs
==
current campaign basis refs
```

If the world/basis moves after preparation:

```text
PREPARATION REALLY HAPPENED

BUT

PREPARATION CURRENTLY APPLICABLE
MAY BECOME FALSE
```

Scar:

```text
PREPARATION BASIS CURRENT AT T1
!=
PREPARATION STILL CURRENT AT T2
```

## Parallel preparation

Multiple preparers may retain independent receipts against the same exact
request identity.

```text
MULTIPLE PREPARERS
!=
SHARED IDENTITY

MULTIPLE PREP ARTIFACTS
!=
MULTIPLE EXECUTION AUTHORITIES

FIRST PREP RECEIPT
!=
PRIORITY
```

Conflicting review results are retained.

```text
REVIEW A = PASS
REVIEW B = OBJECTION

→ BOTH RETAINED
→ NO LAST-WRITE-WINS
→ NO SILENT ADJUDICATION
```

## Pressure cells

```text
P1 ELIGIBLE SELECTED REQUEST
   → bounded prep receipt retained
   → no execution / authority / standing / canonical-mutation effect

P2 UNSELECTED REQUEST
   → preparation rejected as ineligible

P3 SELECTED BUT STALE
   → ordinary preparation rejected
   → current projection BLOCKED_PENDING_REVALIDATION

P4 PREP THEN WORLD MOVES
   → preparation history preserved
   → current readiness PREP_BLOCKED_STALE

P5 FRACTURE DURING PREP
   → preparation artifacts remain historical
   → request becomes obsolete
   → readiness PREP_BLOCKED_OBSOLETE

P6 MULTI-SEAT PREP
   → LABBOIB / COMMANDER / WORKSHOP / MAYA receipts coexist
   → no priority inferred

P7 CONFLICTING REVIEWS
   → PASS and OBJECTION retained
   → readiness exposes review conflict
   → no silent adjudication

P8 PACKET DRAFTED
   → represented EXECUTION_PACKET_v0 retained
   → AUTHORIZATION = NOT_AUTHORIZED
   → readiness may become PREP_READY_FOR_AUTHORITY_REVIEW
   → execution authority remains NONE

P9 PREP REPLAY
   → exact same receipt replay is idempotent
   → same preparation_id with different bytes rejected

P10 AUTHORITY APPEARS LATER
   → old stale preparation remains stale
   → authority does not rewrite preparation applicability
```

## Claim ceiling

A passing candidate may support only that the tested preparation store can
retain append-only preparation receipts against an exact selected request,
preserve parallel/conflicting preparation evidence, retain an unauthorized
represented Twinning packet draft, and derive current preparation readiness
without granting execution, standing, priority, or canonical-mutation effects.

It does not establish:

```text
actual execution authorization
automatic packet authorization
automatic packet dispatch
scheduler behavior
automatic preparer assignment
general packet sufficiency
scientific adjudication
```
