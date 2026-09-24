# Local Model Fitness Round 002

OBJECT_TYPE:
LOCAL_MODEL_FITNESS_RESULT

OBJECT_ID:
LOCAL_MODEL_FITNESS_ROUND_002

STATUS:
FROZEN_COMPARISON

# QWQ 32B

MODEL:
qwen/qwq-32b

RESULT:
NOT_BENCHMARKED

APPARATUS_OUTCOME:
LOAD_GUARD_REJECTED

OBSERVED_MEMORY_REQUIREMENT:
~20.95 GB under the attempted profile

CURRENT_FIT:
RESOURCE_INELIGIBLE_UNDER_ATTEMPTED_PROFILE

CLAIM_CEILING:
No reasoning-quality conclusion is warranted.

# QWEN 27B TURBO VARIANT

MODEL:
qwen3.8-27b-turbo-fable-cold-fusion-735-882-heretic-uncensored-neo-coder-max-mtp

WALL_SECONDS:
571.075675

COMPLETION_TOKENS:
1024

END_TO_END_OUTPUT_TOKENS_PER_SECOND:
1.793107

FINISH_REASON:
length

ASSISTANT_TEXT:
EMPTY

REASONING_CONTENT:
PRESENT

OBSERVED:
- model spent the full output budget in reasoning_content
- no final assistant answer was emitted
- reasoning substantially recognized the benchmark distinctions
- model noticed that its first candidate next pressure duplicated an already-qualified capability
- benchmark contract was not completed
- throughput was operationally poor for routine seat work under the attempted profile

CURRENT_FIT:
NOT_SUITABLE_FOR_ROUTINE_SINGLE_SEAT_WORK_UNDER_ATTEMPTED_PROFILE

# QWEN3-CODER 30B REFERENCE

MODEL:
qwen/qwen3-coder-30b

OBSERVED_REFERENCE:
~9.73 seconds from witnessed timestamps for 149 completion tokens

APPROX_OUTPUT_TOKENS_PER_SECOND:
~15.31

CURRENT_FIT:
BEST_OBSERVED_GENERAL_BOUNDED_WORKER_ACROSS_ROUNDS_001_002

# DEVELOPMENT CONSEQUENCE

Raw parameter count does not predict local operational fitness.

A model may be:
- cognitively promising but memory-ineligible;
- structurally competent but too slow;
- fast but contract-weak;
- or balanced enough to carry a particular bounded seat role.

Therefore:

MODEL_CAPABILITY
!=
MODEL_OPERATIONAL_FIT

and:

MODEL_OPERATIONAL_FIT
=
TASK_FIT
+
RESOURCE_FIT
+
CONTRACT_FIDELITY
+
FAILURE_LEGIBILITY
+
HUMAN_REVIEW_COST

# CLAIM CEILING

This is a workload- and hardware-profile-specific comparison only.
It does not establish general model superiority or permanent seat assignment.
