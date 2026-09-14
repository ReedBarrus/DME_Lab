# Stale `current_result()` Semantics Pressure v0

## Scope

This bounded Phase-C pass tested the read-only operational surface
`ForegroundRepositoryObservationCoordinator.current_result()` after the
external repository changed without another capture. It separated:

```text
current derivation of authoritative history
```

from:

```text
current observation of the external repository
```

No freshness policy, threshold, polling, watcher, automatic capture, read-time
timestamp, latest-by-source production selector, temporal fusion, stale flag,
cache, world-state object, API rename, or production change was added.

Starting state was clean `main` at
`a07ef2e10661f8d1c442a817428737ef945b747c` (`Wound 2`). The current targeted
baseline passed 76/76 and the full baseline passed 352/352. Canonical live
history remained protected.

## Production Contract

The existing implementation says:

```text
Rebuild the current derived state without appending or capturing.
```

Execution matched that docstring. `current_result()` replayed the ledger,
verified integrity and continuity, rebuilt reconstruction, projection, and
companion, and returned no new records or captured observations.

The contract does not claim external-world freshness. The word `current` can be
overread by a consumer who ignores the explicit without-capture boundary, but
the existing API wording did not manufacture a world-current claim. No rename
or repair was warranted in this pass.

## Specimens and Chart 16

| Specimen | Last recorded configuration | External configuration at read | Ledger changed by read | Reconstruction / projection changed | External freshness inferable |
| --- | --- | --- | --- | --- | --- |
| C0 | clean alpha | clean alpha | no | no / no | no; equality known only by control |
| S1 | clean alpha | dirty beta | no | no / no | no |
| S2 | clean alpha | clean committed beta | no | no / no | no |
| R1 | clean alpha | clean committed beta | no | no / no | no |
| F1 | dirty beta after explicit recapture | dirty beta | no | no / no after recapture | no continued equality guarantee |

C0 used an independent clean-alpha repository. S1/F1 shared a second fixture:
S1 read stale history after an uncommitted beta rewrite, then F1 explicitly
captured beta and performed another read. S2/R1 shared a third fixture: S2 read
stale history after beta was committed, then R1 destroyed the coordinator,
opened a fresh one from only root and ledger path, and read again without
capture.

The repeatable comparison surface earned Chart 16. Its coordinates are last
recorded configuration, external configuration at read, ledger conservation,
historical derivation, coordinator lifetime, and source-freshness inference. It
is not a freshness policy or latest-state model.

## C0 — Stable Control

A normal capture committed two clean-alpha observations and two admissions.
With no intervening mutation, `current_result()` left ledger bytes, four record
indices, ordered digests, reconstruction, two-subject projection, and two-row
companion unchanged. Direct experiment control confirmed that the source still
matched alpha.

That equality remained control knowledge. Nothing in `current_result()` proved
that no source change had occurred.

## S1 — Dirty Change Without Recapture

After a successful clean-alpha capture, the external driver rewrote
`state.txt` to beta without committing. It then called only `current_result()`.

Direct control observed beta content and dirty Git status. DME returned exactly
the prior four-record clean-alpha historical derivation. Ledger SHA, record
count, commit indices, ordered digests, reconstruction, projection, and
companion were identical before and after the read. The result was stale with
respect to control truth but correct with respect to authoritative history.

## S2 — Committed Change Without Recapture

An independent fixture captured clean alpha. The external driver rewrote beta,
added it, and committed it before calling only `current_result()`.

Direct control observed beta content, a new HEAD, and clean status. Both
filesystem and Git configurations therefore differed from the last captured
evidence. DME still reproduced the prior clean-alpha history exactly, with no
append and no new source evidence. This supplied the strongest stale specimen
without intra-capture skew.

## R1 — Fresh Process, Same Stale Evidence

After S2, the original coordinator was closed and destroyed. A fresh
coordinator received only root and ledger path and called `current_result()`.
Its complete returned object and normalized historical surface equaled the S2
read. Historical recovery was perfect; source freshness did not improve.

Thus process replacement preserved D-0042 while demonstrating that a fresh
coordinator is not fresh source evidence.

## F1 — Explicit New Observation

After S1 established divergence, an explicit `capture_round()` observed dirty
beta normally. That call, not `current_result()`, advanced history:

```text
records:             4 -> 8
observations:        2 -> 4
projection subjects: 2 -> 4
companion rows:      2 -> 4
```

The four new records occupied indices 5-8. The following `current_result()` was
again append-free and exactly reproduced the newly extended history. External
control found beta equal to the newest recorded source evidence at that point,
but DME did not gain a guarantee that equality would continue after capture.

## Byte and Historical Conservation

Every `current_result()` call preserved:

- ledger SHA-256;
- record count;
- commit indices;
- ordered record digests;
- reconstruction fingerprint and counts;
- projection fingerprint and membership;
- Chart 11 companion fingerprint and rows;
- filesystem/Git source separation.

Every read remained integrity-valid, continuity-valid, replay-reproducible,
reconstructible, and projectable. Staleness was not corruption, structural
failure, or incorrect representation of history.

## Timing and Freshness Evidence

`current_result()` directly exposes no filesystem observation interval or Git
`observed_at` value because it returns projection references rather than raw
reconstruction observations. Those timestamps remain recoverable from the
authoritative observation envelopes through reconstruction.

With a caller-supplied current time and meaningful clock assumptions, a consumer
could calculate the age of recorded evidence. No age, clock identity, precision
contract, or freshness threshold is present in the returned surface. Even a
recent observation time cannot establish that the source has remained equal.

The method call time and replay time add no world knowledge. Existing evidence
cannot establish whether either source changed after its last observation.

## Projection and Companion

Before F1 recaptured the source, S1, S2, and R1 projections contained only the
previously admitted clean-alpha observations. They remained structurally
unchanged and made no `latest` or current-repository-configuration claim.

The Chart 11 companion retained one empty-state row per projected subject. The
read did not collapse filesystem and Git provenance, resolve admission
conflicts, or fuse source times.

## Consumer Interpretation

A consumer may legitimately infer:

```text
this is what DME currently derives from recorded history
```

It may not infer:

```text
this is what the repository currently is
no source change occurred after the last observation
the latest recorded observation is the latest external configuration
```

The safe meaning of `current` is derivation-relative, not world-relative.

## Distinction

Execution independently forced and registered D-0045:

```text
current_derived_history != current_external_configuration
```

S1 and S2 had equal last-capture and read-time historical surfaces while direct
control established different external configurations. R1 preserved the same
result across coordinator replacement. The distinction adds no freshness
policy, source-expiration rule, or generalized present-state ontology.

## Prior Findings

D-0042 remains supported because a fresh coordinator reconstructed the same
durable history. D-0043 remains supported because no acknowledgement evidence
was introduced. D-0044 remains supported because neither read-only derivation
nor explicit recapture creates a global snapshot guarantee. Chart 11 companion
semantics, source separation, append-only history, and the partial-round
boundary remain unchanged.

## Strongest Results

The strongest invariant is that `current_result()` deterministically and
append-freely reconstructs the same authoritative historical surface across
external divergence and coordinator replacement.

The strongest failure is that a structurally valid result can remain
arbitrarily stale with respect to an externally changed repository until a new
capture commits evidence.

The strongest unresolved horizon is that no existing returned evidence
establishes whether either source still equals its most recent recorded
observation.

## Next Smallest Pressure

Isolate the absent-interval alpha-to-beta-to-alpha round trip without adding
polling, latest-state selection, or inferred transformation history.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 104/104. The full suite passed 380/380.
