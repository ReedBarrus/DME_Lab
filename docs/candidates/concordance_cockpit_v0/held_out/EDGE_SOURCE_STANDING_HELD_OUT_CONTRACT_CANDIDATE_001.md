# EDGE_SOURCE_STANDING_HELD_OUT_001

## PROSPECTIVE HELD-OUT CONTRACT CANDIDATE v0

### STATUS

```text
SCIENTIFIC QUESTION:
FROZEN IN INTENT
NOT FROZEN BY THIS ARTIFACT

CONTRACT:
PROSPECTIVE CANDIDATE

FREEZE AUTHORITY:
NONE INFERRED

EXECUTION AUTHORITY:
NONE INFERRED

SCIENTIFIC CELLS:
PROSPECTIVE / UNCONSUMED

PROJECTOR:
UNTOUCHED

IMPLEMENTATION REPAIR:
NONE

SCIENTIFIC RESULT:
NONE

MERGE:
NO
```

This artifact materializes the already-reviewed six-cell geometry against the
qualified protected-grounding-key candidate. It does not freeze or execute it.

---

## 1. SCIENTIFIC QUESTION

```text
CAN SOURCE STANDING
BE DURABLY GROUNDED

SUCH THAT

SOURCE S
MAY ISSUE
RELATION CLASS R
OVER SCOPE Ω

WITHOUT S
BEING ABLE TO
SELF-GRANT THAT JURISDICTION?
```

The bounded output remains only:

```text
SOURCE_STANDING_FOR_CLAIM:
ESTABLISHED
|
NOT_ESTABLISHED
```

---

## 2. EXACT SOURCE LINEAGE

```text
qualified mechanism branch:
concordance-cockpit-edge-source-standing-candidate-v0

qualified mechanism head:
b14edd2217a9dc8c48466df2174371a51690eee0
```

Exact retained apparatus identities:

```text
exact relation-content verifier:
src/cockpit/edge_entitlement_v0.py
blob:
ac3abb625c2a4a005bb5e9a324e77afc9b88ddb6

source-standing evaluator:
src/cockpit/source_standing_v0.py
blob:
a0f26f7190971dbf4bdfa1046de4cb189bf79827

qualified candidate test:
tests/cockpit/test_source_standing_v0.py
blob:
17fd96c3a4ae67db94e55345a5f85a703e5e032e

candidate qualification receipt:
docs/candidates/concordance_cockpit_v0/EDGE_SOURCE_STANDING_QUALIFICATION_001.md
blob:
a998fbb8d1a03fd2fb73a73db80a34320c2786eb
```

Prospective held-out fixture:

```text
docs/candidates/concordance_cockpit_v0/held_out/
EDGE_SOURCE_STANDING_HELD_OUT_FIXTURES_001.json

Git blob:
45850b0b37d072e7b894ecb1dbeb0299ca504f37
```

The fixture content SHA-256 is:

```text
6d3fb573eefcb75bfebb4462021c218be4554b5ccb8d0d2496081b6f9f28444d
```

---

## 3. PROTECTED CLAIM COORDINATES

Across every scientific cell:

```text
SOURCE:
S*

SOURCE IDENTITY VALIDITY:
VALID
(as an experimental protected constant;
not a source-standing conclusion)

CLAIM ARTIFACT ID:
CLAIM-C*

CLAIM:
FROM* MOTIVATED TO*

CLAIM SHA-256:
39857ce13f93d4ba2bc471992f28681658be56dba9df33cdb8df77a478c652b2

FROM:
FROM*

RELATION CLASS:
MOTIVATED

TO:
TO*
```

The exact claim bytes are stored once in the fixture and MUST be reused
byte-for-byte in every cell.

The exact-content verifier is identical across all cells.

No cell may alter:

```text
claim bytes
claim digest
claim artifact id
source_ref
from_ref
relation_type
to_ref
exact-content verifier
standing evaluator implementation
grounding public key
observation schema
classification rule
threat model
```

Cell identity and expected result MUST NOT be passed into the evaluator.

---

## 4. PROSPECTIVE GROUNDING ROOT

The prospective fixture pins:

```text
grounding public-key fingerprint:
0c8175cbbf17b67500b7722af24ccdf4fc825ed8ac0203dba56aa9a1e5a70634
```

The corresponding private grounding key was used only to materialize the
prospective signed standing specimens and is not retained in the contract
fixture.

