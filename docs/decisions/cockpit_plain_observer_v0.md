# Cockpit Plain Observer v0

## Scope and authority

This implementation-development pass built the first deliberately plain,
read-only DME Cockpit observer over the bounded normalized Projection Adapter
model.

After `git fetch origin main`, local `HEAD` and `origin/main` were identical
at:

```text
2858bdad69364b6432ea9bb360be7b3fbd80d233
```

That exact committed tree was the authority and source basis for the real
generated UI specimen. The working tree was clean at entry.

Stage 4C had already recorded a successful bounded adversarial re-pressure of
the remediated adapter. The committed
[`V0_PAGE_SPEC.md`](../cockpit/V0_PAGE_SPEC.md) supplied the implementation
boundary. This pass did not re-adjudicate Stage 4C, modify the adapter or
projection contract, or begin observer usability pressure.

## Framework and runtime choice

The observer uses dependency-free static HTML, CSS, and native JavaScript ES
modules. Node's built-in test runner exercises the frontend model and rendering
semantics. Python's standard-library HTTP server serves the repository locally.

No frontend framework or package dependency was introduced because the bounded
observer requires one static shell, one normalized JSON load, deterministic
node placement, read-only selection, and an inspector. A framework would add a
toolchain and abstraction surface without reducing the current semantic risk.

The implementation contains:

- `src/cockpit/observer/index.html`: static observer shell;
- `src/cockpit/observer/styles.css`: restrained technical dark presentation;
- `src/cockpit/observer/model.mjs`: normalized-field presentation,
  occurrence identity, diagnostic association, explicit activity, and
  relation display eligibility;
- `src/cockpit/observer/render.mjs`: escaped HTML/SVG renderers for the
  header, navigation, map, inspector, and diagnostics;
- `src/cockpit/observer/app.mjs`: one JSON fetch, local selection, copy
  interaction, and explicit load failure handling.

There is no backend, persistent database, authentication, write API,
Controller integration, or agent framework.

## Generated model

The normal UI input is:

```text
generated/cockpit_projection.json
```

It is ignored derived build material, not repository authority. Generate it
from an exact committed source through:

```text
python -m src.cockpit.generate_projection --repo . --source-ref HEAD --freshness-ref origin/main --output generated/cockpit_projection.json
```

The existing adapter resolves `HEAD` to an exact commit before reading. The
generator removes an older output before invoking the adapter and removes
partial output on failure, so a failed generation does not silently leave a
stale generated specimen available as current.

## Data and authority boundary

The serialized input retains all seven contracted surfaces:

```text
repository_state
pressure_nodes
pressure_relations
constraints
evidence_refs
projection_documents
projection_diagnostics
```

The first observer directly renders only:

```text
repository_state
pressure_nodes
pressure_relations
evidence_refs
projection_diagnostics
```

`constraints` and `projection_documents` remain normalized input but are
not rendered in this first specimen. The browser fetches the provided JSON and
does not fetch or parse project Markdown, JSONL, decisions, traces, projection
documents, or Git history. Evidence links are navigation references assembled
from normalized repository identity, exact source commit, and normalized
reference paths; their resolution status is not displayed as proof.

## Observer structure

The page contains:

1. repository/projection header;
2. compact current-navigation strip;
3. Pressure / Resolution Map as the primary visual object;
4. universal pressure inspector;
5. persistent global projection diagnostics.

Every `pressure_nodes` array entry becomes a separately keyed visual
occurrence. Duplicate IDs are counted and marked rather than collapsed.
Occurrence keys include array position and available occurrence provenance;
they are UI addresses, not new project identity.

Every semantic edge object originates in one `pressure_relations` entry. A
pressure-to-pressure relation is drawn only when both endpoints resolve to one
normalized occurrence. Ambiguous or condition-target relations remain visible
as unresolved relation residue rather than acquiring an invented endpoint.
Node placement is a stable array-order grid for readability and is explicitly
labeled composition rather than evidence.

The inspector keeps exact current standing separate from normalized resolution
history. It shows normalized pressure, missing discriminator, resolution,
residue, blockers, unlocks, evidence references, provenance, and locally
associated diagnostics where available.

## Interaction boundary

Implemented interaction is limited to:

- selecting and inspecting one pressure occurrence;
- following a normalized evidence reference;
- copying the selected pressure ID.

Selection changes only local foreground. It does not mutate activity,
standing, relations, the normalized model, repository state, or external
state. There is no form, editable field, mutation request, graph rewrite,
Controller invocation, experiment execution, or repo writeback.

