# Promotion Protocol v0

## Status

```text
PROTOCOL:
PROSPECTIVE

CURRENT CARRIER:
promotion-protocol-v0 branch

AUTHORITY EFFECT:
NONE BY THIS ARTIFACT

PROMOTION EFFECT:
NONE BY THIS ARTIFACT
```

This protocol formalizes how bounded machinery may move across the Article 0
promotion boundary:

```text
DISCOVERY HISTORY
!=
INTEGRATION SURFACE
!=
DURABLE SUBSTRATE
```

It also formalizes retroactive review of promotions that occurred before this
protocol existed.

---

## 1. Governing non-collapses

```text
PROMOTION AUTHORITY
!=
PROMOTABILITY

PROMOTION CANDIDATE
!=
PROMOTION REVIEW

PROMOTION REVIEW
!=
PROMOTION ADJUDICATION

PROMOTION ADJUDICATION
!=
PROMOTION ENVELOPE

PROMOTION ENVELOPE
!=
PROMOTION AUTHORIZATION

PROMOTION AUTHORIZATION
!=
PROMOTION EXECUTION

PROMOTION EXECUTION
!=
PROMOTION RECEIPT

MERGE
!=
PROMOTION

PROMOTION
!=
WHOLE-LINEAGE IMPORT
```

No stage silently implies a later stage.

---

## 2. Normal promotion sequence

```text
PROMOTION_CANDIDATE
→ FRESH_REVIEW
→ ADJUDICATION
→ PROMOTION_ENVELOPE
→ EXPLICIT_HUMAN_AUTHORITY
→ EXECUTION
→ PROMOTION_RECEIPT
```

A HOLD, REJECT, or REQUIRE_REPRESSURE disposition stops the chain unless a new
versioned candidate is materialized.

---

## 3. Promotion candidate

The candidate states exactly what is proposed for promotion.

Minimum required content:

```text
promotion_id
mode
source layer / source status
target layer / target status
subject identity
bounded behavior proposed for reliance
supporting evidence / pressure
claim ceiling
downstream dependency consequence
exact proposed delta
lineage references
known scars / unresolved debt
explicit non-promotions
review burden
```

The candidate is not self-promoting.

```text
CANDIDATE EXISTS
!=
CANDIDATE IS PROMOTABLE
```

The candidate must not contain a reviewer disposition, adjudication verdict, or
execution authorization.

---

## 4. Fresh review

The reviewer asks only:

```text
DOES THIS EXACT CANDIDATE
SATISFY THE BURDEN
FOR THE REQUESTED PROMOTION?
```

The review must bind the exact candidate bytes by SHA-256.

Allowed review dispositions:

```text
ADMIT
HOLD
REJECT
REQUIRE_REPRESSURE
```

The review must separately inspect at minimum:

```text
SUBJECT_IDENTITY
SOURCE_STATUS
TARGET_STATUS
SURVIVING_BOUNDED_BEHAVIOR
EVIDENCE_SUFFICIENCY
CLAIM_CEILING
DEPENDENCY_CONSEQUENCE
INTEGRATION_MINIMALITY
LINEAGE_RECOVERABILITY
KNOWN_DEBT
NON_PROMOTIONS
```

### Reviewer independence

The review artifact must declare whether its author materially authored the
candidate or the proposed integration delta.

Under v0:

```text
CANDIDATE_AUTHOR = TRUE
OR
PROPOSED_DELTA_AUTHOR = TRUE
→ ADMIT IS INVALID
```

Such a reviewer may return HOLD, REJECT, or REQUIRE_REPRESSURE, or may perform
a non-binding design critique, but may not supply the admitting fresh review.

Freshness is about review independence, not model brand or human identity.

---

## 5. Adjudication

Review recommends; adjudication decides promotability.

The adjudication must bind:

```text
candidate SHA-256
review SHA-256
review disposition
adjudicator identity / seat
requested target layer
```

Allowed adjudication decisions:

```text
ADMIT
HOLD
REJECT
REQUIRE_REPRESSURE
```

An ADMIT adjudication establishes only:

```text
PROMOTABLE UNDER THIS BOUNDED REVIEW
```

It does not establish:

```text
AUTHORIZED TO PROMOTE
PROMOTION EXECUTED
MERGED
SCIENTIFIC TRUTH
GLOBAL CORRECTNESS
```

---

## 6. Promotion envelope

Only an ADMIT adjudication may be bound into a promotion envelope.

The envelope freezes the exact prospective consequence:

```text
candidate identity
review identity
adjudication identity
source carrier / source head
target carrier / target head
exact files / objects to add, replace, or remove
expected post-promotion status
explicit non-consequences
rollback / repair posture where applicable
```

The envelope is non-self-authorizing.

```text
ENVELOPE READY
!=
EXECUTION AUTHORIZED
```

The envelope should end in a single explicit human decision object suitable for
authorization.

---

## 7. Explicit authority

Human authorization applies to one exact promotion envelope.

Authorization must not be inferred from:

```text
candidate quality
review ADMIT
adjudication ADMIT
open PR
mergeability
prior related authorization
conversation momentum
```

If the envelope changes after authorization, the authorization is stale.

---

## 8. Execution

Execution performs only the frozen consequence in the authorized envelope.

For Git-carried promotion this may include a merge, cherry-pick, generated
integration commit, registry mutation, or other exact repository delta.

Execution must not strengthen the candidate claim or widen the promoted scope.

