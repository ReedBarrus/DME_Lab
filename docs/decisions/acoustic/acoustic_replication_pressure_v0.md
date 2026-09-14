# Acoustic Replication Pressure v0

## Status Before Acquisition

Measurement, trial order, and discrimination rule were frozen before any new
physical capture. This section and the initial
`traces/acoustic_replication_pressure_v0.json` were materialized before device
enumeration or acquisition for this pass.

Starting local `main` and refreshed `origin/main` were identical at
`c9be23c5a7c3db66d9da677ba01d90952aaef1a3`
(`Horizontal Expansion- Soundscape`). The worktree was clean. The existing
suite passed 451/451 using `python -m unittest discover -s tests`.

## Sole Question

Under a measurement and discrimination rule declared before acquisition, do
five replicated C0, S1, and S2 occurrences exhibit reproducible command-
conditioned differences in local microphone measurements?

Passing the rule licenses only a difference in replicated local microphone
measurements under the named commands and basis. It does not establish speaker
realization, airborne acoustic causality, channel health, routing, jack state,
or a complete room field.

## Frozen Physical Boundary

- Windows WinMM path already earned by the basis-entry pass;
- execution-time input name must contain `XIBERIA`;
- execution-time output name must contain `Speakers` and `Realtek`;
- operator roles: XIBERIA headset microphone and Realtek room stereo;
- fixed speaker and microphone positions;
- jack untouched and playback gain unchanged;
- no deliberate environmental manipulation;
- no feedback or sustained tone;
- 750 ms capture, 200 ms nominal pre-roll;
- 180 ms, 700-1700 Hz, Hann-windowed chirp;
- amplitude 0.02 full scale, approximately -33.98 dBFS;
- no gain increase if separation is absent.

Numeric WinMM IDs are not stable identity. Device selection is by the names
observed at execution. Any missing or ambiguous name match stops acquisition.

## Frozen Trial Order

Python `random.Random(20260903).sample(...)` over five copies of each condition
produced this full order before acquisition:

```text
01 S2
02 S1
03 C0
04 C0
05 S2
06 C0
07 S2
08 S1
09 C0
10 S1
11 S2
12 S1
13 S2
14 C0
15 S1
```

Every physical capture remains a separate occurrence through ingest,
admission, ledger, reconstruction, and projection.

## Frozen Measurement Basis

For each captured microphone channel in every trial:

```text
delta_rms_pcm =
    nominal_response_window.rms_pcm
    - that_trial.baseline_window.rms_pcm
```

The underlying baseline and response-window RMS values remain evidence.
Whole-buffer measurements remain descriptive and cannot replace `delta_rms` as
the primary scalar after acquisition.

## Frozen Discrimination Rule

For each of `S1 vs C0`, `S2 vs C0`, and `S1 vs S2`, each microphone channel is
evaluated independently. The label
`locally_discriminable_under_declared_basis` is allowed only when both are true:

1. the two closed observed `delta_rms` ranges do not overlap; and
2. absolute median separation is greater than
   `3 * max(MAD_A, MAD_B)`.

```text
MAD = median(abs(x - median(x)))
```

If either condition MAD is zero, the per-channel criterion is
`criterion_degenerate_insufficient`; no replacement statistic is introduced
and discrimination is not declared. Range and median calculations are still
preserved.

Five replicates are descriptive evidence under this provisional local rule,
not a generalized statistical model.

## Privacy and Timing

Raw PCM remains ephemeral. Each buffer is reduced to deterministic measurements
and SHA-256 identity before being discarded. No WAV or PCM file is written.

Host capture boundaries and command-submission offsets are retained. No common
hardware clock, synchronization, playback-onset time, acoustic-arrival time,
or causal timing claim is added.

## Pre-Acquisition Stop Conditions

Stop without adapting the experiment if:

- the named Realtek/XIBERIA roles are unavailable or ambiguous;
- the backend or format differs materially from the prior pass;
- fixed arrangement, untouched jack, or unchanged gain cannot be maintained;
- safe low-level operation cannot be preserved.

No physical result has influenced the order, primary measurement, rule, or
zero-MAD policy above. Results are appended only after all 15 captures finish.

## Execution and Operator-Reported Confound

