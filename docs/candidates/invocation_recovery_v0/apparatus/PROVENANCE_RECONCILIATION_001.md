# PROVENANCE_RECONCILIATION_001

## STATUS

```text
INCIDENT FROZEN
RECONCILIATION: PENDING MECHANICAL PRESSURE
APPARATUS QUALIFICATION: NOT YET ATTEMPTED
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

This document does not establish that relation by assertion.

Mechanical pressures R1-R8 must establish it before the status may become
MECHANICALLY PASSED.

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
