# WASAPI Loopback Witness Validation v0

## Scope

This pressure asks one bounded question: can a separately running WASAPI
shared-mode loopback observer acquire content-bearing PCM from the selected
Realtek render endpoint and discriminate no intentional test playback, a
900 Hz render, and a 1500 Hz render without obtaining its witness content from
playback-command metadata?

The pressure validates a **post-mix render-endpoint coordinate**. It does not
validate a driver, DAC, speaker, airborne field, microphone response, causal
audio path, generalized Windows observer, or repository-acoustic tomography.

The repository gate was clean and synchronized before implementation:

- starting `HEAD` and `origin/main`:
  `3d07956f8bfb4b47e35c5f5517857d971ea5c18b` (`Astra Pass-3`);
- divergence: `0 0`;
- starting worktree: clean.

## Preserved boundary

```text
command construction
        !=
render-path observation
        !=
physical acoustic realization
```

The implementation has three roles:

1. the emitter process only submits a short WinMM render buffer;
2. each watcher is a fresh OS process which receives only endpoint ID,
   duration, and artifact paths and reads actual packets through
   `IAudioCaptureClient.GetBuffer`;
3. the orchestrator/evaluator joins the semantic condition label only after
   the watcher has exited and its PCM hash has been verified.

The watcher does not receive a condition label, requested frequency,
amplitude, source waveform, source-buffer hash, or emitter hash. Playback API
success is retained only as supplemental emitter metadata and is not used as
the witness.

## Endpoint and format

Runtime Core Audio enumeration selected exactly one active endpoint; there was
no fallback:

| Field | Observed value |
| --- | --- |
| endpoint ID | `{0.0.0.00000000}.{117c0fd3-c8da-440d-8920-6c1d19b8c217}` |
| friendly name | `Speakers (Realtek High Definition Audio)` |
| state | `1` / active |
| mode | WASAPI shared-mode loopback |
| API | `IAudioCaptureClient` |
| mix format | WAVE_FORMAT_EXTENSIBLE, IEEE float |
| sample rate | 48,000 Hz |
| channels | 2, mask `0x00000003` |
| sample representation | 32-bit little-endian float |
| block alignment | 8 bytes |
| mix-format SHA-256 | `481563cc3d5ff86edd468590cb40a84f756bb38aded20f124cd95bb3d05f8aca` |

The emitter selected WinMM device 0, reported as
`Speakers (Realtek High Definiti` because WinMM truncates the device name.
Core Audio endpoint identity, not that truncated string, is the watcher
binding and the retained source coordinate.

## Packet gate and safety

Before tone acquisition, the watcher initialized, started, and stopped cleanly
on the exact endpoint. With no active render stream it returned no packets.
The predeclared all-zero render then activated the endpoint and yielded 33
actual capture packets / 15,840 frames. Thirteen packets carried the WASAPI
silent flag; one carried data-discontinuity. The captured byte stream had
SHA-256
`0d9a43211bf74b3bcd86937c9668e2c9d6c6019d6aa1ab7b3e87c8ed664e9bde`.
This satisfied the packet gate without audible test content.

The first attempted full orchestration stopped before watcher readiness because
the child was launched by file path and could not import the repository's
`src` package. No tone or primary trial was emitted in that attempt. Child
launch was changed to `python -m src.runtime.wasapi_loopback_witness_validation`,
the focused suite was rerun, and the frozen protocol was retried unchanged.
This was one pre-evidence instrumentation failure; the completed trace itself
contains zero endpoint acquisition failures.

The exploratory preflight used 180 ms tones at amplitude 0.001 (-60 dBFS).
Both intended spectral coordinates appeared. The confirmatory basis was then
left unchanged: 180 ms tones at amplitude 0.002 (-53.9794 dBFS), below the
prior acoustic pressure's 0.02 amplitude. No system gain, amplifier gain,
device setting, placement, or hardware was changed.

## Frozen primary basis

The primary order was frozen under seed `2026090817`:

```text
S1 S1 C0 S1 S2 C0 C0 C0 S2 S1 S2 S2 C0 S1 S2
```

There were five trials per condition. `C0` meant no intentional test
playback, `S1` was 900 Hz, and `S2` was 1500 Hz. Each watcher captured for
0.7 seconds, with emission beginning after 0.18 seconds when applicable. No
trial was excluded.

The frozen measurement was whole-capture single-frequency RMS projection,
combined across endpoint channels. Validation required all of:

- median commanded-frequency dominance at least 12 dB for S1 and S2;
- every commanded trial dominance at least 6 dB;
- each commanded target median at least 12 dB above the same C0 coordinate;
- at most one C0 trial imitating each command relation;
- actual packets in every S1 and S2 trial.

Exact equality with the emitter PCM was neither tested nor required.

## Primary observations

