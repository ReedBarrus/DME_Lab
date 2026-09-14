# Absent-Interval Round-Trip Pressure v0

## Scope

This bounded Phase-C pass compared true stasis with a real but unobserved
alpha-to-beta-to-alpha excursion between two normal captures. It asked whether
equivalent source-relative endpoints license a claim that no intervening
transformation occurred.

No polling, watcher, event synthesis, transition inference, source journal,
change service, temporal fusion, latest-state model, global clock, no-change
record, excursion marker, filesystem hook, Git reflog interpretation, round
identity, or persistent session identity was added.

Starting state was clean `main` at
`938d6f7e48443252d78c193aaf7f129ee5dca26e` (`WOund 4`). The current targeted
baseline passed 104/104 and the full baseline passed 380/380. Canonical live
history and production capture code remained protected.

## Deterministic Fixture

Each independent temporary Git repository began as clean committed alpha with
one tracked `state.txt`. Its mtime was fixed at `946684800000000000` ns before
the initial commit so filesystem identity could be restored exactly.

The external driver owned every mutation and performed none during a capture:

```text
C0: alpha -> alpha
S1: alpha -> beta -> alpha
S2: alpha -> beta
```

For S1, the driver recorded beta content and dirty Git status, restored alpha
content, restored the original `mtime_ns`, and confirmed clean Git status before
the second capture. The excursion knowledge was never written to DME history.

## Chart 17

| Specimen | Control-known path | Filesystem endpoint relation | Git endpoint relation | Observation occurrences | Interval-path inference |
| --- | --- | --- | --- | --- | --- |
| C0 | alpha, alpha | equivalent | equivalent | distinct | unresolved |
| S1 | alpha, beta, alpha | equivalent | equivalent | distinct | unresolved |
| S2 | alpha, beta | different | different | distinct | endpoint change visible; intermediate path unresolved |

The stable comparison earned Chart 17. Its coordinates are control-known path,
filesystem endpoint relation, Git endpoint relation, observation occurrence,
reconstruction, projection, and intervening-transformation inference. It is not
a recurrence or transformation model.

## C0 — True Stasis Control

Two ordinary captures with no mutation produced equal filesystem configuration
surfaces and equal Git configuration surfaces. The filesystem snapshot,
snapshot identity, path, kind, size, hash, `mtime_ns`, scope, and capture-error
state all repeated. Git HEAD, branch, porcelain status, and capture-error state
also repeated.

The captures still committed different observation records at indices 1-2 and
5-6, followed by their admissions. Capture timestamps and record digests
differed. DME could establish equivalent captured endpoints across distinct
occurrences, but could not prove that the interval was static.

## S1 — Hidden Round Trip

After the first clean-alpha capture, the external driver wrote beta and observed
its content hash plus dirty Git status. Without any DME capture, it then wrote
alpha, restored the original mtime, and returned Git to the original clean HEAD
and branch configuration.

The second real capture reproduced the first filesystem configuration exactly,
including snapshot identity:

```text
repo-snapshot-v0:c66b6b6f5a1373a95168c525bec8aa242bfa68cfd508a88575244fab9aa5eb6c
```

The Git configuration was also exactly equivalent. Like C0, S1 produced new
records, commit indices, timestamps, and digests. Its filesystem source and
envelope identities repeated because structural identity repeated; its Git
source and envelope identities changed because current Git identity includes
`observed_at`.

Experiment control knew an excursion occurred. Authoritative DME evidence knew
only two equivalent endpoint configurations at distinct observation
occurrences. The intervening path remained unresolved.

## S2 — Visible Endpoint Difference

S2 left beta in place before the second capture. The filesystem observer changed
snapshot identity, content hash, size, and mtime. Git preserved HEAD and branch
but changed from clean to dirty status. Both source bases therefore detected the
ordinary endpoint difference.

This control demonstrated that the observers were capable of detecting a
present endpoint difference. It did not make the complete intermediate path
available.

## Configuration and Occurrence

For C0 and S1:

```text
same source-relative configuration
different observation occurrence
```

Each history contained eight records, four observations, four admissions, and
four projected subjects. Record IDs, commit indices, capture timestamps, and
digests distinguished the occurrences. They did not establish why the same
configuration appeared twice.

Raw C0 and S1 ledgers were not byte-equal because independently acquired
occurrences carry different times and digests. After separating ordinary
occurrence coordinates from configuration, both exposed the same captured
filesystem and Git configuration sequence. Occurrence multiplicity therefore
did not distinguish stasis from hidden excursion.

## Timing Evidence

Filesystem start/finish timestamps and Git `observed_at` values established two
separate capture occurrences. Elapsed time between them did not establish that
a transformation occurred. Equal endpoints plus later timestamps also did not
establish recurrence through an excursion.

No observation existed during S1's beta interval. The driver's mutation times
were not historical evidence.

## Integrity, Reconstruction, and Recovery

Every specimen passed integrity, start-at-one continuity, canonical replay,
reconstruction, projection, companion, and source-separation checks. Every
second capture returned normally.

After the second capture, each coordinator was destroyed. A fresh coordinator
received only root and ledger path and called `current_result()`. It recovered
eight records and four observations without appending. No process-local driver
path or hidden-excursion flag survived because none was part of DME evidence.

## Projection and Chart 11 Companion

Projection preserved all four admitted observation subjects in every specimen,
including both occurrences of equivalent C0 and S1 configurations. It did not
collapse repeated observations or claim stasis, recurrence, supersession, or a
current coherent world.

The Chart 11 companion remained reproducible with one empty-state row per
projected subject. Filesystem and Git provenance remained separate.

## C0 Versus S1

Authoritative histories could distinguish C0 and S1 as independent occurrence
instances through timestamps and digests. They could not distinguish the
relevant interval predicate:

```text
true stasis
versus
unobserved excursion returning to the same endpoints
```

DME could infer neither that nothing happened in C0 nor that something happened
in S1. Two observations did not imply a transformation; equal configurations
did not imply no transformation.

## Information Boundary

No captured observation information was lost. The beta excursion was never
observed and therefore never entered authoritative history. Its absence is not
DME corruption or loss of previously held evidence; the transformation lay
outside the current observation basis.

## Distinctions and Prior Findings

No distinction was added or amended. Existing D-0012 is sufficient:

```text
snapshot != complete_transformation_history
```

The executed round trip strengthens its evidence without requiring the
attractive but redundant wording `same_observed_endpoint !=
no_intervening_transformation`.

D-0016 remains sufficient for configuration versus occurrence. D-0042 through
D-0045 remain supported unchanged. Chart 11 companion semantics, source
separation, append-only history, and the scoped production coordinator contract
remain preserved.

## Production Contract

No current production wording claims that equivalent endpoints prove an
unchanged interval. No production defect or behavior change was found.

## Strongest Results

The strongest invariant is that equivalent source-relative configurations
remain legible as distinct admitted observation occurrences without overwriting
or collapsing history.

The strongest failure is that endpoint observations alone cannot distinguish
true stasis from an unobserved excursion returning to the same observable
configuration.

The strongest unresolved horizon is that the transformation path inside an
interval with no observation remains unknowable from the current endpoint-only
evidence basis.

## Next Smallest Pressure

Isolate degraded Git-source admission without adding polling, recurrence
operators, or autonomous observation.

## Canonical History

`traces/live_ingest_ledger_v0.jsonl` remained unchanged at SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Verification

Final targeted tests passed 137/137. The full suite passed 413/413.