Therefore future realization must use the already-materialized signed standing
bytes. It MUST NOT regenerate, amend, resign, or mint replacement grounding
specimens.

```text
ROOT PUBLIC KEY PINNED
!=
AUTHORITY TO MINT NEW HELD-OUT STANDING
```

---

## 5. RAW CONTROL REPRESENTATION FOR H4

The prospective fixture contains one claimant-control bundle with both synthetic
claimant-held private signing capabilities:

```text
source key fingerprint:
1103780840ba8c0035cad138c3b6a90e2b6fa5448d90581a49e0bdd510893617

puppet key fingerprint:
6e7b42b16a883c5aba000a792f0406548cab0249e9c51e583a8a5897f8a92306
```

and a single fixed challenge:

```text
EDGE_SOURCE_STANDING_HELD_OUT_001_CONTROL_CHALLENGE
```

with signatures under both keys.

This prospective raw representation establishes only the synthetic cell
construction that both signing capabilities are available inside the same
claimant-control bundle.

It does not establish general control semantics.

The evaluator receives neither private claimant key and receives no semantic
field equivalent to:

```text
claimant_controls_issuer = true
```

---

## 6. PROSPECTIVE STANDING CELLS

All non-H1 standing specimens use:

```text
grant_id:
GRANT-HELD-OUT-001
```

unless a coordinate below necessarily differs.

This removes grant-id drift as an alternate explanation.

### P1 — EXACT STANDING POSITIVE CONTROL

Signed by the protected grounding root.

```text
source_ref:
S*

issuer_ref:
GROUNDING_ROOT*

jurisdiction:
DEVELOPMENTAL_RELATION_ISSUANCE

relation_classes:
[MOTIVATED]

endpoint_pairs:
[(FROM*, TO*)]
```

Standing-basis SHA-256:

```text
46669adfc072827bdce855e30e15b87bf7774e9c7c836a175ffca9c36b1613c3
```

Required eventual observation:

```text
ESTABLISHED
```

### H1 — NO STANDING

```text
standing_basis:
NONE

grounding_signature:
NONE
```

Required eventual observation:

```text
NOT_ESTABLISHED
```

### H2 — WRONG RELATION CLASS

Same protected root, source, jurisdiction, exact endpoint scope, grant_id, and
standing mechanism as P1.

Only the intended relation-coverage coordinate changes:

```text
relation_classes:
[REFERENCED_BY]
```

Standing-basis SHA-256:

```text
63e40584860fd3c9b3aa94d7cb4de9d4b9b9de2fab6cd1857c0f9983b462d216
```

Required eventual observation:

```text
NOT_ESTABLISHED
```

### H3 — ENDPOINT-SCOPE NEAR MISS

Same protected root, source, jurisdiction, MOTIVATED relation coverage,
grant_id, and standing mechanism as P1.

P1 endpoint scope:

```text
[(FROM*, TO*)]
```

H3 endpoint scope:

```text
[(FROM*, TO_NEAR*)]
```

Standing-basis SHA-256:

```text
a8525c81b0551e3f19245f639107ac06461b566f624a71d1459f5a3ca581b2d3
```

The changed detached signature is a deterministic consequence of changed
standing bytes and is not a separate scientific coordinate.

Required eventual observation:

```text
NOT_ESTABLISHED
```

### H4 — PUPPET SELF-GRANT

Same source, developmental-relation jurisdiction, MOTIVATED relation coverage,
exact endpoint pair, and grant_id.

The standing bytes instead name:

```text
issuer_ref:
I*
```

and pin the claimant-held puppet key fingerprint. The standing specimen is
signed by that puppet key, not by the protected grounding root.

Standing-basis SHA-256:

```text
671d662244c89c3bbcee04361837fb21a72ccb7e6f60d379821f596b11f8ed3a
```

The claimant-control bundle prospectively contains both S* and I* signing
capabilities.

Required eventual observation:

```text
NOT_ESTABLISHED
```

This cell pressures:

```text
ISSUER IDENTITY DIFFERENT
!=
INDEPENDENT GROUNDING
```

### H5 — REAL BUT WRONG JURISDICTION

Same protected root, source, MOTIVATED relation coverage, exact endpoint pair,
grant_id, and standing mechanism as P1.

Only the intended jurisdiction coordinate changes:

```text
jurisdiction:
OTHER_LEGITIMATE_JURISDICTION
```

Standing-basis SHA-256:

