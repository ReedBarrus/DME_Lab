# Cockpit Projection Adapter Pressure v0

## Scope and repository gate

This pass asked whether the bounded Cockpit Projection Adapter could turn
damaged, ambiguous, stale, unsupported, or conflicting committed repository
state into a cleaner normalized projection than the source warranted.

After `git fetch origin main`, local `HEAD` and `origin/main` were identical at
`c4256e077c69d03b1461755dbaa20c2ff5f1c15f` with a clean worktree.

This was implementation pressure below the Cockpit UI boundary. It was not a
scientific pressure, website pass, Controller pass, generalized parser or
ontology pass, or adapter-remediation pass.

## Predeclared semantic rule

A scenario `SURVIVES` when the changed or ambiguous condition remains
recoverably visible in normalized output or diagnostics and the adapter does
not strengthen the source.

A scenario is a `CONTRACT_VIOLATION` when the adapter emits a plausible clean
projection while materially hiding, inventing, collapsing, or strengthening
the tested source condition.

A scenario is `BASIS_INSUFFICIENT` when the committed fixture or observation
cannot discriminate the intended behavior. A contract gap exposed by the
optional duplicate-identity case is retained as `CONTRACT_AMBIGUITY` rather
than supplied by the harness.

The rules were frozen before scenario execution. Adapter success was not
required for the pressure runner itself to succeed.

## Healthy baseline

The adapter projected the exact starting commit and compared it with
`origin/main`:

| Surface | Observed control |
| --- | --- |
| Source commit | `c4256e077c69d03b1461755dbaa20c2ff5f1c15f` |
| Freshness | `current` |
| Active pressure | `null`; `agreement`; `explicit_none` from both declared sources |
| Pressure nodes | 19 |
| Pressure relations | 24 |
| Constraints | 46 |
| Evidence references | 214 |
| Projection documents | 3 |
| Diagnostics | 0 |
| PR-018 | `OPEN`; not active |
| PR-019 | current `BOUNDED_RESOLUTION`; R0 `BASIS_INSUFFICIENT`; R1 `BOUNDED_RESOLUTION` |
| Controller | `projection_document`; `PARKED` |

Zero baseline diagnostics established only the control specimen.

## Pressure basis

The bounded runner created named temporary Git repositories, committed each
source wound, invoked the unchanged adapter against an exact commit, retained a
compact normalized observation, and applied the predeclared classification.

No current scientific evidence was used as mutable fixture data. No random
fuzzing, arbitrary semantic scraping, or source repair occurred.

## Scenario observations

### P1 — Missing required source

- **Mutation:** omitted `PRESSURE_RESOLUTION_MAP.md` from the committed tree.
- **Intended discriminator:** the map absence must remain visible and the
  projection must not appear complete.
- **Observed:** projection status was `partial`; node count was zero; the
  required source inventory marked the map missing. Diagnostics included
  `missing_required_source` and a secondary `source_conflict` from the
  unavailable map navigation versus retained `PROJECT_STATE.md` navigation.
- **Classification:** `SURVIVES`.

The adapter did not use a working-tree, cached, or similarly named substitute.

### P2 — Unknown pressure standing

- **Mutation:** set one valid node's exact standing to `GOBLIN_PENDING`.
- **Intended discriminator:** preserve the raw token without a nearest-known
  substitution.
- **Observed:** value remained `GOBLIN_PENDING`, status became
  `unknown_standing`, and an `unknown_standing` diagnostic was emitted.
- **Classification:** `SURVIVES`.

### P3 — Broken evidence reference

- **Mutation:** pointed one explicit Evidence link to the nonexistent committed
  path `docs/decisions/not-present.md`.
- **Intended discriminator:** retain the occurrence as broken navigational
  residue without treating it as warrant.
- **Observed:** the reference remained in `evidence_refs` with target kind
  `decision`, resolution status `broken`, original target, origin, and
  provenance. A `broken_reference` diagnostic was emitted.
- **Classification:** `SURVIVES`.

### P4 — Source conflict

- **Mutation:** the map declared `Active pressure: none` while
  `PROJECT_STATE.md` declared `Active experimental pressure: PR-018`.
- **Intended discriminator:** retain both declarations and no unsupported clean
  winner.
- **Observed:** normalized active pressure had value `null`, status
  `conflicting`, both raw declarations with separate provenance, and a
  `source_conflict` diagnostic.
- **Classification:** `SURVIVES`.

### P5 — Relation-looking prose

- **Mutation:** ordinary Pressure prose mentioned `PR-002` while both relation
  fields were em dashes; a later committed control explicitly declared
  `Blocked by: PR-002`.
- **Intended discriminator:** incidental prose must produce no edge, while the
  explicit field must produce one.
- **Observed:** the prose specimen produced zero PR-001 relations. The control
  produced exactly one `blocked_by` relation targeting PR-002.
- **Diagnostics:** none.
- **Classification:** `SURVIVES`.

### P6 — Malformed pressure structure

- **Mutation:** removed the required colon from the supported `**Standing:**`
  field marker, producing the nearby unsupported `**Standing**` form.
- **Intended discriminator:** parser narrowness must remain visible without
  scraping neighboring prose; an independent valid node must survive.
