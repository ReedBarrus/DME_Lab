# Local Model Benchmark Protocol V0

OBJECT_TYPE:
LOCAL_MODEL_BENCHMARK_PROTOCOL

OBJECT_ID:
LOCAL_MODEL_BENCHMARK_PROTOCOL_V0

STANDING:
CANDIDATE_ONLY

# PURPOSE

Measure model fitness for bounded DME seat work without conflating model size,
seat identity, authority, or one-off subjective impressions.

# BENCHMARK CLASSES

1. EXACT_FORMAT
   - small required-output contract
   - tests literal field compliance

2. EVIDENCE_RECONSTRUCTION
   - one self-contained evidence bundle
   - tests complete bounded recovery without repo access

3. CONTRADICTION_DETECTION
   - intentionally inconsistent evaluator result
   - tests whether contradiction is surfaced rather than normalized away

4. NEXT_PRESSURE_SELECTION
   - one planner state + finite candidate operation list
   - tests concrete pressure selection rather than horizon restatement

5. FAILURE_LEGIBILITY
   - one deliberately missing load-bearing field
   - expected result is explicit UNRESOLVED / rejection, not invented repair

# FIXED EXECUTION ENVELOPE

For comparable runs:

temperature:
0.0

tools:
NONE

history:
NONE

repo_access:
NONE

network_access:
NONE

publication:
NONE

human_authorization:
REQUIRED

# MEASUREMENTS

For each invocation capture:

MODEL_ID
MODEL_PROFILE_ID
PROMPT_SHA256
REQUEST_BODY_SHA256
RESPONSE_BODY_SHA256
PROMPT_TOKENS
COMPLETION_TOKENS
WALL_SECONDS
OUTPUT_TOKENS_PER_SECOND
FORMAT_FIDELITY
CONTRACT_FIDELITY
EVIDENCE_COMPLETENESS
UNSUPPORTED_INFERENCE
FAILURE_LEGIBILITY
CLAIM_CEILING_DISCIPLINE

# ASSIGNMENT RULE

Do not select a model by raw speed alone.

Candidate assignment should minimize the cost of a scientifically usable result:

usable_result_cost
=
latency
+
contract_failure_cost
+
hallucination_repair_cost
+
human_review_cost

# INITIAL COMPARISON SET

BASELINE:
qwen/qwen3-coder-30b

CANDIDATE_FAST:
meta-llama-3.1-8b-instruct
Hermes 3B exact ID pending

CANDIDATE_DEEP:
qwen/qwq-32b

CANDIDATE_DIVERSITY:
microsoft/phi-4

# CLAIM CEILING

This protocol can qualify model-task fit in tested workloads only.

It does not establish general model superiority, autonomous model selection,
or authority to retune/load/unload models without the declared local control
surface.
