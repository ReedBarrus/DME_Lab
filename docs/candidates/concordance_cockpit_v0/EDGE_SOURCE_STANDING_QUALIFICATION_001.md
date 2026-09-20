# EDGE_SOURCE_STANDING_001

## PROTECTED GROUNDING KEY CANDIDATE v0 — QUALIFICATION RECEIPT

### STATUS

```text
MECHANISM CANDIDATE:
IMPLEMENTED

SYNTHETIC SIX-CELL QUALIFICATION:
PASS

PROJECTOR:
UNTOUCHED

PROJECTOR INTEGRATION:
NONE

HELD-OUT CONTRACT FREEZE:
NO

HELD-OUT EXECUTION:
NO

SCIENTIFIC PROMOTION:
NONE

MERGE:
NO
```

### LINEAGE

```text
source branch:
concordance-cockpit-v0-edge-entitlement-candidate

source head:
184e7ddfc2f659dc275fdb98f8b331b72aba9382

candidate branch:
concordance-cockpit-edge-source-standing-candidate-v0

design commit:
868841408a0dc95694480e0347b26778a0971e36

implementation commit:
27333611cfa90c4ef597fdc34892c985b6ab6acb

initial qualification-test commit:
332b73c3a98b8f4b806c71122b5321349bbda314

non-substantive attempted binding commit:
d8301cafe70e33e96240e7237f5c1473db692bff

corrected concrete relation binding:
5a7d294698e2bd6221287a74df2f6c67dba999d1

raw evidence commit:
0a9b3414215fcdb41866dfd3f9e9b4951fb4f9aa
```

### EXACT QUALIFIED BLOBS

```text
candidate design:
4005b4d9682ec4c986394dc7b6c6848a6d9a0f02

source-standing implementation:
a0f26f7190971dbf4bdfa1046de4cb189bf79827

qualification test:
17fd96c3a4ae67db94e55345a5f85a703e5e032e

raw qualification evidence:
7e2a5b604ff4988499d922e313c42edc969b29b6

retained exact-content verifier:
ac3abb625c2a4a005bb5e9a324e77afc9b88ddb6
```

The source-standing implementation, qualification test, and retained exact-content
verifier were reconstructed locally from committed bytes and reproduced these
Git blob identities exactly before the successful qualification run.

### SELECTED CANDIDATE MECHANISM

The bounded candidate uses:

```text
one protected grounding Ed25519 private signing capability
+
one evaluator-pinned grounding public key
+
exact signed standing bytes
+
exact relation-class membership
+
exact ordered endpoint-pair membership
```

The protected grounding private key is synthetic fixture state outside the
claimant harness and is not an evaluator input or retained evidence artifact.

The retained evidence contains the public grounding key, signed standing bytes,
detached signatures, claimant public keys/control-challenge signatures, claim
bytes, and observed vector, but not the protected grounding private key.

### RAW MECHANICAL REPRESENTATIONS

```text
RAW STANDING BASIS:
canonical standing JSON bytes

RAW GROUNDING / ORIGIN EVIDENCE:
detached Ed25519 signature under evaluator-pinned public key

CLAIMANT-CONTROL PRESSURE:
one claimant harness mechanically exercises both S* and puppet I* signing keys

RELATION COVERAGE:
exact relation_classes membership

SCOPE COVERAGE:
exact ordered endpoint-pair membership

DERIVED OUTPUT ONLY:
SOURCE_STANDING_FOR_CLAIM
=
ESTABLISHED | NOT_ESTABLISHED
```

No candidate input named or equivalent to:

```text
independent
grounding_accepted
claimant_controls_issuer
standing_valid
authorized
cell_id
expected_result
```

is used.

### ADMINISTRATION / MATERIALIZATION PREFLIGHT

The first execution against commit:

```text
332b73c3a98b8f4b806c71122b5321349bbda314
```

used the abstract design symbol `R*` literally as the concrete claim relation.

The retained exact-content verifier admits its existing relation vocabulary, so
the exact claim failed upstream in every cell.

