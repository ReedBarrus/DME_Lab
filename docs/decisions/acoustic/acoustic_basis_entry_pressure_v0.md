# Acoustic Basis Entry Pressure v0

## Scope and Starting Boundary

This pass asked whether one bounded physical playback-command and microphone-
capture specimen could enter the current observation, admission, ledger,
reconstruction, and projection machinery without silently identifying:

```text
requested excitation
physical speaker realization
acoustic field
microphone transduction
sampled waveform
inferred source state
```

Starting `main` and refreshed `origin/main` were identical at
`21e35cae4fe633f8715ffbc6c5dd7142c7f68d5d`
(`Capstone for the Wounds`). The starting worktree was clean.

The requested `docs/contracts/runtime.md` was absent from the authoritative
repository. The existing ingest, ledger, and projection contracts plus the
implemented ingest, replay, reconstruction, and projection path were inspected.
The missing document did not create a lineage discrepancy and was not invented.

This was not an audio subsystem. It added no permanent dependency, production
source abstraction, device service, scheduler, watcher, feedback, room model,
speaker diagnosis, or continuous capture. Canonical live history was not used.

## Baseline

The exact requested command failed before the physical pass:

```text
python3 -m pytest -q
Python was not found; run without arguments to install from the Microsoft Store,
or disable this shortcut from Settings > Apps > Advanced app settings > App
execution aliases.
```

The installed interpreter was Python 3.14.3. The corresponding pytest command
also failed because pytest was not installed:

```text
python -m pytest -q
C:\Python314\python.exe: No module named pytest
```

No package was installed. The repository's existing unittest suite was run
through the installed interpreter and passed 442/442 before experiment code.

## Capability and Safety Boundary

No ffmpeg, ffplay, SoX, Audacity, VLC, `sounddevice`, PyAudio, or `soundfile`
facility was installed. Windows WinMM was already available through the Python
standard library's `ctypes` boundary.

At execution, WinMM exposed one two-channel input and four two-channel outputs.
The selected devices recorded in the trace were:

```text
input 0:  Microphone (XIBERIA)
output 0: Speakers (Realtek High Definiti...)
```

The operator later identified Realtek as the room stereo and XIBERIA as the
headphones/headset microphone. The operator also warned that the room stereo
can produce substantial volume. These are operator-provided provenance, not
machine-verified device-role facts.

The open-loop safety boundary was:

- fixed speaker and microphone positions;
- no jack movement;
- no microphone-to-speaker feedback;
- 750 ms capture per specimen;
- 180 ms Hann-windowed 700-1700 Hz linear chirp;
- requested amplitude 0.02 full scale, approximately -33.98 dBFS;
- one excitation per requested channel;
- no sustained tone and no gain increase.

System output gain and physical sound pressure were not observed. After the
pass, the operator reported hearing no playback. That report is human
provenance; it is not proof that the speaker emitted no acoustic energy.

The capability preflight and execution enumerations did not retain the same
numeric ordering for the four output names. The execution trace records the
name paired with the selected ID inside the actual run. A WinMM device index is
therefore not treated as a stable hardware identity from this evidence.

## Physical Specimen in Its Own Terms

Three real microphone captures were performed. Raw PCM existed only in process
memory long enough to derive measurements and SHA-256 identity; it was not
written to disk or committed.

| Specimen | Requested playback | Requested PCM lane | Command submitted inside host capture | Capture errors | Response-window RMS, mic channels 0 / 1 |
| --- | --- | --- | --- | --- | --- |
| C0 | none | none | no | 0 | 0.478771 / 0.478714 |
| S1 | 180 ms chirp | left | yes, at host offset 0.2004924 s | 0 | 0.478885 / 0.478828 |
| S2 | equivalent mono chirp | right | yes, at host offset 0.2000464 s | 0 | 2.507981 / 2.506155 |

The S1 response-window values differed from C0 by approximately 0.000114 PCM
RMS on each captured channel. S2 differed from C0 by approximately 2.029 PCM
RMS. Relative to its own pre-roll baseline, S2's response window was about
14.41 dB and 14.29 dB higher on the two captured channels. Peak magnitude was
12 out of the signed-16-bit range.

These are measurements of sampled microphone buffers under three commanded
conditions. There was one occurrence per command and no declared
discrimination threshold. The numeric difference is not a speaker-channel
verdict, a repeatability result, or causal attribution.

## Command, Observation, and Inference

### What was commanded

- C0 requested capture with no playback.
- S1 submitted the bounded chirp in the left lane of stereo PCM to the selected
  Realtek WinMM output.
