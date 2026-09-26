# Local Model QwQ 32B Short Probe 001

OBJECT_TYPE:
LOCAL_MODEL_RUNTIME_OBSERVATION

MODEL:
qwen/qwq-32b

REQUEST:
ROUND019_REPLAY_RECEIPT_PROBE

STATUS:
MODEL_REACHED_BUT_OUTPUT_INCOMPLETE

WALL_SECONDS:
48.673794

PROMPT_TOKENS:
87

COMPLETION_TOKENS:
64

END_TO_END_OUTPUT_TOKENS_PER_SECOND:
1.314876

FINISH_REASON:
length

ASSISTANT_TEXT:
EMPTY

REASONING_CONTENT:
PRESENT

# OBSERVATION

Under the profile used for this invocation, QwQ loaded successfully after prior
resource-guard failures and consumed the entire 64-token output budget in
reasoning_content without emitting the requested final answer.

# NON-COLLAPSES

MODEL_LOADED
!=
TASK_COMPLETED

REASONING_CONTENT_PRESENT
!=
CONTRACT OUTPUT PRODUCED

RESOURCE_LOAD_SUCCESS
!=
OPERATIONAL_FIT

# CURRENT FIT

QwQ remains unqualified for routine bounded bridge work under this profile.

Its observed ~1.31 end-to-end completion tokens/second plus reasoning-only
budget consumption make it a poor default for short structured actions.

# CLAIM CEILING

This observation is specific to this prompt, output budget, runtime profile, and
hardware state. It does not establish general QwQ capability or incapability.
