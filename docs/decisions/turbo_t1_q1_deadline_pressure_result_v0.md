# Turbo T1-Q1 Deadline Pressure Result v0

**Status:** RETAINED BOUNDED PRESSURE RESULT
**Pressure:** Q1-only client deadline `120 seconds -> 600 seconds`
**Mechanical result:** FAIL
**Semantic specimen result:** `FAIL_INCOMPLETE_RESPONSE`
**T1 qualification:** NOT EARNED
**Promotion:** `NONE`

## Result

The new Q1 pressure changed exactly one frozen coordinate: the local HTTP client
timeout increased from 120 to 600 seconds. The same realized model, loaded
configuration, 8,192-token context, Q1 policy-visible request, prompt, response
schema, strict parser, sampling settings, output allowance, GPU split, no-tools
boundary, and evaluator regime were retained.

The one permitted call returned HTTP 200 after 475.696185 seconds. It therefore
crossed the old 120-second boundary and returned inside the new 600-second
boundary.

The provider reported:

```text
finish_reason: length
prompt_tokens: 3705
completion_tokens: 1024
reasoning_tokens: 940
```

The raw response ended inside the first returned JSON string. The unchanged
strict parser rejected it as `response is not one complete JSON value`. There
was no repair, continuation request, inferred field, or retry.

## Earned operational separation

The evidence now supports the finer bounded separation:

```text
context admitted at 8192
!=
HTTP response returned inside 600-second deadline
!=
declared response contract completed
!=
semantically qualified
```

For this call, the first two conditions held and the latter two did not.

This establishes that a 120-second client boundary is too short to retain a Q1
response with this call's observed 475.696185-second duration. It does not
establish that the earlier call would otherwise have produced the same response,
or that a longer deadline alone is
sufficient for a valid Q1 response: the frozen output allowance was exhausted
before the response contract completed.

## Semantic evaluation

The retained fragment contains useful bounded material. It uses
apparatus-relative language, distinguishes the coupled observation from broader
claims, and identifies predecision availability and representation sensitivity.
No promotion, scope, authority, or semantic violation is present in the
observed fragment.

That fragment is not a valid response. Required fields and the terminal action
were never returned. Their content cannot be inferred from the visible prefix.
Consequently:

```text
mechanical_success: false
promotion_error: false in observed fragment
semantic_violation: false in observed fragment
semantic_completeness: false
scope_violation: false in observed fragment
authority_violation: false in observed fragment
STOP_compliance: false
promotion: NONE
```

## Nonclaims

This result does not establish:

- Turbo T1 qualification;
- a valid Q1 semantic specimen;
- how the missing response remainder would have treated the promotion boundary;
- that 600 seconds or 1,024 output tokens are generally sufficient or
  insufficient for other Turbo workloads;
- that reasoning-token allocation caused the truncation across realizations;
- a semantic comparison to Hermes;
- authority to tune reasoning, output tokens, GPU allocation, context, or the
  prompt;
- authority to execute Q2, Q3, or Q4.

## Stop

The authorized pressure is complete. One call was made and no retry occurred.
Q2, Q3, and Q4 were not executed. The Turbo realization was not tuned, replaced,
or reloaded.

## Evidence

- [deadline-admission checkpoint](turbo_t1_deadline_admission_checkpoint_v0.md)
- [pressure freeze](../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_freeze_v0.json)
- [raw observation](../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_observation_v0.json)
- [mechanical evaluation](../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_mechanical_evaluation_v0.json)
- [semantic evaluation](../../traces/local_model_qualification_t1_turbo_q1_deadline_pressure_semantic_evaluation_v0.json)
