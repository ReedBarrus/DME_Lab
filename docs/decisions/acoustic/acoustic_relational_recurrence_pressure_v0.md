# Acoustic Relational Recurrence Pressure v0

## Status Before Acquisition

The order, unchanged measurement/discrimination semantics, and cross-run
recurrence criterion below were materialized in code, this record, and
`traces/acoustic_relational_recurrence_pressure_v0.json` before device
enumeration or physical acquisition.

Refreshed local `main` and `origin/main` were identical at
`94543eafd8f6feadc45248e6b5d7861be6526212` (`Sound Test 1`), with divergence
`0/0` and a clean worktree. The baseline suite passed 461/461 using
`python -m unittest discover -s tests`.

## Sole Question

Does the prior primary replacement block's pairwise relation recur after an
independently initialized bounded acquisition process despite variation in
absolute microphone-response magnitude?

The tested transformation is only:

```text
prior bounded acquisition occurrence
-> prior process and device handles ended
-> new Python process and WinMM backend instance
-> new bounded acquisition occurrence
```

This does not claim a complete reset of the room, hardware, driver, routing, or
Windows audio state.

## Frozen Physical and Epistemic Boundary

- input role: fixed XIBERIA headset microphone;
- output role: fixed Realtek room stereo;
- positions fixed, jack untouched, and system/output gain unchanged;
- 750 ms two-channel capture at 48 kHz signed 16-bit PCM;
- 180 ms, 700-1700 Hz Hann-windowed chirp at 0.02 full scale
  (approximately -33.98 dBFS);
- no feedback, sustained tone, device movement, jack manipulation, gain
  increase, Windows observer, new dependency, or intentional media playback;
- ambient silence is not machine verified; any operator confirmation remains
  provenance only;
- raw PCM remains ephemeral unless the result independently forces otherwise.

## Frozen Seed and Trial Order

Python `random.Random(20260910).sample(...)` over five labels per condition
produced a new order, distinct from the prior block:

```text
01 S2
02 C0
03 C0
04 S2
05 C0
06 S1
07 S1
08 S2
09 S1
10 C0
11 S1
12 S2
13 S1
14 S2
15 C0
```

Each capture must remain a separate occurrence through the temporary pipeline.

## Unchanged Measurement and Discrimination Rule

For each microphone channel and trial:

```text
delta_rms_pcm =
    nominal_response_window.rms_pcm
    - that_trial.baseline_window.rms_pcm
```

A pair is `locally_discriminable_under_declared_basis` only if its observed
closed ranges do not overlap and its absolute median separation is greater than
`3 * max(MAD_A, MAD_B)`, where `MAD = median(abs(x - median(x)))`. If either MAD
is zero, the criterion is degenerate/insufficient; no substitute is allowed.

The descriptive ratio `median_separation / max(MAD_A, MAD_B)` will be reported
but cannot replace either frozen condition.

## Frozen Relational Recurrence Criterion

The new block is `relationally_recurrent_under_declared_basis` only if both
captured microphone channels independently reproduce all three verdicts:

```text
S1 vs C0 -> not locally discriminable
S2 vs C0 -> locally discriminable
S1 vs S2 -> locally discriminable
```

Absolute S2 magnitude equality is not required. This criterion will not be
weakened or rerun after inspecting data.

Passing licenses only recurrence of the command-conditioned local sampled-
microphone relation under the unchanged basis. It cannot establish speaker
health, stable transfer function, airborne causality, stable emitted amplitude,
stable routing, hardware-state identity, or a general acoustic law.

## Pre-Acquisition Stop Conditions

Stop rather than adapt if device names/roles are missing or ambiguous, the
WinMM backend or format differs materially, the low-level fixed arrangement
cannot be maintained, or safe execution is unavailable. Results are appended
only after one fresh 15-capture block completes.

## Execution Boundary Actually Performed

After predeclaration and a 461/461 baseline, a separate command started a new
Python process (recorded PID 24628) solely for this block. That process created
a new `_WinMMBackend` instance at `2026-09-08T08:05:41.321026Z`. WinMM input and
output handles were opened and closed within each trial; no prior-process handle
was reused. The 15 captures ran from `2026-09-08T08:05:41.387216Z` through
`2026-09-08T08:05:55.663750Z`.

Execution-time enumeration again found exactly one matching input,
`Microphone (XIBERIA)`, and one matching output,
`Speakers (Realtek High Definiti`, both reporting two channels. A five-second
pause-media notice preceded the run. No operator confirmation was received;
ambient silence was not machine verified. There was no rerun, gain change, or
adaptation after inspecting the result.

This is evidence of a fresh process/backend and per-trial handle lifecycle, not
a complete reset of the physical room, hardware, driver, routing, or Windows
audio state.