## Failure presentation

The implementation distinguishes:

- projection `complete`, `partial`, and `failed`;
- JSON unavailable or unreadable;
- freshness `current`, `stale`, `unknown`, and missing;
- explicit none and missing navigation values;
- source conflict;
- broken evidence reference;
- unknown standing with exact retained value;
- duplicate pressure identity and ambiguous target;
- unsupported structure retained as diagnostic residue;
- diagnostics present, present-and-empty, and unavailable.

Partial and failed models render surviving normalized content with a global
wound. JSON load failure removes the normal observer surfaces and displays
`PROJECTION UNAVAILABLE`; it does not infer repository state or show a cached
clean model. Unsupported history residue remains diagnostic material and is not
promoted into resolution history.

## Synthetic rendering fixtures

Seven small fixtures under `tests/cockpit/fixtures/observer/` cover:

- partial projection plus `unsupported_structure`;
- duplicate pressure ID plus ambiguous relation target;
- source conflict;
- stale freshness;
- failed projection;
- unknown standing;
- broken evidence reference.

JSON unavailability is exercised by a failed supplied fetch. These fixtures
are synthetic rendering inputs, not repository truth or a parallel project.

## Verification

Focused frontend and generation evidence:

- Node observer tests: 15/15 passed;
- Python generator tests: 2/2 passed;
- JavaScript syntax checks: passed;
- Python generator compilation: passed.

The focused tests establish that:

- normalized JSON loads through a supplied URL without repository access;
- every pressure entry remains independently addressable;
- only normalized relation entries create semantic edge objects;
- duplicate IDs do not collapse or gain a selected target;
- explicit none remains distinct from missing;
- OPEN and UI selection do not create ACTIVE;
- current and historical standings remain separately accessible;
- diagnostics remain globally visible;
- current, stale, and unknown freshness differ;
- source conflict, unknown standing, broken evidence, unsupported structure,
  failure, and unavailability remain visible;
- the first renderer omits deferred constraints and projection documents;
- no write interaction exists;
- failed generation removes stale derived output.

Existing bounded Cockpit adapter, pressure, remediation, and re-pressure tests:
39/39 passed.

Full hardware-free Python suite: 549/549 passed.

`git diff --check` passed.

## Current repository smoke

The generator projected exact commit
`2858bdad69364b6432ea9bb360be7b3fbd80d233` and compared it with
`origin/main`. The generated model reported:

- projection `complete`;
- freshness `current`;
- active pressure `none selected`;
- PR-018 `OPEN` and inactive;
- PR-019 current `BOUNDED_RESOLUTION`;
- PR-019 R0 `BASIS_INSUFFICIENT`;
- PR-019 R1 `BOUNDED_RESOLUTION`;
- 19 pressure-node occurrences;
- 24 explicit pressure relations;
- 46 constraints retained in normalized input;
- 214 evidence references;
- three projection documents retained in normalized input;
- zero projection diagnostics.

A preinstalled headless Chrome load of the locally served observer completed
with rendered repository status, current freshness, explicit-none activity,
pressure nodes, exact standings, and zero-diagnostic text. This was a page-load
smoke only, not a visual correctness or usability result.

## Known limitations

- The stable grid is a composition baseline, not a claim of usable graph
  layout.
- Relation labels are primarily recovered through inspection; crossing lines
  have not been usability-pressured.
- Condition-target and ambiguous relations remain in explicit unresolved
  residue rather than receiving richer graph terminals.
- No zoom, pan, generalized graph navigation, search, or filtering is present.
- No Constraints, Lineage, Horizon, or SYSTEM view is implemented.
- No beautiful Observatory aesthetic or deployment automation is present.
- The page-load smoke did not automate node selection or establish accessibility,
  responsive quality, comprehension, reconstruction speed, or inference safety.
- The adapter and observer remain bounded to the current normalized contract
  and named specimens.

## Bounded adjudication

The strongest supported implementation claim is:

> The first read-only observer renders the bounded normalized Cockpit model and
> preserves the named epistemic distinctions required by the v0 page spec.

This does not establish usability success, reduced reconstruction cost, visual
semantic safety, general projection reliability, or production readiness.
Those require the next bounded observer usability and unsupported-inference
pressure.

## Stop boundary

This pass changed no Projection Adapter behavior, projection contract, Pressure
/ Resolution Map, constraint, scientific decision, trace, Controller, chart,
`D-*` constraint, or `PR-*` node. It did not begin usability pressure,
aesthetic refinement, automatic deployment, or any read-write surface.
