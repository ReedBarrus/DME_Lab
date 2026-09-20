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
schemas/promotion_authorization_v0.schema.json
schemas/promotion_receipt_v0.schema.json

bootstrap-specific first-adoption shapes:

schemas/bootstrap_adoption_object_v0.schema.json
schemas/bootstrap_adoption_review_v0.schema.json
schemas/bootstrap_adoption_authorization_v0.schema.json
schemas/bootstrap_adoption_preflight_v0.schema.json
schemas/bootstrap_adoption_receipt_v0.schema.json
schemas/bootstrap_adoption_receipt_verification_v0.schema.json
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

The bootstrap event must bind one exact protocol object end-to-end.

### 13.1 Bootstrap-specific object family

The first-adoption chain is:

```text
BOOTSTRAP_ADOPTION_001 OBJECT
→ FRESH BOOTSTRAP REVIEW
→ BOOTSTRAP-SPECIFIC HUMAN AUTHORIZATION
→ BOOTSTRAP PREFLIGHT
→ EXECUTION
→ BOOTSTRAP ADOPTION RECEIPT
```

The ordinary:

```text
promotion_authorization_v0
```

shape is not valid bootstrap authority.

Bootstrap authority uses:

```text
bootstrap_adoption_authorization_v0
```

because:

```text
PROTOCOL ADOPTION EVENT
!=
OBJECT PROMOTION UNDER PROTOCOL
```

The bootstrap review, authority, preflight, and receipt must all carry the same:

```text
event_id = BOOTSTRAP_ADOPTION_001
protocol_object_id = PROMOTION_PROTOCOL_v0
protocol_path = docs/operations/PROMOTION_PROTOCOL_v0.md
protocol_git_blob_sha = exact reviewed protocol blob
```

Every artifact after the bootstrap object must also bind the exact bootstrap
object identity it consumes.

Reference presence alone is insufficient:

```text
REFERENCE PRESENT
!=
REFERENCE CONSISTENT
```

Cross-object equality is therefore checked by bootstrap preflight before
execution can be admitted and by the terminal-chain verifier before a receipt
is accepted as chain-consistent.

Content-address dependencies must remain acyclic:

```text
ONE-WAY CONTENT ADDRESSING
!=
MUTUAL CONTENT-ADDRESS CYCLE
```

A bootstrap object may pin the exact implementation that consumes it. That
implementation must derive the bootstrap object's identity from the supplied
bytes rather than embedding the bootstrap object's content hash in its own
bytes.

### 13.2 Fresh bootstrap review

The fresh review must bind:

```text
exact protocol Git blob
exact bootstrap-object Git blob
review disposition
reviewer independence
bounded review basis
```

The protocol/candidate materializer may not supply an admitting fresh review
when the bootstrap review declares that materializer as the relevant author.

An admitting review does not create adoption authority.

```text
REVIEW ADMIT
!=
BOOTSTRAP AUTHORITY
```

### 13.3 Bootstrap-specific human authority

Human bootstrap authority must be represented by a typed
`bootstrap_adoption_authorization_v0` object.

It must bind at minimum:

```text
BOOTSTRAP_ADOPTION_001
exact protocol Git blob
exact bootstrap-object Git blob
exact admitting review identity
exact authorized adoption effect
target repository / target ref / pull request
explicit non-authorizations
```

Bootstrap authority does not arise from an ordinary promotion envelope and does
not use ordinary promotion authorization semantics.

```text
BOOTSTRAP ADOPTION AUTHORITY
!=
BOOTSTRAP ADOPTION SUCCESS
```

### 13.4 Bootstrap preflight

Preflight is the mechanical administration gate.

It must verify from actual supplied artifacts and repository state:

```text
reviewed protocol identity unchanged
bootstrap-object protocol identity unchanged
review binds the exact bootstrap object
authorization binds the exact review
authorization binds the exact protocol object
authorization binds the exact bootstrap object
bootstrap precondition still true
target repository / ref / PR consequence unchanged
PR head matches the authorized head
all required identities are mutually consistent
```

The precondition is external repository truth, not a fact manufactured by
schema validity.

```text
SCHEMA-LOCAL STATE CLOSURE
!=
EXTERNAL HISTORICAL TRUTH
```

