# PROVENANCE_RECONCILIATION_001

## STATUS

```text
INCIDENT FROZEN
RECONCILIATION: MECHANICALLY PASSED
APPARATUS QUALIFICATION: PRESSURE PASSED / RECEIPT NOT YET FROZEN
HELD-OUT REALIZATION: UNTOUCHED
```

## Authorized basis

```text
repository:
ReedBarrus/DME_Lab

frozen repaired contract:
0138cdf83192bd967ff2be961aa6011646bb5701

apparatus branch:
invocation-recovery-apparatus-v0

incident start head:
96ed2bbbe7f023ff2cd25b9868dee821bbdb1a9a

main:
8a5321c098b7f3a944e180612cd2e670b20f282e

two-lane-coordination-v0:
8a5321c098b7f3a944e180612cd2e670b20f282e
```

At incident freeze the apparatus branch was mechanically observed as:

```text
16 commits ahead of repaired contract
0 behind
merge base = repaired contract head
```

## Frozen distinctions

```text
GIT SERIALIZATION
!=
WORK COORDINATION

LINEAR HISTORY
!=
SINGLE-INVOCATION LINEAGE

CONTENT IDENTITY
!=
PROVENANCE IDENTITY

COMMIT AUTHORSHIP
!=
OCCUPANT / INVOCATION ATTRIBUTION

BYTE EQUIVALENCE
!=
PROVENANCE RECONCILIATION

NO MERGE CONFLICT
!=
NO COORDINATION CONFLICT

TWO PATHS HOLD IDENTICAL BYTES
!=
BOTH PATHS ARE CANONICAL APPARATUS INPUTS
```

## Observed from Git

Git mechanically exposes two repository path families containing the four
successor-visible common components.

### Manifest-referenced family

```text
docs/candidates/invocation_recovery_v0/apparatus/common/
  RECOVERY_ROLE_HEADER_v0.txt
  TASK_BASIS_v0.txt
  RECOVERY_TASK_INSTRUCTION_v0.txt
  RECOVERY_RESPONSE_SCHEMA_v0.txt
```

The frozen candidate manifest:

```text
docs/candidates/invocation_recovery_v0/apparatus/common/
COMMON_COMPONENT_MANIFEST_v0.json
```

references only those four paths.

Observed common-component manifest Git blob:

```text
7a0f2e832ba1c5f1d6cf15dd1f4b89381a3abe4c
```

### Concurrent residue family

```text
fixtures/invocation_recovery_v0/common/
  01_RECOVERY_ROLE_HEADER_v0.txt
  02_TASK_BASIS_v0.txt
  08_RECOVERY_TASK_INSTRUCTION_v0.txt
  09_RECOVERY_RESPONSE_SCHEMA_v0.txt
```

### Pairwise Git blob identity

```text
RECOVERY_ROLE_HEADER
fc5f06b00d5405328537d3e55ab7ba3e07f47ec4

TASK_BASIS
1d912c8556afb677fdfb3cc7ac7a2188c205e5cd

RECOVERY_TASK_INSTRUCTION
e9797fdf5e10bcb5affbe7e69afa103068d0fc5e

RECOVERY_RESPONSE_SCHEMA
78f64a50edfaeb908bb0ac7a10acfb16601d6ffa
```

Each observed pair currently shares one exact Git blob identity.

Git also exposes a linear commit history containing both path families.

That linear history is not treated as evidence that one invocation authored
both families, nor that one path family is canonical.

## Observed from execution transcript / non-Git observation

The execution transcript reports that separate work activity materialized the
second path family while another apparatus-construction trajectory was active.

This attribution is retained only as transcript evidence.

It is not strengthened into a Git-proven occupant, invocation, or ownership
claim.

```text
TRANSCRIPT ATTRIBUTION
!=
GIT-PROVEN INVOCATION PROVENANCE
```

## Candidate reconciliation relation

The only admissible canonicality criterion for this reconciliation is:

```text
CANONICAL APPARATUS INPUT
=
OBJECT REACHABLE THROUGH
COMMON_COMPONENT_MANIFEST_v0
AND ACTUALLY CONSUMED BY
THE SUCCESSOR-INPUT ASSEMBLER
```

while:

```text
CONCURRENT RESIDUE
=
BYTE-EQUIVALENT OBJECT PRESENT
IN REPOSITORY HISTORY
BUT OUTSIDE THE APPARATUS
SEMANTIC DEPENDENCY CLOSURE
```

This relation is established mechanically by the retained R1-R8 pressure
results below. Canonicality is not inferred from path preference, write order,
directory naming, commit authorship, or narrative intent.

## Required reconciliation pressures

```text
R1 manifest references only intended manifest-referenced family
R2 assembler resolves common components only through manifest closure
R3 residue path is not transitively consumed
R4 every pair is byte-identical at frozen incident specimen
R5 removing residue in isolated copy does not change A-F assembled bytes
R6 repaired contract remains exact 0138cdf...
R7 history is not rewritten and no exclusive invocation provenance is claimed
R8 semantic dependency closure is unique despite repository residue
```