- S2 submitted the same mono chirp in the right lane. The stereo command hashes
  differed while the mono waveform hash remained equal.

A successful `waveOutWrite` command submission was observed. Exact DAC output,
amplifier state, speaker-cone motion, and emitted acoustic waveform were not.

### What was directly observed

- successful WinMM input/output API results;
- host-side capture start and finish call boundaries;
- host-side command-submission time and monotonic offset;
- 36,000 two-channel signed-16-bit PCM frames per capture;
- raw buffer byte counts and SHA-256 hashes;
- deterministic pre-roll, response-window, and whole-buffer RMS/peak
  measurements;
- zero acquisition errors returned by the bounded calls.

The directly retained observation is the derived measurement record plus raw
buffer identity, not the raw PCM itself.

### What was only inferred or left unresolved

The following were not directly observed and are not asserted:

- whether either requested speaker lane was physically realized;
- whether the S2 measurement difference was acoustic response, electrical or
  routing crosstalk, background variation, or another mechanism;
- the emitted speaker waveform;
- microphone transfer function or exact transduction;
- the complete room acoustic field;
- speaker health, channel health, or jack state;
- a causal command-to-response relationship.

The operator's inaudibility report and prior intermittent-channel report remain
provenance beside, not replacements for, machine measurements.

## Timing Boundary

The warranted ordering for S1 and S2 is only:

```text
host waveInStart call boundary
-> host waveOutWrite submission boundary
-> capture buffer completion observed by host
```

WinMM supplied no common hardware clock, playback onset timestamp, acoustic
arrival timestamp, or ADC/DAC synchronization claim. The response window is
anchored to the host command-submission offset and labeled accordingly. The
experiment does not claim simultaneous playback and capture or exact acoustic
latency.

## Questions Exposed by the Specimen

1. **What was commanded?** C0 none; S1 and S2 the same short chirp in different
   stereo PCM lanes.
2. **What was directly observed?** Host API outcomes, sampled buffers, hashes,
   timings at host boundaries, and deterministic buffer measurements.
3. **What physical occurrence is inferred?** Any actual speaker realization,
   propagation, and causal response remain inferred or unresolved.
4. **Which timing is warranted?** Host call ordering and elapsed offsets only.
5. **Does microphone response prove speaker realization?** No. It supports only
   local sampled-response measurements under differing commands.
6. **Can equivalent commands yield non-equivalent observations?** Not tested;
   there was only one occurrence for each command.
7. **Can non-equivalent commands yield indistinguishable measurements?** Not
   decided. S1 and S2 vectors were numerically unequal, but no threshold,
   replicates, noise model, or distribution was established.
8. **What is lost through the pipeline?** Raw PCM was intentionally discarded
   before ingest. Projection additionally omits retained command, measurement,
   timing, error, and hash detail while preserving subject navigation.
9. **Did a repository-shaped assumption misrepresent the specimen?** No. The
   minimum comparator accepted a structurally valid non-repository envelope,
   and the generic ledger/reconstruction path preserved its payload. The
   admitted decision remained structural only.
10. **Was a new distinction forced?** No. The new domain exposed a local
    pre-ingest reduction boundary and physical residue, but no new non-
    equivalence required a registry entry.
11. **Are repository distinctions analogous?** Some post-hoc correspondences
    are useful but remain bounded, described below.
12. **What remains acoustically specific?** Analog propagation, device routing,
    channel mapping, transduction, gain, latency, room response, noise, and the
    privacy/storage status of sampled room audio.

## Generic Pipeline Result

The pressure harness constructed one structurally legitimate ingest envelope
per measurement record and used a temporary JSONL ledger:

```text
three acoustic measurement observations
-> three observation records
-> COMPARATOR_V0
-> three admitted decisions
-> six contiguous records
-> replay
-> admission reconstruction
-> three projection rows
-> three empty non-admitted companion rows
```

Integrity, start-at-one continuity, independent replay, reconstruction,
projection, and companion reproduction all passed. All three decisions had the
basis `comparison valid under comparator`.

That decision establishes only minimum observation-envelope structure. It does
not establish physical playback, speaker success, causal response, acoustic
truth, waveform completeness, or device identity stability. No production
semantic overclaim or schema defect was found.

## Information Conservation and Loss

The surfaces preserve different evidence:

| Surface | Command metadata | Derived measurements | Raw hash | Raw PCM |
| --- | --- | --- | --- | --- |
| process-local captured specimen | yes | yes | yes | ephemeral only |
| acoustic ingest signal payload | yes | yes | yes | no |
| temporary ledger nested observation | yes | yes | yes | no |
| reconstruction nested observation | yes | yes | yes | no |
| admitted projection | no | no | no | no |