Executed:

```text
python -m unittest -v tests.cockpit.test_source_standing_v0

6 tests
4 passed
2 failed
```

Observed failure surface:

```text
P1:
NOT_ESTABLISHED
reason = EXACT_CLAIM_CONTENT_NOT_ESTABLISHED

H1:
NOT_ESTABLISHED
reason = EXACT_CLAIM_CONTENT_NOT_ESTABLISHED
```

This did not instantiate the intended standing pressure because the protected
claim precondition failed before standing evaluation.

Disposition:

```text
QUALIFICATION ADMINISTRATION / MATERIALIZATION FRACTURE
NOT A SOURCE-STANDING SCIENTIFIC RESULT
```

The geometry was not changed. The abstract coordinates were concretely bound to
the retained relation vocabulary:

```text
R*     := MOTIVATED
R_ALT  := REFERENCED_BY
```

at commit:

```text
5a7d294698e2bd6221287a74df2f6c67dba999d1
```

### SUCCESSFUL EXECUTED QUALIFICATION

Executed against exact committed bytes:

```text
python -m unittest -v tests.cockpit.test_source_standing_v0

6 tests
6 passed
0 failed
```

Environment used for the selected candidate:

```text
cryptography:
46.0.4
```

### RAW OBSERVED VECTOR

The retained raw run used exact claim:

```text
source:
S*

claim:
FROM* MOTIVATED TO*

claim sha256:
39857ce13f93d4ba2bc471992f28681658be56dba9df33cdb8df77a478c652b2

grounding public-key fingerprint:
c4486645fed7b6f35ced8562a8c536d8c0f705b22bfb30dda85ffa31fea32f36
```

Observed:

```text
P1:
ESTABLISHED
reason =
EXACT_TESTED_SOURCE_RELATION_SCOPE_STANDING_ESTABLISHED
standing sha256 =
ab68e73531c7f306c30ab030c5718f81aa47ec0cd1110f403b60abf8a3cd9c61

H1:
NOT_ESTABLISHED
reason =
NO_GROUNDED_STANDING_BASIS

H2:
NOT_ESTABLISHED
reason =
RELATION_CLASS_NOT_COVERED
standing sha256 =
eef72d7544d05cd9cd2ec7f9582f4d18e3d3a42b21ea1a6e7bf3e574f691ba07

H3:
NOT_ESTABLISHED
reason =
ENDPOINT_SCOPE_NOT_COVERED
standing sha256 =
1212930e572dd7c42ac32e7cc450e677057bb8b4c35daac0557fa658e4c07eeb

H4:
NOT_ESTABLISHED
reason =
GROUNDING_SIGNATURE_INVALID
standing sha256 =
4648b7ce46a01afb170d4f528650f735906d6cf72e8319cc8124fa0ca31db875

H5:
NOT_ESTABLISHED
reason =
JURISDICTION_NOT_COVERED
standing sha256 =
7992383fabd2bb5b3432e81716ad183c0d0da4339a26dcf58df8ace0dddd1556
```

The raw evidence artifact retains the exact signed bytes and signatures for this
run.

### H4 CONTROL OBSERVATION

The H4 fixture used one claimant harness holding two distinct Ed25519 signing
capabilities:

```text
source identity:
S*

puppet issuer:
I*

source key fingerprint:
07339ff4206c658f9d9da8beb2729893b1e95f8320a9a6885d31d576f9f5c671

puppet key fingerprint:
2f16c37bc2efffdafd0cec32758741f4365a03a5101ba220ef9a5ca9af5a7726
```

The exact retained raw evidence contains a fixed challenge plus signatures
produced by the same claimant harness under both keys.

The candidate receives no boolean saying those identities share control.

The puppet standing assertion contained the right source, jurisdiction,
relation class, and endpoint pair, but its signature did not verify under the
protected grounding public key.

Observed:

```text
H4:
NOT_ESTABLISHED
GROUNDING_SIGNATURE_INVALID
```

Thus, in this tested mechanism:

```text
ISSUER IDENTITY DIFFERENT
!=
INDEPENDENT GROUNDING
```

### SURVIVING TESTED RELATIONS

Within this exact synthetic candidate and threat model:

```text
EXACT CLAIM CONTENT
+
PROTECTED-ROOT-GROUNDED STANDING
+
RIGHT JURISDICTION
+
RIGHT RELATION CLASS
+
EXACT ENDPOINT-PAIR COVERAGE

→
SOURCE_STANDING_FOR_CLAIM = ESTABLISHED
```

The tested hostile cases preserve:

```text
NO GROUNDED STANDING
→ NOT_ESTABLISHED

VALID ROOT GROUNDING
+
WRONG RELATION CLASS
→ NOT_ESTABLISHED

VALID ROOT GROUNDING
+
RIGHT RELATION CLASS
+
OUT-OF-SCOPE ENDPOINT
→ NOT_ESTABLISHED

DISTINCT CLAIMANT-CONTROLLED PUPPET ISSUER
+
APPARENT EXACT GRANT
→ NOT_ESTABLISHED

VALID ROOT GROUNDING
+
WRONG JURISDICTION
→ NOT_ESTABLISHED
```

Therefore the tested candidate preserves:

```text
SOURCE IDENTITY
!=
SOURCE STANDING

VALID GROUNDING SIGNATURE
!=
RELATION-CLASS COVERAGE

VALID GROUNDING SIGNATURE
!=
ENDPOINT-SCOPE COVERAGE

ISSUER IDENTITY DIFFERENT
!=
INDEPENDENT GROUNDING

GENERAL / OTHER STANDING
!=
DEVELOPMENTAL-RELATION STANDING

STANDING FOR R*
!=
STANDING FOR THIS R* CLAIM
```

### IMPORTANT BOUNDARY

The qualification does not prove general control independence.

It assumes, under the authorized synthetic threat model, that the grounding
private key used to create P1/H2/H3/H5 is outside the claimant harness.

The candidate mechanically verifies the consequence of that protected root
through the pinned public key; it does not establish universal key custody,
general issuer independence, or a general standing architecture.

### CLAIM CEILING

This qualification supports only:

```text
UNDER THE TESTED THREAT MODEL,

THE EXACT TESTED PROTECTED-GROUNDING-KEY CANDIDATE
MECHANICALLY DISTINGUISHES

SOURCE S*

WITH ROOT-GROUNDED STANDING
FOR THE TESTED DEVELOPMENTAL-RELATION JURISDICTION,
RELATION CLASS MOTIVATED,
AND EXACT ORDERED ENDPOINT PAIR (FROM*, TO*)

FROM THE FIVE TESTED
NON-STANDING / WRONG-RELATION /
OUT-OF-SCOPE / PUPPET-SELF-GRANT /
WRONG-JURISDICTION CONDITIONS.
```

It does not establish:

```text
the relation is true
the claim is causally correct
the claim is adjudicated
the claim should be incorporated
the source has broader standing
the source may delegate standing
the source may expand standing
the source may self-grant future standing
general standing semantics
general scope semantics
general control semantics
a universal governance mechanism
projector correctness
held-out scientific standing
```

### HARD STOP

```text
QUALIFICATION STOP CONDITION A:
REACHED

RAW STANDING BASIS:
MECHANICALLY REPRESENTED

RAW GROUNDING / ORIGIN EVIDENCE:
MECHANICALLY REPRESENTED IN TESTED CANDIDATE

CLAIMANT-CONTROL SELF-GRANT PRESSURE:
MECHANICALLY REPRESENTED

RELATION COVERAGE:
MECHANICALLY REPRESENTED

EXACT ENDPOINT-PAIR SCOPE:
MECHANICALLY REPRESENTED

SIX-CELL VECTOR:
SURVIVES TESTED SCOPE

REPAIR:
NONE AFTER PASS

PROJECTOR INTEGRATION:
NONE

FREEZE:
NO

HELD-OUT EXECUTION:
NO

MERGE:
NO
```
