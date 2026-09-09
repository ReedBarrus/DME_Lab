# DME Cockpit Projection Contract v0

## Status and Scope

This is the bounded projection contract for the first DME Cockpit.

It defines the boundary between committed DME_Lab repository state and a
derived, read-only normalized model suitable for later display. It does not
implement the adapter or the website, establish empirical standing, supersede
repository evidence, or authorize project mutation.

The contract is intentionally smaller than the full Cockpit design. A later
adapter may implement only the surfaces declared here and must expose what it
cannot parse.

## Governing Principle

> Normalization may reorganize information, but it may not silently strengthen
> it.

The projection must preserve epistemic standing:

```text
OPEN                 -> OPEN
BASIS_INSUFFICIENT   -> BASIS_INSUFFICIENT
missing              -> missing
unknown              -> unknown
conflict             -> conflict
broken evidence link -> broken evidence link
```

It must not perform these substitutions:

```text
missing              -> false
unknown standing     -> nearest known standing
conflicting surfaces -> silently selected winner
absence of evidence  -> negative evidence
derived relation     -> causal relation
repository adjacency -> causal lineage
projection           -> authority
```

Copied text may be trimmed or structurally separated only when its meaning and
source remain recoverable. Display-friendly labels must not replace exact
source values.

## Authority and Transformation Boundary

The Cockpit reads committed repository artifacts. The repository remains the
authority; neither the normalized model nor its display is a second authority.

```text
authoritative repository artifact
-> deterministic parse
-> normalized derived object
-> Cockpit display projection
```

Each step must retain recoverable lineage to the artifact and source commit.
Parsing does not make the parsed representation authoritative. Normalization
does not establish a new claim. Display does not change standing.

Existing repository authority rules continue to apply. In particular:

- current committed repository evidence outranks a derived summary or map;
- `PROJECT_STATE.md` is fast-entry working memory, not evidence for itself;
- `PRESSURE_RESOLUTION_MAP.md` is derived navigation and explicitly defers to
  the decisions, traces, tests, and repository state it cites;
- contracts state bounded design or maturity claims only within their declared
  scope;
- projection documents remain non-authoritative projections;
- the constraint registry is non-authoritative constraint memory;
- contradictory or stronger committed evidence wins only where an existing
  repository rule actually establishes that result.

When parsed repository surfaces disagree, the adapter must retain the
conflicting values and their provenance, emit a conflict diagnostic, and apply
only an explicit existing authority rule. If no such rule yields an answer,
the normalized value remains conflicting or unresolved.

Conversation is not a Cockpit source. DME_Theory may provide lineage outside
this contract but is not Cockpit authority.

## Permitted v0 Source Surface

The adapter is allowlist-based. File presence alone does not authorize
semantic extraction.

### Required v0 sources

| Source | Permitted use |
| --- | --- |
| `PROJECT_STATE.md` | Parse explicitly labeled current project and development standing needed by the current-state surface; retain the source section. |
| `PRESSURE_RESOLUTION_MAP.md` | Parse current navigation, pressure nodes, explicit pressure relations, evidence links, and explicit resolution-history entries. |
| `docs/constraints/registry.jsonl` | Parse one constraint record per JSONL line using the record's actual fields. |
| `docs/constraints/README.md` | Supply the declared constraint-registry role, field meaning, standing vocabulary, and constraint/local-distinction boundary. |
| Git repository metadata | Identify repository, branch, source commit, adapter version or build revision where available, and freshness-check basis. |

A missing required source produces a visible `missing_required_source`
diagnostic and a partial or failed projection. It must not be replaced with a
cached or inferred value without labeling that older basis explicitly.

### Permitted bounded supporting sources

These sources may be read only for the stated use:

- paths explicitly referenced by a parsed pressure node or constraint may be
  checked for existence and exposed as evidence navigation targets;
