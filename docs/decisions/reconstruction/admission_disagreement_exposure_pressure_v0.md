# Admission Disagreement Exposure Pressure v0

## Scope

This pass isolates one seam:

```text
authoritative replay
-> admission reconstruction
-> admitted projection
-> read-only admission-decision companion
```

Starting state was clean `main` at
`60a185eb89fbcd46aaf6a801e8b44f23e2d2e732`. Baseline targeted tests passed
31/31 and the full suite passed 234/234.

The experiment did not use or modify `docs/projection/Persistent_Ecology.md`.
It did not change current any-admitted projection semantics or canonical live
history.

## Specimens

One temporary JSONL ledger used existing observation/admission APIs to produce:

| Specimen | Reconstructed decisions | Projection member |
| --- | --- | --- |
| S0 | admitted | yes |
| S1 | admitted, rejected | yes |
| S2 | admitted, unresolved | yes |
| S3 | admitted, rejected, unresolved | yes |
| S4 | admitted, admitted | yes |
| X0 exclusion | rejected | no |

The normal comparator produced `admitted`, the event-time-required comparator
produced `rejected` for the deliberately absent event time, and an unavailable
comparator produced `unresolved`.

All five specimens containing an admitted decision remained members under the
existing projection. X0 did not enter the projection.

## Candidate Ladder

The executed candidates were:

- C0: current projection membership only
- C1: generic disagreement flag
- C2: unique non-admitted decision states
- C3: counts for each decision state
- C4: admission record IDs grouped by decision
- C5: complete reconstructed admission evidence

Because the companion accompanies admitted projection membership, `admitted`
is already established by the projection. C2 therefore preserves only the
additional states `rejected` and `unresolved`. An empty list explicitly marks a
projected subject with no tested non-admitted state.

## Chart 11

Execution earned a stable candidate-by-criterion surface.

| Candidate | Projection unchanged | Rejected visible | Unresolved visible | Required patterns separated | Multiplicity | Evidence navigable | Adds resolution | Sufficient |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0 projection only | yes | no | no | no | no | yes, via subject ID | no | no |
| C1 generic flag | yes | no | no | no | no | yes, via subject ID | no | no |
| C2 unique non-admitted states | yes | yes | yes | yes | no | yes, via subject ID | no | yes |
| C3 decision counts | yes | yes | yes | yes | yes | yes, via subject ID | no | yes |
| C4 grouped admission IDs | yes | yes | yes | yes | yes | yes | no | yes |
| C5 full admission evidence | yes | yes | yes | yes | yes | yes | no | yes |

C0 cannot expose disagreement. C1 distinguishes uncontested from opposed
evidence but maps S1, S2, and S3 to the same `true` value, collapsing rejected,
unresolved, and mixed evidence.

C2 is the first sufficient representation. C3 through C5 add multiplicity,
direct admission-record identity, or copied comparator/provenance detail. Those
dimensions are real, but the declared question does not require them.

Selection did not use implementation convenience, field-count preference,
naming, UI anticipation, or a tie-break. It followed the executed
information-preservation ladder.

## Evidence Recovery

Every companion row retains `subject_record_id`. Existing reconstruction
supports this exact navigation path:

```text
companion.subject_record_id
-> reconstruction observation_record_id
-> admissions
-> complete comparator, comparison, decision, and basis evidence
```

No guessing is required. Duplicating admission-record IDs or full provenance in
C2 adds no required recoverability under this bounded reconstruction.

## Promotion

After the experiment-local ladder selected C2, the narrow pure derivation
`derive_non_admitted_decision_states(...)` was promoted beside
`derive_admitted_projection(...)`.

The function:

- returns one row per current projection member, in projection order
- exposes unique `rejected` and `unresolved` states
- does not count or rank evidence
- does not choose a comparator
- does not resolve disagreement
- does not mutate reconstruction or projection
- performs no ledger or canonical-history write
- creates no authoritative state or persistent store

The existing admitted-projection function is behaviorally unchanged.

## Result

The smallest sufficient tested companion is:

```text
subject_record_id
non_admitted_decision_states: [] | [rejected] | [unresolved] | [rejected, unresolved]
```

This sharpens D-0041 without requiring a new distinction:

```text
projection_membership != admission_resolution
```

Evidence exposure remains non-adjudicating. No comparator hierarchy, conflict
policy, voting, confidence, trust, scheduler, agent, generalized view system,
or persistent ecology machinery was added.

Charts 4 through 10, D-0040, D-0041, reconstruction semantics, any-admitted
projection semantics, and canonical live history remain preserved under their
original scopes.

## Unresolved Horizon

Multiplicity and direct admission-record identity remain available through
larger candidates and existing reconstruction. No current decision-relevant
pressure establishes that either belongs in the companion.

## Next Smallest Frontier

Ask whether a concrete read-only consumer requires multiplicity or direct
admission-record identity beyond the selected unique non-admitted states. Do
not expand the representation without that pressure.