- **Observed:** wounded standing remained `missing` with null raw and normalized
  values; a `parse_failure` diagnostic was emitted; projection status was
  `partial`; the independent PR-002 standing remained
  `BOUNDED_RESOLUTION`.
- **Classification:** `SURVIVES`.

### P7 — Malformed constraint among valid records

- **Mutation:** committed valid D-0001, one malformed JSON line, then valid
  D-0002.
- **Intended discriminator:** retain both valid constraints and the malformed
  line as separate residue.
- **Observed:** D-0001 and D-0002 remained independently projectable; a
  `parse_failure` diagnostic identified the malformed line; projection status
  was `partial`.
- **Classification:** `SURVIVES`.

### P8 — Resolution-history wound

- **Healthy control:** current `BOUNDED_RESOLUTION` plus R0
  `BASIS_INSUFFICIENT` and R1 `BOUNDED_RESOLUTION` were all represented.
- **Mutation:** renamed only the recognized `Resolution history` heading to
  `Prior resolutions`; both visibly history-like R entries remained unchanged
  in the committed source.
- **Intended discriminator:** if the narrow parser cannot recover the history,
  that loss must remain visible rather than hiding behind a clean current
  standing.
- **Observed:** current standing remained clean `BOUNDED_RESOLUTION`,
  `resolution_history` became an empty list, and no `parse_failure` or
  `unsupported_structure` diagnostic identified the lost PR-001 material.
- **Classification:** `CONTRACT_VIOLATION`.

The parser was allowed to reject the unsupported heading. The violation is the
silent loss of the historical wound, not the refusal to accept an alternate
Markdown heading.

No adapter remediation was attempted.

### P9 — Stale projection basis

- **Mutation:** projected commit A after a later commit B changed PR-001 on the
  freshness ref.
- **Intended discriminator:** report A as stale against B while continuing to
  project A's content.
- **Observed:** `source_commit` remained A, `observed_tail` was B, freshness was
  `stale`, and PR-001 retained A's `BOUNDED_RESOLUTION` rather than B's `OPEN`.
- **Diagnostics:** none.
- **Classification:** `SURVIVES`.

### P10 — Projection-document containment

- **Mutation:** inserted `PR-999`, `ACTIVE PIPELINE`, `SUPER_CONTROLLER`, and
  `RUNNING` text into the explicitly non-authoritative Controller projection.
- **Intended discriminator:** speculative content must not cross the evidence
  horizon into earned or active normalized state.
- **Observed:** Controller remained a `projection_document` with standing
  `PARKED`; no PR-999 node or relation was created; active pressure remained
  explicit none.
- **Diagnostics:** none.
- **Classification:** `SURVIVES`.

### P11 — Duplicate pressure ID

- **Mutation:** committed two explicit PR-001 headings with different titles
  and standings.
- **Intended discriminator:** duplicate identity must not silently collapse;
  unspecified validity or consumer handling must not be invented.
- **Observed:** both nodes remained in the normalized list, one with
  `BOUNDED_RESOLUTION` and one with `OPEN`; no diagnostic described their shared
  ID.
- **Classification:** `CONTRACT_AMBIGUITY`.

The projection contract does not currently define pressure-ID uniqueness,
duplicate-conflict diagnostics, or consumer semantics. The harness therefore
does not impose a rule.

## Adjudication

The bounded result is:

```text
bounded_adapter_pressure_exposed_unresolved_wound
```

Classification totals:

| Classification | Count |
| --- | ---: |
| `SURVIVES` | 9 |
| `CONTRACT_VIOLATION` | 1 |
| `BASIS_INSUFFICIENT` | 0 |
| `CONTRACT_AMBIGUITY` | 1 |

The strongest supported adapter behavior is that, across the named bounded
specimens, required-source absence, unknown standing, broken links, explicit
source conflict, explicit-only relations, malformed field and JSONL residue,
stale commit basis, and projection-document containment remained observable.

The strongest behavior not supported is general contract-safe projection.
Visible history-like source material can currently disappear when its section
heading is unsupported while leaving a plausible clean current standing. The
contract also does not yet establish duplicate pressure-ID behavior.

This does not establish reliability for arbitrary Markdown damage, semantic
conflict, future source shapes, concurrency, or hostile input.

## Durable artifacts and verification

- runner: `src/runtime/cockpit_projection_adapter_pressure.py`;
- focused verification: `tests/cockpit/test_projection_adapter_pressure.py`;
- compact trace: `traces/cockpit_projection_adapter_pressure_v0.json`;
- this decision.

Verification completed:

- focused existing adapter plus pressure tests: 22/22 passed;
- full hardware-free suite: 530/530 passed;
- the runner completed successfully while retaining a semantic violation;
- the starting adapter implementation was not changed;
- the Cockpit projection contract was not changed.

## Repository standing

This pass adds no Pressure / Resolution Map node, chart, constraint, scientific
standing, Controller authority, website code, UI, or generated current
projection snapshot.

The existing projection contract is sufficient to classify P8 as a violation.
P11 remains contract ambiguity. Any later contract tightening or adapter
remediation requires a separately selected pass.

## Stop boundary

Stop after preserving the observations and bounded adjudication. Do not repair
the resolution-history wound, choose duplicate-ID semantics, refactor the
adapter, begin another adapter pass, or construct the Cockpit UI here.