- `docs/projection/Controller.md`, `docs/projection/Persistent_Ecology.md`, and
  `docs/projection/Persistent_Research_Autonomy.md` may be indexed as projection
  documents with their explicit status and source path;
- `docs/cockpit/README.md` and this contract may be exposed as Cockpit design
  documentation, not project evidence;
- selected files in `docs/contracts/` may later populate an earned-system or
  contract-maturity view, but only after the adapter declares an explicit
  allowlist and parser for their headings and status vocabulary;
- decision, trace, test, contract, and commit targets explicitly named by
  evidence references may be classified by target kind and checked for link
  resolution without treating their contents as validation of the referring
  claim.

### Optional or future sources

- additional `docs/decisions/*` semantic fields;
- additional `docs/projection/*` documents;
- selected trace summaries;
- selected test identifiers and outcomes;
- selected implementation structure;
- richer Git lineage beyond the declared build basis.

Each addition requires an explicit parser boundary and provenance rule. This
contract does not permit arbitrary semantic scraping of the repository, full
Git history reconstruction, or inference from incidental filenames or prose.

## Normalized Model Boundary

The v0 model contains only these top-level surfaces:

```text
repository_state
pressure_nodes
pressure_relations
constraints
evidence_refs
projection_documents
projection_diagnostics
```

The serialized container format remains an implementation choice. These names
describe contract surfaces, not a universal schema or ontology.

Meaningful normalized objects carry provenance sufficient to answer, "Where
did this come from?" The minimum provenance shape is:

```text
source_path
source_commit
source_kind
source_anchor  # section, line, JSONL record, or other stable locator when feasible
```

`source_anchor` may be missing when the source format supplies no stable
anchor. The adapter must not invent one merely for completeness.

Where a field can be absent, malformed, unknown, or conflicting, the object
must preserve the value, its status, its source, and relevant diagnostics.
This is a local representation discipline, not a universal value algebra.

## Repository State

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Identify the exact repository and projection basis and expose only explicitly declared current-state fields. |
| Sources | Git metadata; bounded current-standing sections of `PROJECT_STATE.md`; current-navigation fields of `PRESSURE_RESOLUTION_MAP.md`. |
| Copied or normalized | Repository identity, branch, source commit, projection/build time, adapter version when available, declared active pressure, and explicitly declared current/open standing summaries. Exact status tokens remain available. |
| Derived | Freshness status only from an explicit comparison between `source_commit` and an observed repository tail, with comparison time and observed tail retained. Counts may be derived only from successfully parsed objects and must state their basis. |
| Prohibited inference | Current external state, source freshness from process freshness, active pressure from `OPEN`, next-pressure selection, empirical standing from `PROJECT_STATE.md`, or authority from the projection build. |
| Missingness | Missing Git fields, missing current-standing sections, and unavailable freshness checks remain missing or unknown with diagnostics. |
| Provenance | Every source-derived field retains its source path or Git query kind, source commit, and source anchor where feasible. |

`projection_time` describes when the projection was produced. It is not an
observation time for the represented evidence.

## Pressure Nodes

`PRESSURE_RESOLUTION_MAP.md` is the sole v0 structural source for pressure
nodes. The map remains derived and is never evidence for itself.

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Preserve the map's bounded navigation without creating research authority. |
| Sources | One explicitly headed `PR-*` node and any explicitly headed resolution-history subsection in `PRESSURE_RESOLUTION_MAP.md`. |
| Copied or normalized | Pressure ID, title, pressure statement, exact standing, missing discriminator, resolution so far, residue, blocked-by entries, unlocks entries, evidence references, and resolution history where present. |
| Derived | Stable display labels, section grouping, and relation objects copied from explicit `Blocked by` or `Unlocks` fields. Derived values must point back to the exact node field. |
| Prohibited inference | Active status from `OPEN`, missing relations from prose adjacency, causal lineage, next-pressure selection, unstated blockers or unlocks, generalized dependencies, or empirical truth from map presence. |
| Missingness | An em dash or explicitly absent relation is preserved as absent, not false and not an inferred empty dependency claim. A missing required node field is missing or malformed, never filled from a neighboring node. |
| Provenance | The node and each history entry retain map path, source commit, and node/history heading anchor. Evidence links retain their own source anchor. |