## All Fifteen New Measurements

Values are PCM RMS. `b`, `r`, and `d` are the per-trial baseline, nominal
response window, and frozen `delta_rms = r - b`.

| Seq | Condition | ch0 b | ch0 r | ch0 d | ch1 b | ch1 r | ch1 d |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | S2 | 0.477215 | 1.468436 | 0.991221 | 0.484392 | 1.468007 | 0.983615 |
| 2 | C0 | 0.475438 | 0.481113 | 0.005675 | 0.484795 | 0.479000 | -0.005795 |
| 3 | C0 | 0.477761 | 0.479800 | 0.002039 | 0.484257 | 0.477796 | -0.006461 |
| 4 | S2 | 0.475849 | 1.451878 | 0.976029 | 0.485063 | 1.454519 | 0.969456 |
| 5 | C0 | 0.474890 | 0.478313 | 0.003423 | 0.484526 | 0.479457 | -0.005069 |
| 6 | S1 | 0.477215 | 0.480086 | 0.002871 | 0.485063 | 0.479343 | -0.005720 |
| 7 | S1 | 0.474890 | 0.480485 | 0.005595 | 0.484392 | 0.478885 | -0.005507 |
| 8 | S2 | 0.476533 | 1.343764 | 0.867231 | 0.483854 | 1.352264 | 0.868410 |
| 9 | S1 | 0.475438 | 0.480599 | 0.005161 | 0.484929 | 0.479629 | -0.005300 |
| 10 | C0 | 0.477488 | 0.480257 | 0.002769 | 0.484257 | 0.479286 | -0.004971 |
| 11 | S1 | 0.475849 | 0.479457 | 0.003608 | 0.485734 | 0.479629 | -0.006105 |
| 12 | S2 | 0.475164 | 1.609423 | 1.134259 | 0.484392 | 1.613743 | 1.129351 |
| 13 | S1 | 0.475164 | 0.479457 | 0.004293 | 0.484123 | 0.479743 | -0.004380 |
| 14 | S2 | 0.475575 | 1.391744 | 0.916169 | 0.483585 | 1.386258 | 0.902673 |
| 15 | C0 | 0.478578 | 0.481511 | 0.002933 | 0.482372 | 0.479572 | -0.002800 |

All trials returned zero capture errors. Their 15 trial IDs and 15 raw-buffer
SHA-256 values are individually distinct. Raw PCM was not persisted.

## New-Block Condition Summaries

| Condition | Channel | range | median | MAD |
| --- | --- | --- | ---: | ---: |
| C0 | 0 | [0.002039, 0.005675] | 0.002933 | 0.000490 |
| C0 | 1 | [-0.006461, -0.002800] | -0.005069 | 0.000726 |
| S1 | 0 | [0.002871, 0.005595] | 0.004293 | 0.000868 |
| S1 | 1 | [-0.006105, -0.004380] | -0.005507 | 0.000213 |
| S2 | 0 | [0.867231, 1.134259] | 0.976029 | 0.059860 |
| S2 | 1 | [0.868410, 1.129351] | 0.969456 | 0.066783 |

No MAD is zero, so the frozen rule did not degenerate.

## New-Block Pairwise Verdicts

The normalized value is descriptive only and was not substituted for either
part of the frozen rule.

| Pair | Channel | ranges overlap? | median separation | `3 * max(MAD)` | separation / max MAD | Verdict |
| --- | --- | --- | ---: | ---: | ---: | --- |
| S1 vs C0 | 0 | yes | 0.001360 | 0.002604 | 1.566820 | not locally discriminable |
| S1 vs C0 | 1 | yes | 0.000438 | 0.002178 | 0.603306 | not locally discriminable |
| S2 vs C0 | 0 | no | 0.973096 | 0.179580 | 16.256198 | locally discriminable |
| S2 vs C0 | 1 | no | 0.974525 | 0.200349 | 14.592411 | locally discriminable |
| S1 vs S2 | 0 | no | 0.971736 | 0.179580 | 16.233478 | locally discriminable |
| S1 vs S2 | 1 | no | 0.974963 | 0.200349 | 14.598970 | locally discriminable |

Both microphone channels reproduce the complete frozen pattern. Therefore the
result is `relationally_recurrent_under_declared_basis`.

## Run-to-Run Numerical Variation

