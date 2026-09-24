# Local Model Surface V0

OBJECT_TYPE:
LOCAL_MODEL_CAPABILITY_MAP

OBJECT_ID:
LOCAL_MODEL_SURFACE_V0

STANDING:
CURRENT_LOCAL_INVENTORY_PROJECTION

This map records locally available LM Studio models as operational candidates.
It is descriptive only. It does not authorize model use outside the bridge
policy and does not grant any model repository, filesystem, tool, network,
publication, or execution authority.

# CURRENTLY OBSERVED INSTALLED MODELS

## qwen/qwen3-coder-30b

Observed class:
30B-A3B, Q4_K_M, ~18.6 GB

Current bridge standing:
ALLOWED / USED

Observed practical role:
- planner-seat candidate occupant
- structured reconstruction
- contract-sensitive development work

Current note:
Best observed local balance so far between response quality and throughput.

## microsoft/phi-4

Observed class:
15B, Q4_K_M, ~9.1 GB

Current bridge standing:
ALLOWED / USED

Observed practical role:
- evaluator / adjudicator candidate

Current note:
Substantially slower in current configuration and has produced both useful
adjudication and contract-following failures. Retain as a diversity/check model,
not the default worker, pending tuning evidence.

## qwen/qwq-32b

Observed class:
32B, Q4_K_M, ~19.9 GB

Exact local identifier:
VISIBLE_FROM_UI_AS qwen/qwq-32b

Bridge standing:
NOT_YET_ALLOWLISTED

Candidate role:
- high-depth evaluator / adversarial reasoning
- expensive cross-check seat

## qwen2.5-vl-7b

Observed class:
7B, Q4_K_M, ~6.0 GB

Exact local identifier:
VISIBLE_FROM_UI_AS qwen/qwen2.5-vl-7b

Bridge standing:
NOT_YET_ALLOWLISTED

Candidate role:
- visual / multimodal evidence work
- not preferred for ordinary text-only seat work unless benchmark earns it

## hermes-3-llama-3.2-3b

Observed class:
3B, Q4_K_M, ~2.0 GB

Exact local identifier:
NEEDS_CONFIRMATION_FROM_LMS_LS

Bridge standing:
NOT_YET_ALLOWLISTED

Candidate role:
- cheap mechanical extractor
- schema / formatting worker
- very fast bounded witness checks

## meta-llama-3.1-8b-instruct

Observed class:
8B, Q4_K_M, ~4.9 GB

Exact local identifier:
VISIBLE_FROM_UI_AS meta-llama-3.1-8b-instruct

Bridge standing:
NOT_YET_ALLOWLISTED

Candidate role:
- fast general bounded worker
- extractor / validator / low-cost reconstruction

## DavidAU Qwen 27B Turbo variant

Observed class:
27B, Q4_K_M, ~19.9 GB

Exact local identifier:
NEEDS_CONFIRMATION_FROM_LMS_LS

Bridge standing:
NOT_YET_ALLOWLISTED

Candidate role:
- alternative medium/heavy worker
- benchmark against qwen3-coder-30b before assigning a seat role

# MODEL ASSIGNMENT LAW

SEAT CONTRACT
!=
MODEL

MODEL IDENTITY
!=
SEAT IDENTITY

MODEL PERFORMANCE
!=
MODEL AUTHORITY

A seat may later select from qualified model profiles without changing its
seat-level authority envelope.

# CANDIDATE MODEL-FIT DIMENSIONS

For each bounded workload family, track:

- contract fidelity
- exact-format fidelity
- hallucination / unsupported repair rate
- evidence-use completeness
- boundedness / claim-ceiling discipline
- latency
- prompt tokens
- completion tokens
- output tokens / second
- memory footprint
- GPU offload / context configuration
- failure legibility

# INITIAL ROLE HYPOTHESES

FAST_MECHANICAL_WORKER:
- Hermes 3B candidate
- Llama 8B candidate

GENERAL_BOUNDED_WORKER:
- Qwen3-Coder 30B baseline

DEEP_EVALUATOR:
- QwQ 32B candidate

DIVERSITY_CHECK:
- Phi-4 candidate after tuning

VISION_WORKER:
- Qwen2.5-VL 7B candidate

These are hypotheses only. Benchmark evidence must earn assignment.

# SECURITY POSTURE

Adding a model to inventory does not authorize invocation.

Model use remains gated by:
- bridge allowlist
- immutable request identity
- local human approval
- no model repo access
- no tools
- no network
- no automatic publication

No wildcard model allowlist should be used merely for convenience.

# NEXT ACTION

Obtain exact identifiers from:

lms ls

Then add only exact intended models to bridge policy and run a same-prompt
benchmark matrix before assigning stable seat roles.
