# Degraded Git-Source Admission Pressure v0

## Scope

This bounded Phase-C pass tested whether the existing foreground path can admit
and project a well-formed Git observation when real Git acquisition fails. It
separated three layers:

```text
raw Git acquisition quality
-> structural admission decision
-> downstream projection exposure
```

No trust score, confidence value, source-health ontology, comparator hierarchy,
automatic rejection, retry, fallback Git path, polling, watcher, source weight,
new admission policy, or production change was added.

Starting state was clean `main` at
`d129a6da2a617ccbc6e6a4bf871bd49768688e3e`
(`The completion of the Real Wound 4`). The current targeted baseline passed
137/137 and the full baseline passed 413/413. Canonical live history remained
protected.

## Natural Fixtures and Chart 18

| Specimen | Git acquisition | `capture_errors` | Envelope valid | Comparator | Admission | Projection | Errors directly in projection |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| C0 | successful | 0 | yes | `ingest_candidate_envelope_minimum_v0` | admitted | included | no |
| S1 | degraded | 3 | yes | `ingest_candidate_envelope_minimum_v0` | admitted | included | no |

C0 used an ordinary clean Git repository. S1 used an ordinary filesystem
directory containing `state.txt` but no `.git` directory. Both used the real
filesystem observer, real Git observer, promoted foreground coordinator, normal
ingest path, and normal projection. No observer stub or invented payload was
used.

The stable three-layer comparison earned Chart 18. Its coordinates are raw
acquisition quality, error carriage, structural schema, named comparator
decision, reconstruction recovery, projection exposure, and companion exposure.
It is not a trust or source-health policy.

## C0 — Healthy Git Control

The filesystem and Git observers returned without capture errors. Git supplied
HEAD, `main`, and clean porcelain status. Its observation envelope passed the
minimum comparator, received an admitted decision, reconstructed normally, and
entered projection. The Chart 11 companion row contained no non-admitted state.

## S1 — Natural Degraded Acquisition

In the non-Git directory, `observe_git_state()` still returned a normal
observation object. All three real commands failed:

```text
rev-parse HEAD
branch --show-current
status --porcelain=v1
```

Each error reported that the directory was not a Git repository. The raw object
contained three `capture_errors`; `head_sha`, `branch`, and `status_porcelain`
were `None`. The filesystem observation remained healthy.

The foreground call returned normally and committed four records. S1 therefore
established that a failed Git acquisition attempt can itself be represented as
well-formed historical evidence.

## Envelope and Schema

`make_git_ingest_envelope()` successfully wrapped the degraded object. The
envelope preserved errors in two places:

```text
provenance.capture_errors
signal.payload.capture_errors
```

The signal payload retained the raw null Git fields. The complete observation
record passed the schema used by `COMPARATOR_V0`.

The comparator requires record identity, commit index, envelope, integrity, an
observation record with source/provenance/observation, and an ingest observation
with `envelope_identity`, `source`, and `signal`. The signal must contain
identity, type, and payload. It does not inspect:

- Git HEAD;
- branch;
- porcelain status;
- `capture_errors`;
- semantic success of the source acquisition.

Its identity and version are:

```text
ingest_candidate_envelope_minimum
ingest_candidate_envelope_minimum_v0
```

## Admission Meaning

S1 received:

```text
decision: admitted
basis: comparison valid under comparator
```

The decision certifies structural admissibility under that named comparator. It
does not certify that Git state was successfully acquired, that null fields are
trustworthy source values, or that the represented source claim is
epistemically resolved.

The correct interpretation is:

```text
the degraded acquisition attempt was admitted as evidence
```

not:

```text
a trustworthy Git source state was certified
```

The presence of errors also does not imply that the failure evidence should be
discarded.

## Exact `capture_errors` Visibility

| Surface | Directly visible? | Detail |
| --- | --- | --- |
| Raw Git observation | yes | top-level `capture_errors` |
| Git ingest-envelope provenance | yes | copied list |
| Git ingest-envelope signal payload | yes | original raw object |
| Observation record outer provenance | no | coordinator provenance carries mode, envelope identity, observer, and version |
| Ledger nested observation provenance | yes | full ingest envelope preserved |
| Ledger nested signal payload | yes | raw Git object preserved |
| Reconstruction outer provenance | no | reflects observation-record outer provenance |
| Reconstruction nested observation provenance | yes | full ingest envelope preserved |
| Reconstruction nested signal payload | yes | raw Git object preserved |
| Admitted projection row | no | subject/admission IDs, source, and reconstruction type only |
| Chart 11 companion row | no | subject ID and non-admitted decision states only |
| Fresh `current_result()` | no | no raw captures; projection and companion contain no errors |
| Fresh authoritative reconstruction | yes | nested signal payload recovers all three errors |

The degraded condition is therefore preserved in authoritative history and
recoverable without process-local knowledge. It ceases to be directly visible
at the projection/companion and `current_result()` surfaces, which retain
navigation coordinates rather than source-quality detail.

This is a projection boundary, not erasure of authoritative information.

## Integrity, Reconstruction, and Recovery

C0 and S1 each produced four contiguous records, two observations, two
admissions, two projection subjects, and two companion rows. Both histories
passed record integrity, start-at-one continuity, canonical replay,
reconstruction, projection, companion reproduction, and source-separation
checks. Neither contained orphan admissions.

After capture, each coordinator was destroyed. A fresh coordinator received
only root and ledger path. `current_result()` was append-free and still projected
the Git subject. Independent reconstruction from replay recovered all S1 error
objects from the nested observation without failed-process state.

## Projection and Chart 11 Companion

The admitted projection included S1's Git subject but did not expose
`capture_errors`. The Chart 11 companion contained an empty non-admitted-state
list because the decision was admitted; it also did not expose source errors.

Projection membership therefore reports the existing any-admitted relationship,
not acquisition success or source trust. Consumers needing the error detail can
navigate to authoritative reconstruction using the subject identity.

## Production Contract

Existing admission wording says only that comparison was valid under the named
comparator. No coordinator, comparator, projection, or decision wording claims
that admitted Git evidence means successful Git capture. The structural
comparator behaved according to its contract, so no production defect or change
was warranted.

## Distinction

Execution independently forced and registered D-0046:

```text
structural_admissibility != source_capture_success
```

S1 combined failed acquisition, preserved errors, null Git fields, valid
minimum structure, an admitted decision, and projection membership. The
distinction creates no trust score, rejection rule, retry policy, or source
quality ontology.

## Prior Findings

D-0012, D-0016, and D-0042 through D-0045 remain supported unchanged. Chart 11
companion semantics, source separation, append-only history, and the scoped
foreground coordinator contract remain preserved. No prior result was
invalidated.

## Strongest Results

The strongest invariant is that a well-formed failed acquisition remains
integrity-valid, replayable, and fully recoverable as authoritative evidence
through reconstruction.

The strongest failure is that projection membership and an admitted decision do
not directly expose or certify the underlying Git acquisition quality.

The strongest unresolved horizon is whether a concrete projection consumer
requires direct source-quality exposure without traversing authoritative
reconstruction.

## Next Smallest Pressure

Require a concrete consumer before adding source-quality companion data, trust
policy, retry, confidence, or source ranking.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 166/166. The full suite passed 442/442.