### Standing and activation

`OPEN` means reachable or open. It does not mean `ACTIVE`. A pressure becomes
active only when an authoritative source explicitly marks it active. Rendering,
selection, hover, or graph position cannot activate it.

An unrecognized standing token is preserved verbatim with status
`unknown_standing`. It must not be mapped to the closest known standing.

### Explicit relations only

`blocked_by` and `unlocks` may contain either a pressure ID or declared textual
condition. The adapter must preserve that distinction. It may create a
pressure-to-pressure relation only when the map explicitly names a pressure ID
in the corresponding field.

An em dash means no relation is established by the map. It must not become a
negative claim that no dependency exists.

### Resolution history

Current standing and resolution history are separate fields. A history entry
contains at least its retained label, exact historical standing, summary, and
provenance. A historical result never overwrites the current standing, and the
current standing never erases a failed or insufficient prior specimen.

For example, a node may currently retain `BOUNDED_RESOLUTION` while an R0 entry
retains `BASIS_INSUFFICIENT`. Both must remain inspectable without being merged
into a single cleaned status.

## Pressure Relations

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Provide renderable edges for relations the map explicitly states. |
| Sources | Parsed `Blocked by` and `Unlocks` fields only. |
| Copied or normalized | Relation kind, source pressure ID, target pressure ID or declared condition text, and exact source field. |
| Derived | Reciprocal navigation may be displayed only as a derived view and must name the one explicit source relation from which it came. It must not be written back as another asserted map relation. |
| Prohibited inference | Relations from file order, section membership, shared evidence, matching words, temporal adjacency, Git adjacency, or likely causality. |
| Missingness | Absent or em-dash relations remain absent; unresolved target IDs remain unresolved references. |
| Provenance | Map path, source commit, node anchor, and exact relation field are required. |

## Constraints

`docs/constraints/registry.jsonl` is the record source. Its README defines the
registry's current non-authoritative role and vocabulary.

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Expose reusable scoped limits on admissible equivalence or inference. |
| Sources | One JSONL record in `docs/constraints/registry.jsonl`, interpreted under `docs/constraints/README.md`. |
| Copied or normalized | Historical `D-*` identifier, `left`, `relation`, `right`, `scope`, `basis`, `provenance`, `standing`, and `note` when present. |
| Derived | Display labels and resolvable evidence-reference objects for provenance entries. |
| Prohibited inference | Universal truth, confidence score, active requirement, pressure direction, dependency edges to every mentioned concept, or a persistent local distinction event. |
| Missingness | Missing required record fields and malformed JSONL lines remain visible diagnostics; valid neighboring records remain independently projectable. An absent optional note remains absent. |
| Provenance | Registry path, source commit, JSONL line or record anchor, and the record's own provenance list are preserved separately. |

The contract preserves:

```text
constraint != local distinction event
```

A constraint may be linked to evidence where it was applied. The adapter must
not synthesize a distinction object, distinction store, dependency graph, or
new registry entry from that relationship.

## Evidence References

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Support navigation from a represented claim or object toward a committed evidence surface. |
| Sources | Explicit links or provenance paths in permitted parsed sources. |
| Copied or normalized | Original target, label when present, referring object, inferred target kind only from a bounded path/URL rule, and source location of the reference. |
| Derived | Link-resolution status at the declared source commit: resolved, broken, external-unchecked, or unsupported. |
| Prohibited inference | That a resolved link proves, validates, uniquely supports, or remains sufficient for the displaying claim. |
| Missingness | A missing target remains unresolved; a nonexistent committed path remains `broken_reference` and is not dropped. |
| Provenance | Referring source path, source commit, source anchor, original target text, and any checked target path are retained. |

