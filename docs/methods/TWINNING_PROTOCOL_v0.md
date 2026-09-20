# TWINNING_PROTOCOL_v0

**Status:** PROVISIONAL DEVELOPMENT METHOD  
**Authority:** workflow control only; does not establish runtime agent architecture  
**Purpose:** preserve a recoverable boundary between semantic interpretation,
human authorization, bounded execution, and returned evidence during persistent
development.

## 1. Scope

Twinning Protocol v0 is a small reciprocal handoff contract for DME_Lab
development.

It exists because persistent execution can advance faster than interpretation.

```text
execution capacity
!=
interpretive capacity

development throughput
!=
epistemic throughput

artifact accumulation
!=
earned state advancement
```

The protocol does not establish autonomous science, model governance, agent
identity, consensus truth, a scheduler, or a generalized orchestration runtime.

Its first job is narrower:

> make the transition from interpreted standing to authorized execution, and
> from execution back to evidence, explicit enough that neither side can
> silently strengthen the other's claims.

## 2. Roles

The current roles are operational chairs, not permanent identities.

### Council

The Council consists of independent interpretation surfaces.

Current instantiation:

- **SolA** — maximal justified compression: strongest coherent reconstruction
  supported by the evidence.
- **SolB / LabBoiB** — minimal unjustified promotion: adversarial reconstruction,
  surviving uncertainty, false distinctions, and unsupported strengthening.

Council may interpret, compare, challenge, and propose reachable pressures.

Council does **not** authorize execution merely by agreement.

### Executive

Current Executive: **Reed**.

The Executive:

- selects or authorizes active development pressure;
- resolves whether a proposed packet may cross into execution;
- may preserve disagreement rather than choose between unsupported claims;
- may stop, dwell, narrow, continue, or redirect authorized work.

The Executive does not rewrite repository/runtime evidence by declaration.

### Workshop

The Workshop is any implementation capable of consuming an authorized execution
packet and returning evidence.

Current possible occupants include Astra, Codex, scripts, human operators, local
models, or bounded combinations of them.

Workshop may execute inside the authorized envelope.

Workshop does **not** promote semantic standing or silently open a new pressure.

### Evidence substrate

Repository state, runtime behavior, tests, traces, and retained artifacts remain
the evidence surface.

Participant narratives are claims about that evidence, not substitutes for it.

## 3. Authority topology

```text
COUNCIL
interpretation / candidate pressures
        |
        v
EXECUTIVE
authorization / selection
        |
        v
EXECUTION_PACKET_v0
        |
        v
WORKSHOP
bounded operations
        |
        v
EVIDENCE_RETURN_v0
        |
        v
COUNCIL
independent metabolization
        |
        v
EXECUTIVE
adjudication / next authorization
```

Standing laws:

```text
Workshop may execute but cannot promote meaning.

Council may interpret but cannot silently authorize execution.

Executive may authorize but does not overwrite evidence.

execution authorization
!=
semantic promotion authorization

semantic interpretation
!=
execution authorization

successful execution
!=
adjudicated consequence
```

## 4. EXECUTION_PACKET_v0

An execution packet is the bounded Council-to-Workshop handoff that becomes live
only after Executive authorization.

It should contain no more structure than required to keep the execution boundary
recoverable.

### Required fields

```text
PACKET_ID
BASIS
CURRENT_PRESSURE
ADMITTED_EVIDENCE
UNRESOLVED
AUTHORIZED_OPERATIONS
UNAUTHORIZED_EXTRAPOLATIONS
REQUIRED_EVIDENCE_RETURN
STOP_OR_ESCALATE_IF
EXECUTION_QUESTIONS
AUTHORIZATION
```

### Field meaning

**PACKET_ID**  
Stable identifier for this handoff.

**BASIS**  
Repository/commit/runtime coordinates and prior standing the packet assumes.
If the basis changes materially, the Workshop must expose that fact.

**CURRENT_PRESSURE**  
The one bounded question or development objective that authorizes the run.

**ADMITTED_EVIDENCE**  
Evidence or standing already accepted for this packet. This is not a license to
generalize beyond its declared scope.

**UNRESOLVED**  
Known uncertainty that must remain unresolved unless execution actually
produces discriminating evidence.

**AUTHORIZED_OPERATIONS**  
Operations, files, tests, fixtures, instrumentation, or bounded refactors the
Workshop may perform without renewed Executive authorization.

**UNAUTHORIZED_EXTRAPOLATIONS**  
Semantic or operational boundary crossings the Workshop must not perform.
Examples may include activating a new pressure, inventing policy to resolve
ambiguity, adding generalized architecture, mutating excluded state, or treating
a passing test as semantic promotion.

