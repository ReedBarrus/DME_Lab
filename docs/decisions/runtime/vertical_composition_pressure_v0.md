# Vertical Composition Pressure v0

## Scope

This pass composed the currently earned bounded stack over one temporary Git
repository:

```text
repository reality
-> filesystem and Git capture
-> separate ingest/provenance envelopes
-> append ledger
-> integrity and continuity
-> replay
-> admission reconstruction
-> admitted projection
-> ordered-digest historical relation
```

It did not change production contracts or implementations. It added no
conflict-resolution policy, comparator hierarchy, generalized interpreter,
consequence engine, scheduler, planner, agent runtime, or persistent witness.

Starting lineage was clean `main` at
`62ceb9a7c998c9e124e765a3f5aa73f5381d8fe8`. The prior tie-order experiment
reproduced Chart 9 C2 unchanged and preserved D-0040.

## Fixture and Control

The runner creates a temporary repository containing only `state.txt`, commits
`alpha`, then captures Phase A with the real `repo_snapshot_v0` and
`git_state_v0` observers.

The Phase-A ledger contains two observation records followed by ordinary v0
admission records. Integrity and continuity pass. Reconstruction and projection
are reproducible. The two sources and their provenance identities remain
separate. An ordered four-digest witness records Phase-A history without adding
persistent witness infrastructure.

Phase B changes `state.txt` to `beta` without committing it. Filesystem capture
records the new content digest; Git capture records ` M state.txt` against the
unchanged initial commit. Both observations and their admissions extend the
same temporary ledger. The Phase-A historical relation is `RECOVERED`.

## Conflicting Admission Pressure

The Phase-B filesystem observation is evaluated twice:

- `ingest_candidate_envelope_minimum_v0`: `admitted`
- `ingest_candidate_envelope_event_time_required_v0_pressure`: `rejected`

Replay and reconstruction retain both admission records. The admitted
projection retains the subject because at least one decision is admitted, and
it exposes only the admitted admission-record ID.

This exactly follows the current projection rule. It does not establish an
admission-resolution policy. The bounded information loss is that projection
membership alone cannot distinguish uncontested admission from membership with
opposed evidence.

No actual contract claim raises unjustified certainty. The unsupported
inference exposed by composition is:

```text
projection membership
-> uncontested admission
```

## Integrity-Valid Historical Mutation

A copy of the nine-record conflict ledger changes only
`envelope.provenance.composition_pressure_mutation` on Phase-A record 1 and
recomputes its current digest. Record ID, commit index, record count, admission
references, and canonical DME_Lab history remain unchanged.

The copy passes per-record integrity and ledger continuity. Reconstruction is
structurally successful and the admitted projection is exactly unchanged. The
Phase-A ordered-digest relation is `MISMATCHED` at position 1.

The experiment therefore preserves these facts simultaneously:

```text
integrity valid
continuity valid
reconstruction structurally successful
projection unchanged
history mismatched
```

Successful reconstruction does not overwrite the historical mismatch.

## Unresolved Operation Pressure

The Phase-A witness and legitimate Phase-B extension naturally reproduce the
existing operation-recognition ambiguity. Prefix and ordered-subsequence both
accept the relation while equality does not. With two matching realizations,
operation identity remains `UNRESOLVED`; no tie-break or unique name is added.

The fixed prefix evaluator can still return `RECOVERED` for its declared
relation. Thus relation resolution remains distinct from whole-state or
operation-identity resolution.

## Chart 10

Execution earned a bounded scenario-by-coordinate matrix because every row uses
the same fixture lineage and every column keeps one stable meaning.

| Scenario | Integrity | Continuity | Historical relation | Reconstruction | Projection members | Conflict evidence | Unresolved retained |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| S0 clean Phase A | valid | valid | RECOVERED | STRUCTURALLY_SUCCESSFUL | 2 | not present | no |
| S1 legitimate Phase B | valid | valid | RECOVERED | STRUCTURALLY_SUCCESSFUL | 4 | not present | no |
| S2 conflicting admissions | valid | valid | RECOVERED | STRUCTURALLY_SUCCESSFUL | 4 | reconstruction only | yes |
| S3 prior-history mutation | valid | valid | MISMATCHED | STRUCTURALLY_SUCCESSFUL | 4 | reconstruction only | yes |
| S4 unresolved operation | valid | valid | RECOVERED | STRUCTURALLY_SUCCESSFUL | 4 | not present | yes |

Chart 10 is not a generalized state model. It is reusable only for these
declared bounded coordinates.

## Epistemic Strength Transitions

| Boundary | Information lost? | Certainty increased? | Justified? |
| --- | --- | --- | --- |
| empty capture-error evidence -> observation | no | no | yes |
| opposed admissions -> projection membership | yes | yes, membership only | yes under any-admitted rule |
| historical mismatch -> reconstruction success | no in composed result | no | yes |
| ambiguous operation -> operation identity | no | no | yes; remains UNRESOLVED |
| unresolved lower coordinate -> whole-state certainty | no | no | yes; whole certainty not claimed |

The fixture did not exercise a non-empty capture-error composition, so that
case remains open.

## Result

The answer to the success question is partial:

- `MISMATCHED`, `UNRESOLVED`, and `STRUCTURALLY_SUCCESSFUL` remain independent
  in the composed experiment.
- `RECOVERED` is asserted only under the explicit ordered-digest prefix basis.
- the admitted projection alone does not preserve the difference between
  uncontested membership and membership with opposed admission evidence.

This supports D-0041:

```text
projection_membership != admission_resolution
```

Charts 4, 6, 7, 8, and 9 remain valid under their original scopes. Composition
does not rewrite their candidate sets, bases, admissible domains, single-rule
regimes, or bounded tie linearizations.

## Next Smallest Frontier

Isolate the smallest read-only projection companion that exposes admission
disagreement without selecting comparator authority or resolving the conflict.

