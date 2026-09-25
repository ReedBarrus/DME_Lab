# Planner Coordination Workflow V0

OBJECT_TYPE:
GENERAL_COORDINATION_GUIDE

OBJECT_ID:
PLANNER_COORDINATION_WORKFLOW_V0

STANDING:
OPERATIVE_COORDINATION_GUIDE

# PURPOSE

Describe the bounded coordination workflow used by the planner/coordinator to
turn current Atlas state into one concrete pressure, package the right evidence,
route that pressure to either a fresh chat thread or the local LM Studio bridge,
freeze the returned result, and advance only through explicit settlement /
adjudication.

This guide is a coordination surface, not an authority grant.

# CORE LOOP

ATLAS / CURRENT OPERATIVE FRAME
→ identify newest unresolved load-bearing seam
→ select one bounded pressure
→ choose destination
→ build exact packet
→ bind exact evidence
→ invoke one fresh occupant
→ witness result
→ freeze source output
→ independent settlement / adjudication
→ update qualified state only if earned
→ choose next pressure

# PLANNER ROLE

The planner does not execute, qualify, or authorize by itself.

It may:

- reconstruct current target, horizon, trajectory, qualified standing, candidate
  state, unresolved load, and provenance handles;
- identify the smallest next pressure;
- choose a destination appropriate to that pressure;
- assemble deterministic evidence;
- define the expected output contract;
- preserve claim ceilings;
- freeze returned results;
- route those results to separate review.

It must not:

- self-adjudicate its own result;
- silently promote candidate output;
- infer missing evidence;
- treat a model invocation as authority;
- treat a witness as settlement;
- treat settlement as qualification;
- treat qualification as automatic Atlas mutation.

# DESTINATION SELECTION

## Fresh Chat / Independent Thread

Use when the task benefits from an independent model context or when a human can
carry a self-contained packet directly.

Typical uses:

- adjudication;
- reflection / horizon review;
- lifecycle completeness review;
- adversarial evaluation;
- cross-model semantic comparison.

Packet rule:

ONE PACKET
+ ONE DESTINATION
+ ONE ROLE
+ ONE REQUIRED RETURN OBJECT

The packet should be self-contained whenever possible.

## Local LM Studio Bridge

Use when the task is bounded, repeatable, and should be exercised through the
local seat apparatus.

Typical uses:

- planner-seat pressure runs;
- exact-format tests;
- bounded evaluator cells;
- model-fit tests;
- lifecycle mechanics;
- replay / retry / authority / settlement cells.

Bridge use preserves:

REMOTE REQUEST
!=
LOCAL AUTHORIZATION

The local operator still approves the invocation.

# PACKET CONSTRUCTION

A good pressure packet contains:

OBJECT_TYPE
ROLE
MODE
TARGET
CURRENT QUALIFIED STATE
CURRENT CANDIDATE STATE
UNRESOLVED LOAD
CANDIDATE LAW / PRESSURE LAW
SPECIMEN OR INPUT SET
PROHIBITIONS
REQUIRED OUTPUT
CLAIM CEILING
STOP

Packets should expose only the evidence needed for the pressure.

# EVIDENCE APERTURE

PACKET REFERENCES EVIDENCE
!=
MODEL RECEIVES EVIDENCE

Therefore evidence must either:

A. be embedded directly into a self-contained packet; or
B. be assembled deterministically through the evidence-bundle system.

The model does not receive repository browsing merely because the coordinator
has repository access.

# EVIDENCE BUNDLE SYSTEM

The deterministic bundle assembler exists to transport exact evidence without
granting repository access.

Flow:

manifest
→ immutable Git coordinates
→ exact blob resolution
→ declared identity verification
→ deterministic ordered assembly
→ bundle SHA-256
→ local witness
→ optional use as one model-visible prompt

V0 evidence items are full-text only.

Each item declares:

- label
- source_ref
- path
- sha256
- mode = full_text

The assembler preserves manifest order and adds no hidden context.

Command:

python tools/bridge_evidence_bundle_v0.py bridge/evidence_manifests/<manifest>.json

Generated local bundles live under:

bridge/bundles/

# MANIFEST ROLE

The manifest is not scientific interpretation.

It is a deterministic declaration of the evidence aperture.

EVIDENCE SELECTION
!=
SCIENTIFIC STANDING

BUNDLE ASSEMBLY
!=
SEMANTIC RETRIEVAL

MODEL HAS EVIDENCE
!=
MODEL HAS REPOSITORY ACCESS

A manifest should bind only evidence already selected by the coordinator or
another explicitly authorized selection surface.

# REQUEST MANIFEST ROLE

A bridge request binds one invocation proposal to:

- request_id
- immutable source_ref
- input_path or stable Git input identity
- model
- temperature
- max_tokens
- purpose
- current policy constraints

The trusted local bridge resolves the exact prompt object, presents the approval
surface, invokes LM Studio with one user message and no tools, and writes a
result witness.

