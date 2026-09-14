# Acoustic Source-Coordinate Witness Selection Pressure v0

## Scope and Starting Boundary

This pass asks only which concrete observation point could expose part of the
unknown acoustic source-realization region before DME ingest. It performs
selection and reconnaissance. It does not emit or capture audio, actuate or
move hardware, change gain, install a dependency, implement an observer,
retain PCM, or modify production runtime.

Repository synchronization was established before the inspection:

- starting `HEAD`: `2618453d233a5867757c22ff732459f701834372`
  (`Predictive Transformation Selection`);
- `origin/main`: `2618453d233a5867757c22ff732459f701834372` after
  `git fetch origin main`;
- divergence: `0 0`;
- initial worktree: clean.

The earned starting result remains
`no_cross_domain_prediction_yet_earned`. The missing evidence is not another
microphone occurrence. It is an independently observed, pre-ingest acoustic
source-domain coordinate stronger than requested condition, occurrence ID,
admission, or an unknown realization, with observable equality/change and a
repository comparison at the same relational scale.

## Evidence Inspected Without Audio

The host reported Windows build `26200`, 64-bit. Read-only inspection found:

- built-in `MMDevAPI.dll`, `AudioSes.dll`, and `winmm.dll`, all reporting file
  version `10.0.26100.1`;
- a present Core Audio render endpoint named
  `Speakers (Realtek High Definition Audio)`;
- the current WinMM enumeration still exposed the Realtek speakers as output
  device 0 and only `Microphone (XIBERIA)` as a capture device;
- Core Audio additionally enumerated an iPhone hands-free microphone and
  speaker, but the microphone was not exposed by the current WinMM enumeration
  and its placement, capture fitness, and independence were not established;
- a non-present `Line In (Realtek High Definition Audio)` endpoint, but no
  present capture endpoint named `Stereo Mix`, `Waveout Mix`, `Mixed Output`,
  or `What You Hear`;
- no command named `ffmpeg`, `ffplay`, `sox`, `audacity`, `vlc`,
  `SoundVolumeView`, or `svcl`;
- no Python module named `sounddevice`, `pyaudio`, `soundfile`, `comtypes`, or
  `pycaw`.

The current pressure runtime calls `waveOutWrite`, then polls the output
header's `WHDR_DONE` flag before reset and close. It retains the time at which
the command was submitted, not the later done transition. Microsoft's
`WAVEHDR` contract says that `WHDR_DONE` is set by the device driver when it is
finished with the buffer and returns it to the application. That is real
completion metadata, but it is not an independently sampled render waveform.

