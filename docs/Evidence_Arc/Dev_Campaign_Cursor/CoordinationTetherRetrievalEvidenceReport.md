Coordination / Tether / Retrieval Evidence Report
Proposed path: docs/Evidence_Arc/Dev_Campaign_Cursor/Coordination_Tether_Retrieval_Evidence_001.md
Status: Evidence checkpoint
Scope: Two-consumer coordination registry, invocation tethering, cursor reconstruction, unread-delta reachability, and ChatGPT repository-read boundary
Standing: Bounded empirical support only. This report does not promote generalized coordination architecture, automatic synchronization, multi-agent liveness, or external authority.
1. Purpose
This checkpoint freezes the evidence accumulated while moving from bilateral ChatGPT↔Codex continuity into the first inspectable two-consumer coordination surface.
The pressure sequence asked whether a persistent semantic consumer could remain distinct from:
\[
\text{cursor}
\neq
\text{invocation}
\neq
\text{tether}
\neq
\text{working state}
\neq
\text{capability}
\neq
\text{payload delivery}
\neq
\text{semantic application}
\neq
\text{acknowledgement}
\]The campaign did not attempt to build a general agent coordinator.
Instead, it added and pressured the smallest relationships necessary to answer:
Who is the persistent consumer, where is it positioned, what runtime invocation is associated with it, what unread material exists, and what can the current invocation legitimately recover?

2. Prior Basis
Before this evidence arc, the continuity substrate had already established:
\[
\text{UNINITIALIZED}
\neq
\text{POSITIONED}
\]\[
\text{event presented}
\neq
\text{event semantically applied}
\neq
\text{event durably acknowledged}
\]\[
\text{semantic application}
\neq
\text{standing promotion}
\]\[
\text{cursor continuity}
\neq
\text{working-state continuity}
\]Acknowledgement was constrained to the contiguous consumed prefix.
A successful bounded ChatGPT→Codex→ChatGPT roundtrip had also shown that task semantics could cross retained continuity without human reconstruction.
A later multi-round council demonstrated machine-speed deliberative narrowing without standing or authority inflation.
Those results created pressure for a visible coordination surface.
3. Coordination Registry
A bounded registry was created with exactly two semantic consumers:
Consumer	Role
chatgpt-main	semantic integrator / continuity consumer
codex-main	repository implementation / continuity consumer


The registry stores identity and references but derives cursor-dependent state from the authoritative continuity artifacts.
For each consumer, the surface can expose:
consumer_id, role, cursor_ref, cursor state, last seen event, unread count, invocation association, activity state, and optional working-state reference.
Critically, the registry does not become a second cursor store.
Live pressure confirmed that advancing codex-main through legitimate ACK_ONE changed its projected coordinate and unread count without modifying the registry identity state or affecting chatgpt-main.
Earned distinction
\[
\boxed{
\text{registry projection change}
\neq
\text{registry mutation}
}
\]This established the registry as a projection surface rather than an independent continuity authority.
4. Registry Failure Legibility
The registry retained unsupported conditions explicitly instead of guessing.
Observed cases included:
Condition	Projection
missing cursor	MISSING_CURSOR
uninitialized cursor	BOOTSTRAP_REQUIRED
stale invocation reference	STALE_REF
invocation not retained	NONE / NOT_RETAINED
activity not demonstrated	UNKNOWN
working-state reference absent	NOT_RETAINED
consumer at stream head	unread 0


