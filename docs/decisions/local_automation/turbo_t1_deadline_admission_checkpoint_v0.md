# Turbo T1 Deadline-Admission Checkpoint v0

**Status:** RETAINED BOUNDED CHECKPOINT
**Repository basis:** `a092bb4679e90a709c8086870fdd06aa89a50e7b`
**T1 qualification:** NOT EARNED
**Campaign outcome:** `INSUFFICIENT_EVIDENCE`
**Promotion:** `NONE`
**Scientific standing:** NONE

## Checkpoint claim

The completed Turbo T1 cross-realization comparison produced no semantic model
evidence. It established one operational distinction:

```text
context-admissible
!=
deadline-admissible
!=
semantically-qualified
```

Here, context admission means only that the exact rendered input plus the
declared output reserve fit inside the configured context. Deadline admission
means that the request also returns an evaluable response within a declared
execution deadline. Neither condition is semantic qualification.

## Established

The identified Turbo realization was loaded with a frozen configured context of
8,192 tokens. Exact preflight admitted all three T1 requests:

| Specimen | Rendered input | Output reserve | Total requirement |
| --- | ---: | ---: | ---: |
| Q1 | 3,705 | 1,024 | 4,729 |
| Q2 | 2,959 | 1,024 | 3,983 |
| Q3 | 6,707 | 1,024 | 7,731 |

Each specimen then received exactly one local inference call under the same
frozen 120-second client timeout. Every call reached that deadline without a
returned model response. Each observation retained:

- valid execution-basis provenance;
- successful context admission;
- one call and zero retries;
- unchanged protected surfaces;
- `TimeoutError: timed out`;
- no raw model response.

The three retained outcomes are apparatus errors after context admission. They
are not semantic failures.

## Not established

The evidence does not establish:

- a semantic comparison between Turbo and Hermes;
- Turbo T1 qualification or routing eligibility;
- general competence or incompetence of this model, model family, size, or
  quantization;
- that 120 seconds is generally insufficient for all Turbo workloads;
- that the model could not complete any specimen after the client stopped
  waiting;
- that a longer deadline will produce a valid or semantically adequate result;
- any scientific standing or project-state change.

Absence of a returned response inside the frozen deadline is not evidence of a
particular semantic transformation.

## Open pressure

The smallest next pressure is whether the unchanged Turbo realization can
return one bounded T1-Q1 response under a longer declared deadline before any
realization tuning is attempted.

Freeze the pressure as:

```yaml
realization: unchanged Turbo realization
specimen: T1-Q1 only
prompt and evaluator: unchanged
configured context: 8192
sampling: unchanged
tools and write authority: none
client timeout: 600 seconds
automatic retries: 0
```

Exactly one coordinate changes:

```text
client timeout: 120 seconds -> 600 seconds
```

Reasoning mode, context, MTP, output allowance, prompt, response schema, parser,
GPU split, source packet, authority, and evaluation regime remain unchanged.

This is a new deadline-admission pressure derived from the retained timeout
evidence. It is not a repair, replacement, or retry of the completed
120-second cross-realization campaign. That campaign and all its results remain
immutable.

## Stop boundary

The new pressure authorizes one Q1 call only. Stop after its raw observation,
mechanical evaluation, and independent semantic evaluation are retained. Do not
run Q2, Q3, or Q4. Do not tune or load another realization.

## Evidence

- [Turbo cross-realization comparison](t1_hermes_turbo_cross_realization_comparison_v0.md)
- [Turbo realization freeze](../../../traces/local_model_qualification_t1_turbo_freeze_v0.json)
- [Turbo Q1 observation](../../../traces/local_model_qualification_t1_turbo_q1_observation_v0.json)
- [Turbo Q2 observation](../../../traces/local_model_qualification_t1_turbo_q2_observation_v0.json)
- [Turbo Q3 observation](../../../traces/local_model_qualification_t1_turbo_q3_observation_v0.json)