```text
EXECUTION SUCCESS
!=
PROMOTION CORRECTNESS
```

Unexpected delta or stale basis produces a failed / invalid administration,
not an improvised promotion.

---

## 9. Promotion receipt

The receipt is written only after execution or a valid retroactive
ratification/repair administration.

Minimum receipt content:

```text
promotion_id
mode
candidate identity
review identity
adjudication identity
authorization reference
envelope identity
observed pre-state
observed post-state
exact executed delta
resulting carrier
resulting status
non-promotions
deviations
terminal disposition
```

A receipt records what happened. It does not rewrite the basis that justified
the promotion.

---

## 10. Retroactive formalization

A promotion that occurred before this protocol existed must not be fictionalized
as if the protocol preceded it.

Use:

```text
mode:
RETROACTIVE_FORMALIZATION
```

The candidate must state:

```text
CURRENT REALITY:
already promoted / already durable

ORIGINAL PATH:
pre-protocol

QUESTION:
should the existing durable standing be RATIFIED,
HELD FOR REPAIR,
REJECTED,
or REPRESSURED under this protocol?
```

Retroactive review and adjudication do not re-execute the original merge.

If adjudicated ADMIT and separately authorized, the execution consequence is:

```text
RATIFY_EXISTING_DURABLE_STATE
+
WRITE FORMAL RECEIPT
```

not:

```text
RE-MERGE ORIGINAL CHANGE
```

If HOLD, REJECT, or REQUIRE_REPRESSURE:

```text
DO NOT ERASE ORIGINAL HISTORY
DO NOT PRETEND THE DURABLE BYTES DISAPPEARED
MARK / REPAIR STANDING EXPLICITLY
```

This preserves:

```text
ORIGINAL PROMOTION EVENT
!=
LATER PROMOTION RATIFICATION
```

---

## 11. Article 0 bootstrap scar

The first Article 0 promotion occurred before this protocol existed.

That event is retained as:

```text
HUMAN AUTHORIZATION
→ MATERIALIZATION
→ MERGE
```

without a durable pre-promotion candidate, fresh review, adjudication,
promotion envelope, or post-execution promotion receipt.

This protocol does not retroactively claim those missing stages occurred.

The first intended use of this protocol is therefore a retroactive
formalization of:

```text
PROMOTION_BOUNDARY_001
```

from its actual current durable state.

---

## 12. Schemas

Normative object shapes are carried by:

```text
schemas/promotion_candidate_v0.schema.json
schemas/promotion_review_v0.schema.json
schemas/promotion_adjudication_v0.schema.json
schemas/promotion_envelope_v0.schema.json
schemas/promotion_receipt_v0.schema.json
```

Schema validity establishes object-shape validity only.

```text
SCHEMA VALID
!=
PROMOTABLE
!=
AUTHORIZED
!=
EXECUTED
```

---

## 13. Bootstrap adoption of this protocol

This protocol itself is a proposed operational process, not a promotion result.

Its first repository adoption is governed by a one-time, historically typed
bootstrap event rather than by this protocol's ordinary promotion sequence.

```text
PROTOCOL ADOPTION EVENT
!=
OBJECT PROMOTION UNDER PROTOCOL
```

The bootstrap path is available only while:

```text
NO DURABLE PROMOTION PROTOCOL EXISTS
```

The bootstrap event must bind the exact protocol object reviewed and authorized.

Required bootstrap sequence:

```text
BOOTSTRAP_ADOPTION_001
→ HUMAN REVIEW OF EXACT PROTOCOL
→ EXPLICIT HUMAN ADOPTION AUTHORITY FOR EXACT PROTOCOL
→ PREFLIGHT
→ EXECUTION
→ BOOTSTRAP ADOPTION RECEIPT
```

Preflight must verify at minimum:

```text
reviewed protocol identity unchanged
bootstrap precondition still true
authorization binds exact reviewed protocol object
target carrier / exact repository consequence unchanged
```

Successful terminal adoption must establish:

```text
protocol_adopted = true
bootstrap_consumed = true
bootstrap_adoption_eligible = false
```

Any terminal bootstrap failure must preserve:

```text
protocol_adopted = false
bootstrap_consumed = false
```

Therefore, for terminal bootstrap administration:

```text
protocol_adopted
IFF
bootstrap_consumed
```

and specifically:

```text
false / true
→ INVALID: genesis consumed without durable protocol

true / false
→ INVALID: durable protocol with reusable bootstrap bypass
```

The bootstrap exception self-extinguishes by succeeding:

```text
BOOTSTRAP LEGITIMACY BASIS:
NO DURABLE PROMOTION PROCEDURE EXISTS

BOOTSTRAP EFFECT:
CREATE FIRST DURABLE PROMOTION PROCEDURE

AFTER SUCCESS:
BOOTSTRAP LEGITIMACY BASIS = FALSE
```

The bootstrap receipt is not a promotion receipt:

```text
BOOTSTRAP RECEIPT
!=
PROMOTION RECEIPT
```

The bootstrap event must not claim:

```text
PROMOTION_PROTOCOL_v0
PASSED
PROMOTION_PROTOCOL_v0
```

It records instead that explicit human review and explicit human bootstrap
adoption authority caused the first durable adoption of the exact protocol
while no durable promotion protocol yet existed.

After successful adoption, future promotion events -- including the retroactive
formalization of PROMOTION_BOUNDARY_001 -- use PROMOTION_PROTOCOL_v0.

No object on this branch may self-adjudicate or self-authorize that adoption.
