# INVOCATION_RECOVERY_001 — APPARATUS QUALIFICATION_001

## STATUS

```text
DETERMINISTIC APPARATUS QUALIFICATION: PASSED
PROVENANCE RECONCILIATION: MECHANICALLY PASSED
HELD-OUT A-F REALIZATION: UNTOUCHED
SUCCESSOR MODEL INVOCATIONS: 0
SCIENTIFIC CELLS CONSUMED: 0
MERGE: NOT AUTHORIZED
```

## One-way qualification identity

This receipt pins the already-tested implementation head.

It does not require the implementation head to contain this receipt.

```text
QUALIFIED IMPLEMENTATION HEAD:
db38387562f4c9c0deba5fbd96e8a468ec518bd0

QUALIFICATION RECEIPT:
stored on a successor commit

RELATION:
QUALIFICATION RECEIPT
→ pins prior qualified implementation head
```

Therefore:

```text
IMPLEMENTATION IDENTITY
!=
RECEIPT-BEARING COMMIT IDENTITY
```

and no reciprocal content-hash relation is introduced.

## Frozen repaired contract

```text
contract branch:
invocation-recovery-contract-v0

contract head:
0138cdf83192bd967ff2be961aa6011646bb5701

contract semantic mutation during apparatus qualification:
NONE
```

The deterministic pressure mechanically verified no diff in:

```text
docs/candidates/invocation_recovery_v0/INVOCATION_RECOVERY_001.md
docs/candidates/invocation_recovery_v0/PRESSURE_DESIGN_001.md
```

against the exact repaired contract head.

## Qualified apparatus implementation identities

```text
lab/ops/candidates/invocation_recovery_001/apparatus.py
Git blob:
d6c4809fbca771b1a1b9866501b71302e42ddf01

tests/lab/test_invocation_recovery_001_apparatus.py
Git blob:
53acd40fde3aaca2dce15c24d6920669e4d22a3c

.github/workflows/invocation-recovery-001-apparatus.yml
Git blob:
05b525245892d19459f228a910b2182d917a90f8
```

## Common successor-visible component identities

The manifest-referenced common component family is:

```text
docs/candidates/invocation_recovery_v0/apparatus/common/
```

Exact identities:

```text
RECOVERY_ROLE_HEADER_v0.txt

byte_count:
458

Git blob SHA-1:
fc5f06b00d5405328537d3e55ab7ba3e07f47ec4

SHA-256:
5a2bf2b2ee3a540591e7c592fbadf2586467319a8cd5b9a4b882be92273466ec


TASK_BASIS_v0.txt

byte_count:
921

Git blob SHA-1:
1d912c8556afb677fdfb3cc7ac7a2188c205e5cd

SHA-256:
762deb3eeac111c5f30ea6fb03ea1611494cf1252043a817a1f79249dd354a96


RECOVERY_TASK_INSTRUCTION_v0.txt

byte_count:
355

Git blob SHA-1:
e9797fdf5e10bcb5affbe7e69afa103068d0fc5e

SHA-256:
0ba5965c65a2147fe013917d43371affa125076ec0a7d20d3e3eeeae62746ea2


RECOVERY_RESPONSE_SCHEMA_v0.txt

byte_count:
556

Git blob SHA-1:
78f64a50edfaeb908bb0ac7a10acfb16601d6ffa

SHA-256:
e11cd797da1d1a54351c7983fcc487912c786b9d1c981a372d32a69ed3101c6b
```

Common component manifest:

```text
docs/candidates/invocation_recovery_v0/apparatus/common/
COMMON_COMPONENT_MANIFEST_v0.json

Git blob:
7a0f2e832ba1c5f1d6cf15dd1f4b89381a3abe4c
```

The apparatus pressure verified these exact bytes before any held-out cell
consumption.

## Synthetic fixture identity

```text
lab/ops/candidates/invocation_recovery_001/
fixture_manifest_v0.json

Git blob:
87caf1e99960d18b3da3bad65ddf8cee95fef903
```

The fixture retains:

```text
H1:
0138cdf83192bd967ff2be961aa6011646bb5701

H2:
d4e3c5323eba941baa9b7b476152ec5227fb517d
```

with H2 mechanically verified as a Git descendant of H1.

No packet-applicability witness is supplied from H1 to H2.

## Frozen evaluation key identity

```text
lab/ops/candidates/invocation_recovery_001/
evaluation_key_v0.json

Git blob:
a14c6abc1b4c85486b740192a9cd504588605954
```

Scorer independence was mechanically pressured:

```text
FROZEN EVALUATION KEY
!=
SOURCE OF ITS OWN CORRECTNESS
```

For every A-F cell, the frozen key must equal an independent derivation from:

```text
packet bytes
checkpoint basis
dependency presence
semantic-debt presence
current basis evidence
coordination delta
authority witness
frozen invalidity precedence
```

Key tampering is rejected.

## Provenance reconciliation identity

```text
docs/candidates/invocation_recovery_v0/apparatus/
PROVENANCE_RECONCILIATION_001.md

Git blob:
c96a53d91c3aeb7f5c98cab28891625c2c1459e5
```

Reconciliation result:

```text
CONCURRENT MATERIALIZATION:
OBSERVED

EXCLUSIVE INVOCATION PROVENANCE:
NOT CLAIMED

CANONICAL APPARATUS INPUT:
MANIFEST-REACHABLE + ASSEMBLER-CONSUMED OBJECTS

CONCURRENT RESIDUE:
PRESERVED OUTSIDE APPARATUS DEPENDENCY CLOSURE

APPARATUS SEMANTIC DEPENDENCY CLOSURE:
UNIQUE

PROVENANCE_RECONCILIATION:
MECHANICALLY PASSED
```

The collision specimen remains in repository history.

No rebase, force push, squash, authorship rewrite, or residue deletion was used.

## Deterministic qualification command

```text
python -m unittest tests.lab.test_invocation_recovery_001_apparatus -v
```

The workflow additionally executes:

```text
python -m py_compile \
  lab/ops/candidates/invocation_recovery_001/apparatus.py \
  tests/lab/test_invocation_recovery_001_apparatus.py

test ! -e lab/ops/candidates/invocation_recovery_001/held_out_realization
```

## Qualifying CI evidence

```text
workflow:
INVOCATION_RECOVERY_001_APPARATUS

qualifying run:
35561746599

qualifying job:
106215778848

qualified head:
db38387562f4c9c0deba5fbd96e8a468ec518bd0

status:
COMPLETED

conclusion:
SUCCESS
```

Observed deterministic pressure:

```text
Ran 28 tests in 0.310s
OK
```

Observed held-out guard:

```text
HELD_OUT_REALIZATION_UNTOUCHED
```

An earlier candidate-head run also passed:

```text
run:
35561664941

job:
106215541780

head:
35386e22f5546bfa08f3a1647523472433bdf1b2

Ran 28 tests in 0.324s
OK
```

The later qualifying run is authoritative for this receipt.

## Pressure coverage

The deterministic suite passed pressure covering:

```text
common-component exact byte identities
manifest drift rejection
packet canonicalization
packet digest validation
frozen invalidity precedence
nine-component successor-input assembly
answer-leakage structural membrane
A-F fixture construction
H1 / H2 basis mechanics
raw coordination evidence
authority witness presence / absence
independent frozen-K derivation
evaluation-key correspondence
administration-invalidity detection
no-retry enforcement
raw input/output retention mechanics
observable-vector derivation
batch disposition
provenance reconciliation R1-R8
```

## Provenance reconciliation R1-R8

```text
R1 manifest references only manifest-referenced family:
PASS

R2 assembler consumes common components only through manifest closure:
PASS

R3 residue path is not transitively consumed:
PASS

R4 canonical/residue pairs are byte-identical at incident specimen:
PASS

R5 residue presence/absence cannot change A-F input bytes:
PASS

R6 repaired contract remains exact:
PASS

R7 collision history preserved / exclusive invocation provenance not claimed:
PASS

R8 semantic dependency closure is unique:
PASS
```

## No held-out realization

No qualifying test invokes a successor model.

Synthetic expected outputs used by scorer/store unit tests are deterministic
test fixtures generated locally from the frozen evaluation key. They are not
held-out successor responses and consume no A-F scientific cell.

```text
HELD-OUT SUCCESSOR MODEL INVOCATIONS:
0

HELD-OUT A-F CELLS CONSUMED:
0

HELD-OUT REALIZATION DIRECTORY:
ABSENT

LIVE SEATS INSTANTIATED:
0

LIVE CURSORS MOVED:
0

ASSIGNMENTS CREATED:
0

BELLS EMITTED:
0

WAKE OPPORTUNITIES CREATED:
0

AUTHORITY GRANTED:
0

EXTERNAL CONSEQUENCE:
NONE
```

## Qualified claim ceiling

This qualification establishes only that the deterministic
INVOCATION_RECOVERY_001 apparatus can:

```text
materialize and validate the frozen synthetic packet/fixture basis

pin and verify exact common successor-visible bytes

assemble the frozen nine-component successor input membrane

retain exact raw input/output bytes

mechanically detect administration invalidity

enforce no-retry state

derive frozen expected decisions independently from raw mechanics

score structured outputs against the frozen key

derive the frozen observable vector

derive the frozen batch disposition

and mechanically recover one unique apparatus semantic dependency closure
despite preserved concurrent byte-identical repository residue
```

It does not establish:

```text
held-out recovery success
same-class recovery success
replacement-class recovery success
stale-basis detection by a successor model
coordination-invalidity detection by a successor model
missing-dependency detection by a successor model
missing-semantic-debt detection by a successor model
general model interchangeability
general agent persistence
authority inheritance
live scheduling
live continuity
or autonomous execution
```

Those remain untouched held-out pressure.

## Terminal apparatus state at qualification

```text
CONTRACT:
UNCHANGED

PROVENANCE INCIDENT:
PRESERVED

PROVENANCE RECONCILIATION:
MECHANICALLY PASSED

APPARATUS:
DETERMINISTICALLY PRESSURED

APPARATUS QUALIFICATION:
PASSED

APPARATUS IMPLEMENTATION IDENTITY:
db38387562f4c9c0deba5fbd96e8a468ec518bd0

HELD-OUT REALIZATION:
UNTOUCHED

SUCCESSOR MODEL INVOCATIONS:
0

SCIENTIFIC CELLS CONSUMED:
0

MERGE:
NO
```