```text
reference exists != referenced evidence validates the displaying claim
link resolution  != epistemic warrant
```

The adapter may report whether a path exists at the source commit. It may not
adjudicate the evidence merely because it can open the file.

## Projection Documents

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Make declared future or speculative surfaces navigable beyond the evidence horizon without presenting them as earned. |
| Sources | Only explicitly allowlisted documents under `docs/projection/`. |
| Copied or normalized | Source path, title, explicit projection status or standing, explicit non-authority boundary, and short descriptive metadata if a bounded parser supports it. |
| Derived | A fixed classification such as `projection_document`, based on allowlist membership plus the document's explicit projection declaration. |
| Prohibited inference | Implemented components, runtime state, earned architecture, authorized work, causal graph, or executable operations from speculative diagrams or prose. |
| Missingness | Missing or unparseable status remains unknown with a diagnostic; projection classification does not supply a guessed standing. |
| Provenance | Source path, source commit, title/status anchor, and parser version are retained. |

The parked Controller may therefore appear as a projection document whose
exact standing is `PARKED`. Nothing described inside it becomes Controller
state, an implementation requirement, or action authority.

## Projection Diagnostics

| Contract aspect | Requirement |
| --- | --- |
| Purpose | Keep source and projection failures visible without repairing them through guesswork. |
| Sources | Parser, normalization, link-resolution, conflict, and freshness checks. |
| Copied or normalized | Diagnostic kind, affected source/object/field, observed raw value where safe, message, severity as adapter-operational impact rather than epistemic confidence, and provenance. |
| Derived | Partial-versus-failed projection status from declared required-source and parser rules. |
| Prohibited inference | Empirical falsity, negative evidence, source corruption, claim invalidity, or a repaired value solely from adapter failure. |
| Missingness | A diagnostic with unavailable detail retains that missing detail; diagnostics themselves must not be silently suppressed. |
| Provenance | Source path or Git query, source commit, source anchor where feasible, adapter version, and check kind. |

Expected diagnostic classes include:

- `parse_failure`
- `unsupported_structure`
- `missing_required_source`
- `broken_reference`
- `unknown_standing`
- `source_conflict`
- `stale_projection_basis`

Names may change during implementation. Their observable failure semantics may
not disappear.

### Missingness behavior

- Missing field: preserve missing at that field and diagnose when required.
- Missing source artifact: preserve the absent source and mark the projection
  partial or failed according to its required status.
- Malformed field: retain the raw value where safe, do not substitute a clean
  value, and emit `parse_failure` or `unsupported_structure`.
- Unknown standing: retain the exact token and emit `unknown_standing`.
- Unresolved evidence reference: retain the reference and its unresolved
  status.
- Parser error: retain the affected source boundary and emit a diagnostic;
  do not reuse an older result as current.
- Conflicting source values: retain all conflicting values with provenance and
  emit `source_conflict`.
- Unsupported artifact structure: expose the artifact as unsupported rather
  than scraping likely-looking prose.

## Freshness Basis

Every projection must expose at least:

- repository identity;
- branch;
- source commit;
- projection/build time;
- adapter version or build revision when available.

```text
source commit != current repository tail
projection time != evidence observation time
```

A projection built from commit X remains a projection of X after the branch
advances. It may be called current only after a recorded freshness check shows
that its `source_commit` equals the observed tail for the declared repository
and branch. A failed or unavailable check leaves freshness unknown. An older
projection must be labeled stale when the check demonstrates a newer tail.

## Determinism

Given the same declared repository source state and the same adapter version,
the normalized projection output should be deterministic except for explicitly
excluded runtime metadata such as projection time and freshness-check time.

Ordering rules, parser versions, allowlists, and derivations must be explicit
enough that repeated builds do not silently select different values. This is a
contract expectation only; no adapter is implemented here.

