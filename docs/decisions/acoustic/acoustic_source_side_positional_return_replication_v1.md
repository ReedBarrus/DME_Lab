# Acoustic Source-Side Positional Return Replication v1

## Scope and repository gate

This independently selected replication asks PR-019 again under a newly
declared quiet endpoint condition:

> Under a recurrent independently observed post-mix endpoint relation and a
> fixed microphone, does controlled speaker A1 -> B -> A2 displacement produce
> a discriminable B microphone realization and return recurrence toward A1?

It is not a contamination-comparison experiment, PR-018, prospective
cross-domain prediction, tomography, generalized acoustics, or production
observer work.

After `git fetch origin main`, the authoritative starting `HEAD` and
`origin/main` were identical at
`dbaa52a043bde027bb7dfeabde8422a685338149`. The worktree was clean. Concurrent
cockpit and controller documentation at that commit was preserved unchanged.

## Independent lineage

The prior PR-019 decision and trace remain unchanged. The new trace records the
prior trace SHA-256
`333aeffb52f54915f358ec96940ab715f3d24467fb532c5b9dcb5da722a2fcd2`
and its status `source_side_positional_return_evidence_insufficient` as lineage,
not calibration.

No prior measurement changed the waveform, amplitude, bins, metrics,
thresholds, positions, trial timing, exclusions, or expected direction. The
replication was adjudicated before any retrospective comparison.

## Quiet-source and operator basis

The frozen operator declaration was:

```text
no known intentional unrelated endpoint playback initiated by the operator
```

The operator reported that a computer game was present but paused with its
audio off. This declaration does not establish a physically silent room or a
perfectly isolated render path. The independently captured WASAPI endpoint
remained the source gate.

The original PR-019 marks were reused:

- Realtek room speaker at the original marked A/A1 position;
- B/B1 approximately 8 inches from A in the previously declared lateral
  direction;
- XIBERIA microphone position, orientation, support, and cable fixed for the
  complete primary sequence;
- speaker height and orientation preserved as closely as the marks allowed;
- gain, routing, device configuration, and physical settings unchanged.

The A/B geometry and fixed-microphone configuration are operator provenance,
not machine-measured coordinates.

## Frozen preflight and protocol

One preflight was sufficient. It acquired endpoint packets and a complete
microphone buffer with no capture errors. Median microphone supported-band
response was `6.172974` dB over pre-roll, passing the unchanged 6 dB preflight
criterion. No retry or adjustment occurred.

The protocol then froze before A1:

- 180 ms, 700-1700 Hz Hann-windowed linear chirp;
- 0.020 full-scale amplitude on the right output lane;
- 750 ms paired capture with 200 ms nominal pre-roll;
- ten bins from 750 through 1650 Hz;
- absolute source-normalized microphone response in dB;
- RMS Euclidean distance and coordinate-wise median centroids;
- endpoint maximum shape distance no greater than 0.75 dB and mean-level range
  no greater than 1.0 dB;
- B distance greater than 1.5 dB and three times the larger A1/B
  within-position median distance;
- A2 closer to A1 than B, A1-to-A2 no greater than half A1-to-B, and at least
  four of five A2 trials individually closer to A1.

## Primary acquisition

Exactly five A1, five B, and five A2 trials were captured and retained. No
trial was excluded, relabeled, or repeated.

| Block | Complete trials | Within-position median absolute distance |
| --- | ---: | ---: |
| A1 | 5/5 | 4.989712 dB |
| B | 5/5 | 3.106452 dB |
| A2 | 5/5 | 3.926156 dB |

Primary evidence retained:

- 15 distinct endpoint PCM hashes and 15 distinct microphone PCM hashes;
- 15 distinct external watcher PID values across 15 watcher invocations;
- 74-75 endpoint packets per trial and 539,520 endpoint frames total;
- zero endpoint, microphone, or orchestration failures;
- no retained raw endpoint or microphone PCM.

Each trial independently observed post-mix Realtek endpoint PCM through a fresh
separate-process WASAPI shared-mode loopback watcher and XIBERIA microphone PCM
through the existing WinMM observer. Position labels were joined after capture.

## Endpoint source gate

Both frozen source criteria passed:

| Criterion | Required | Observed | Result |
| --- | ---: | ---: | --- |
| maximum endpoint shape pair distance | <= 0.75 dB | `4.291113e-6` dB | passed |
| endpoint mean-level range | <= 1.0 dB | 0.116591 dB | passed |

This licenses the post-mix relation as recurrent under the declared basis. It
does not establish driver receipt, physical speaker output, or endpoint
isolation beyond the retained observations.

