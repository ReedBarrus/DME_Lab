# Acoustic Positional Transformation Pressure v0

## Scope and repository gate

This pressure asks whether a recurrent independently observed post-mix render
condition produces a discriminable sampled-microphone realization under a
controlled A1 -> B displacement, and whether the realization recurs toward A1
after an independently captured return to A2.

It is a bounded physical-transformation pressure. It is not tomography, a room
transfer-function measurement, generalized acoustics, driver/DAC validation,
pure airborne-causality evidence, or production observer design.

Before work, refreshed `origin/main` and local `HEAD` were identical at
`a7ea13d45b60f7109dd0abe35bf23fc695ed30c5` with divergence `0 0`; the
worktree was clean. The canonical live ledger began with SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.

## Physical and observer protocol

The positions were marked before primary evidence:

- A: operator-confirmed original XIBERIA microphone position;
- B: operator-reported lateral displacement from A by approximately the
  microphone's own length, with height and orientation held fixed;
- A2: operator-confirmed return to the original marked A position, with
  original height and orientation restored;
- speaker position, system gain, routing, and hardware settings remained
  unchanged by operator report.

The exact displacement, height, orientation, and return placement were not
machine measured. They are human intervention provenance, not instrumented
geometry.

Each trial independently captured both:

```text
Realtek post-mix endpoint PCM
    via a fresh separate-process WASAPI shared-mode loopback watcher

XIBERIA microphone PCM
    via the existing Windows WinMM waveIn observer
```

The endpoint watcher received only endpoint ID, duration, and ephemeral output
paths. It did not receive position, waveform, frequency band, command buffer,
or condition metadata. The orchestrator joined the position label only after
both captured byte streams were hashed and measured. Playback completion was
not used as either witness.

## Preflight and frozen stimulus

Three exploratory A-position preflights were retained separately from primary
evidence. All acquired endpoint packets and complete microphone buffers with
no reported capture failure:

| Amplitude | Nominal level | Median microphone supported-band response over pre-roll | Freeze result |
| ---: | ---: | ---: | --- |
| 0.005 | -46.02 dBFS | -9.03 dB | inadequate |
| 0.010 | -40.00 dBFS | -6.10 dB | inadequate |
| 0.020 | -33.98 dBFS | 9.23 dB | sufficient |

No level above the previously exercised 0.02 regime was attempted. Before A1,
the primary stimulus was frozen as the existing 180 ms, 700-1700 Hz,
Hann-windowed linear chirp at 0.02 full scale on the previously responsive
right output lane. Capture duration remained 750 ms with a 200 ms nominal
pre-roll.

Primary acquisition was exactly five A1, five B, and five A2 trials. Every
trial was retained; none was excluded, repeated, or relabeled.

## Frozen response representation

The evaluator projected endpoint and microphone magnitude at ten predeclared
frequencies from 750 through 1650 Hz in 100 Hz steps. For every trial it
retained:

- endpoint spectral magnitude and endpoint level-normalized shape;
- absolute microphone response and microphone pre-roll magnitude;
- per-bin microphone response divided by independently observed endpoint
  magnitude, expressed in dB;
- the absolute source-normalized response vector and its mean level;
- the same vector with its mean removed as the level-normalized spectral shape.

This is named a source-normalized microphone spectral signature. It is not a
physical transfer function. Timing uses host command-submission offsets and is
not hardware synchronized.

The frozen response distance is RMS Euclidean distance between absolute
source-normalized dB vectors. Centroids are coordinate-wise medians. The
within-position scale is the median trial-to-centroid distance.

## Frozen criteria

Source stability had to pass before positional attribution:

- maximum pairwise endpoint shape distance no greater than 0.75 dB;
- endpoint mean-level range no greater than 1.0 dB across all 15 primary
  trials.

B was discriminable from A1 only if their centroid distance exceeded both
1.5 dB and three times the larger A1/B within-position median distance.

A2 recurrence required all of:

- the A2 centroid was closer to A1 than B;
- A1-to-A2 distance was no more than half the A1-to-B separation;
- at least four of five A2 trials were individually closer to the A1 centroid
  than the B centroid.

The rules and exact status mapping were frozen before A1. Absolute response,
level-normalized shape, source stability, within-position variability,
cross-position separation, and return recurrence remain separate evidence.

## Endpoint source gate

Every primary trial reacquired the exact active endpoint:

- friendly name: `Speakers (Realtek High Definition Audio)`;
- endpoint ID:
  `{0.0.0.00000000}.{117c0fd3-c8da-440d-8920-6c1d19b8c217}`;
- mode: WASAPI shared-mode loopback through `IAudioCaptureClient`;
- mix: 48 kHz, stereo, WAVE_FORMAT_EXTENSIBLE 32-bit float;
- mix-format SHA-256:
  `481563cc3d5ff86edd468590cb40a84f756bb38aded20f124cd95bb3d05f8aca`.

The 15 fresh primary watcher processes acquired 49-52 packets per trial, 763
packets and 366,240 endpoint frames total. All 15 watcher PIDs were unique and
external to the emitter/microphone process. Across the three preflights and 15
primary trials, all 18 watcher PIDs were unique. Endpoint acquisition failures:
0.

