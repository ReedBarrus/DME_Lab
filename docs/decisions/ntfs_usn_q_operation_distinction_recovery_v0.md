# NTFS USN Q_OPERATION Distinction Recovery v0

## Scope

This decision records the completed first PR-006 `Q_OPERATION` pressure. It
compresses the committed trace and the preserved Astra adjudication without
rerunning the fixture, changing the qualified USN basis, or pressuring
`Q_CONTENT`.

## Consumer question

> Between equivalent endpoint captures, did the selected file undergo at least
> one qualifying NTFS unnamed-data overwrite-category operation?

## Executed pair

| Arm | Controlled history | Endpoint result | USN result |
| --- | --- | --- | --- |
| S | A with no selected-file intervention to A | C0 = A; C1 = A | no positive qualifying witness retained; S = E |
| O | A through one synchronous same-length A -> A overwrite to A | C0 = A; C1 = A | one associated V2 `CLOSE + DATA_OVERWRITE` record; matching complete file identity; `SourceInfo == 0`; acquisition reached frozen E |

Endpoint-content observation collided. The qualified USN coordinate positively
exposed ARM O.

## Adjudication

```text
Q_OPERATION DISTINCTION RECOVERY PASSES
Q_OPERATION: BOUNDEDLY RESOLVED
```

Supported Claim A:

> Two controlled endpoint-equivalent histories were produced, and the
> qualified USN coordinate positively exposed the overwrite history.

Unsupported stronger Claim B:

> The observer symmetrically demonstrated quiet stasis versus operation over
> comparable nontrivial intervals.

ARM S had `S == E`. Its completed acquisition and empty witness result are
vacuous for the empty journal interval. ARM S remains a valid controlled
no-intervention comparator because its history comes from fixture control, but
it does not demonstrate nontrivial quiet observation. No rerun is required for
Claim A; the minimum repair is none.

## Negative completeness

The pressure does not earn:

```text
no qualifying witness -> no operation occurred
```

ARM O supplies a qualified positive. ARM S supplies no qualified positive, and
its known no-intervention history comes from controlled-history provenance.
No scoped or general negative-completeness rule is established.

## Bounded stitched distinction

Endpoint-content observation, qualified NTFS operation evidence, and
controlled-history provenance jointly recover:

```text
equal endpoint content with controlled no-intervention provenance
!=
equal endpoint content with demonstrated overwrite-category activity
```

This is a bounded stitched distinction, not generalized composition
machinery.

## PR-001 relation

The result recovers one bounded operational distinction hidden by the selected
endpoint-content basis: an added qualified operation coordinate can positively
expose activity that endpoint content leaves invisible.

PR-001 remains bounded by:

```text
endpoint equivalence != complete transformation history
```

The pressure did not recover PR-001's hidden alpha -> beta -> alpha path or
reconstruct intermediate content.

## Remaining standing

`Q_CONTENT` remains:

```text
UNRESOLVED — NOT PRESSURED
```

The smallest remaining invisible distinction is:

```text
A -> A overwrite
!=
A -> B -> A hidden logical-content excursion
```

The qualified USN operation basis cannot distinguish those by itself. Broader
PR-006 therefore remains `OPEN`; recording the bounded `Q_OPERATION` result
does not globally close or activate it.

## Local and global discipline

- Endpoint collision: `LOCAL-ONLY SURVIVOR`.
- Positive operation witness: `LOCAL-ONLY SURVIVOR`.
- `Q_OPERATION` differential recovery: `LOCAL-ONLY SURVIVOR`.
- Symmetric stasis-versus-operation observation: `BASIS INSUFFICIENT`.
- Negative completeness: `BASIS INSUFFICIENT`.
- Bounded endpoint plus operation stitching: `LOCALLY + COMPOSITIONALLY EARNED`.
- `Q_CONTENT`: `BASIS INSUFFICIENT`.
- Generalized NTFS/Windows observation: `OVERBUILT`.
- Observational geometry: `OVERBUILT`.

No new runtime, sensor, event ontology, geometry, atlas, chart, constraint, or
general observer is earned.

## Evidence

- `traces/ntfs_usn_q_operation_pressure_v0.json`
- `src/runtime/ntfs_usn_q_operation_pressure.py`
- `tests/runtime/test_ntfs_usn_q_operation_pressure.py`
- `docs/methods/Observation_Basis/Astra_Q_OPERATION_Adjudication.md`
- `docs/decisions/ntfs_usn_observation_basis_qualification_v0.md`
