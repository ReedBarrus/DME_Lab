# LP-001 Pre-Execution Qualification v0

**Status:** FROZEN BEFORE LP-001 CELL EXECUTION
**Purpose:** mechanically close anti-coaching and RECOVERABLE preconditions
**LP-001 cells authorized by this artifact:** NO

## 1. Exact packet basis

Target packet:

`LP001_L1_TARGET_LINEAGE_PACKET_v0.md`

Git blob:

`43dbc28ae5befe0c803d74f00847b4ff10c80516`

Matched-control packet:

`LP001_LC_MATCHED_CONTROL_PACKET_v0.md`

Git blob:

`187f3352c85cbc1e92f479ab5012e770763275d9`

Observed packet geometry before LP-001 execution:

```text
L1
lines = 33
whitespace_words = 277
utf8_bytes = 2116

LC
lines = 33
whitespace_words = 277
utf8_bytes = 2125
```

The byte-count difference remains below 1%.

Exact model-token counts are not exposed by the selected provider surface and
are therefore not claimed equal. Tokenizer/token-mass differences remain an
admitted carrier nuisance inside the varied condition packet.

## 2. Mechanical anti-coaching rule

This rule is evaluated before any LP-001 cell output exists.

For L1 and LC separately:

1. decode the exact packet bytes as UTF-8;
2. preserve LF line structure;
3. for matching only, map ASCII `A-Z` to `a-z`; all other bytes/characters
   remain unchanged;
4. fail if any prohibited literal substring below occurs;
5. fail if any nonblank, non-Markdown-heading line, after trimming ASCII space
   and tab and applying the same ASCII lowercase mapping, begins with any
   prohibited directive prefix below.

### Prohibited literal substrings

```text
rg-017
accepted_for_handoff
routing/eligibility_rules.md
state_ref
decision_ref
rule_ref
rule_basis
quality_gate
owner_ack
fallback_route
requested_route
sufficiency:
smallest consequential loss:
basis used:
boundary consequence:
action:
new distinction:
missing:
determine whether
identify the smallest consequential loss
preserve missingness
do not assume
do not infer
```

### Prohibited directive-line prefixes

```text
check 
determine 
identify 
preserve 
reject 
refuse 
select 
infer 
recover 
compare 
treat 
use 
do not 
must 
should 
```

This rule intentionally does not ban generic historical vocabulary such as
`historical`, `carrier`, `handoff`, `rule`, or `provenance`. Those terms
occur naturally in source episodes and may not be reclassified as coaching
after outcomes are visible.

### Frozen pre-run scan result

Using the exact packet blobs above:

```text
L1 prohibited literal hits: 0
L1 prohibited directive-line hits: 0

LC prohibited literal hits: 0
LC prohibited directive-line hits: 0

ANTI_COACHING_STATUS: PASS
```

No post-output human judgment about "held-out terminology" may invalidate or
rescue a batch. Any future change to this rule requires a new contract version
before any cell output exists.

## 3. RECOVERABLE qualification surface

RECOVERABLE is qualified before RUN01 and without the held-out specimen.

Each qualification attempt uses:

```text
MODEL LABEL:
GPT-5.6 Sol

REASONING CONFIGURATION:
High

REALIZATION TOPOLOGY:
one fresh text invocation per qualification attempt

CONVERSATION INHERITANCE:
none

ACCOUNT / PERSONAL MEMORY:
must be absent

TOOLS:
none

WEB / REPOSITORY RETRIEVAL:
none

FILES:
only the exact condition packet being qualified

CROSS-ATTEMPT OUTPUT VISIBILITY:
none
```

If this surface cannot guarantee absence of prior conversation/account-memory
injection, qualification is not admissible.

## 4. Exact RECOVERABLE prompt

For each attempt, serialize exactly:

```text
You are a packet-only reconstruction checker.

Use only the CONDITION_PACKET below.
Do not use outside knowledge.
Do not infer a held-out task.
Use the packet's exact source terms where the response schema asks for them.

CONDITION_PACKET:

<EXACT CONDITION_PACKET BYTES>

Return exactly six single-line fields and no other text:

INITIAL_POSTURE:
FRACTURE:
ADJUDICATION_BASIS:
MINIMAL_REPAIR:
VERIFICATION_OUTCOME:
PRESERVED_NONCLAIM:
```

The placeholder is replaced by the exact packet bytes. UTF-8, LF newlines, and
one blank line around the inserted packet are fixed.

## 5. Exact qualification attempt order

Exactly four attempts are permitted:

```text
Q01 L1
Q02 LC
Q03 LC
Q04 L1
```

There are exactly two attempts per packet.

No failed, inconvenient, malformed, or unavailable qualification attempt may be
selectively replaced inside this qualification version.

If any attempt cannot be completed on the frozen invocation surface, LP-001 is
`NOT_READY` under this qualification version. A later qualification requires a
new versioned qualification record; it does not replace or erase this attempt
set.

## 6. Deterministic RECOVERABLE scoring

A qualification response passes only if:

1. it contains exactly the six required single-line fields, each exactly once;
2. there is no extra nonblank line;
3. after ASCII lowercasing each field value, every required anchor for that
   field is present as a literal substring.

No synonym substitution is accepted for this pre-run readiness check.

### L1 required anchors

```text
INITIAL_POSTURE
  mm-002
  checkpoint
  four council round artifacts

FRACTURE
  agent_context.md
  continuity/sync_ritual.md
  same path

ADJUDICATION_BASIS
  immutable history
  exact blobs
  later same-path agent_context.md

MINIMAL_REPAIR
  additional envelope
  pre-handoff continuity basis
  exact operational file identities

VERIFICATION_OUTCOME
  targeted observers
  fresh cold-open auditors
  no further consequential loss

PRESERVED_NONCLAIM
  automatic dependency discovery
  generalized dependency graph
  current authority
```

### LC required anchors

```text
INITIAL_POSTURE
  trial order
  device roles
  waveform
  measurement rule
  discrimination rule

FRACTURE
  first completed capture block
  overlapped unrelated video audio
  human provenance
  machine-verified diagnosis

ADJUDICATION_BASIS
  retained
  excluded
  did not prove

MINIMAL_REPAIR
  replacement block
  already frozen
  no gain increase
  adaptive rule change

VERIFICATION_OUTCOME
  fifteen captures
  locally discriminable
  not locally discriminable

PRESERVED_NONCLAIM
  airborne acoustic causality
  generalized statistical validity
  authority over unrelated specimens
```

Both L1 attempts and both LC attempts must pass all six fields.

The qualification scorer performs only these literal checks. It may not add a
new semantic criterion after seeing a response.

## 7. Frozen qualification record requirement

Before RUN01, the four raw qualification outputs, their SHA-256 identities, and
the mechanical pass/fail vector for every field must be frozen in one retained
qualification record.

Required final state:

```text
Q01 L1 PASS
Q02 LC PASS
Q03 LC PASS
Q04 L1 PASS

RECOVERABLE_STATUS: PASS
```

Anything else leaves LP-001 `NOT_READY`.

Qualification outputs and the qualification record are not supplied to LP-001
cells or to the LP-001 scorer.

## 8. Claim ceiling

Passing this qualification establishes only that the exact L1 and LC packets
produced the declared six-element packet reconstruction under this frozen
pre-run checker.

It does not establish behavioral materiality, beneficial effect, historical
truth beyond the packet, or a unique causal mechanism for lineage.