The API interpretation below is grounded in Microsoft's documentation for
[WASAPI loopback recording](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording),
[loopback stream flags](https://learn.microsoft.com/en-us/windows/win32/coreaudio/audclnt-streamflags-xxx-constants),
[Core Audio user-mode components](https://learn.microsoft.com/en-us/windows/win32/coreaudio/user-mode-audio-components),
[capture packets and their timestamps](https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudiocaptureclient-getbuffer),
[session state](https://learn.microsoft.com/en-us/windows/win32/api/audiopolicy/nf-audiopolicy-iaudiosessioncontrol-getstate),
[endpoint peak meters](https://learn.microsoft.com/en-us/windows/win32/coreaudio/peak-meters),
[audio-clock position](https://learn.microsoft.com/en-us/windows/win32/api/audioclient/nf-audioclient-iaudioclock-getposition),
[WinMM playback position](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveoutgetposition),
and [`WAVEHDR`](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/ns-mmeapi-wavehdr).

## Observation Boundaries

The following boundaries remain distinct throughout the audit:

1. command requested;
2. software render buffer exists;
3. buffer submitted to an audio API;
4. endpoint/session reports active delivery or exposes the shared render mix;
5. driver/device receives or finishes a render stream;
6. electrical output exists;
7. speaker transducer actuates;
8. airborne acoustic field exists;
9. microphone transduces a local field;
10. sampled microphone PCM exists.

These numbers identify observation claims, not a claim that every device
implements one uniform ten-stage pipeline.

## Candidate Witness Matrix

| Witness | Observation boundary | Available now? | Independence class | Coordinate exposed | What it proves | What it cannot prove | Scale match to repo | New dependency/hardware | Smallest validation pressure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. WASAPI shared-mode loopback on the named Realtek render endpoint | 4; a hardware loopback pin could move the implementation source toward 5, but none is evidenced here | available with small built-in implementation, not currently implemented | `independent-software-observer` only when run in a separate process | mix-format PCM packets, frame counts, flags, stream-relative device positions, QPC timestamps, endpoint identity | the Windows audio engine exposed an observed render-endpoint mix downstream of application submission | exclusive-mode streams; attribution to this command without a quiet/control design; driver receipt when the software-copy path is used; boundaries 6-10 | `matched_scale_candidate` | no third-party dependency or new hardware; does require a new pressure-only observer regime | separate observer, frozen C0/S1/S1 schedule, ephemeral packets, endpoint/device-clock keyed hashes and measurements, existing mic capture |
| B. Core Audio session active/inactive/expired state | 4 status | available with small built-in implementation | `same-process-but-separately-observed` | categorical session state over host polling times | one or more streams in the session were running while active | non-silent samples, the intended buffer, mix content, device receipt, or boundaries 6-10 | `no_scale_match` | no dependency/hardware; new status reader | observe state transitions around a no-audio software-only stream control; insufficient for the wound even if it works |
| C. WASAPI state: endpoint meter, capture/render padding, `IAudioClock`, or `IAudioClock2` | 3-5 metadata; endpoint meter is a boundary-4 reduced signal observation | available with small built-in implementation | `same-process-but-separately-observed` | peak per device period, queued/available frame count, stream/device position and QPC correlation | a render-endpoint stream progressed or the endpoint mix had a nonzero peak during a period | sample identity or exclusive attribution; meter/clock state alone cannot establish electrical output, speaker motion, or field | `partial_scale_match` for meter values; otherwise `no_scale_match` | no dependency/hardware; new status reader | pair meter/clock readings with a frozen command/control, but reject as sole witness if PCM identity remains absent |
| D. Current WinMM completion plus optional `waveOutGetPosition` | 3 and boundary-5 driver completion/status | `WHDR_DONE` is available now and already polled; position is available with a small built-in change | `same-process-but-separately-observed` | done bit and optional playback position in a supported WinMM time format | the driver finished with and returned the submitted data block; position can progress after open | independently observed sample content, post-mix identity, routing beyond the selected handle, or boundaries 6-10 | `no_scale_match` | none, but exposing it would modify the pressure observer | retain a host timestamp for done or position progression; useful provenance, not sufficient source-coordinate evidence |
| E. PnP/MMDevice endpoint presence, default/role, and driver status | 4 capability/control metadata only | available now for presence; richer MMDevice properties need a small built-in reader | `independent-software-observer` | endpoint ID, friendly name, present/OK state, role and format metadata | Windows currently enumerates a named logical endpoint and backing device | an active stream, non-silent signal, rendered samples, or physical output | `no_scale_match` | none | re-enumerate before/after without audio; cannot validate the missing coordinate |
| F. Outgoing-buffer hash or render interception | 2 for current hash; 4 only if interception becomes loopback | hash available now; independent interception is not | `command-derived` | exact constructed PCM bytes, parameters, and hash | this process constructed buffer X | that Windows accepted, mixed, rendered, or physically emitted X | `no_scale_match` | none for hash; interception collapses into candidate A or another new observer | compare command hash with separately captured loopback bytes only after defining format conversion; command hash alone is rejected |
| G. Existing hardware/driver loopback | potentially 5 or 6, depending the device's undocumented tap | not available / not evidenced | `unknown` | potentially a driver mix or electrical-return waveform | only the boundary documented for that particular loopback implementation | anything upstream or downstream not covered by the device-specific tap | `partial_scale_match` if content-bearing | may require enabling an undocumented device or hardware routing | first establish a present endpoint and its documented tap boundary; none exists in current evidence |
| H. External electrical-output observation | 6 | requires new hardware | `independent-physical-observer` | voltage waveform at a declared output point with the instrument's clock | electrical output existed at that point and had the observed waveform | speaker motion, airborne field, or microphone reception | `matched_scale_candidate` at finite content-observation scale | isolated interface, ADC, or oscilloscope and safe connection | conceptually compare commanded conditions with ephemeral voltage captures; out of scope and stronger than currently necessary |
| I. Second independent microphone or sensor | 9 and 10, indirectly boundary 8 at its location | not available / not evidenced as a usable independent path; one extra PnP microphone endpoint is present but unvalidated and absent from current WinMM enumeration | `independent-physical-observer` if physically independent and separately clocked | local-pressure transduction and sampled PCM at a second declared location | a second sensor observed a local field | electrical output, direct speaker actuation, the entire room field, or source attribution | `partial_scale_match` | may require a new device path, observer, placement basis, or hardware | only after identity, placement, clock, and independence are established; not the smallest source witness |
| J. Speaker accelerometer, laser/vibration sensor, or contact microphone | 7 proxy | requires new hardware | `independent-physical-observer` | local transducer motion or vibration over the sensor clock | motion occurred at the instrumented point | electrical cause, full diaphragm motion, airborne field, or microphone reception | `partial_scale_match` | new hardware and physical setup | freeze sensor attachment and compare control/command occurrences; out of scope and stronger than necessary |
| K. No suitable current witness | none | available as the conservative fallback | `unknown` | none | only that current evidence does not justify promotion | it does not prove no witness could be built | `no_scale_match` | none | preserve the wound until a bounded observer is separately authorized |

## Coordinate Quality Audit

### A. WASAPI endpoint-loopback PCM

- **Observed value:** packets of the selected render endpoint's shared-mode mix,
  with format, frame count, silent/discontinuity/timestamp flags, device position,
  and QPC time for each packet.
- **Scope:** all audio in the endpoint mix by default, not just the pressure
  process. Endpoint identity and quiet/control conditions therefore belong in
  the observation scope.
- **Clock basis:** `IAudioCaptureClient::GetBuffer` supplies a stream-relative
  device-frame position and a correlated QPC value in 100 ns units. This is an
  endpoint timing basis; it is not a shared DAC/microphone hardware clock.
- **Identity basis:** exact endpoint ID + mix format + bounded device-frame
  interval + canonical packet bytes and flags. A SHA-256 can identify that
  observed finite interval after capture; it does not identify the command.
- **Equality test:** identical scoped endpoint, format, frame interval, flags,
  and canonical PCM bytes.
- **Change test:** any declared identity component differs. Derived RMS or peak
  can be reported separately but cannot replace byte equality.
- **Source-relative meaning:** Windows made mix PCM available on the selected
  render endpoint after application submission and audio-engine mixing.
- **Blind spots:** other sessions contaminate the mix; protected or exclusive
  content can be absent; endpoint processing and hardware-pin behavior can
  differ; no electrical output, speaker motion, airborne field, or microphone
  reception follows from the loopback packets.

Microsoft specifies loopback only for a shared-mode render endpoint. The audio
engine copies the stream being played into a capture buffer; on hardware that
supports a loopback pin it may use that pin, otherwise it copies audio-engine
output while also sending data toward the hardware render pin. Current host
inspection did not determine which path the Realtek endpoint would use.
Therefore the defensible current boundary is 4, not 5 or 6.

This observation is **post-system-mix** for the selected endpoint in the normal
shared-mode software path and is downstream of the application's
`waveOutWrite`. It can distinguish “the process constructed/submitted a
buffer” from “a post-mix render stream was independently present.” It cannot
show that the loopback bytes equal the input bytes without accounting for
format conversion, mixing, volume, and processing. It cannot prove electrical
output or speaker actuation.

### B/C. Endpoint, session, meter, and clock coordinates

`AudioSessionStateActive` means that a session has at least one running stream;
it does not say that the running samples are non-silent. Endpoint presence says
the logical device is enumerated, not that it is delivering audio.

An endpoint peak meter is more than configuration metadata: for a render
device it reports the maximum sample magnitude in the output stream during the
preceding device period. It is still a lossy scalar with no waveform identity
or source attribution. Padding, position, and clock readings establish buffer
or stream progression. They are timing/status coordinates, not independent
observations of the rendered signal's content. These can support a loopback
witness but cannot substitute for it.

### D. WinMM completion coordinate

The existing `WHDR_DONE` poll observes the driver returning the exact buffer
owned by the submitting process. Its value is meaningful: it is stronger than
the retained submission timestamp. Its independence remains only
`same-process-but-separately-observed`, and its identity is inherited from the
submitted buffer rather than independently measured at the endpoint.
`waveOutGetPosition` could add a playback-position series, but neither result
contains post-mix sample values. They improve delivery provenance without
closing the source-coordinate wound.

### G-J. Physical coordinates

An electrical tap crosses boundary 6; a motion sensor crosses boundary 7; a
second microphone crosses boundaries 9-10 and samples boundary 8 only at its
location. Those witnesses are epistemically stronger along different parts of
the chain, but all introduce a new device/observer/placement basis. The current
wound does not require proof of physical emission if boundary-4 post-mix PCM
already supplies an independently observed source-relative content coordinate.
Maximum physical instrumentation is therefore not selected.

## Same-Scale Comparison

The strongest proposed pairing is:

| Dimension | Repository coordinate | Acoustic coordinate |
| --- | --- | --- |
| coordinate | filesystem structural snapshot under a declared root/exclusion scope | render-endpoint mix PCM under declared endpoint/format/device-frame scope |
| equality | identical canonical structural entries and snapshot identity | identical canonical PCM bytes, packet flags, endpoint/format, and frame interval |
| change | at least one scoped structural fact changes | at least one scoped mix-content or scope fact changes |
| transformation | repeat observation without a selected source change, or make a bounded filesystem change | repeat observation without a selected command change, or make a bounded requested-render change |
| preserved relation sought | equal observed source-relative content can coexist with distinct observation occurrences | equal observed source-relative content can coexist with distinct observation occurrences |
| residue | symbolic paths, file hashes, exclusions, interval capture, non-atomic filesystem world | time-indexed continuous-signal reduction, endpoint mixing, other sessions, conversions, device clock, no physical-output proof |

This is a `matched_scale_candidate`, not an earned correspondence. Both sides
would have finite, content-bearing, independently observed, source-relative
coordinates before DME ingest, and both support exact equality/change without
using occurrence IDs or requested labels. The residues prevent equivalence:
one is a structural snapshot and one is a temporal mixed stream. A future
pressure must show that the proposed acoustic coordinate is actually
observable and that its equality/change is not reconstructed from the command.

Endpoint state, buffer completion, and device presence have
`no_scale_match`: they are operation/status coordinates rather than
content-bearing source observations. Peak meter and physical-proxy candidates
have only `partial_scale_match` unless a declared content identity and scope are
earned.

## Minimal Sufficient Witness

The weakest materially improving claim is:

> A separately running observer obtained post-mix PCM Y from the selected
> Realtek render endpoint over device-frame interval I.

That claim is stronger than “the chirp buffer was constructed” and “WinMM
accepted/returned the buffer,” while remaining weaker than “the speakers
emitted the intended airborne field.” It is sufficient to introduce a
content-bearing acoustic coordinate at the same candidate relational scale as
a repository snapshot. No electrical or mechanical witness is currently
required.

The host contains the Windows APIs needed to attempt this, but it contains no
installed loopback utility/library and the repository contains no independent
loopback observer. Creating one would be a **new observer regime**. Built-in API
availability establishes feasibility, not an existing witness observation.

## Frozen Future Validation Pressure

This design is a proposal only and is not authorized or executed here.

```text
requested source condition (C0, then S1, then repeated S1)
        -> separate-process WASAPI loopback on the exact Realtek endpoint
        -> existing XIBERIA microphone observation
```

Before any execution, freeze endpoint ID, shared mix format, safe existing
amplitude, device-frame windowing, quiet-room/no-other-render-session rule,
packet canonicalization, exact-equality rule, derived change rule, microphone
measurement, occurrence order, and raw-PCM deletion.

Observe ephemeral loopback packets with device position/QPC and the existing
microphone reduction for each occurrence. Retain only bounded metadata,
canonical hashes, measurements, and capture errors; delete loopback and mic PCM
after reduction.

- **Witness success:** the independent process returns well-timestamped
  mix-format packets from the exact endpoint; the C0/S1 observations expose an
  observed change, and repeated S1 observations make equality or inequality an
  empirical result rather than a requested-label assumption.
- **Witness failure:** initialization, endpoint binding, timestamps, packets,
  or declared scope are unavailable; all packets are unusably silent or
  contaminated; or the observer cannot distinguish C0 from a delivered S1
  under the frozen rule.
- **Command/witness circularity:** the “observed” identity is copied from the
  command buffer or its metadata, the observer runs only inside the submitting
  code path, or packet content is inferred from `waveOutWrite`/`WHDR_DONE`
  rather than read from `IAudioCaptureClient`.
- **Claim licensed by success:** an independently observed post-mix endpoint
  coordinate existed, with declared equality/change and timing, downstream of
  command submission and before microphone ingest.
- **Claims still unlicensed:** byte identity with the requested buffer absent a
  conversion proof; exclusive attribution absent a clean endpoint scope;
  driver receipt on a specific hardware path; electrical output; speaker
  actuation; airborne-field identity; causal attribution of microphone PCM;
  tomography; or a cross-domain prediction.

## Required Result

```text
candidate_requires_new_basis
```

WASAPI endpoint loopback is the concrete legitimate candidate. The current
host supplies the built-in API and target endpoint, but not an existing
independent observer or an observed coordinate. A future pressure would need a
new, pressure-only, separate-process software observer regime. That condition
matches `candidate_requires_new_basis` even though it requires neither a
third-party dependency nor new hardware.

No other current candidate supplies content-bearing, independently observed
source coordinates. WinMM completion is retained as a useful unexposed status
fact, not promoted into render truth.

## Distinction and Production Status

No distinction is added or amended. Existing source/observation,
state/occurrence, raw/derived, and structural-admission/source-success
boundaries express every failure encountered here. “Source coordinate,”
“witness,” and “render truth” are not registered.

No runtime, source, observer, dependency, trace, test, device setting, or
canonical ledger is changed. No audio is emitted or captured, and no PCM is
retained.

## Verification and Artifacts

Tests:

- baseline full hardware-free suite: 469/469 passed;
- final full hardware-free suite: 469/469 passed;
- runner: `python -m unittest discover -s tests -v`; neither run executed a
  hardware-dependent pressure.

Canonical live history `traces/live_ingest_ledger_v0.jsonl` had SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after this pass. No `.wav`, `.pcm`, or `.raw` artifact was created.

Artifacts intended to change:

- this decision record;
- `PROJECT_STATE.md`.

Final `HEAD` and `origin/main` remain
`2618453d233a5867757c22ff732459f701834372` with divergence `0 0`. The final
worktree contains only the two scoped documentation changes above.
