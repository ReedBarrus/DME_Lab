# Local Model Load Failure — QwQ 32B 001

OBJECT_TYPE:
LOCAL_MODEL_LOAD_FAILURE_WITNESS

MODEL:
qwen/qwq-32b

REQUEST:
ROUND018_BENCH_QWQ32

STATUS:
APPARATUS_LOAD_FAILURE

OBSERVED_ERROR:
LM Studio HTTP 400 while attempting to load the model.

LM Studio reported that model loading was stopped because current settings
required approximately 20.95 GB of memory and continuing could overload the
system.

# NON-COLLAPSES

MODEL_LOAD_FAILURE
!=
MODEL_REASONING_FAILURE

RESOURCE_INELIGIBLE_UNDER_CURRENT_PROFILE
!=
MODEL_UNUSABLE_UNDER_ALL_PROFILES

BRIDGE_REQUEST_FAILURE
!=
SCIENTIFIC_BENCHMARK_RESULT

# CURRENT DISPOSITION

The QwQ benchmark is paused.

Do not weaken LM Studio safety guardrails merely to force the model to load.

First retry only under a lower-cost local profile, such as:
- unload unnecessary resident models;
- context length 4096 rather than 8192;
- parallel predictions 1 rather than 4;
- maximize safe GPU offload / Flash Attention if supported.

If the model still fails the load guard, retain it as unavailable under the
current hardware profile rather than forcing execution.

# CLAIM CEILING

No model-fit conclusion for QwQ 32B is established from this event.
