# Turbo T1 Completion-Budget Admission Checkpoint v0

**Status:** RETAINED BOUNDED CHECKPOINT
**Repository basis:** `3a869d7a6579400746e463c3f812641b0573765f`
**T1 qualification:** NOT EARNED
**Promotion:** `NONE`
**Scientific standing:** NONE

## Checkpoint claim

The Turbo T1-Q1 deadline pressure returned successfully at the transport layer
inside its declared 600-second deadline, but exhausted its 1,024-token
completion allowance before satisfying the response contract.

The earned operational distinction is now:

```text
context-admissible
!=
deadline-admissible
!=
completion-budget-admissible
!=
response-contract-complete
!=
semantically-qualified
```

These are apparatus boundaries. They are not model intentions, semantic
faculties, or scientific claims.

## Established

The exact Q1 request was context-admitted at 8,192 tokens. With the client
timeout changed from 120 to 600 seconds and all other declared coordinates
held constant, one call returned HTTP 200 after 475.696185 seconds.

The provider reported:

```text
finish_reason: length
prompt_tokens: 3705
completion_tokens: 1024
reasoning_tokens: 940
```

The response ended inside its first JSON string. The frozen strict parser
rejected it without repair. The retained result was:

```text
mechanical: FAIL
semantic specimen: FAIL_INCOMPLETE_RESPONSE
promotion: NONE
```

The returned fragment was bounded and useful, but it did not expose all
required fields or a terminal action. Missing content remains missing.

## Not established

The evidence does not establish:

- that Turbo failed Q1 semantically;
- what the unreturned fields or terminal action would have contained;
- that reasoning-token use is fixed near 940 tokens;
- that 1,024 completion tokens are generally insufficient for Turbo;
- that 2,048 completion tokens will complete this response contract;
- that the earlier 120-second call would have returned the same response;
- Turbo T1 qualification or a semantic comparison to Hermes;
- authority to tune reasoning mode, context, MTP, prompt, GPU split, or the
  response contract.

## Open pressure

The smallest next pressure changes only the Q1 completion allowance:

```yaml
realization: unchanged Turbo realization
specimen: T1-Q1 only
prompt, schema, parser, and evaluator: unchanged
configured context: 8192
temperature: 0.0
top_p: 1.0
client timeout: 600 seconds
max_tokens: 2048
tools and write authority: none
automatic retries: 0
```

The admission arithmetic becomes:

```text
rendered input: 3705
completion reserve: 2048
total requirement: 5753
configured context: 8192
```

The pressure is context-admissible with 2,439 tokens of unused context capacity
under this conservative input-plus-reserve accounting.

Exactly one coordinate changes:

```text
max_tokens: 1024 -> 2048
```

This is a new completion-budget pressure, not a retry or repair of either prior
Q1 observation. Both earlier results remain immutable.

## Stop boundary

Authorize one Q1 call only. Retain its raw observation, mechanical evaluation,
and independent semantic evaluation. Do not run Q2, Q3, or Q4. Do not tune or
reload the realization.

## Evidence

- [deadline-pressure result](turbo_t1_q1_deadline_pressure_result_v0.md)
- [deadline-pressure observation](../../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_observation_v0.json)
- [deadline-pressure mechanical evaluation](../../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_mechanical_evaluation_v0.json)
- [deadline-pressure semantic evaluation](../../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_semantic_evaluation_v0.json)