Four distinct endpoint PCM hashes occurred across primary trials, while the
endpoint level-normalized shape maximum pair distance was approximately
`7.78e-15` dB and mean-level range was 0.516145 dB. Both frozen source
stability criteria passed. Repeated hashes or shapes do not collapse distinct
process/timestamped observation occurrences.

## Microphone observations and positional result

Every primary XIBERIA capture contained 36,000 stereo signed-16-bit frames and
had a distinct SHA-256. No microphone capture failure occurred. Raw PCM was
ephemeral and deleted after hashing and deterministic measurement.

Within-position absolute-response variation remained visible:

| Block | Median trial-to-centroid distance | Maximum trial-to-centroid distance | Absolute response mean range |
| --- | ---: | ---: | ---: |
| A1 | 3.152864 dB | 3.891726 dB | -37.633017 to -36.334626 dB |
| B | 3.099483 dB | 4.219465 dB | -57.590808 to -56.020302 dB |
| A2 | 3.328102 dB | 4.170418 dB | -37.033963 to -34.389840 dB |

The frozen B-discrimination threshold was 9.458592 dB. Observed centroid
distances were:

| Comparison | Distance |
| --- | ---: |
| A1 to B | 22.603324 dB |
| A1 to A2 | 3.824222 dB |
| A2 to B | 24.203247 dB |

B therefore discriminated from A1. A2 was closer to A1 than B, its A1 distance
was 0.169 of the A1-to-B separation, and all five A2 trials were individually
closer to the A1 centroid than to B. All three frozen return criteria passed.

As a separately preserved descriptive view, level-normalized shape-centroid
distances were 11.600441 dB for A1-to-B, 2.985879 dB for A1-to-A2, and
11.938349 dB for A2-to-B. Thus the return relation appears in spectral shape as
well as absolute level; this post-hoc summary does not replace the frozen
absolute-response criterion.

## Adjudication

The exact primary status is:

```text
positional_acoustic_transformation_recurrent
```

The strongest bounded interpretation is:

```text
recurrent observed endpoint relation
+
operator-controlled microphone-position change
->
changed sampled-microphone realization

operator-reported return to original position
->
recurrence toward the original sampled-microphone realization
```

This result supports a recurrent position-conditioned microphone realization
under the declared intervention and observer basis. It does not identify the
physical mechanism or license a pure airborne-causality claim.

## Observation and inference boundary

Directly observed:

- endpoint identity, mix format, packet content, flags, positions, QPC values,
  capture windows, hashes, and spectral signatures;
- sampled XIBERIA microphone PCM before deletion, hashes, response/pre-roll
  spectra, absolute response, and level-normalized shape;
- 15 distinct paired primary occurrences and their retained process/time
  metadata;
- source stability, within-position variation, separation, and return
  distances derived under the frozen rule.

Observed through operator provenance, not machine geometry:

- A1 -> B -> A2 intervention order;
- approximate one-microphone-length lateral movement;
- fixed/restored height and orientation and unchanged speaker/settings.

Not observed or licensed:

- specific driver receipt, DAC behavior, or speaker mechanics;
- complete airborne field or isolation of an airborne mechanism from all other
  consequences of the intervention;
- exact displacement or pose, a room transfer function, or a general acoustic
  law;
- microphone causality beyond the declared intervention basis;
- tomography, a cross-domain predictive transformation, or production
  observer semantics.

## Artifacts and canonical history

Durable scoped artifacts:

- `src/runtime/acoustic_positional_transformation_pressure.py`, staged
  pressure-only acquisition and pure evaluator; its pre-primary frozen
  SHA-256 is
  `7b39119b98553564e6fde5e38ac00ab3eab34002c46ceabf3cea2157f8dfa16d`;
- `tests/runtime/test_acoustic_positional_transformation_pressure.py`, pure
  rule/status checks plus retained-trace verification;
- `traces/acoustic_positional_transformation_pressure_v0.json`, complete
  preflight, primary, operator, packet, PCM-hash, measurement, and adjudication
  evidence;
- this decision and `PROJECT_STATE.md`.

No `.pcm`, `.wav`, or `.raw` artifact is retained. The canonical live ledger
was neither used nor mutated and retained SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after adjudication.

## Distinction, chart, and production standing

No new distinction is required. Existing configuration/occurrence,
raw/derived, source/observation, and request/physical-realization boundaries
express the evidence and residue. No chart is added. Neither observer is
promoted into a production capture source, adapter, or generalized acoustic
system.

No next physical transformation is selected or authorized by this result.

## Verification

- pre-primary focused positional suite: 9/9 passed;
- pre-primary full hardware-free suite: 493/493 passed;
- final focused positional suite: 10/10 passed;
- final full hardware-free suite: 494/494 passed;
- primary paired trials: 15/15 complete and retained;
- primary endpoint watcher processes: 15 unique and external;
- all preflight plus primary watchers: 18 unique;
- endpoint and microphone capture failures: 0;
- canonical history changed: no.