Projection retains `subject_record_id` and admission-record navigation, so the
ingested metadata remains recoverable through reconstruction. No downstream
surface can recover the discarded raw waveform from its cryptographic hash or
measurements. This is an intentional pre-ingest privacy/reduction boundary,
not ledger corruption or projection erasure.

If a later claim requires waveform morphology, phase, spectral detail not
derived here, or independent remeasurement, then raw-specimen preservation or
a richer explicitly selected measurement basis would be required. That
requirement was not silently introduced in this pass.

## Local Result Before Registry Comparison

The bounded physical entry succeeded as an invariance result:

```text
qualitatively non-repository observation metadata
-> current generic structural admission and history machinery
-> deterministic recovery without semantic inflation
```

The physical wound is not a diagnosed faulty channel. It is the unavailable
translation from requested digital actuation and local microphone measurements
to actual physical realization. The deliberate raw-data reduction adds a
second boundary: downstream history can reconstruct exactly the evidence that
was admitted, but not the physical waveform discarded before admission.

## Post-Hoc Registry Correspondence

Only after the local result was established were possible correspondences
considered:

- D-0046 (`structural_admissibility != source_capture_success`) is a useful
  analogy for why acoustic admission cannot certify physical actuation. The
  correspondence is partial: this pass lacks independent ground truth for
  actuation success, so it does not experimentally reproduce D-0046.
- D-0020 (`raw_observation != derived_comparison`) helps name the raw-PCM versus
  measurement-summary boundary. Acoustic privacy makes the reduction
  operationally important, but different nouns do not require a new D-number.
- D-0026 and D-0027 still describe authoritative-history, reconstruction, and
  projection boundaries after the non-repository observation enters the stack.
- D-0021's stable-source-identity concern is suggestive of the observed WinMM
  index/name instability, but a one-run device enumeration is not enough to
  claim a general identity law.
- D-0044 is only linguistically adjacent to playback/capture timing. This pass
  did not reproduce its shared-world-configuration pressure and claims no
  tomography or translation map.

These correspondences are evidence of possible recurrence in the broader
method, not proof of a universal structure.

## Distinction, Chart, and Production Status

No registry distinction was added or amended. The acoustic specimen did not
force a non-equivalence unavailable from the current bank.

No new chart was earned. Three single occurrences without a discrimination
criterion do not form a stable acoustic coordinate surface.

No production module, contract, schema, comparator, reconstruction, or
projection behavior changed. The harness remains pressure-only and unexported.

## Answer and Smallest Unresolved Pressure

One bounded physical command/capture specimen exposed a new entry constraint
without exposing a production defect: when sensitive raw physical samples are
intentionally reduced before ingest, the chosen measurements define the
recoverable observation basis. Later reconstruction cannot answer questions
that basis discarded.

The current machinery can faithfully carry that bounded evidence if requested
actuation, sampled observation, operator provenance, missing physical
realization, and timing limitations remain explicit. It cannot turn the
resulting admitted projection into knowledge of what the speakers physically
did.

The smallest unresolved pressure is whether repeated C0/S1/S2 occurrences,
under a declared conservative range-finding and discrimination criterion, can
establish command-conditioned differences in local microphone response without
claiming speaker realization. This is a possible later question, not a selected
next implementation. No additional sound is emitted in this pass.

## Artifacts and Canonical History

Artifacts:

- `src/runtime/acoustic_basis_entry_pressure.py`;
- `tests/runtime/test_acoustic_basis_entry_pressure.py`;
- `traces/acoustic_basis_entry_pressure_v0.json`;
- this decision record.

The trace contains command metadata, device enumeration, host timing,
deterministic measurements, raw-buffer hashes, pipeline results, and epistemic
limits. It contains no raw PCM recording.

`traces/live_ingest_ledger_v0.jsonl` had SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after the experiment.

Final hardware-free verification with all artifacts present:

- focused acoustic pressure tests: 9/9 passed;
- relevant acoustic, reconstruction, projection, vertical-composition, and
  foreground pressure tests: 248/248 passed;
- full unittest suite: 451/451 passed.

The first focused run exposed one test-only false positive: a raw-text search
for `raw_pcm` matched the legitimate metadata key `raw_pcm_persisted`. The test
was corrected to recursively reject an actual `raw_pcm` field, then all focused
and composed tests passed. No physical trial was repeated and no further sound
was emitted.
