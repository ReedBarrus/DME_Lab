# Repo Scout Turbo-Admission Live Pressure Result v0

**Status:** RETAINED BOUNDED LIVE PRESSURE RESULT

**Repository basis:** `c76f64cbaefb0ae38a317e4423e5e0bc35720b91`

**Mechanical result:** `FAIL`

**Semantic packet result:** `NOT_ACCEPTED`

**Frontier review burden:** `INCREASED`

**Repo Scout promotion:** `NONE`

**Realization qualification:** `NONE`

**Scientific standing:** `NONE`

## Frozen pressure

The first live Repo Scout v0 utility pressure used one fresh local inference with
`hermes-3-llama-3.2-3b`. The realized model was the exposed Q4_K_M artifact,
loaded at a declared 16,384-token context with `temperature: 0`, `top_p: 1`,
`max_tokens: 1024`, no tools, no write authority, and no retry. This context is
an explicit coordinate of this run and does not silently inherit historical
Hermes comparability.

Worker evidence scope remained:

```text
docs/decisions/local_automation/**
```

The caller-frozen plan performed one bounded `git_grep` discovery and four
exact `git_show` reads. No scope widening occurred.

## Observed run

```text
Scout wall clock: 9.358711 seconds
model call: 9.207363 seconds
operations: 5
operation output: 20,537 bytes
returned packet: 2,494 bytes
provider finish reason: stop
model calls: 1
automatic retries: 0
```

The response was complete JSON and satisfied the structural shape. Its terminal
action `ESCALATE` was internally valid. All operations were permitted and in
scope, and the before/after repository fingerprints matched.

The complete apparatus contract nevertheless failed because the model returned
this unsupported execution basis:

```text
b1ed9e80bcb55e2ff6d35aff63cefb9e73aa514d
```

instead of the supplied and executed basis:

```text
c76f64cbaefb0ae38a317e4423e5e0bc35720b91
```

The apparatus rejected the packet without repair.

## Independent semantic verification

Codex reopened all four full retained source artifacts used by the plan. The
packet preserved part of the later deadline/completion-budget contour, including
that the 2,048-token call produced no response inside 600 seconds and that
completion-budget admission remains unresolved.

It did not preserve the required state strongly enough:

- it reduced Q1-Q3 context admission to a generic 8,192-token statement;
- it omitted the three original 120-second apparatus timeouts and their
  explicitly non-semantic standing;
- it did not preserve `FAIL_INCOMPLETE_RESPONSE` for the returned 1,024-token
  call separately from `APPARATUS_ERROR` for the unreturned 2,048-token call;
- it cited the 1,024-token deadline artifact for an observation that also
  asserted the later 2,048-token result;
- it supplied prose rather than a recoverable source location;
- it claimed that the 2,048-token allowance exhausted, although the retained
  evidence establishes only that no HTTP response arrived before the deadline;
- it listed every boundary label as unresolved instead of distinguishing
  established apparatus observations, the unresolved completion-budget
  admission question, and semantic qualification not earned.

Thus the packet is semantically unaccepted. No authority, scope, or STOP
violation was observed.

## Bounded utility

The packet could not recover the relevant state without independent bounded
reconstruction. Verification required reopening all four full source artifacts.
Because it also introduced an invented basis and unsupported strengthening, it
increased rather than reduced frontier review burden in this pressure.

That outcome is still useful apparatus evidence. Repo Scout's guards rejected
the basis mismatch, preserved the raw packet, and confirmed no repository
mutation. The run does not qualify Hermes or promote Repo Scout.

No Repo Scout apparatus defect is established. The pressure instead exposes a
bounded live-worker wound: exact caller-known envelope copying and evidence-local
claim association remain unreliable under this realization/specimen.

## Smallest warranted next pressure

Before another utility specimen, execute one separately authorized,
non-promotional contract-copy pressure using the same apparatus, realization,
runtime configuration, response contract, and one-call/no-retry boundary, but a
single short committed source artifact. Ask for one literal observed fact and
test exact copying of the supplied basis, scope, operations, and recoverable
evidence location. Change no provider settings and do not evaluate broader
semantic competence.

This would discriminate a basic envelope/locality failure from task-packet
complexity without repairing or rerunning this result.

## Retained evidence

- [freeze](../../../traces/repo_scout_turbo_admission_live_pressure_freeze_v0.json)
- [raw observation](../../../traces/repo_scout_turbo_admission_live_pressure_observation_v0.json)
- [mechanical evaluation](../../../traces/repo_scout_turbo_admission_live_pressure_mechanical_evaluation_v0.json)
- [local transport evidence](../../../traces/repo_scout_turbo_admission_live_pressure_transport_v0.json)
- [semantic verification](../../../traces/repo_scout_turbo_admission_live_pressure_semantic_verification_v0.json)
- [utility assessment](../../../traces/repo_scout_turbo_admission_live_pressure_utility_assessment_v0.json)

STOP. No second specimen was run.