This pressure supported:
\[
\boxed{
\text{activity UNKNOWN}
\neq
\text{inactive}
}
\]and:
\[
\boxed{
\text{working\_state\_ref absent}
\neq
\text{no working state exists}
}
\]The surface reports the evidence state, not an inferred world state.
5. Codex Invocation Association
codex-main was associated with one exact retained Codex runtime session artifact:
C:\Users\Admin\.codex\sessions\2026\09\17\
rollout-2026-09-17T18-03-12-01a0b209-f723-7942-896a-907cdef4eeaa.jsonl
The association changed only invocation metadata.
Cursor, unread count, activity state, working-state reference, scientific standing, authority, and the ChatGPT registry entry remained unchanged.
The retained artifact resolved mechanically as AVAILABLE.
This produced:
\[
\boxed{
\text{retained artifact association}
\neq
\text{invocation liveness}
}
\]\[
\boxed{
\text{artifact existence}
\neq
\text{semantic consumption}
}
\]\[
\boxed{
\text{invocation association}
\neq
\text{cursor ownership}
}
\]The session trace is therefore a runtime referent, not authority over the consumer.
6. ChatGPT Invocation Identity Problem
No repository-retained ChatGPT-native conversation/thread identifier was available.
Existing ChatGPT-authored events did not contain a usable thread_id, conversation_id, or equivalent runtime referent.
This ruled out several tempting substitutes:
\[
\text{ChatGPT-authored event}
\neq
\text{ChatGPT invocation identity}
\]\[
\text{consumer identity}
\neq
\text{invocation identity}
\]\[
\text{cursor coordinate}
\neq
\text{invocation identity}
\]A scoped invocation identity was therefore characterized minimally as:
\[
(\text{invocation\_kind},\text{invocation\_ref})
\]but no independently verified ChatGPT-native instance was available.
7. Manual Opaque ChatGPT Tether
Rather than inventing external identity semantics, a bounded local tether was introduced.
Observed association:
tether_id:
  local-tether-chatgpt-main-000001

consumer_id:
  chatgpt-main

invocation_kind:
  chatgpt-thread

invocation_ref:
  CHATGPT-MANUAL-TETHER-001

association_basis:
  MANUAL_ASSERTION

resolution_status:
  OPAQUE
The tether means only:
A human explicitly asserted that this local tether record corresponds to the selected ChatGPT invocation.

It does not establish:
- native ChatGPT thread identity,
- liveness,
- synchronization,
- cursor ownership,
- working-state transfer,
- acknowledgement,
- standing,
- or authority.
Pressure confirmed that rebinding invocation metadata did not move the cursor or alter unread state.
Earned distinctions
\[
\boxed{
\text{local tether identity}
\neq
\text{external invocation identity}
}
\]\[
\boxed{
\text{manual assertion}
\neq
\text{independent verification}
}
\]\[
\boxed{
\text{opaque reference}
\neq
\text{resolvable artifact}
}
\]\[
\boxed{
\text{rebinding metadata}
\neq
\text{cursor movement}
}
\]This allowed ChatGPT occupancy to become experimentally addressable without pretending product-native identity had been solved.
8. Fresh-Invocation Occupant Pressure
A second fresh ChatGPT invocation was manually given:
CHATGPT-MANUAL-TETHER-002
The fresh invocation reconstructed:
TETHER: CHATGPT-MANUAL-TETHER-002
BOUND_CONSUMER: chatgpt-main
CURSOR: CE-000006
UNREAD_DELTA: 4
MODE: reconstruct / inspect
CURSOR_ADVANCE: NO
This was the first bounded evidence that a fresh occupant could recover the persistent consumer coordinate without inheriting the old thread's conversational history.
It supported:
\[
\boxed{
\text{tether token}
+
\text{retained coordination state}
\rightarrow
\text{recoverable consumer coordinate}
}
\]within the tested configuration.
But it did not yet establish semantic reconstruction.
9. Coordinate Recovery Without Delta Recovery
The fresh invocation could recover:
consumer: chatgpt-main
cursor: CE-000006
unread_delta_count: 4
but initially could not recover the four unread event bodies.
Importantly, it refused to infer their contents.
The strongest legitimate state at that point was:
RECOVERED:
consumer identity
cursor coordinate
unread cardinality

NOT RECOVERED:
unread event payloads

THEREFORE:
no semantic delta legitimately consumed
no cursor advance justified
no post-CE-000006 working-state claim justified
This earned:
\[
\boxed{
\text{cursor coordinate}
\neq
\text{unread cardinality}
}
\]\[
\boxed{
\text{unread cardinality}
\neq
\text{unread event identity}
}
\]and:
\[
\boxed{
\text{cursor-addressable continuity}
\not\Rightarrow
\text{semantic reconstructability}
}
\]This was not a generic “memory failure.” It was a localized reachability failure.
10. Payload Availability Diagnosis
Repository inspection found that the unread event bodies were already retained.
chatgpt-main was positioned at:
CE-000006
and the stream contained:
CE-000007
CE-000008
CE-000009
CE-000010
The registry projection internally computes:
_events_after(...)
but exposes only:
len(delta)
as unread_event_count.
The full unread event bodies remain available through the separate canonical read-only retrieval surface:
python tools/continuity.py delta --consumer chatgpt
Therefore the root cause was not missing data.
It was a projection/reachability boundary:
\[
\boxed{
\text{repository payload availability}
\neq
\text{consumer-surface delivery}
}
\]More specifically:
cursor
→ event selection
→ unread cardinality projected

