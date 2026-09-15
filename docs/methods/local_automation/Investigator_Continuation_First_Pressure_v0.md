# Investigator Continuation — First Pressure v0

**Status:** bounded implementation / evaluation method  
**Scientific authority:** NONE  
**Pressure-selection authority:** limited to the first continuation-efficiency specimen described here  
**Repository mutation authority:** implementation files and tests only; no autonomous research mutation  
**Acceptance authority:** external Codex / frontier / human adjudication

This method operationalizes only the first executable pressure projected in
`docs/projection/Investigator_Continuation_v0.md`.

It does **not** authorize interruption recovery, worker routing, scheduling,
daemons, autonomous objective selection, generalized persistence, retry engines,
or scientific authority transfer.

## 1. Question

Test only:

> Can a finalized, basis-checked continuation packet reduce total
> fresh-investigator reconstruction burden on one clean bounded task without
> degrading continuation correctness?

A positive result supports only that narrow claim under the realized specimen.

## 2. Required separation

The implementation must preserve three surfaces:

```text
MECHANICAL BASIS
exact reproducible repository / packet / source coordinates

PRIOR PROJECTED STANDING
claims retained from investigator N

CURRENT ADMISSION
checks performed by investigator N+1 before using those claims
```

No packet field grants current authority merely because it survived handoff.

## 3. Smallest implementation surface

Implement only enough machinery to construct, finalize, verify, and admit one
`investigator_continuation_v0` packet under a clean committed basis.

The expected minimum code surface is:

```text
schema
packet builder / canonical serializer
packet integrity verifier
repository-basis admission verifier
unit tests
```

Exact file placement should follow existing repository conventions. Do not add a
scheduler, router, controller, background process, model loop, UI, or startup
integration in this pass.

### 3.1 Builder responsibility

The builder may mechanically attach:

- declared repository identity;
- current exact `HEAD` commit;
- current branch;
- clean-worktree requirement / observation;
- exact committed source identities (`path + git_blob`);
- packet identity;
- diagnostic generation time;
- packet finalization and digest.

The builder must **not** invent semantic continuation standing. It receives the
prior objective, prior established claims, unresolved residue, and
`must_revalidate` entries from the caller and validates only their structural
references.

### 3.2 Admission responsibility

Admission verifies only what is mechanically checkable in v0:

```text
schema supported
packet COMPLETE
packet digest valid
repository identity matches declared target
current worktree clean
HEAD matches packet basis_commit
branch matches packet branch
all cited source paths resolve at current HEAD
all cited Git blobs match packet identities
all semantic source_refs resolve to issued source_ids
```

Admission returns structured check evidence. It does not silently repair a
failed check and does not convert packet prose into current authority.

For checks that matter to admission, preserve at least:

```text
MATCH
MISMATCH
CHECKED_ABSENT
CHECK_FAILED
NOT_CHECKED
```

Equivalent names are acceptable if the distinctions remain recoverable.

## 4. Packet finalization and digest

The first implementation must choose one deterministic digest rule and document
it in code/tests.

Use this v0 rule unless repository pressure requires an equivalent simpler
mechanism:

1. construct the complete packet with `integrity.packet_status = "COMPLETE"`;
2. omit `integrity.packet_digest` from the digest input;
3. serialize the remaining object as UTF-8 JSON with recursively sorted object
   keys and compact separators `,` and `:`;
4. compute lowercase SHA-256 hexadecimal over those exact bytes;
5. insert the digest as `integrity.packet_digest`;
6. when writing a packet artifact, write the final object to a temporary file
   outside the source worktree and atomically replace/finalize the target file
   where the host permits it.

The packet artifact itself is **not** part of the repository basis for the
first pressure. Keep packet and measurement artifacts outside the tested source
worktree so creating them does not invalidate the clean-worktree condition or
advance `HEAD`.

A parseable packet with missing/invalid finalization or digest is not
admissible.

## 5. Clean repository basis

v0 deliberately does not solve dirty-worktree continuation.

Before packet construction and before packet admission:

```text
git status --porcelain
```

must establish a clean tested worktree.

If the worktree is dirty, the v0 operation stops rather than inventing a
fingerprint or treating committed blobs as identities of uncommitted bytes.

The implementation must not clean, reset, stash, checkout, or otherwise mutate
the worktree to manufacture eligibility.

## 6. Source identity

Every semantic source reference must resolve through a packet-local source
manifest:

```json
{
  "source_id": "source-0001",
  "path": "docs/...",
  "git_blob": "<exact Git blob>"
}
```

The blob must be derived from the packet's exact committed basis. Free-form
paths inside semantic claims are not substitutes for `source_id` references.

For this first pressure, only committed sources are admissible.

## 7. Minimal packet shape

The first implementation should remain close to:

```json
{
  "schema": "investigator_continuation_v0",
  "continuation_id": "...",
  "predecessor_id": null,
  "integrity": {
    "packet_status": "COMPLETE",
    "packet_digest": "...",
    "generated_at": "..."
  },
  "mechanical_basis": {
    "repository": "ReedBarrus/DME_Lab",
    "basis_commit": "...",
    "branch": "main",
    "clean_worktree_required": true,
    "source_manifest": []
  },
  "prior_projected_standing": {
    "prior_objective_projection": {
      "statement": "...",
      "source_refs": []
    },
    "prior_established": [],
    "unresolved": [],
    "must_revalidate": [],
    "inflight_attempts": []
  }
}
```

For the **first clean continuation pressure**, `inflight_attempts` should remain
empty unless the chosen specimen unavoidably contains an in-flight consequence.
Do not implement the later interruption taxonomy merely because the field
exists.

`predecessor_id` may be null. Multiple future packets may share one predecessor;
no uniqueness or newest-wins behavior should be implemented.