**REQUIRED_EVIDENCE_RETURN**  
Artifacts and observations owed back to Council.

**STOP_OR_ESCALATE_IF**  
Conditions that terminate delegated freedom. A stop condition is not failure; it
protects the authority boundary.

**EXECUTION_QUESTIONS**  
Questions execution itself may legitimately answer. These distinguish desired
observations from assumptions the Workshop should fill.

**AUTHORIZATION**  
Explicit Executive authorization state. A represented packet is not executable
authority until authorized.

```text
represented packet
!=
authorized packet
```

## 5. EVIDENCE_RETURN_v0

Workshop returns evidence, not a completion badge.

### Required fields

```text
PACKET_ID
BASIS_OBSERVED
OPERATIONS_EXECUTED
CHANGES
TESTS_AND_RUNTIME_RESULTS
DIRECT_EVIDENCE
UNEXPECTED_OBSERVATIONS
ASSUMPTIONS_MADE
DELEGATED_DECISIONS
REFUSED_OR_ESCALATED_DECISIONS
SURVIVING_UNKNOWNS
WORKSHOP_CLAIMS
CANDIDATE_NEXT_PRESSURES
PROTOCOL_FRICTION
```

### Return rules

**BASIS_OBSERVED**  
Report the actual basis encountered. Do not silently claim the packet's starting
basis if the world changed.

**OPERATIONS_EXECUTED**  
What actually ran, not merely what was requested.

**CHANGES**  
Files, commits, fixtures, configuration, or other material changes.

**TESTS_AND_RUNTIME_RESULTS**  
Exact tests/commands/results where practical, including failures.

**DIRECT_EVIDENCE**  
Traces, diffs, outputs, specimens, or other retained evidence supporting claims.

**UNEXPECTED_OBSERVATIONS**  
Anything materially outside the anticipated execution story.

**ASSUMPTIONS_MADE**  
Assumptions required to continue. If an assumption should have required
Executive judgment, report the boundary breach or escalation rather than hiding
it.

**DELEGATED_DECISIONS**  
Choices made within explicitly delegated authority.

**REFUSED_OR_ESCALATED_DECISIONS**  
Choices not taken because they crossed authority, semantic, safety, or basis
boundaries.

**SURVIVING_UNKNOWNS**  
What execution did not establish.

**WORKSHOP_CLAIMS**  
Workshop interpretation of the evidence. These remain claims until Council
metabolization and Executive adjudication.

**CANDIDATE_NEXT_PRESSURES**  
Questions exposed by the run. They are not automatically active.

**PROTOCOL_FRICTION**  
Evidence about the packet itself: ambiguity, missing information, expensive or
impossible evidence demands, ignored fields, or recurring escalation points.

## 6. Council metabolization

SolA and SolB should receive the same Evidence Return and underlying artifacts
when practical.

They independently transform:

```text
raw execution evidence
->
surviving claims
+
fractures
+
candidate distinctions
+
false distinctions
+
surviving uncertainty
+
reachable pressures
```

### SolA bias

```text
What is the maximal justified compression of this evidence?
What prior standing survives?
What composes?
What is the strongest consequence actually established?
```

### SolB bias

```text
What is the minimal boundary against unjustified promotion?
What fractured?
What remains unresolved?
What architecture or meaning outran its warrant?
What would falsify the leading interpretation?
```

The biases do not constrain either twin from reporting the other's kind of
finding.

## 7. Twin disagreement

Twin disagreement must remain visible until its cause is understood or the next
decision does not require resolution.

Useful classifications:

```text
TWIN_AGREEMENT
same bounded reconstruction with similar limits

TWIN_COMPLEMENT
different observations that compose without conflict

TWIN_TENSION
different interpretations of the same evidence

TWIN_CONTRADICTION
claims cannot simultaneously hold under the same basis

TWIN_BASIS_SPLIT
apparent disagreement caused by different observational bases
```

None of these categories establishes truth by itself.

If disagreement affects the next consequential authorization and retained
evidence cannot discriminate it, standing remains unresolved.

## 8. Workshop counsel

The Workshop should also report evidence about how well the protocol itself
works.

Useful questions include:

- Were authority boundaries machine-interpretable?
- What information had to be guessed?
- Which requested evidence was expensive or impossible to produce?
- Which stop conditions were ambiguous?
- What decisions repeatedly required escalation?
- Which packet fields did not affect execution?
- What additional observation would have materially improved the run?
- Did any packet language appear to authorize more than the Executive intended?