while

selected event payloads
→ canonical delta command
→ not projected through registry
The registry was functioning according to its bounded contract; the consumer lacked the next read surface.
11. Capability Boundary
The fresh ChatGPT invocation initially attempted the canonical command in a runtime that did not contain the repository:
/mnt/data/tools/continuity.py
was unavailable.
The invocation correctly stopped rather than fabricating the delta.
After moving to a ChatGPT surface with the GitHub connector available, the consumer could read the active continuity-delta-v0 branch, inspect the cursor and canonical event stream, and recover exactly:
CE-000007
CE-000008
CE-000009
CE-000010
without acknowledgement or modification.
This is strong evidence for another orthogonal factorization:
\[
\boxed{
\text{tethered ChatGPT}
\neq
\text{repository-capable ChatGPT}
}
\]The tether answers:
Which semantic consumer is this invocation associated with?

The connector answers:
What repository evidence can this invocation reach?

Neither implies the other.
12. Exact Unread Delta Recovered
The connector-enabled invocation recovered:
CE-000007
COUNCIL_COUNTERPROPOSAL
ChatGPT round 2 displaced an inspect-command proposal with a narrower startup-pointer candidate and separated:
durable documentation
runtime injection
observed compliance
CE-000008
COUNCIL_RESPONSE
Codex accepted only the root AGENTS.md pointer plus a fresh startup pressure and refused to generalize the result into delivery or reliability.
CE-000009
COUNCIL_CHECKPOINT
The multi-round deliberation passed after two Codex response rounds.
The inspect proposal was displaced.
No scientific standing or authority changed.
CE-000010
STARTUP_DISCOVERABILITY_PROBE
The root AGENTS.md pointer existed and the event explicitly instructed consumers to treat the event only as reported experimental state.
Again:
scientific standing unchanged
external authority unchanged
no broader work authorization
This produced the first complete demonstrated path:
\[
\boxed{
\text{manual tether}
\rightarrow
\text{consumer identity}
\rightarrow
\text{cursor coordinate}
\rightarrow
\text{repository read capability}
\rightarrow
\text{canonical event stream}
\rightarrow
\text{exact unread payload}
}
\]13. Retrieval Is Still Not Application
The recovery of CE-000007…CE-000010 does not itself establish that the fresh invocation has reconstructed the valid current semantic working state.
The following distinction remains active:
\[
\boxed{
\text{payload retrieval}
\neq
\text{semantic application}
\neq
\text{acknowledgement}
}
\]The consumer has obtained the events.
It has not yet been pressured to determine:
- which referenced artifacts are necessary,
- which event claims survive inspection,
- which claims remain merely reported,
- what working state legitimately follows,
- what current frontier can be recovered,
- and whether old-thread conversation contributes any necessary information absent from retained artifacts.
That is the next frontier.
14. Consolidated Earned Distinctions
The evidence arc currently supports the following bounded distinction set:
registry identity
!= cursor authority

registry projection change
!= registry mutation

invocation association
!= semantic consumption

activity UNKNOWN
!= inactive

working_state_ref absent
!= no working state exists

retained artifact association
!= invocation liveness

artifact existence
!= semantic consumption

local tether identity
!= external invocation identity

manual assertion
!= independent verification

opaque reference
!= resolvable artifact

rebinding metadata
!= cursor movement

ChatGPT-authored activity
!= ChatGPT invocation identity

same consumer and cursor
!= same invocation

consumer coordinate
!= invocation-local semantic state

cursor coordinate
!= unread cardinality

unread cardinality
!= unread event identity

unread event identity
!= payload availability

repository payload availability
!= consumer-surface delivery

opaque invocation tether
!= repository/tool capability

tethered ChatGPT
!= repository-capable ChatGPT

payload retrieval
!= semantic application

