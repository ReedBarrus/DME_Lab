# EDGE_SOURCE_STANDING_001

## PROTECTED GROUNDING KEY CANDIDATE v0

### STATUS

```text
BOUNDED MECHANISM CANDIDATE
SYNTHETIC QUALIFICATION ONLY
PROJECTOR UNTOUCHED
NO HELD-OUT FREEZE
NO HELD-OUT EXECUTION
NO SCIENTIFIC PROMOTION
NO MERGE
```

### SOURCE BASIS

```text
source branch:
concordance-cockpit-v0-edge-entitlement-candidate

source head:
184e7ddfc2f659dc275fdb98f8b331b72aba9382

surviving fracture:
EXACT CLAIM DECLARED
!=
CLAIM SOURCE ENTITLED
```

### SELECTED CANDIDATE MECHANISM

The smallest executable candidate uses exactly one protected grounding signing
capability and one verifier-pinned Ed25519 public key.

The grounding private key is qualification-fixture state outside the claimant
surface. It is never accepted by the evaluator as caller input.

A standing basis is durable bytes containing only:

```text
schema_version
grant_id
source_ref
issuer_ref
issuer_key_fingerprint
jurisdiction
relation_classes[]
endpoint_pairs[]
```

plus a detached Ed25519 signature.

The evaluator derives only:

```text
SOURCE_STANDING_FOR_CLAIM:
ESTABLISHED
|
NOT_ESTABLISHED
```

It does not receive:

```text
independent
grounding_accepted
claimant_controls_issuer
standing_valid
authorized
cell_id
expected_result
```

### RAW MECHANICAL COORDINATES

```text
RAW STANDING BASIS:
exact standing JSON bytes

RAW GROUNDING / ORIGIN EVIDENCE:
detached signature verified under the evaluator-pinned grounding public key

CONTROL-INDEPENDENCE CARRIER:
the protected grounding private key is absent from the claimant harness;
the claimant harness separately controls both S* and a distinct puppet issuer I*
and can exercise both claimant-held signing capabilities.

RELATION COVERAGE:
exact membership of R* in signed relation_classes

SCOPE COVERAGE:
exact ordered pair (FROM*, TO*) in signed endpoint_pairs
```

Control independence is therefore not represented by:

```text
issuer_ref != source_ref
```

and the issuer label itself has no standing effect.

### BOUNDED TRUST / THREAT ASSUMPTION

This candidate assumes only for this synthetic qualification that the protected
grounding private key is outside the claimant-controlled surface.

The apparatus pressures a claimant that may generate arbitrary alternate keys,
identities, labels, digests, claim bytes, standing bytes, and a puppet issuer
identity under the same claimant harness.

This candidate does not prove universal key custody or general control
semantics.

### DERIVATION

For an exact claim C* = (FROM*, R*, TO*) from S*:

```text
exact claim content established
AND
standing basis present
AND
standing signature verifies under pinned grounding public key
AND
issuer_key_fingerprint matches that pinned public key
AND
standing.source_ref == S*
AND
standing.jurisdiction == DEVELOPMENTAL_RELATION_ISSUANCE
AND
R* is explicitly covered
AND
(FROM*, TO*) is explicitly covered

→ SOURCE_STANDING_FOR_CLAIM = ESTABLISHED
```

Any failed predicate returns NOT_ESTABLISHED.

### NON-COLLAPSES

```text
VALID SIGNATURE
!=
RIGHT RELATION CLASS

VALID SIGNATURE
!=
RIGHT ENDPOINT SCOPE

DISTINCT ISSUER ID
!=
INDEPENDENT GROUNDING

ROOT-GROUNDED STANDING
!=
CLAIM TRUE

SOURCE_STANDING_FOR_CLAIM
!=
GLOBAL AUTHORITY
```

### SCOPE CARRIER

Only exact ordered endpoint-pair membership is implemented.

No wildcard, range, namespace, hierarchy, inheritance, graph-neighborhood,
role-scope, or lattice semantics exist.

### QUALIFICATION CELLS

The candidate must execute the authorized six-cell synthetic geometry exactly:

```text
P1 → ESTABLISHED
H1 → NOT_ESTABLISHED
H2 → NOT_ESTABLISHED
H3 → NOT_ESTABLISHED
H4 → NOT_ESTABLISHED
H5 → NOT_ESTABLISHED
```

H3 is also the mandatory composite counterfeit:

```text
valid source
+ real root-grounded standing
+ right relation class
+ wrong exact endpoint pair
→ NOT_ESTABLISHED
```

H4 must use one claimant harness that can mechanically exercise signing
capabilities for both S* and a distinct I*. Its standing assertion must contain
the right source, relation class, jurisdiction, and endpoint pair, but be signed
only by the claimant-controlled puppet key.

### CLAIM CEILING

A PASS may support only that, under this exact tested threat model, this exact
candidate distinguishes the tested root-grounded source/relation/exact-scope
case from the five tested non-standing, wrong-standing, and out-of-scope
conditions.

It does not establish relation truth, adjudication, incorporation, broader
standing, delegation, self-expansion, general scope/control/standing semantics,
a governance mechanism, projector correctness, or held-out scientific standing.

### STOP

Materialize candidate, synthetic fixtures/tests, execute qualification, retain
exact identities and result, then stop on PASS or first fracture. Do not repair
past that stop.
