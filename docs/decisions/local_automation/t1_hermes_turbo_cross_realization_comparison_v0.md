# T1 Hermes / Turbo Cross-Realization Comparison v0

**Status:** RETAINED BOUNDED COMPARISON
**Turbo T1 qualification:** NOT EARNED
**Campaign outcome:** `INSUFFICIENT_EVIDENCE`
**Promotion:** `NONE`
**Q4:** HELD OUT / NOT EXECUTED

## Scope

This comparison changes one intended coordinate: the identified local
realization. It reuses the frozen Q1-Q3 task family, source packets, prompt
templates, response contracts, strict parsers, sampling settings, fresh-context
rule, one-call rule, no-tools boundary, and evaluator regime.

The realized systems are not otherwise identical. Turbo identity and runtime
coordinates were more completely exposed, and its context was deliberately
re-frozen from 4,096 to 8,192 before any scientific inference. Hermes Q1/Q2
context remains unknown; Hermes Q3 exposed 4,096 through its retained rejection.

## Turbo realization basis

```text
requested / loaded identifier:
qwen3.8-27b-turbo-fable-cold-fusion-735-882-heretic-uncensored-neo-coder-max-mtp

display name:
Qwen3.8 27B TurboFCFusion 735 882 Here Uncen NEO CODER MAX

architecture: qwen35
format: gguf
quantization: Q4_K_M, 4 bits per weight
configured context: 8192
model-supported maximum context: 262144
runtime engine: llama.cpp-win-x86_64-nvidia-cuda12-avx2@2.37.0
LM Studio app: 0.4.24+1
LM Studio CLI commit: ff50809
endpoint: http://127.0.0.1:1234/v1/chat/completions
temperature: 0.0
top_p: 1.0
max_tokens: 1024
tools / MCP / repository authority: none
```

Model artifact digest remains unknown. The model-supported maximum context is
not the configured context.

## Admission and execution

Exact preflight used the loaded realization's prompt template and tokenizer.
The 1,024-token output allowance was included:

| Specimen | Rendered input | Total with reserve | 8,192 admission | Retained execution |
| --- | ---: | ---: | --- | --- |
| Q1 | 3,705 | 4,729 | admitted | one call; timeout; no response |
| Q2 | 2,959 | 3,983 | admitted | one call; timeout; no response |
| Q3 | 6,707 | 7,731 | admitted | one call; timeout; no response |

Every call used execution-basis commit
`b1ed9e80bcb55e2ff6d35aff63cefb9e73aa514d`, which resolved and equaled
committed `HEAD` before inference. Each retained one call and zero retries.
Protected surfaces remained unchanged during each invocation.

The common terminal classification is:

```text
mechanical: APPARATUS_ERROR
semantic: NOT_EVALUABLE_APPARATUS_ERROR
promotion: NONE
```

All three failures were `APPARATUS_TIMEOUT_AFTER_CONTEXT_ADMISSION` at the
frozen 120-second client timeout. Timeout is not semantic failure. No response
exists from which to evaluate promotion error, semantic violation,
completeness, scope, authority, or model STOP compliance.

## Bounded Hermes / Turbo comparison

Hermes Q1 and Q2 returned mechanically valid symbolic responses. Q1 retained
useful evidence but omitted part of the required promotion boundary. Q2
materially misrepresented P8/P11 and introduced unsupported strengthening.
Turbo returned no symbolic response on Q1 or Q2, so it neither preserves nor
loses those distinctions in the retained evidence. They are unobserved.

Turbo Q3 does establish one narrower apparatus difference:

```text
Turbo Q3 request plus output reserve admitted at configured 8192
!=
Hermes Q3 request rejected at exposed 4096
```

The Turbo Q3 call then timed out. Admission therefore did not become a semantic
observation. Context configuration, runtime allocation, and realization differ;
the evidence does not attribute admission or timeout to model family, parameter
count, or semantic capability.

Because Turbo produced no model response, no cross-realization semantic
transformation pattern can be evaluated. The Semantic Compression Dynamics
projection gains no new standing.

## Apparatus change

The only implementation addition is a thin cross-realization harness that:

- reuses the committed Q1-Q3 policy-visible packet builders, prompts, schemas,
  and parsers;
- freezes the exposed Turbo identity and 8,192-token loaded configuration;
- retains exact request hashes and token admission records;
- rejects provenance, model identity, or loaded-configuration drift before a
  call;
- writes separate raw observation and mechanical evaluation artifacts.

It is not a scheduler, model router, daemon, worker system, or qualification
authority.

## Standing and STOP

```text
T1 QUALIFICATION: NOT EARNED
CAMPAIGN OUTCOME: INSUFFICIENT_EVIDENCE
PROMOTION: NONE
Q4: NOT EXECUTED
```

No other model was loaded. No scientific standing, project-state surface,
pressure map, or projection was modified.

## Evidence

- [Turbo freeze](../../../traces/local_model_qualification_t1_turbo_freeze_v0.json)
- [Turbo Q1 observation](../../../traces/local_model_qualification_t1_turbo_q1_observation_v0.json)
- [Turbo Q1 mechanical evaluation](../../../traces/local_model_qualification_t1_turbo_q1_mechanical_evaluation_v0.json)
- [Turbo Q1 semantic evaluation](../../../traces/local_model_qualification_t1_turbo_q1_semantic_evaluation_v0.json)
- [Turbo Q2 observation](../../../traces/local_model_qualification_t1_turbo_q2_observation_v0.json)
- [Turbo Q2 mechanical evaluation](../../../traces/local_model_qualification_t1_turbo_q2_mechanical_evaluation_v0.json)
- [Turbo Q2 semantic evaluation](../../../traces/local_model_qualification_t1_turbo_q2_semantic_evaluation_v0.json)
- [Turbo Q3 observation](../../../traces/local_model_qualification_t1_turbo_q3_observation_v0.json)
- [Turbo Q3 mechanical evaluation](../../../traces/local_model_qualification_t1_turbo_q3_mechanical_evaluation_v0.json)
- [Turbo Q3 semantic evaluation](../../../traces/local_model_qualification_t1_turbo_q3_semantic_evaluation_v0.json)
- [machine-readable comparison](../../../traces/local_model_qualification_t1_hermes_turbo_comparison_v0.json)
- [Hermes checkpoint](hermes_t1_qualification_checkpoint_v0.md)
