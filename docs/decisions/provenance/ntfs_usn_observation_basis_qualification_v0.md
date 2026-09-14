# NTFS USN Observation-Basis Qualification v0

## Scope

This recording pass conserves the completed AA/AB qualification and selects
its first consumer question. It does not run another experiment, activate or
resolve PR-006, test hidden logical-content traversal, or introduce another
observer.

The detailed adjudication is retained in
`docs/methods/Observation_Basis/Basis_Qualification.md`; the native run is
retained in `traces/ntfs_usn_observation_basis_qualification_v0.json`.

## Adjudicated result

The qualification verdict is:

```text
LOCAL BASIS QUALIFIED
```

Both independently frozen arms completed under the declared warrant. Each
returned one associated `USN_RECORD_V2` for the same complete 64-bit file
identity with `USN_REASON_CLOSE | USN_REASON_DATA_OVERWRITE` and
`SourceInfo == 0`. Journal identity, retained range, file identity, acquisition,
and fresh lifecycle association remained valid.

The qualified basis is:

```text
identified NTFS volume
+ identified USN journal instance
+ frozen [S,E)
+ complete V2 64-bit file identity association
+ fresh controlled lifecycle
+ completed bounded V2 acquisition
+ associated CLOSE + DATA_OVERWRITE record
+ frozen SourceInfo == 0 realization
-> bounded NTFS unnamed-data overwrite-operation-category evidence
```

This is a local operation-category basis, not a generalized Windows or NTFS
observer.

## Empirically earned boundary

ARM AA retained equal A endpoints while independently returning the qualifying
operation-category record. ARM AB retained unequal A and B endpoints while
returning the same qualifying category.

Therefore the fixture empirically conserves:

```text
endpoint logical-content state
!=
NTFS overwrite-operation-category evidence
```

and directly refutes within the qualified fixture:

```text
DATA_OVERWRITE -> logical endpoint byte inequality
```

Repeat-run stability remains useful residue. It is not retroactively made a
blocker to this completed bounded qualification.

## Selected consumer fork

`Q_OPERATION` is selected:

> Between equivalent endpoint captures, did the selected file undergo at least
> one qualifying NTFS unnamed-data overwrite-category operation?

The qualified basis is fit to pressure this question without another
observation basis. No `Q_OPERATION` experiment has yet been authorized or
executed.

`Q_CONTENT` remains explicitly unresolved:

> Between equivalent endpoint captures, did the selected file's logical content
> actually depart from A and later return to A?

The current USN basis is insufficient by itself for `Q_CONTENT`. Endpoint
content plus qualified operation evidence can distinguish equal endpoints with
no demonstrated activity from equal endpoints with a qualifying overwrite
occurrence. It cannot distinguish an A -> A overwrite from an A -> B -> A
hidden content excursion.

## PR-006 standing

PR-006 remains `OPEN`. Its separately justified bounded-observation-basis
blocker is satisfied only for `Q_OPERATION`. Consumer selection does not mark
the pressure `ACTIVE`, authorize an experiment, or resolve PR-006.

No hidden traversal was executed. No new sensor, general event ontology,
composition machinery, observational geometry, constraint, chart, or
production observer is earned.

## Local and global discipline

- `LOCAL-ONLY SURVIVOR`: bounded NTFS operation-category basis.
- `LOCALLY + COMPOSITIONALLY EARNED`: operation evidence remains distinct from
  logical-content evidence.
- `BASIS INSUFFICIENT`: repeat-run recurrence and hidden logical-content
  traversal.
- `COMPOSITIONALLY COMPATIBLE`: endpoint-content evidence and operation
  evidence may remain two distinct coordinates.
- `OVERBUILT`: a general Windows event observer, shared event ontology, or
  observational geometry.

## Evidence

- `docs/methods/Observation_Basis/Warrant_Synthesis_Chat.md`
- `docs/methods/Observation_Basis/Basis_Qualification.md`
- `src/runtime/ntfs_usn_observation_basis_qualification.py`
- `tests/runtime/test_ntfs_usn_observation_basis_qualification.py`
- `traces/ntfs_usn_observation_basis_qualification_v0.json`
