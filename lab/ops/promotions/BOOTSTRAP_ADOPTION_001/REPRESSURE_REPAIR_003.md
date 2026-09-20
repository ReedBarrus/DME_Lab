# BOOTSTRAP_ADOPTION_001 — REPRESSURE_REPAIR_003

## Status

```text
PRIOR COMMANDER DISPOSITION:
REQUIRE_REPRESSURE

REPAIR_002 SURVIVING CLOSURES:
AUTHORITY TYPE
TERMINAL GEOMETRY
SELF-GOVERNANCE NONCLAIM

REPAIR_002 SURVIVING FRACTURES:
MUTUAL CONTENT-HASH CYCLE
TERMINAL RECEIPT CHAIN CONSERVATION

REPAIR_003 SCOPE:
IDENTITY TRANSPORT ONLY

FRESH REPRESSURE:
NOT YET PERFORMED

BOOTSTRAP AUTHORITY:
NONE

PREFLIGHT:
NOT RUN

EXECUTION:
NO

ADOPTION:
NO

BOOTSTRAP_CONSUMED:
false
```

## Governing repair laws

```text
ONE-WAY CONTENT ADDRESSING
!=
MUTUAL CONTENT-ADDRESS CYCLE

REFERENCE PRESENT
!=
REFERENCE CONSERVED

RECEIPT VERIFIER IDENTITY
!=
RECEIPT CHAIN VALIDITY
```

## Repair A — acyclic preflight identity

The bootstrap object pins the exact preflight implementation:

```text
tools/bootstrap_adoption_preflight_v0.py
blob:
fc506070475e6e506f144f8652ff4ffeb000eebd
```

The exact preflight no longer embeds any bootstrap-object content hash.

Instead it:

```text
consumes actual bootstrap-object bytes
→ derives actual bootstrap-object Git blob
→ compares review.bootstrap_object_git_blob_sha
   against that derived identity
→ compares authorization.bootstrap_object_git_blob_sha
   against that derived identity
```

The dependency is therefore:

```text
BOOTSTRAP OBJECT
→ pins PREFLIGHT IMPLEMENTATION

PREFLIGHT
→ derives BOOTSTRAP OBJECT IDENTITY
```

not:

```text
BOOTSTRAP OBJECT HASH
↔
PREFLIGHT IMPLEMENTATION HASH
```

## Repair B — executable terminal chain conservation

Added:

```text
tools/bootstrap_adoption_receipt_verifier_v0.py
```

Exact verifier blob:

```text
7aa3bbeff12b79facf1b6faecf825609772776f4
```

The bootstrap object pins that verifier implementation.

The verifier consumes actual bytes for:

```text
protocol
bootstrap object
review
authorization
preflight
receipt
preflight implementation
verifier implementation
```

and derives their Git blob identities.

It checks:

```text
actual protocol
↔ bootstrap object

actual preflight implementation
↔ bootstrap object

actual verifier implementation
↔ bootstrap object

actual review
↔ protocol + bootstrap object

actual authorization
↔ review + protocol + bootstrap object

actual preflight
↔ authorization + review + protocol + bootstrap object

actual receipt
↔ preflight + authorization + review + protocol + bootstrap object
```

The verifier does not hardcode:

```text
bootstrap-object blob
review blob
authorization blob
preflight artifact blob
receipt blob
```

Those are derived from supplied bytes.

## Repair C — receipt / verifier division

The receipt schema retains terminal-state geometry and now also requires:

```text
terminal_chain_verification_required = true

terminal_chain_verifier_git_blob_sha =
7aa3bbeff12b79facf1b6faecf825609772776f4
```

The receipt does not contain a self-declared verifier PASS.

A separate typed verification result is carried by:

```text
schemas/bootstrap_adoption_receipt_verification_v0.schema.json
```

A PASS verification requires every declared chain-consistency check to PASS.

This preserves:

```text
RECEIPT SCHEMA VALID
!=
RECEIPT CHAIN VERIFIED
```

and:

```text
VERIFIER EXISTS
!=
VERIFIER PASSED
```

## Acyclic dependency order

```text
PROMOTION_PROTOCOL_v0
        ↓
PREFLIGHT IMPLEMENTATION
TERMINAL CHAIN VERIFIER
        ↓
BOOTSTRAP OBJECT
        ↓
REVIEW / AUTHORIZATION / PREFLIGHT / RECEIPT SHAPES
        ↓
TERMINAL CHAIN VERIFICATION RESULT
```

No required content-address edge points back upstream.

## Exact Repair 003 identities

```text
PROMOTION_PROTOCOL_v0
c6cebdc70c07816167ff9499b5690fcb16b4354e

BOOTSTRAP_ADOPTION_001 object
982b471694d6e0c218ebd60b2f22db2466626780

bootstrap_adoption_object_v0 schema
305c3876cb8b6287b10dbaa3bdf38b84558e4a47

bootstrap_adoption_review_v0 schema
b21d33ba743605ec51ac871fb0b640db92711b4a

bootstrap_adoption_authorization_v0 schema
ad7b30b5a28ddea9a21315d5aa605e13c50f2776

bootstrap_adoption_preflight_v0 schema
a77ba6e5e3a282d66a918f0be94e0b5cf8d276f4

bootstrap_adoption_receipt_v0 schema
b0de62fd6d7e2465c3da195d7ea6ebea15614b75

bootstrap_adoption_receipt_verification_v0 schema
ab69c407d831abc5faab7fb58df2d3d42500afce

bootstrap_adoption_preflight_v0.py
fc506070475e6e506f144f8652ff4ffeb000eebd

bootstrap_adoption_receipt_verifier_v0.py
7aa3bbeff12b79facf1b6faecf825609772776f4
```

## Nonclaims

Repair 003 does not claim:

```text
fresh review passed
bootstrap authority exists
preflight ran
receipt verifier ran
execution occurred
protocol was adopted
bootstrap was consumed
Article 0 was ratified
scientific standing changed
PR #30 should merge
```

## Next lawful operation

```text
EXACT REPRESSURE_REPAIR_003 SURFACE
→ FRESH INDEPENDENT REPRESSURE
```

No later authority is inferred.