This creates a second loop:

```text
development loop:
Council -> Executive -> Workshop -> evidence -> Council

protocol-learning loop:
packet design -> Workshop friction -> Council/Executive review -> protocol amendment
```

Protocol feedback does not automatically amend the protocol. Preserve it as
evidence and change the method only when the friction is consequential enough to
justify the change.

## 9. Portability hypothesis

The current protocol intentionally places portability at the handoff surface:

```text
consume EXECUTION_PACKET_v0
+
respect authority / stop conditions
+
emit EVIDENCE_RETURN_v0
```

Any implementation that can satisfy that contract is a candidate Workshop
occupant.

This is only a hypothesis until independently pressured.

Do not infer from the existence of this document that cloud Codex, Astra, local
models, scripts, or humans are behaviorally interchangeable.

## 10. First protocol pressure

A useful first bounded pressure is:

> Give the same authorized execution packet independently to two Workshop
> implementations and test whether both correctly recover what they may change,
> what they may not infer, what evidence they owe, and when they must stop.

The protocol passes only in the narrow tested regime if the authority boundary
survives both executions without hidden semantic strengthening.

Differences are evidence. Do not normalize them away.

## 11. Worked example — read-only cursor retrieval

This example is a development specimen derived from the current cursor work. It
illustrates packet shape; it does not establish a generalized cursor protocol.

### EXECUTION_PACKET_v0

```text
PACKET_ID:
  CHATGPT-MANUAL-TETHER-002

BASIS:
  retained registry projection reports consumer chatgpt-main at CE-000006
  with four unread events
  canonical retrieval surface named by the operator:
  python tools/continuity.py delta --consumer chatgpt

CURRENT_PRESSURE:
  recover the unread delta from the existing retained source without changing
  consumer acknowledgement state

ADMITTED_EVIDENCE:
  a retained registry projection reports four unread events
  the named delta command is the intended read-only retrieval surface

UNRESOLVED:
  exact unread payloads remain unknown until retrieved
  whether the Workshop can directly execute/read the repository source remains
  unknown to the receiver before attempting access

AUTHORIZED_OPERATIONS:
  inspect the named retained source
  execute/read the named delta retrieval if available
  report the recovered unread delta

UNAUTHORIZED_EXTRAPOLATIONS:
  do not acknowledge events
  do not modify or advance any consumer cursor
  do not infer unread payloads if direct retrieval is unavailable
  do not substitute conversational memory for repository evidence

REQUIRED_EVIDENCE_RETURN:
  exact retrieval attempted
  payloads recovered, if any
  repository/runtime evidence supporting the recovery
  anything still unknown

STOP_OR_ESCALATE_IF:
  the named source cannot be executed or read directly
  retrieval requires acknowledging/modifying/advancing a cursor
  basis differs materially from the stated retained projection

EXECUTION_QUESTIONS:
  can the four unread events be recovered from the retained source?
  what payloads does that source actually return?

AUTHORIZATION:
  READ_ONLY_RETRIEVAL_AUTHORIZED
```

### Valid Evidence Return shape

If retrieval succeeds:

```text
OPERATIONS_EXECUTED:
  named read-only delta retrieval

DIRECT_EVIDENCE:
  returned unread payloads / exact source output

SURVIVING_UNKNOWNS:
  any facts not represented by the returned source

REFUSED_OR_ESCALATED_DECISIONS:
  none, unless the source requested a mutation

WORKSHOP_CLAIMS:
  bounded claims only about what the retained source returned
```

If direct source access is unavailable:

```text
OPERATIONS_EXECUTED:
  attempted direct read / execution

DIRECT_EVIDENCE:
  access failure or unavailable execution surface

SURVIVING_UNKNOWNS:
  unread payloads remain unknown

REFUSED_OR_ESCALATED_DECISIONS:
  refused to infer payloads from prior conversation or advance the cursor

WORKSHOP_CLAIMS:
  no working-state claim beyond the access failure is warranted
```

The example preserves the intended asymmetry:

```text
permission to inspect
!=
permission to mutate

knowledge that unread events exist
!=
knowledge of their payloads

failed retrieval
!=
license to infer
```

## 12. v0 amendment rule

Keep this method small.

Do not add fields merely because they might be useful.

Amend only when a real execution shows that the existing packet or return
surface cannot preserve a consequential boundary, repeatedly creates
unnecessary epistemic work, or prevents a legitimate bounded operation.

Pressure the protocol before elaborating it.