## 8. Minimum deterministic tests

Before any fresh-investigator A/B run, establish at least these pressures:

1. clean matching basis + correct blobs + correct digest -> admission succeeds;
2. packet content tampered after finalization -> digest rejection;
3. missing/non-`COMPLETE` finalization -> rejection;
4. changed `HEAD` -> basis mismatch, no silent reuse;
5. dirty worktree -> v0 rejection without cleanup/mutation;
6. changed cited source at a new commit -> source/basis mismatch is visible;
7. unknown semantic `source_ref` -> builder/schema/admission rejection;
8. missing cited source -> `CHECKED_ABSENT`, not `MATCH` or generic false;
9. failed Git/source observation -> `CHECK_FAILED`, not absence;
10. `generated_at` age alone never changes admission standing;
11. packet construction / admission performs no repository mutation;
12. two packets may share the same `predecessor_id` without implicit winner
    selection.

Use existing repository testing conventions. Do not weaken unrelated tests to
make this surface pass.

## 9. First live specimen

After deterministic implementation passes, freeze one real, bounded,
non-mutating continuation question whose legitimate outcome can be independently
adjudicated from repository evidence.

Recommended first specimen:

> Determine the smallest documentation reconciliation currently warranted for
> `README.md` / local-automation status now that Repo Scout and local-model
> qualification pressure have executable evidence. Do not edit files. Return
> only the bounded documentation changes that are actually supported and the
> claims that must remain explicitly unimplemented.

This question is useful because it is real, bounded, current, and has a narrow
correctness surface without requiring a model invocation, repository mutation,
or worker routing.

The packet may retain prior standing needed to navigate toward the relevant
method/decision evidence, but it may not contain a current-authority declaration
or a pre-written final answer.

## 10. Information-value preflight

Before either condition begins, freeze an explicit information-value preflight.
The packet intervention must:

```text
contain consequential prior standing whose reuse is expected to remove real
  historical reconstruction work
identify the reconstruction work expected to be avoided
contain more than navigation bookmarks
not place the same retained standing broadly back under must_revalidate
exclude the current task answer or a pre-written equivalent
permit mechanical provenance admission without re-proving the retained
  semantic claims
leave current applicability and current authority unresolved for the new
  investigator
```

If those conditions cannot be established before A or B starts, stop rather
than revise the intervention after observing one condition. Passing this
preflight does not establish packet usefulness, correctness, or efficiency.

## 11. A/B conditions

Create two isolated fresh worktrees or equivalent clean repository copies from
one exact frozen commit. Do not run A and then reuse its mutated state for B.

### Condition A — ordinary reconstruction

Provide:

- normal repository access;
- normal `AGENT_CONTEXT.md` startup protocol;
- the frozen specimen question;
- no inherited chat context;
- no continuation packet.

### Condition B — continuation-assisted reconstruction

Provide exactly the same basis, repository access, task instruction, model /
frontier realization, and evaluator, plus:

- one finalized continuation packet;
- instruction to verify/admit the packet before relying on it;
- instruction to reconstruct independently only where admission fails or the
  packet leaves consequential residue unresolved.

The packet is the only intended informational intervention.

## 12. Correctness gate

Efficiency is not evaluated until both conditions are independently checked
against authoritative repository evidence.

A competent result must at minimum:

```text
identify the frozen basis correctly
preserve projection / method / decision authority distinctions
not convert prior packet claims into current authority
retain consequential unresolved or unimplemented boundaries
reach the same legitimate documentation recommendation / abstention,
or an independently acceptable bounded equivalent
```

The continuation packet must not serve as its own answer key.

A faster wrong answer is a failed continuation specimen.

## 13. Cost accounting

Record continuation work on separate surfaces; do not collapse them into one
score or infer that reconstruction displacement is an established mechanism.

Condition A:

```text
C_A = ordinary fresh reconstruction work
```

Condition B:

```text
C_B =
continuation-specific packet-production overhead
+ packet admission / revalidation
+ selective reconstruction
```

Do **not** charge ordinary predecessor research to B merely because it happened
before handoff. Do charge extra source reading, summarization, serialization,
manual correction, or adjudication performed only to manufacture the packet.

Observe and retain separately where feasible:

```text
historical reconstruction burden
packet-production burden
packet-admission burden
duplicated reconstruction
current-task adjudication
frontier work / newly inspected consequential residue
total wall time / tool and attention cost
correctness
boundedness
```

Each surface may retain its own supporting coordinates, including files or
source bytes examined, Git operations, tool calls, orientation tests, human
clarification, duplicate work, and stale assumptions. Movement from historical
reconstruction into frontier work is trajectory evidence, not by itself a cost
reduction or continuation benefit.

A positive first result requires competent continuation first, then a meaningful
reduction in at least one scarce continuation coordinate without hidden offsetting
cost being ignored.

## 14. Stop conditions

Stop and retain the result rather than widening the apparatus if:

- packet integrity cannot be made deterministic;
- clean-basis admission is ambiguous;
- semantic standing requires new authority machinery;
- the implementation begins requiring worker routing or scheduling;
- the A/B specimen cannot be independently adjudicated;
- the packet merely embeds the final answer rather than reducing navigation
  cost;
- continuation-specific production cost dominates the saved reconstruction
  burden.

Any of those outcomes is useful evidence against the current mechanism or
specimen.

## 15. Explicitly deferred

This first pressure does not test or authorize:

- Qwen interrupted-attempt recovery;
- automatic retry;
- local-model invocation;
- worker qualification/routing;
- dirty-worktree continuation;
- repeated continuation chains;
- scheduler/heartbeat operation;
- autonomous research resumption;
- commit authority for any model.

Those remain separate pressures.
