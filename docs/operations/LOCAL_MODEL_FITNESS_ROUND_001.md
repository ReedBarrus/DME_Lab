# Local Model Fitness Round 001

OBJECT_TYPE:
LOCAL_MODEL_FITNESS_RESULT

OBJECT_ID:
LOCAL_MODEL_FITNESS_ROUND_001

STATUS:
FROZEN_COMPARISON

PROMPT:
bridge/prompts/LOCAL_MODEL_FITNESS_BENCHMARK_001.md

# HERMES 3B

MODEL:
hermes-3-llama-3.2-3b

WALL_SECONDS:
15.206713

OUTPUT_TOKENS_PER_SECOND:
11.508076

OBSERVED:
- explicit unresolved handling preserved
- authority boundary preserved
- candidate-pending separation collapsed
- next-pressure field remained generic rather than concrete/testable
- claim ceiling overclaimed successful bounded pressure construction
- output included extra prose outside the exact requested form

CURRENT FIT:
FASTISH_MECHANICAL_CANDIDATE_WITH_CONTRACT_WOUNDS

# LLAMA 8B

MODEL:
meta-llama-3.1-8b-instruct

WALL_SECONDS:
11.323719

OUTPUT_TOKENS_PER_SECOND:
3.002547

OBSERVED:
- did not follow required field schema
- collapsed response into an unrelated JSON tool-like object
- recognized RESULT_SETTLEMENT_RULE as unresolved
- did not provide the required bounded planning object

CURRENT FIT:
NOT_QUALIFIED_FOR_THIS_STRUCTURED_SEAT_TASK

# QWEN3-CODER 30B

MODEL:
qwen/qwen3-coder-30b

OBSERVED_WALL_SECONDS_FROM_TIMESTAMPS:
~9.73

OBSERVED_COMPLETION_TOKENS:
149

APPROX_OUTPUT_TOKENS_PER_SECOND:
~15.31

OBSERVED:
- exact required field family substantially preserved
- missing RESULT_SETTLEMENT_RULE surfaced explicitly
- candidate-pending separation preserved
- authority boundary preserved
- produced a concrete-seeming next pressure rather than horizon restatement
- next pressure was only weakly grounded in the supplied single-seat operation list
- claim ceiling overreached by saying the pressure can be executed, although the benchmark established proposal only
- unresolved list was mildly inconsistent by questioning candidate separation after marking it preserved

CURRENT FIT:
BEST_OBSERVED_GENERAL_BOUNDED_WORKER_IN_ROUND_001_WITH_CLAIM_CEILING_WOUND

# ROUND 001 BOUNDED COMPARISON

No model is qualified generally.

For this prompt only:

Qwen3-Coder 30B produced the strongest bounded planning response.

Hermes 3B preserved several safety distinctions but failed candidate-state
separation and next-pressure specificity.

Llama 8B failed the required output contract.

# NEXT TEST

Benchmark the heavier alternative local models against the same immutable
prompt before assigning stable seat roles:

- qwen/qwq-32b
- qwen3.8-27b-turbo-fable-cold-fusion-735-882-heretic-uncensored-neo-coder-max-mtp

Then run a second planner-specific benchmark that restricts next-pressure
selection to an explicit finite operation set and tests claim-ceiling discipline.

# CLAIM CEILING

This comparison supports workload-specific model-fit hypotheses only.

It does not establish general model ranking, stable seat assignment, or
automatic model routing.