The first 15-capture block ran from `2026-09-08T07:13:33.043271Z` through
`2026-09-08T07:13:47.390539Z`. After it completed, the operator reported that
video audio had been playing and likely overlapped the block, then explicitly
authorized another attempt. That report is human provenance, not a
machine-verified diagnosis. The entire first block remains in
`traces/acoustic_replication_pressure_v0_observer_reported_video_contaminated.json`
and is excluded from the primary comparison rather than silently discarded.
Its broad, overlapping deltas are consistent with the reported confound but do
not prove its source.

The replacement 15-capture block ran from `2026-09-08T07:16:58.309270Z`
through `2026-09-08T07:17:12.603709Z`. It used the already frozen order and
rule, the same selected execution-time device names, and the same waveform and
level. Ambient audio state was not machine verified. Across both blocks, 30
physical captures occurred: 10 C0, 10 S1, and 10 S2. The primary adjudication
below uses exactly the five replacement occurrences per condition authorized
after the confound report.

Observed configuration for both blocks:

- input: WinMM device 0, `Microphone (XIBERIA)`, two reported channels;
- output: WinMM device 0, `Speakers (Realtek High Definiti`, two reported
  channels;
- capture: 48 kHz, signed 16-bit little-endian PCM, two channels, 36,000
  frames;
- playback: 180 ms, 700-1700 Hz, Hann-windowed chirp, 0.02 full scale
  (`-33.9794` dBFS), requested only for S1/S2;
- no output-level increase, sustained tone, or microphone-to-speaker feedback;
- zero reported acquisition errors in all 30 captures.

## Replacement Per-Trial Measurements

Values are PCM RMS. Each row is an independently retained physical occurrence;
`b`, `r`, and `d` mean that trial's pre-roll baseline, nominal response window,
and frozen `delta_rms = r - b` respectively.

| Seq | Condition | ch0 b | ch0 r | ch0 d | ch1 b | ch1 r | ch1 d |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | S2 | 0.475712 | 1.423969 | 0.948257 | 0.484929 | 1.418394 | 0.933465 |
| 2 | S1 | 0.474890 | 0.480485 | 0.005595 | 0.483585 | 0.479629 | -0.003956 |
| 3 | C0 | 0.477897 | 0.479972 | 0.002075 | 0.484795 | 0.479800 | -0.004995 |
| 4 | C0 | 0.473792 | 0.478599 | 0.004807 | 0.483585 | 0.478198 | -0.005387 |
| 5 | S2 | 0.476396 | 1.519085 | 1.042689 | 0.483315 | 1.513662 | 1.030347 |
| 6 | C0 | 0.476259 | 0.481170 | 0.004911 | 0.483988 | 0.479686 | -0.004302 |
| 7 | S2 | 0.475164 | 1.355281 | 0.880117 | 0.483585 | 1.356696 | 0.873111 |
| 8 | S1 | 0.475986 | 0.479457 | 0.003471 | 0.486270 | 0.479229 | -0.007041 |
| 9 | C0 | 0.475027 | 0.480428 | 0.005401 | 0.485332 | 0.479515 | -0.005817 |
| 10 | S1 | 0.475712 | 0.483216 | 0.007504 | 0.483585 | 0.480143 | -0.003442 |
| 11 | S2 | 0.476123 | 1.546927 | 1.070804 | 0.485198 | 1.542952 | 1.057754 |
| 12 | S1 | 0.480207 | 0.481739 | 0.001532 | 0.488007 | 0.480143 | -0.007864 |
| 13 | S2 | 0.476123 | 1.606251 | 1.130128 | 0.483988 | 1.598605 | 1.114617 |
| 14 | C0 | 0.476123 | 0.479057 | 0.002934 | 0.484929 | 0.477395 | -0.007534 |
| 15 | S1 | 0.476942 | 0.480086 | 0.003144 | 0.483585 | 0.478943 | -0.004642 |

Every trial also retains its unique trial and observation IDs, replicate index,
predeclared full order, device observations, command metadata and waveform
hashes, host timing, whole-buffer measurements, raw-buffer SHA-256, and error
list in the trace. Raw PCM was discarded after measurement and hashing.

## Within-Condition Variation