| Condition | Channel | prior median | new median | shift | prior MAD | new MAD | prior range | new range |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| C0 | 0 | 0.004807 | 0.002933 | -0.001874 | 0.000594 | 0.000490 | [0.002075, 0.005401] | [0.002039, 0.005675] |
| C0 | 1 | -0.005387 | -0.005069 | +0.000318 | 0.000430 | 0.000726 | [-0.007534, -0.004302] | [-0.006461, -0.002800] |
| S1 | 0 | 0.003471 | 0.004293 | +0.000822 | 0.001939 | 0.000868 | [0.001532, 0.007504] | [0.002871, 0.005595] |
| S1 | 1 | -0.004642 | -0.005507 | -0.000865 | 0.001200 | 0.000213 | [-0.007864, -0.003442] | [-0.006105, -0.004380] |
| S2 | 0 | 1.042689 | 0.976029 | -0.066660 | 0.087439 | 0.059860 | [0.880117, 1.130128] | [0.867231, 1.134259] |
| S2 | 1 | 1.030347 | 0.969456 | -0.060891 | 0.084270 | 0.066783 | [0.873111, 1.114617] | [0.868410, 1.129351] |

S2's lower and upper range-endpoint shifts were `-0.012886/+0.004131`
on channel 0 and `-0.004701/+0.014734` on channel 1. Thus the exact numerical
realization changed, including lower S2 medians, while the three pairwise
discrimination relations remained invariant on both channels.

## Direct Observation, Pipeline, and Information Boundary

Direct evidence includes device enumeration/names, requested command and PCM
lane, successful WinMM calls, host capture boundaries and command offsets,
captured buffers before deletion, per-window and whole-buffer measurements,
raw-buffer hashes, and empty acquisition-error lists. It does not directly
observe speaker realization, emitted amplitude, airborne causality, transfer
function, routing, synchronized timing, hardware-state identity, or the ambient
room field.

Each new occurrence became one observation and one admission record in a
temporary 30-record ledger. All 15 structurally admitted. Integrity and
continuity passed; replay, reconstruction, projection, and companion were
reproducible. Reconstruction recovered all 15 distinct trial identities and
nested observations. Projection retained 15 separate subject-navigation rows;
it did not collapse repeated conditions, but it still does not directly expose
commands or measurements. Raw PCM morphology remains irrecoverable after the
intentional ephemeral reduction.

Fresh initialization and recurrence created no new identity or reconstruction
ambiguity in this specimen. Run identity, condition, and occurrence remain
separate in the trace and nested reconstructed observations.

## Distinction and Scope Status

No new distinction or chart is forced, and the registry remains unchanged
through D-0046. D-0016 remains a bounded post-hoc correspondence because
equivalent condition/configuration labels do not collapse occurrence identity.
D-0020 also recurs because pairwise and cross-run comparisons are derived from,
not identical to, raw observations. The fresh-process boundary is compatible
with D-0042's separation of coordinator lifetime and historical continuity but
does not extend its repository-scoped evidence into a general hardware claim.

The licensed conclusion is only: under the same declared measurement basis,
the same command-conditioned local microphone-response relation recurred across
two independently initialized bounded acquisition blocks. The magnitude shift
remains unexplained by design.

The smallest newly forced pressure is whether this run-relative relational
recurrence is sufficient for any concrete consumer decision despite unresolved
physical mechanism and amplitude variation. No such consumer exists in scope,
so this is a question, not authorization for another acoustic experiment or a
new architecture.

## Artifacts, Tests, and Canonical History

Artifacts:

- `src/runtime/acoustic_basis_entry_pressure.py` reuses the existing observer,
  measurement derivation, WinMM capture, structural admission, and temporary
  pipeline while adding only a new-order recurrence mode and pure evaluators;
- `tests/runtime/test_acoustic_relational_recurrence_pressure.py` verifies the
  frozen order/rules, strict all-pair/all-channel recurrence criterion,
  descriptive-only normalized separation, final trace, process boundary, and
  occurrence preservation without accessing audio hardware;
- `traces/acoustic_relational_recurrence_pressure_v0.json` retains the 15
  observations, independent new-block analysis, cross-run comparison,
  recurrence verdict, temporary-pipeline audit, and epistemic boundaries;
- this decision record and `PROJECT_STATE.md` record the bounded outcome.

Tests:

- baseline full suite before edits/acquisition: 461/461 passed;
- focused acoustic suite after acquisition: 27/27 passed;
- relevant acoustic/reconstruction/projection/vertical/foreground composition:
  103/103 passed;
- final full suite: 469/469 passed;
- runner: `python -m unittest`; hardware acquisition is not part of ordinary
  regression tests.

Both the starting and final repository HEAD remain
`94543eafd8f6feadc45248e6b5d7861be6526212` (`Sound Test 1`). The canonical
live-history ledger was not used or mutated; its SHA-256 remained
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`.
The trace parses as JSON, `git diff --check` reports no whitespace errors, the
registry has no diff, and the repository contains no `.wav`, `.pcm`, or `.raw`
file.