```text
cce3bf71682a76fd74938de9f580b2475f87655e4c2b450415892999ab009052
```

Required eventual observation:

```text
NOT_ESTABLISHED
```

---

## 7. H6

```text
H6:
ABSENT
EXCLUDED BY DESIGN REVIEW
NOT A SCIENTIFIC CELL
NOT TO BE MATERIALIZED OR EXECUTED
```

---

## 8. FUTURE REALIZATION PROCEDURE

A future separately authorized realization must:

1. reconstruct the exact pinned verifier/evaluator bytes;
2. require runtime dependency `cryptography == 46.0.4` or stop as
   administration-invalid;
3. verify the prospective held-out fixture Git blob and content SHA-256;
4. construct the evaluator using only the pinned grounding public key;
5. reuse the single exact claim byte string for every cell;
6. call `SourceStandingEvaluatorV0.derive` once per P1/H1/H2/H3/H4/H5 using
   only that cell's prospectively materialized standing bytes/signature;
7. pass no cell id, expected result, independence label, authority label,
   grounding verdict, or control verdict into the evaluator;
8. retain only:
   `status`, `reason`, and `standing_sha256` per cell;
9. complete all observations before applying the expected vector;
10. treat any initialization / identity / dependency failure before evaluation
    as administration-invalid rather than a scientific result.

This contract does not authorize that procedure.

---

## 9. OBSERVATION SCHEMA

For each scientific cell retain only:

```text
status:
ESTABLISHED | NOT_ESTABLISHED

reason:
candidate-emitted reason string

standing_sha256:
hex digest | null
```

No output field may claim:

```text
CLAIM_TRUE
RELATION_ESTABLISHED
CLAIM_ADJUDICATED
CLAIM_INCORPORATED
SOURCE_AUTHORIZED_GLOBALLY
```

---

## 10. EXPECTED VECTOR / FUTURE PASS PREDICATE

Expected vector exists only for post-observation adjudication:

```text
P1:
ESTABLISHED

H1:
NOT_ESTABLISHED

H2:
NOT_ESTABLISHED

H3:
NOT_ESTABLISHED

H4:
NOT_ESTABLISHED

H5:
NOT_ESTABLISHED
```

A future mechanical PASS requires exact match to all six coordinates.

Any other vector is mechanical failure / fracture of the held-out candidate.

An administration-invalid run produces no scientific vector.

---

## 11. CROSS-CELL PROHIBITIONS

```text
EVIDENCE FROM ONE CELL
MUST NOT
ESTABLISH ANOTHER CELL

CELL RESULT
MUST NOT
BE REUSED AS INPUT

EXPECTED VECTOR
MUST NOT
BE USED DURING EVALUATION

P1 SUCCESS
MUST NOT
CAUSE HOSTILE-CELL ACCEPTANCE

H1-H5 FAILURE
MUST NOT
BE PRE-LABELED FOR THE EVALUATOR
```

---

## 12. CLAIM CEILING

Even a future exact six-cell PASS may establish only:

```text
UNDER THE TESTED THREAT MODEL,

THE EXACT PINNED PROTECTED-GROUNDING-KEY CANDIDATE
MECHANICALLY DISTINGUISHES

SOURCE S*

WITH THE PROSPECTIVELY MATERIALIZED
ROOT-GROUNDED STANDING

FOR DEVELOPMENTAL_RELATION_ISSUANCE,
RELATION CLASS MOTIVATED,
AND EXACT ORDERED ENDPOINT PAIR (FROM*, TO*)

FROM THE FIVE PROSPECTIVELY MATERIALIZED
NON-STANDING / WRONG-RELATION /
OUT-OF-SCOPE / PUPPET-SELF-GRANT /
WRONG-JURISDICTION CONDITIONS.
```

It would not establish:

```text
relation truth
causal correctness
adjudication
incorporation
broader source standing
delegation
standing expansion
future self-grant
general standing semantics
general scope semantics
general control semantics
universal governance
projector correctness
```

---

## 13. AUTHORITY BOUNDARY

```text
THIS ARTIFACT:
MATERIALIZES A PROSPECTIVE CONTRACT ONLY

CONTRACT FREEZE:
NOT AUTHORIZED HERE

HELD-OUT EXECUTION:
NOT AUTHORIZED HERE

PROJECTOR REPAIR:
NO

PROJECTOR INTEGRATION:
NO

SCIENTIFIC PROMOTION:
NO

MERGE:
NO
```