## Preservation rule

The concurrent residue is retained durably.

Do not:

```text
rebase it away
force push it away
squash it away
rewrite authorship
silently delete it
claim exclusive invocation provenance
```

It remains a natural specimen for future TWO_LANE_COORDINATION_001 pressure.

## Current scientific boundary

```text
HELD-OUT SUCCESSOR MODEL INVOCATIONS:
0

HELD-OUT A-F CELLS CONSUMED:
0

SCIENTIFIC REALIZATION:
NONE
```

This artifact records the incident before apparatus qualification work proceeds.


## Mechanical reconciliation result

Executed deterministic apparatus workflow:

```text
workflow:
INVOCATION_RECOVERY_001_APPARATUS

run:
35561664941

job:
106215541780

tested apparatus head:
35386e22f5546bfa08f3a1647523472433bdf1b2

command:
python -m unittest tests.lab.test_invocation_recovery_001_apparatus -v

observed:
Ran 28 tests in 0.324s
OK
```

### R1 — manifest closure

```text
PASS
```

The manifest references only:

```text
docs/candidates/invocation_recovery_v0/apparatus/common/
```

and references no path in:

```text
fixtures/invocation_recovery_v0/common/
```

### R2 — assembler consumption

```text
PASS
```

The successor-input assembler obtains common components only through
`validate_common_component_manifest(...)` and succeeds in an isolated root
containing the manifest-referenced family with the residue family absent.

### R3 — residue outside transitive dependency closure

```text
PASS
```

In an isolated root, every residue file was replaced with poison bytes while the
manifest-referenced family was left intact.

All A-F assembled successor-input bytes remained exactly equal to baseline.

Therefore the residue path family is not transitively consumed by successor
input assembly.

### R4 — pairwise byte identity

```text
PASS
```

At the frozen incident specimen each canonical/residue pair reproduces one exact
Git blob:

```text
ROLE HEADER:
fc5f06b00d5405328537d3e55ab7ba3e07f47ec4

TASK BASIS:
1d912c8556afb677fdfb3cc7ac7a2188c205e5cd

TASK INSTRUCTION:
e9797fdf5e10bcb5affbe7e69afa103068d0fc5e

RESPONSE SCHEMA:
78f64a50edfaeb908bb0ac7a10acfb16601d6ffa
```

### R5 — residue presence/absence invariance

```text
PASS
```

A-F successor input assembly was compared between isolated roots with and
without the residue family.

Every assembled byte stream was identical.

### R6 — repaired contract unchanged

```text
PASS
```

The pressure mechanically ran:

```text
git diff --exit-code
0138cdf83192bd967ff2be961aa6011646bb5701
--
docs/candidates/invocation_recovery_v0/INVOCATION_RECOVERY_001.md
docs/candidates/invocation_recovery_v0/PRESSURE_DESIGN_001.md
```

and observed no contract-byte difference.

### R7 — incident history preserved / no exclusive provenance claim

```text
PASS
```

The four concurrent materialization commits remain ancestors of the tested
apparatus head:

```text
893695cb5f84c20d29220fad1b780220b81c3184
a7c93c7a9dc9ef891dd2f626a1c8a1476ddc9f96
8e7b58d443d3b3fa440f630c8c212cab561cf403
ec34811624ed15200c15a2c4d28881e1175f660e
```

No rebase, force push, squash, authorship rewrite, or residue deletion was used.

This artifact continues to distinguish Git-observed topology from transcript
attribution and does not claim exclusive single-invocation provenance.

### R8 — unique semantic dependency closure

```text
PASS
```

The mechanically consumed common-component dependency closure contains exactly
four unique manifest paths.

The apparatus implementation contains no dependency on the residue path family.

Poisoning residue bytes leaves successor assembly invariant.

## Reconciliation conclusion

```text
CONCURRENT MATERIALIZATION:
OBSERVED

BYTE CONFLICT:
NONE

EXCLUSIVE INVOCATION PROVENANCE:
NOT CLAIMED

APPARATUS SEMANTIC DEPENDENCY CLOSURE:
UNIQUE

CANONICAL APPARATUS INPUT:
MANIFEST-REACHABLE + ASSEMBLER-CONSUMED OBJECTS

CONCURRENT RESIDUE:
PRESERVED OUTSIDE APPARATUS DEPENDENCY CLOSURE

PROVENANCE_RECONCILIATION:
MECHANICALLY PASSED
```

The collision remains durable evidence suitable for future
TWO_LANE_COORDINATION_001 Cell Zero pressure.

## Held-out boundary after reconciliation

The same workflow explicitly verified:

```text
HELD_OUT_REALIZATION_UNTOUCHED
```

No successor model was invoked by this apparatus workflow and no A-F scientific
cell was consumed.
