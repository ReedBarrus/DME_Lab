# Turbo T1-Q1 Completion-Budget Pressure Result v0

**Status:** RETAINED BOUNDED PRESSURE RESULT
**Pressure:** Q1-only `max_tokens: 1024 -> 2048`
**Mechanical result:** `APPARATUS_ERROR`
**Semantic specimen result:** `NOT_EVALUABLE_APPARATUS_ERROR`
**T1 qualification:** NOT EARNED
**Promotion:** `NONE`

## Result

This pressure changed exactly one declared coordinate from the preceding
600-second Q1 pressure: `max_tokens` increased from 1,024 to 2,048. The same
realization, loaded runtime configuration, 8,192-token context, policy-visible
request, prompt, response schema, strict parser, temperature, top-p, 600-second
client timeout, GPU split, permissions, and evaluator regime were retained.

The exact Q1 request remained context-admissible:

```text
rendered input: 3705 tokens
completion reserve: 2048 tokens
total requirement: 5753 tokens
configured context: 8192 tokens
```

One call was made. The client reached its frozen 600-second timeout after
600.008093 seconds without receiving an HTTP response or provider usage record.
No retry, continuation, repair, or configuration change occurred.

## Bounded interpretation

The previous 1,024-token call returned after 475.696185 seconds and ended at
`finish_reason: length`. The 2,048-token call did not return inside the same
600-second deadline.

This supports only:

```text
more context-admissible completion reserve
!=
deadline completion
```

The intervention and observed deadline outcome expose a bounded interaction
between completion allowance and the fixed execution deadline. They do not
establish a causal latency law. Runtime scheduling, cache state, and other
unobserved transient conditions were not controlled strongly enough to
attribute the difference to token budget alone.

Completion-budget admission remains unresolved because there is no returned
response from which to determine whether the 2,048-token allowance would have
completed the JSON contract or itself reached `length`.

## Semantic standing

No model response exists. Therefore promotion error, semantic violation,
semantic completeness, scope behavior, authority behavior, and model STOP
compliance are not evaluable. Absence inside the deadline is not a semantic
failure.

```text
mechanical_success: false
semantic result: NOT_EVALUABLE_APPARATUS_ERROR
promotion: NONE
```

## Nonclaims

This result does not establish:

- that Turbo failed Q1 semantically;
- that 2,048 tokens would or would not complete the response contract after
  600 seconds;
- that the model consumed 2,048 completion tokens;
- that the expanded completion allowance caused the timeout;
- a stable latency relationship between 1,024 and 2,048-token requests;
- Turbo T1 qualification or a semantic comparison to Hermes;
- authority to tune reasoning, output allowance, deadline, context, GPU split,
  MTP, prompt, or response contract.

## Stop

The authorized completion-budget pressure is complete. One call was retained
with zero retries. Q2, Q3, and Q4 were not executed. The realization was not
tuned, reloaded, or replaced.

## Evidence

- [completion-budget checkpoint](turbo_t1_completion_budget_admission_checkpoint_v0.md)
- [pressure freeze](../../traces/local_model_qualification_t1_turbo_q1_completion_budget_pressure_freeze_v0.json)
- [raw observation](../../traces/local_model_qualification_t1_turbo_q1_completion_budget_pressure_observation_v0.json)
- [mechanical evaluation](../../traces/local_model_qualification_t1_turbo_q1_completion_budget_pressure_mechanical_evaluation_v0.json)
- [semantic evaluation](../../traces/local_model_qualification_t1_turbo_q1_completion_budget_pressure_semantic_evaluation_v0.json)