## B discrimination and A2 recurrence

The frozen absolute-response centroid distances were:

| Comparison | Distance |
| --- | ---: |
| A1 to B | 19.932989 dB |
| A1 to A2 | 9.170599 dB |
| A2 to B | 14.378831 dB |

B required more than `14.969136` dB separation and achieved `19.932989` dB.
It therefore discriminated from A1.

All return conditions passed:

- A2 was closer to A1 than B;
- A1-to-A2 was approximately 0.460 of A1-to-B, below the frozen 0.5 maximum;
- all five A2 trials were individually closer to the A1 centroid than B.

## Independent adjudication

The outcome class is E. The exact replication status is:

```text
source_side_positional_return_replication_recurrent
```

The strongest licensed interpretation is:

```text
recurrent independently observed post-mix endpoint relation
+
operator-controlled physical speaker-position change
+
operator-reported fixed microphone configuration
->
changed sampled-microphone realization

operator-reported speaker return
->
recurrence toward the original sampled-microphone realization
```

This strengthens a relative-physical-configuration interpretation and weakens
a microphone-handling-only account under the declared basis. It does not
identify the physical mechanism.

## Retrospective lineage note

This comparison was made only after the replication adjudication was frozen:

| Evidence surface | Prior PR-019 specimen | Independent replication |
| --- | --- | --- |
| source gate | failed: 7.127182 dB shape distance; 5.002234 dB level range | passed: `4.291113e-6` dB; 0.116591 dB |
| B discrimination | failed: 15.525299 dB versus 19.892900 dB required | passed: 19.932989 dB versus 14.969136 dB required |
| A2 relation | numerical return conditions passed but were unlicensed | all return conditions passed after source and B gates |
| operator provenance | game audio later reported during primary acquisition | no known intentional unrelated endpoint playback declared before preflight |

The table describes different retained specimens. It does not infer that game
audio caused the prior failure or that the quiet-source declaration caused the
replication result.

## Observation and inference boundary

Directly observed:

- endpoint identity, format, packets, PCM hashes, spectra, process and capture
  metadata;
- XIBERIA microphone hashes and deterministic spectral reductions;
- complete A1, B, and A2 blocks;
- source stability, B separation, and A2 recurrence under the frozen rules.

Operator provenance only:

- no known intentional unrelated endpoint playback;
- fixed microphone position, orientation, support, and cable;
- speaker A1 -> B -> A2 movement, approximate displacement, height,
  orientation, and return placement;
- unchanged physical settings.

Not observed or licensed:

- causal explanation of the prior failed-basis specimen;
- physical silence or perfect render-path isolation;
- exact speaker or microphone geometry;
- pure airborne causality, driver receipt, DAC behavior, speaker mechanics, or
  electrical output;
- a physical transfer function or general acoustic law;
- tomography, prospective cross-domain prediction, or automatic PR-018
  readiness.

## Map, constraint, and production standing

PR-019 advances to `BOUNDED_RESOLUTION` under the independent replication while
preserving the prior `BASIS_INSUFFICIENT` specimen in its resolution history.
PR-016 remains `BOUNDED_RESOLUTION`, PR-017 remains `CANDIDATE_SURVIVED`, and
PR-018 remains `OPEN` with `cross_domain_prediction_not_earned`.

No new constraint or chart is warranted. No observer or runtime component is
promoted into production, and no persistent distinction event is created.

## Artifacts and verification

Durable scoped artifacts:

- `src/runtime/acoustic_source_side_positional_return_replication.py`;
- `tests/runtime/test_acoustic_source_side_positional_return_replication.py`;
- `traces/acoustic_source_side_positional_return_replication_v1.json`;
- this decision and the PR-019 resolution-history map update.

The original PR-019 trace and decision retained SHA-256 values
`333aeffb52f54915f358ec96940ab715f3d24467fb532c5b9dcb5da722a2fcd2`
and `d758b575ec991b81cc7f707ca8214d076ce113f104b3ba22c5971e69eb2ce5a3`
respectively.

The canonical live ledger retained SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after acquisition and was not mutated.

Verification:

- pre-primary focused suites: 35/35 passed;
- pre-primary full hardware-free suite: 507/507 passed;
- final focused suites including retained-trace verification: 36/36 passed;
- final full hardware-free suite: 508/508 passed;
- primary paired trials: 15/15 complete and retained;
- primary capture and process failures: 0;
- `git diff --check`: passed, including separate checks for untracked artifacts.

## Stop boundary

This replication stops after PR-019 adjudication and map integration. PR-018 is
not activated, reconsidered, or redesigned here. No next experiment is
selected.