Schema shapes require and constrain the witness/result. The preflight mechanism
must derive the repository-state result.

The bootstrap object pins the exact preflight implementation. The preflight
implementation derives the actual bootstrap-object Git blob from supplied
bytes and compares review and authorization bindings against that derived
identity. It must not hardcode the bootstrap-object content hash.

```text
BOOTSTRAP OBJECT
→ pins PREFLIGHT IMPLEMENTATION

PREFLIGHT IMPLEMENTATION
→ derives BOOTSTRAP OBJECT IDENTITY

NOT:

BOOTSTRAP OBJECT HASH
↔
PREFLIGHT IMPLEMENTATION HASH
```

Execution is admitted only when the typed preflight result is `PASS`.

```text
PREFLIGHT PASS
IS NECESSARY
BEFORE
BOOTSTRAP EXECUTION
```

A failed or unresolved preflight does not authorize execution.

### 13.5 Terminal geometry

Successful adoption must establish all of:

```text
terminal_result = ADOPTED
observed_precondition = TRUE
protocol_adopted = true
bootstrap_consumed = true
bootstrap_adoption_eligibility = INELIGIBLE
resulting_carrier = present
preflight_result = PASS
```

Failure must never produce a durable-adoption claim or consume genesis:

```text
protocol_adopted = false
bootstrap_consumed = false
resulting_carrier = null
```

Failure does not have one uniform eligibility consequence.

If the actual precondition is false:

```text
terminal_result = PRECONDITION_FALSE
bootstrap_adoption_eligibility = INELIGIBLE
```

For failures where the precondition was verified true and no protocol was
adopted:

```text
bootstrap_adoption_eligibility = ELIGIBLE
```

If the administration cannot establish whether the precondition still holds:

```text
bootstrap_adoption_eligibility = UNRESOLVED
```

Therefore:

```text
FAILURE
!=
UNIFORM ELIGIBILITY CONSEQUENCE
```

### 13.6 Terminal chain verification

Schema-valid receipt references are not sufficient evidence that the receipt
belongs to the exact administration chain.

```text
REFERENCE PRESENT
!=
REFERENCE CONSERVED
```

The bootstrap object pins one exact terminal-chain verifier implementation.
That verifier consumes the actual:

```text
protocol bytes
bootstrap-object bytes
review bytes
authorization bytes
preflight bytes
receipt bytes
```

and derives each Git blob identity from those supplied bytes.

It must verify at minimum:

```text
protocol identity matches bootstrap object
review identity matches bootstrap object + protocol
authorization identity matches review + bootstrap object + protocol
preflight identity matches authorization + review + bootstrap object + protocol
receipt identity references match actual review + authorization + preflight bytes
receipt protocol/bootstrap references match actual protocol/bootstrap bytes
receipt preflight_result matches the consumed preflight result
```

The verifier must not hardcode the content hash of a downstream receipt or
bootstrap object whose bytes also pin the verifier. Its implementation identity
is distinct from the validity of the chain it checks.

```text
RECEIPT VERIFIER IDENTITY
!=
RECEIPT CHAIN VALIDITY
```

A bootstrap receipt is administratively chain-valid only when:

```text
RECEIPT SCHEMA:
VALID

AND

PINNED TERMINAL-CHAIN VERIFIER:
PASS
```

The verifier does not create authority, perform execution, adopt the protocol,
or rewrite the receipt.

### 13.7 Self-extinguishing genesis

The bootstrap exception self-extinguishes by succeeding:

```text
BOOTSTRAP LEGITIMACY BASIS:
NO DURABLE PROMOTION PROCEDURE EXISTS

BOOTSTRAP EFFECT:
CREATE FIRST DURABLE PROMOTION PROCEDURE

AFTER SUCCESS:
BOOTSTRAP LEGITIMACY BASIS = FALSE
```

For a successful terminal bootstrap event:

```text
protocol_adopted = true
bootstrap_consumed = true
bootstrap_adoption_eligibility = INELIGIBLE
```

A successful receipt with any different combination is invalid.

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

No bootstrap object, review, authorization, preflight, or receipt may
self-adjudicate or self-authorize adoption.