| Condition | Channel | observed range | median | MAD | range width |
| --- | --- | --- | ---: | ---: | ---: |
| C0 | 0 | [0.002075, 0.005401] | 0.004807 | 0.000594 | 0.003326 |
| C0 | 1 | [-0.007534, -0.004302] | -0.005387 | 0.000430 | 0.003232 |
| S1 | 0 | [0.001532, 0.007504] | 0.003471 | 0.001939 | 0.005972 |
| S1 | 1 | [-0.007864, -0.003442] | -0.004642 | 0.001200 | 0.004422 |
| S2 | 0 | [0.880117, 1.130128] | 1.042689 | 0.087439 | 0.250011 |
| S2 | 1 | [0.873111, 1.114617] | 1.030347 | 0.084270 | 0.241506 |

S2 has visibly greater absolute within-condition spread than C0 or S1, but its
entire observed range remains separated from both under the declared rule.
Neither microphone channel has zero MAD, so the criterion did not degenerate.

## Pairwise Declared-Rule Results

| Pair | Channel | ranges overlap? | median separation | `3 * max(MAD)` | Verdict |
| --- | --- | --- | ---: | ---: | --- |
| S1 vs C0 | 0 | yes | 0.001336 | 0.005817 | not locally discriminable |
| S1 vs C0 | 1 | yes | 0.000745 | 0.003600 | not locally discriminable |
| S2 vs C0 | 0 | no | 1.037882 | 0.262317 | locally discriminable |
| S2 vs C0 | 1 | no | 1.035734 | 0.252810 | locally discriminable |
| S1 vs S2 | 0 | no | 1.039218 | 0.262317 | locally discriminable |
| S1 vs S2 | 1 | no | 1.034989 | 0.252810 | locally discriminable |

This is outcome B plus D in the prompt's non-exclusive vocabulary: S2 is
locally discriminable from C0, S1 is not, and S2 is also locally discriminable
from S1. It establishes only replicated command-conditioned differences in
the local sampled-microphone measurement under this provisional basis.

## Answers to the Fourteen Questions

1. The exact within-condition ranges, medians, and MADs are reported above.
2. S1 does not satisfy the rule against C0 on either channel: ranges overlap
   and median separation also fails the threshold.
3. S2 satisfies the rule against C0 on both channels.
4. S1 and S2 satisfy the rule against each other on both channels.
5. Yes, all three pair verdicts are consistent across the two captured
   microphone channels. This does not establish independent microphones or a
   physical mechanism.
6. Yes. Repeated equivalent commands produced distinct occurrence identities,
   raw-buffer hashes, and numerical observations. The five values were never
   collapsed into one specimen.
7. Yes. The non-equivalent C0 and S1 commands produced overlapping observed
   `delta_rms` ranges. Pairs involving S2 did not overlap in the replacement
   block.
8. The qualitative one-off S2 excursion is reproduced: all five S2 deltas are
   far above their own pre-roll baselines and separate from C0. Its earlier
   magnitude is not reproduced exactly: the original S2 deltas were 2.030766
   and 2.022301, while replacement S2 ranges are 0.880117-1.130128 and
   0.873111-1.114617.
9. No obvious common monotonic drift appears in the interleaved replacement
   sequence. S2 varies and its third occurrence is the lowest, followed by two
   higher occurrences; C0 and S1 also fluctuate non-monotonically. Fifteen
   short host-timed trials cannot exclude slower drift or unobserved ambient
   changes. The first block's extreme occurrence-specific excursions are
   excluded following the video-audio report.
10. Directly observed were API results, device names/enumeration, host call
    boundaries and offsets, captured PCM before deletion, deterministic
    measurements and hashes, requested commands, and zero returned capture
    errors. Speaker realization, airborne path, channel health, routing,
    transduction mechanism, synchronized onset/arrival, and full room state
    remain inferred or unknown.
11. The criterion neither failed operationally nor degenerated. It rejected
    S1/C0 and accepted both S2 comparisons exactly as declared.
12. No new local acoustic registry distinction is forced. The result is a
    bounded discriminability result, not a new ontological non-equivalence.