| Condition | Packet/frame result | Retained PCM hashes | Spectral result |
| --- | --- | --- | --- |
| C0, 5/5 | 0 packets and 0 frames in every interval | empty-byte SHA-256 `e3b0c442...b855` in 5/5 | neither command relation observed; 0 imitations |
| S1, 5/5 | 33-34 packets, 15,840-16,320 frames | 2 distinct hashes | median 900 Hz projection `0.000374164`; 900-over-1500 median `78.451 dB` |
| S2, 5/5 | 31-35 packets, 14,880-16,800 frames | 2 distinct hashes | median 1500 Hz projection `0.000363444`; 1500-over-900 median `68.518 dB` |

All ten commanded trials contained capture packets. Together they yielded 339
packets and 162,720 frames. S1 per-channel RMS ranged from approximately
0.000630 to 0.000639 full scale; S2 ranged from approximately 0.000621 to
0.000660. Both channels carried the same declared relation.

C0's result is packet absence during an interval with no intentional render,
not a claim that the API returned silent PCM and not a claim about physical
silence. Its empty-byte hash and zero derived projections preserve that
missingness explicitly.

Repeated hashes within a condition are observed outcomes, not collapsed
occurrence identities. Packet counts, capture windows, watcher PIDs, and
timestamps preserve the distinct acquisitions. Numerical or hash identity
across runs was not a criterion.

## Process-lifetime reacquisition

The trace contains 19 unique external watcher PIDs: two packet-gate attempts,
two preflight captures, and fifteen primary captures. Every primary watcher
reacquired the exact endpoint ID, friendly name, and mix-format hash. All
watcher PIDs differ from the orchestrator PID and from one another. Endpoint
acquisition failures: 0.

Emitter and watcher were separate OS processes. The watcher command boundary
contained no playback frequency, waveform, amplitude, or semantic condition.
Fresh-process reacquisition therefore succeeded without requiring numerical
PCM identity.

## Adjudication

Every frozen discrimination criterion passed. The primary status is:

```text
post_mix_loopback_witness_validated
```

The strongest licensed conclusion is:

> A separate software observer acquired content-bearing post-mix PCM from the
> selected Windows render endpoint and discriminated the tested render
> conditions.

This establishes a bounded render-path source-relative coordinate downstream
of application submission and observable through Windows shared-mode loopback.
It resolves the prior `candidate_requires_new_basis` implementation gap for
this host and pressure only.

## Observation and inference boundary

Directly observed:

- Core Audio endpoint ID, friendly name, state, and shared mix format;
- actual `IAudioCaptureClient` packet availability, frames, flags,
  stream/device positions, QPC positions, and observer timestamps;
- ephemeral captured bytes, their SHA-256 hashes, per-channel RMS, peaks, and
  900/1500 Hz projections;
- repeated endpoint/mix reacquisition across independent watcher processes.

Not observed and not inferred:

- receipt of these exact samples by a particular hardware driver or device;
- DAC voltage, speaker mechanics, or airborne sound;
- microphone response, playback-to-microphone causality, or physical silence;
- exclusive attribution in the presence of unrelated endpoint audio;
- a generalized Windows observation architecture, acoustic tomography, or a
  cross-domain predictive transformation.

## Artifact and history standing

Raw PCM was ephemeral. Each watcher hashed its complete byte stream before the
orchestrator independently verified the hash, derived measurements, and
deleted the raw file. The trace retains all packet metadata and per-observation
hashes. No raw `.pcm`, `.wav`, or `.raw` artifact is retained in the repository.

Durable bounded artifacts:

- `src/runtime/wasapi_loopback_witness_validation.py`, pressure-only
  instrumentation, SHA-256
  `14c5e5b99ad5c4248fdac479203c7705c090975cbd9fc9007e872fbaa84ddab7`;
- `tests/runtime/test_wasapi_loopback_witness_validation.py`, twelve
  hardware-free evidence checks;
- `traces/wasapi_loopback_witness_validation_v0.json`, full machine-readable
  trace, SHA-256
  `573e0bb377eb398c1aa55561c194fccdd4ffa5298b7ddeb682b8d62e6a8a4bcc`;
- this decision and `PROJECT_STATE.md`.

Canonical live history `traces/live_ingest_ledger_v0.jsonl` retained SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after acquisition. It was not appended or otherwise mutated.

## Distinction, chart, and production status

No distinction is added or amended. Existing source/observation,
raw/derived, configuration/occurrence, and structural/source-success
boundaries are sufficient to express the result. The requested render buffer
and observed endpoint mix remain different evidence objects without requiring
a new registry entry.

No chart is added. No watcher is promoted into a production source, adapter,
capture pipeline, or generalized framework. The implementation remains
pressure-only instrumentation.

## Verification

- focused witness suite: 12/12 passed;
- full hardware-free repository suite: 484/484 passed;
- primary audio trials: 15/15 retained, five per condition;
- distinct external watcher processes: 19;
- endpoint acquisition failures: 0;
- canonical history changed: no;
- `git diff --check`: passed, including separate checks for untracked artifacts.

No commit or push is part of this pressure. The final worktree intentionally
contains only the bounded decision/state update, pressure-only implementation
and tests, and machine-readable trace.
