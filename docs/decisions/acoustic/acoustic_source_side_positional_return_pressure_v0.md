# Acoustic Source-Side Positional Return Pressure v0

## Scope and repository gate

PR-019 asked whether, under a recurrent independently observed post-mix
endpoint relation and a fixed microphone, controlled speaker A1 -> B -> A2
displacement would produce a discriminable B microphone realization and return
recurrence toward A1.

This was one bounded physical pressure. It was not PR-018, prospective
cross-domain prediction, tomography, generalized acoustics, a physical
transfer-function measurement, or production observer work.

After `git fetch origin main`, local `HEAD` and `origin/main` were identical at
`fbf73bd2d8de2e58f0dd209c1d1cc4408c4a1e31` with a clean worktree. Reed then
explicitly selected and authorized PR-019.

## Physical and observer protocol

PR-019 reused PR-016's paired acquisition and pure evaluator while changing
the operator intervention locus:

```text
PR-016: speaker fixed; microphone A1 -> B -> A2
PR-019: microphone fixed; speaker A1 -> B -> A2
```

The operator marked the setup before primary evidence and reported:

- the room speaker bound to `Speakers (Realtek High Definition Audio)` was at
  its original A position for A1;
- B was approximately 8 inches toward the operator's left / speaker's right,
  in the same direction used for the prior microphone displacement;
- the microphone position, orientation, support, and cable remained untouched;
- speaker height and orientation were preserved where practical and restored
  at A2;
- gain, routing, device configuration, and physical settings were unchanged.

The geometry and fixed-device claims are operator provenance. They were not
machine measured.

Each trial independently observed both post-mix Realtek endpoint PCM through a
separate-process WASAPI shared-mode loopback watcher and XIBERIA microphone PCM
through the existing WinMM observer. Position metadata was joined after
capture. Playback completion was not used as either witness.

## Frozen basis

The successful preflight froze the unchanged PR-016 basis before A1:

- 180 ms, 700-1700 Hz Hann-windowed linear chirp;
- 0.020 full-scale amplitude on the right output lane;
- 750 ms paired capture with 200 ms nominal pre-roll;
- ten bins from 750 through 1650 Hz;
- absolute source-normalized microphone response in dB;
- RMS Euclidean distance and coordinate-wise median centroids;
- endpoint maximum shape distance no greater than 0.75 dB and mean-level range
  no greater than 1.0 dB;
- B centroid distance greater than 1.5 dB and greater than three times the
  larger A1/B within-position median distance;
- A2 closer to A1 than B, A1-to-A2 no greater than half A1-to-B, and at least
  four of five A2 trials individually closer to A1.

All five A1, five B, and five A2 trials were retained. None was excluded,
relabeled, or repeated.

## Preflight and instrumentation residue

The first unchanged 0.020 preflight acquired endpoint packets, a complete
microphone buffer, and no capture errors, but its median microphone
supported-band response was only `1.741909` dB over pre-roll. It did not freeze
the primary protocol.

The first retry invocation then stopped before capture with a local
`KeyError` while loading a trace created before an operator-confirmation list
was added. No sound was emitted. That instrumentation failure is retained.

After the compatibility path was corrected and 28 focused checks
passed, one unchanged-protocol retry acquired complete witnesses with no
capture error and a median supported-band microphone response of `8.895672`
dB. It passed the 6 dB preflight threshold and froze the protocol. The failed
preflight and no-sound instrumentation failure remain in the trace.

## Primary acquisition

All 15 requested paired observations completed:

| Block | Complete trials | Within-position median absolute distance |
| --- | ---: | ---: |
| A1 | 5/5 | 3.756001 dB |
| B | 5/5 | 6.630967 dB |
| A2 | 5/5 | 3.266571 dB |

Primary evidence retained:

- 15 distinct endpoint PCM hashes and 15 distinct microphone PCM hashes;
- 15 watcher invocations with 14 distinct PID values, all external to the
  emitter/microphone process;
- 74-75 endpoint packets per trial and 539,040 endpoint frames total;
- zero primary endpoint or microphone capture failures;
- no retained raw endpoint or microphone PCM.

Every watcher reacquired the same endpoint ID,
`{0.0.0.00000000}.{117c0fd3-c8da-440d-8920-6c1d19b8c217}`, friendly name, and
48 kHz stereo float mix-format hash
`481563cc3d5ff86edd468590cb40a84f756bb38aded20f124cd95bb3d05f8aca`.
Endpoint identity and format stability did not establish content recurrence.