# WITNESSING

A returned model answer is not immediately interpreted as truth.

First freeze it.

For local bridge results, the witness records:

- request identity;
- source identity;
- model identity;
- prompt / request / response identity;
- timestamps;
- token counts and runtime when available;
- exact raw response;
- extracted assistant text;
- explicit no-tools / no-repo / no-network posture.

The original output remains immutable for later review.

# RESULT HANDLING

MODEL RESPONSE
!=
RESULT WITNESS
!=
CANDIDATE SETTLEMENT
!=
QUALIFIED STANDING
!=
AUTHORITY
!=
ATLAS MUTATION

The coordinator should:

1. freeze the source result;
2. identify obvious apparatus failures separately from model failures;
3. send the frozen result to an independent evaluator when standing matters;
4. preserve field-level distinctions such as accepted / held / rejected /
   unresolved;
5. update the current operative frame only after the relevant qualification is
   earned.

# SCIENTIFIC / PLANNING CADENCE

Preferred cadence:

OBSERVE
→ EVALUATE
→ PROJECT
→ REVIEW
→ AUDIT
→ REDUCE / COMPRESS
→ RUN
→ FREEZE
→ ADJUDICATE
→ REPAIR
→ QUALIFY
→ SELECT NEXT PRESSURE

The planner usually operates at the first, middle, and final portions:

CURRENT FRAME
→ NEXT PRESSURE
→ PACKET / EVIDENCE APERTURE
...
QUALIFIED RESULT
→ UPDATED FRAME
→ NEXT PRESSURE

# FRESHNESS / INDEPENDENCE

Use fresh threads or distinct local model occupants when the pressure depends on
independence.

Do not rely on predecessor hidden reasoning.

A fresh evaluator receives only the frozen evidence required by the contract.

Same-model or same-thread review should not be treated as independent unless a
separate warrant exists.

# FAILURE HANDLING

Classify failures before reacting.

Examples:

INPUT IDENTITY FAILURE
→ apparatus rejection
→ model not invoked

MODEL LOAD FAILURE
→ apparatus / resource failure
→ no reasoning-quality conclusion

TRANSPORT FAILURE AFTER INVOCATION START
→ invocation outcome may be unresolved
→ no silent replay

FORMAT FAILURE
→ model contract-fidelity wound

OVERCLAIM
→ hold or reject affected fields
→ do not rewrite the source output

MISSING EVIDENCE
→ explicit unresolved
→ do not infer

# ARTIFACT / MEMORY MANAGEMENT

Before creating a new artifact:

1. identify its topological family;
2. write it directly to the canonical folder;
3. when a family reaches roughly 15-20 siblings, review for subdivision by
   relation / lineage before chronology;
4. maintain small README indexes for dense families;
5. preserve historical immutable references;
6. update only live/current references after moves.

General workflow surface:

docs/operations/ARTIFACT_TOPOLOGY_BATCHING_WORKFLOW_V0.md

Machine-readable rules:

config/artifact_topology_rules_v0.json

# COORDINATOR CHECKLIST

Before sending a pressure:

[ ] What exact unresolved relation is being tested?
[ ] What is already qualified?
[ ] What is only candidate?
[ ] What must remain held fixed?
[ ] What model / destination is appropriate?
[ ] Is the packet self-contained?
[ ] If not, what exact evidence bundle is required?
[ ] Are all evidence identities immutable?
[ ] Is the output schema explicit?
[ ] Is the claim ceiling explicit?
[ ] Is authority effect NONE unless separately granted?
[ ] Is execution effect NONE unless separately granted?
[ ] What result will count as success, failure, or unresolved?
[ ] Who/what independently adjudicates the result?

After return:

[ ] Freeze source output.
[ ] Distinguish model failure from apparatus failure.
[ ] Preserve source bytes / witness identity.
[ ] Do not self-promote.
[ ] Route to settlement / adjudication if standing matters.
[ ] Update current frame only with earned changes.
[ ] Select one next bounded pressure.

# SIMPLE COORDINATOR TEMPLATE

CURRENT TARGET:
<target>

CURRENT QUALIFIED STATE:
<qualified only>

CURRENT CANDIDATES:
<candidate only>

UNRESOLVED LOAD:
<exact seams>

NEWEST LOAD-BEARING WOUND:
<one seam>

NEXT PRESSURE:
<one bounded test>

DESTINATION:
<FRESH CHAT | LOCAL BRIDGE>

EVIDENCE APERTURE:
<self-contained packet | evidence manifest path>

MODEL / ROLE:
<occupant / role>

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE

EXPECTED RETURN:
<exact output object>

CLAIM CEILING:
<maximum warranted result>

NEXT STEP IF CLEAN:
<next seam>

NEXT STEP IF WOUNDED:
<repair pressure>

# CLAIM CEILING

This guide describes the current coordination method.

It does not establish autonomous planning, autonomous evidence selection,
automatic scientific qualification, or automatic Atlas mutation.