13. D-0016 (`structural_state_identity != observation_occurrence_identity`)
    becomes a stronger post-hoc correspondence because repeated same-condition
    trials remained distinct occurrences with non-identical measurements.
    D-0020 (`raw_observation != derived_comparison`) also recurs: the pairwise
    verdict is derived and was not ingested as a raw observation. Neither was
    preselected as the experiment's template or amended by this pass.
14. Acoustic-specific residue includes the unexplained S2 magnitude variation,
    lack of hardware synchronization, unknown physical realization and routing,
    unobserved ambient field, absent waveform morphology after ephemeral PCM
    disposal, and sensitivity demonstrated by the operator-reported video
    overlap. None is resolved into mechanism here.

## Pipeline and Information Loss

Each of the 15 replacement occurrences became one raw observation and one
structural admission record in a temporary 30-record ledger. All 15 were
admitted by COMPARATOR_V0's structural basis. Integrity and continuity checks
passed, and replay, reconstruction, projection, and companion reproduction were
deterministic. Reconstruction recovered 15 distinct trial IDs and their nested
observations. Projection retained 15 separate subject-navigation rows, so it
did not collapse equal condition labels into one occurrence.

The raw observation and nested reconstructed observation directly retain
command, derived measurements, raw-buffer hash, occurrence identity, and
capture errors. The current projection does not expose command, measurement,
or raw hash directly; it preserves navigation to the authoritative
reconstruction. Raw PCM is unavailable everywhere after its intentional
ephemeral reduction. Consequently waveform morphology and any feature not
derived before deletion cannot be recovered.

Replication introduced no new representational failure. Configuration,
condition, and occurrence identity survive in the nested observation, while
the existing projection remains intentionally sparse.

## Distinction and Scope Status

No distinction was added or amended, and no chart was earned. The registry
remains unchanged through D-0046. No production contract, comparator,
reconstruction, projection, schema, or exported audio architecture changed.
The existing pressure harness alone gained a bounded replication mode.

The strongest warranted result is: under the fixed low-level WinMM arrangement
and frozen `delta_rms` rule, the five S2 replacement occurrences are locally
discriminable from both five C0 and five S1 occurrences on both captured
microphone channels; S1 and C0 are not discriminable. No mechanism follows.

The smallest unresolved pressure produced by this result is why S2's local
response magnitude varies across occurrences and between the original and
replacement runs while remaining separated in the replacement block. That is
a question only, not authorization for spatial variation, feedback, Windows
events, additional sensing, gain changes, or another experiment.

## Artifacts, Verification, and Canonical History

Changed artifacts:

- `src/runtime/acoustic_basis_entry_pressure.py` adds the predeclared order,
  measurement evaluator, device-name gate, 15-trial runner, and temporary
  pipeline path while leaving the original default three-trial mode intact;
- `tests/runtime/test_acoustic_replication_pressure.py` exercises order,
  criterion, zero-MAD behavior, persisted trace, occurrence preservation, and
  pipeline visibility without touching audio hardware;
- `traces/acoustic_replication_pressure_v0.json` is the primary replacement
  block;
- `traces/acoustic_replication_pressure_v0_observer_reported_video_contaminated.json`
  retains the excluded first block and its operator provenance;
- this decision record and `PROJECT_STATE.md` record the bounded result.

Verification:

- baseline before acquisition: 451/451 passed with
  `python -m unittest discover -s tests`;
- focused acoustic tests after acquisition: 19/19 passed;
- relevant acoustic/reconstruction/projection/vertical/foreground composition:
  95/95 passed;
- final full unittest suite: 461/461 passed;
- `pytest 8.3.5` was present under Python 3.12 and ran 460/461; its one failure
  was the pre-existing intra-capture timing assertion because two successive
  `datetime.now()` values were exactly equal in that interpreter. The same
  isolated test passed under the repository's `python` (Python 3.14.3), as did
  the full unittest suite. No unrelated timing code was changed;
- the `python3` command is a nonfunctional Microsoft Store alias and was not
  installed or used for tests;
- both replication JSON traces parse successfully, `git diff --check` reports
  no whitespace errors, and no `.wav`, `.pcm`, or `.raw` file exists in the
  repository.

The canonical live-history ledger was not used or mutated. Its SHA-256 remained
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after both acquisition blocks.
