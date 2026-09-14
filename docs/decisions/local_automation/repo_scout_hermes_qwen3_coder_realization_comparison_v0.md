# Repo Scout Hermes / Qwen3 Coder Realization Comparison v0

**Status:** RETAINED NON-ADMISSIBLE LIVE PRESSURE RESULT

**Repository basis:** `d5f366cbe866386b81d4b6eb67b04c89c1b40e80`

**Source equivalence:** `PASS`

**Apparatus equivalence:** `PASS`

**Qwen mechanical result:** `APPARATUS_ERROR_CLIENT_INTERRUPTION`

**Qwen semantic result:** `NOT_EVALUABLE_APPARATUS_ERROR`

**Cross-realization comparison:** `NON_ADMISSIBLE`

**Repo Scout promotion:** `NONE`

**Realization qualification:** `NONE`

**Scientific standing:** `NONE`

## Frozen comparison basis

Hermes B was not rerun. The committed B result supplied the source, exact
question, caller-frozen plan, allowed operation, budgets, corrected model-owned
contract, evaluator, and authority boundary.

The apparatus and source at the Qwen basis resolve to the same Git blobs used
by Hermes B:

```text
apparatus: src/runtime/repo_scout.py
Git blob: 90fc6509ad50355a43ec733251039bcd53108d8b

source: docs/decisions/local_automation/turbo_t1_q1_completion_budget_pressure_result_v0.md
Git blob: 865b73e0c0703831132cccb8478bf76a68d8b004
```

The only declared intervention was realization. The locally available model
was frozen as `qwen/qwen3-coder-30b`, Qwen3 MoE, `30B-A3B`, GGUF `Q4_K_M`,
18,632,365,388 bytes, loaded at 16,384 context with parallel 1, maximum GPU
offload, flash attention, no speculative draft/MTP, temperature 0, top-p 1,
and `max_tokens` 1,024. LM Studio exposed app version `0.4.24+1` and CLI commit
`ff50809`; a model artifact digest and runtime engine version remained missing.

## One-call result

Exactly one fresh Qwen call was initiated with zero retries. The LM Studio
server log records:

```text
16:22:38  call began
16:22:49  prompt processing completed
16:24:02  client disconnected; generation stopped
```

The client process ended before Repo Scout returned or persisted its normal
observation. Consequently, no complete client HTTP response, exact client
duration, serialized request copy, strict parse, mechanical envelope, derived
terminal action, or runner before/after repository fingerprint pair survives.
No second Qwen call was made.

The server log retained a 1,072-byte response-content prefix. It ends inside
the second evidence observation and is not a complete JSON model proposal.
That prefix is retained verbatim in transport-recovery evidence but is not
repaired, completed, or selectively scored.

## Mechanical and semantic standing

Basis, apparatus, source, scope, and realization preflight passed before the
call. Reaching the model call also establishes that the one frozen read
operation completed through the apparatus sequence. The interruption prevented
the remaining mechanical checks from completing.

This is an apparatus error, not a Qwen semantic failure. All model-owned
conservation criteria remain unevaluated:

- source-supported observation fidelity;
- missingness preservation;
- source association and recoverable location;
- distinction preservation and unsupported strengthening; and
- escalation quality.

The partial server-log prefix receives neither credit nor penalty because the
strict apparatus never received a complete proposal.

## Cross-realization interpretation

The requested Hermes/Qwen comparison is non-admissible. Hermes B produced a
mechanically valid, fully evaluable proposal; this Qwen run did not preserve a
complete result. Model duration, total Scout duration, packet size, semantic
conservation, and utility therefore cannot be compared on the requested basis.

The Qwen run created greater frontier burden than Hermes B because recovery
required reopening retained artifacts and a local server log without yielding
an evaluable packet. This is a property of this interrupted run, not evidence
of general Qwen utility or incapability.

```text
realization capability
!=
apparatus capability
!=
task utility
!=
qualification
!=
authority
```

## Next pressure

Repository evidence does **not** yet warrant moving Qwen3 Coder into bounded
candidate-patch generation or another transformation regime. The present
regime has not produced an observable complete Qwen result.

The smallest warranted pressure is apparatus-only and uses no model: simulate
a client interruption and require the frozen invocation, operation evidence,
serialized request, call-attempt marker, and repository fingerprints to remain
retained. A later live Qwen call would require separate authorization and would
be a new pressure, not a repair or retry of this run.

## Retained evidence

- [freeze](../../../traces/repo_scout_qwen3_coder_realization_comparison_freeze_v0.json)
- [interrupted observation](../../../traces/repo_scout_qwen3_coder_realization_comparison_interrupted_observation_v0.json)
- [transport recovery](../../../traces/repo_scout_qwen3_coder_realization_comparison_transport_recovery_v0.json)
- [mechanical evaluation](../../../traces/repo_scout_qwen3_coder_realization_comparison_mechanical_evaluation_v0.json)
- [semantic evaluation](../../../traces/repo_scout_qwen3_coder_realization_comparison_semantic_evaluation_v0.json)
- [cross-realization comparison](../../../traces/repo_scout_qwen3_coder_realization_comparison_v0.json)
- [utility assessment](../../../traces/repo_scout_qwen3_coder_realization_comparison_utility_assessment_v0.json)

STOP. Hermes was not rerun, no second Qwen call occurred, and no patch-writing
task was executed.