## Endpoint source gate

The first attribution gate failed:

| Frozen criterion | Required | Observed | Result |
| --- | ---: | ---: | --- |
| maximum endpoint shape pair distance | <= 0.75 dB | 7.127182 dB | failed |
| endpoint mean-level range | <= 1.0 dB | 5.002234 dB | failed |

After adjudication, the operator reported that background game audio described
as cricket chirping was playing during primary acquisition. The loopback PCM
directly preserves changed post-mix content; attribution of that content to the
game is operator provenance, and the exact affected trial subset is unknown.

Because the rendered source relation was not recurrent under the frozen basis,
speaker-position attribution is not licensed.

## Downstream result

The frozen absolute-response centroid distances were:

| Comparison | Distance |
| --- | ---: |
| A1 to B | 15.525299 dB |
| A1 to A2 | 4.452670 dB |
| A2 to B | 16.884137 dB |

B required more than `19.892900` dB separation because its within-position
median distance was high. Its observed `15.525299` dB distance from A1 did not
pass the frozen discrimination rule.

All three numerical A2 return conditions were true and all five A2 trials were
closer to A1 than B. Those values are retained as descriptive measurements,
not as licensed positional recurrence: the source gate failed and B was not
discriminated.

## Adjudication

The exact PR-019 result is:

```text
source_side_positional_return_evidence_insufficient
```

The evidence separates three layers:

```text
paired acquisition quality: complete
post-mix source recurrence: failed
speaker-position discrimination and return attribution: not licensed
```

This run therefore does not answer whether changing speaker position under a
fixed microphone produces a recurrent position-conditioned microphone
realization. It neither strengthens nor refutes the relative-geometry account
and does not weaken the microphone-handling-only alternative.

No primary trial is repeated. A future clean replication would require a
separate selection and authorization.

## Observation and inference boundary

Directly observed:

- endpoint identity, format, packets, PCM hashes, derived spectra, process and
  capture metadata;
- sampled XIBERIA microphone hashes and deterministic spectral reductions;
- complete A1, B, and A2 trial blocks and their frozen-rule measurements;
- endpoint source-gate failure, B non-discrimination, and descriptive A2
  distances.

Operator provenance only:

- fixed microphone position, orientation, support, and cable;
- speaker A1 -> B -> A2 movement, approximate displacement, height,
  orientation, and return placement;
- unchanged physical settings;
- game-audio contamination and its cricket-like character.

Not observed or licensed:

- application-level attribution of the contaminating endpoint content;
- exact physical geometry or pure airborne causality;
- driver receipt, DAC behavior, speaker mechanics, or electrical output;
- a physical transfer function or general acoustic law;
- tomography, prospective cross-domain prediction, or PR-018 readiness.

## Map, constraint, and production standing

PR-019 moves from `OPEN` to `BASIS_INSUFFICIENT` with exact empirical status
`source_side_positional_return_evidence_insufficient`. PR-016 remains
`BOUNDED_RESOLUTION`, PR-017 remains `CANDIDATE_SURVIVED`, and PR-018 remains
`OPEN` with `cross_domain_prediction_not_earned`.

No new constraint or chart is warranted. Existing raw/derived,
source/observation, configuration/occurrence, and request/physical-realization
boundaries are sufficient. No observer or runtime component is promoted into
production.

## Artifacts and verification

Durable scoped artifacts:

- `src/runtime/acoustic_source_side_positional_return_pressure.py`;
- `tests/runtime/test_acoustic_source_side_positional_return_pressure.py`;
- `traces/acoustic_source_side_positional_return_pressure_v0.json`;
- this decision and the PR-019 map update.

The canonical live ledger retained SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after acquisition and was not mutated.

Verification:

- pre-primary focused suites: 28/28 passed;
- pre-primary full hardware-free suite: 500/500 passed;
- final focused suites including retained-trace verification: 29/29 passed;
- final full hardware-free suite: 501/501 passed;
- primary paired trials: 15/15 complete and retained;
- primary capture failures: 0;
- `git diff --check`: passed, including separate checks for untracked artifacts.

## Stop boundary

PR-019 stops at evidence insufficiency. PR-018 is not activated or redesigned,
and no next experiment is selected here.