semantic application
!= acknowledgement
These should remain scoped to the pressures that produced them.
They are not claims about all agent systems.
15. Stronger Emerging Factorization
The current evidence suggests the coordination surface is decomposing into at least these independently variable dimensions:
\[
\boxed{
C
=
(\text{consumer identity},
\text{cursor},
\text{tether},
\text{invocation},
\text{capability surface},
\text{working state},
\text{standing},
\text{authority})
}
\]This is a descriptive factorization candidate, not a promoted runtime architecture.
The evidence repeatedly shows that silently collapsing any of these coordinates can create false continuity or false authority.
In particular:
\[
\boxed{
\text{consumer position}
\neq
\text{current invocation knowledge}
}
\]A persistent consumer can survive while its occupant changes.
A new occupant can recover the chair and coordinate without inheriting invocation-local history.
Whether it can reconstruct sufficient semantic state is now experimentally addressable.
16. What Survives
The following campaign claims survived the current evidence arc:
The continuity stream can remain the durable source of recorded activity while the registry projects consumer relationships without becoming a second event or cursor authority.
Persistent consumer identity can remain stable across invocation changes.
Invocation identity can be represented independently from consumer identity.
Manual opaque tethering is sufficient for bounded experiments when its evidentiary weakness is explicit.
A fresh ChatGPT invocation can recover a persistent consumer coordinate.
Unread payloads can be recovered from canonical retained state when the invocation has the required repository-read capability.
Capability can be added without silently widening authority or standing.
The old conversation thread is not inherently required to discover retained unread events.
17. What Fractured
Several stronger assumptions failed or were narrowed.
A registry unread count is not sufficient for semantic reconstruction.
A tether does not provide repository access.
A ChatGPT invocation being associated with chatgpt-main does not imply that invocation has inherited the acknowledged semantic state of prior occupants.
Passive invocation association does not establish liveness.
Filesystem existence does not establish semantic validity.
The presence of retained payloads does not mean the current consumer surface can reach them.
A cursor coordinate does not establish that the current invocation personally consumed the history represented by that cursor.
18. Architecture Not Earned
This evidence does not yet justify:
- generalized multi-agent orchestration,
- automatic ChatGPT invocation discovery,
- automatic payload injection,
- automatic tether resolution,
- liveness monitoring,
- routing infrastructure,
- shared mutable cursors,
- cursor leases,
- concurrency control,
- working-state transfer,
- automatic semantic application,
- automatic acknowledgement,
- daemon/service architecture,
- generalized address matrix,
- agent swarm semantics,
- automatic authority delegation.
Several of these are becoming plausible future pressures.
None is yet required to explain the observed evidence.
19. Current Frontier
The fresh tethered ChatGPT invocation can now recover the exact unread payload.
The unresolved transition is:
\[
\boxed{
\text{available unread payload}
\rightarrow
\text{legitimate semantic working-state reconstruction}
}
\]The next pressure should therefore ask a fresh occupant to consume CE-000007…CE-000010 semantically without acknowledging them.
It should resolve only those refs necessary to answer:
What state can legitimately be reconstructed?

What changed?

What did not change?

Which claims remain merely reported?

What evidence must be independently inspected?

Is a current executable frontier recoverable?

What remains unresolved?

Does any necessary information exist only in the old invocation's
conversation history?
Only after this reconstruction is frozen should the original ChatGPT thread be given the same pressure as a control.
That comparison can test:
\[
\boxed{
\text{fresh occupant + retained chair}
}
\]against:
\[
\boxed{
\text{original occupant + retained chair + invocation-local history}
}
\]The difference between those outputs would provide direct evidence about:
\[
\boxed{
\text{retained semantic continuity}
\neq
\text{invocation-local conversational continuity}
}
\]20. Current Campaign State
The evidence arc has progressed from:
\[
\text{continuity stream}
\]to:
\[
\text{persistent consumers}
\]to:
\[
\text{inspectable registry}
\]to:
\[
\text{runtime invocation association}
\]to:
\[
\text{manual ChatGPT tether}
\]to:
\[
\text{fresh-occupant cursor reconstruction}
\]to:
\[
\text{payload reachability diagnosis}
\]to:
\[
\text{connector-mediated canonical delta recovery}
\]without adding generalized coordination architecture and without observed scientific-standing or external-authority inflation.
The next developmental boundary is no longer payload access.
It is semantic reconstruction.
Checkpoint Statement
\[
\boxed{
\begin{aligned}
&\text{Persistent consumer identity is recoverable across invocation change.}\\
&\text{Its cursor coordinate is recoverable independently of invocation history.}\\
&\text{Unread payload existence does not guarantee consumer-surface delivery.}\\
&\text{Repository capability can restore canonical payload reachability.}\\
&\text{Payload retrieval remains distinct from semantic application.}\\
&\text{Semantic application remains distinct from durable acknowledgement.}
\end{aligned}
}
\]