## Display Boundary

```text
normalized model != visual representation
```

CSS, layout, graph position, animation, color, typography, filtering, and
interaction do not alter project standing. Exact textual standing and source
provenance remain inspectable.

A node appearing closer to another node is not evidence of a stronger relation
unless position is explicitly derived from a declared normalized field and the
display says so. Decorative or force-directed adjacency must never be
presented as causal, temporal, or dependency structure.

## Cockpit and Controller Boundary

The Cockpit projection is read-only. The normalized model contains no
executable action authority.

It must not contain:

- command invocation;
- mutation endpoints;
- agent control;
- authorization tokens;
- Controller operations;
- write-back fields.

The Controller remains a parked, non-authoritative projection. Indexing its
document does not reopen it.

## Illustrative Contract Pressures

These are documentation examples, not executable fixtures or new repository
evidence.

| Case | Source condition | Expected normalized behavior |
| --- | --- | --- |
| Normal bounded pressure | A map node declares `BOUNDED_RESOLUTION` with residue and evidence links. | Preserve the exact standing, residue, links, and node provenance; do not upgrade it to universal resolution. |
| Resolution history | A node currently declares `BOUNDED_RESOLUTION`; R0 declares `BASIS_INSUFFICIENT`; R1 declares `BOUNDED_RESOLUTION`. | Keep current standing and both ordered history entries separately. The PR-019 shape is a current repository example, not a hard-coded special case. |
| Absent relation | `Blocked by` or `Unlocks` is an em dash. | Preserve an absent relation with its source field; create no graph edge and no negative dependency claim. |
| Unknown standing | A node contains an unrecognized token. | Preserve the token, mark `unknown_standing`, and do not choose a nearby enum. |
| Broken evidence reference | A parsed link targets no path at the source commit. | Keep the link, mark `broken_reference`, and make no claim about the referring node's truth. |
| Conflicting source surface | Parsed current-standing fields disagree. | Preserve both values and provenance, emit `source_conflict`, and apply only an explicit repository authority rule; otherwise leave unresolved. |
| Projected document | An allowlisted document explicitly declares itself non-authoritative and `PARKED`. | Classify it as a projection document, preserve `PARKED`, and extract no implemented state or action authority from its speculative contents. |
| Malformed input | A constraint JSONL line is invalid or a required map field cannot be parsed. | Emit a diagnostic, preserve the raw boundary where safe, project unaffected valid records, and never invent the missing value. |

## Schema Decision

No JSON Schema is created in this pass.

The current repository uses a shadow-only schema where executable ledger
pressure justified one. No equivalent adapter or fixture pressure yet forces a
machine schema for the Cockpit model. Markdown remains sufficient to define
the bounded semantic boundary; a small descriptive schema is deferred until
adapter implementation reveals an ambiguity that executable checks need to
hold stable.

## Non-Goals

This contract does not authorize or define:

- generalized semantic extraction;
- inferred causal graphs;
- automatic next-pressure selection;
- confidence scoring;
- a generalized ontology;
- a generalized basis engine;
- automatic constraint application;
- local distinction-event generation;
- runtime telemetry synthesis;
- Controller or action integration;
- agent orchestration;
- a persistent database;
- a world-state or runtime world model;
- morphogenetic HTML or executable-document behavior;
- a generalized graph engine;
- arbitrary repository scraping;
- adapter, frontend, or website implementation.

## Success Criterion

The later adapter should make this path unambiguous:

```text
repository evidence
-> deterministic parse
-> bounded normalization
-> explicit diagnostics
-> recoverable provenance
-> read-only projection
```

while preserving:

- what is known;
- what is unresolved;
- what is missing;
- what is projected;
- what failed to parse;
- where each represented claim came from.

If the adapter cannot preserve one of those boundaries, it should produce a
visible partial or failed projection rather than a cleaner claim.
