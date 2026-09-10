# DME Cockpit v0 Page Specification

## Status and gate

This document specifies the first implementable DME Cockpit page. It is a
design specification only. It does not implement a frontend, alter the Cockpit
Projection Adapter, widen the projection contract, or authorize mutation of
repository or external state.

UI construction remains gated on successful Stage 4C adversarial re-pressure
of the remediated Projection Adapter. The repository state from which this
specification was written records that bounded Stage 4C adjudication as
successful and permits a deliberately plain observer specimen. This document
does not independently clear or replace that gate. If the adapter or its
contract changes, current repository evidence must establish the applicable
gate again before UI construction proceeds.

The Cockpit remains:

```text
repository evidence = ultimate authority
normalized model    = derived read-only projection
Cockpit UI          = display of that projection
```

The first implementation question is:

> Does this representation reduce reconstruction cost without causing
> unsupported inference?

It is not: “Is this the final beautiful DME Observatory?”

## Product shape

The v0 product is one coherent desktop observer dashboard with deeper
inspectable surfaces. It is a personal research instrument for Reed, not a
marketing site and not a conventional collection of public-facing pages.

The page should make this recovery sequence inexpensive:

```text
WHERE AM I?
      ↓
WHAT DID REALITY LAST SAY?
      ↓
WHAT IS RESOLVED?
      ↓
WHAT IS STILL WOUNDED?
      ↓
WHAT IS REACHABLE?
      ↓
WHAT EVIDENCE WARRANTS THIS?
```

There is no About, Pricing, Solutions, Customers, Contact Sales, login, or
account surface in v0.

## Sole frontend data boundary

The only legal dynamic input to the v0 frontend is one serialized Projection
Adapter result containing these top-level surfaces:

```text
repository_state
pressure_nodes
pressure_relations
constraints
evidence_refs
projection_documents
projection_diagnostics
```

The architecture is:

```text
committed repository
→ Projection Adapter
→ normalized JSON
→ Cockpit UI
```

The following architecture is prohibited:

```text
committed repository
→ adapter JSON
→ Cockpit UI
↘ frontend independently reparses repository artifacts
```

The browser must not independently parse `PROJECT_STATE.md`,
`PRESSURE_RESOLUTION_MAP.md`, constraint JSONL, decision Markdown, projection
Markdown, or Git history. It must not fetch those artifacts to recover fields,
relations, standing, authority, or competing project truth. A source reference
may be opened for human inspection, but its contents do not feed back into the
rendered model.

The eventual frontend must be able to render a generated JSON specimen with no
repository access. Missing model content remains missing. The visual layer may
format, filter, search, order, and place normalized objects; it may not repair
or semantically supplement them.

## Desktop composition

Use one persistent observer shell. Its initial desktop composition is:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ REPOSITORY / PROJECTION HEADER                                           │
├──────────────────────────────────────────────────────────────────────────┤
│ CURRENT NAVIGATION STRIP                         DIAGNOSTIC SUMMARY       │
├───────────────────────────────────────────────────────┬──────────────────┤
│                                                       │                  │
│ PRESSURE / RESOLUTION MAP                             │ UNIVERSAL        │
│ primary visual object                                 │ INSPECTOR        │
│                                                       │                  │
├───────────────────────────────────────────────────────┴──────────────────┤
│ BOUNDED VIEW SURFACE: CONSTRAINTS / LINEAGE / HORIZON / SOURCE           │
└──────────────────────────────────────────────────────────────────────────┘
```

The lower bounded-view surface may replace or temporarily foreground the map,
but it remains inside the same observer shell. The header, current-navigation
state, and diagnostic state stay recoverable. The map is the default and
primary visual object.

## 1. Repository / projection header

The header is compact and always legible. Its dynamic content comes only from
`repository_state`:

| Display label | Normalized source |
| --- | --- |
| Repository | `repository_identity`, including its status rather than a guessed identity |
| Branch | `branch` |
| Source commit | `source_commit`; display enough characters to discriminate and expose the full value |
| Source ref | `source_ref` when useful for inspection |
| Projection class | `projection_classification` |
| Projection status | `projection_status` |
| Freshness | `freshness.status`, with its comparison ref, observed tail, and check time inspectable |
| Projection time | `projection_time` |
| Adapter version | `adapter_version` |

`DME_LAB` is the stable instrument title, not a recovered repository fact. The
repository identity beside it must retain its normalized status.

`projection_time` must be labeled **PROJECTION TIME**, never “evidence time,”
“last observed,” or “last changed.” It says when the adapter produced this
projection, not when the represented evidence occurred.

Freshness has priority over ornament:

- `current`: quiet, explicit current marker with the compared tail available;
- `stale`: persistent high-visibility wound showing source commit and observed
  tail;
- `unknown`: persistent high-visibility unknown state and available diagnostic;
- missing freshness object or fields: show **MISSING**, not `current` or
  `false`.

## 2. Current navigation strip

Render `repository_state.current_navigation` without converting openness into
activity:

| Segment | Normalized source | Required behavior |
| --- | --- | --- |
| Active pressure | `active_pressure` | Show the exact value and semantic/status fields. An explicit null with `explicit_none` renders **none selected**. Missing renders **missing**. |
| Open / reachable | `newly_reachable_open_pressures` | Show only emitted values or entries; each available pressure ID may foreground its matching node occurrence(s). |
| Shelved | `shelved_pressures` | Show only emitted values or entries and retain their status. |
| Next experimental pressure | `next_experimental_pressure` when present | Preserve explicit none separately from missing. Do not select one from open pressures. |
| Projection diagnostics | `projection_diagnostics` plus `projection_status` | Show total and highest operational severity; zero must be distinguishable from unavailable diagnostics. |

The strip must preserve:

```text
explicit none != missing
OPEN          != ACTIVE
reachable     != selected next pressure
UI selection  != active pressure
```

If active pressure is explicitly none, use approximately:

```text
ACTIVE PRESSURE
none selected
```

Selecting, hovering, centering, or inspecting an open pressure must not give it
the ACTIVE form.

## 3. Pressure / Resolution Map

The Pressure / Resolution Map is the primary v0 visual object. It renders only
`pressure_nodes` and `pressure_relations`.

### Nodes

Create one visual occurrence for every object in `pressure_nodes`. Do not
collapse the array into a dictionary keyed only by pressure ID: duplicate IDs
must remain independently visible and inspectable with occurrence-local
provenance.

The visible node minimum is:

- exact pressure ID;
- title;
- exact current standing;
- a form-based standing treatment;
- wound marker when a diagnostic affects the occurrence or one of its fields;
- history marker when `resolution_history` is non-empty;
- ambiguity marker when identity is duplicated or unique lookup is unresolved.

The node may expose pressure, missing discriminator, resolution, residue, and
relations through progressive inspection. It must not derive priority,
importance, confidence, activity, or causal centrality from the amount of text,
the number of evidence links, or graph position.

### Edges

Only objects in `pressure_relations` may create semantic graph edges. Preserve
the emitted relation kind, source pressure ID, target kind, target pressure ID
or condition text, raw source field, provenance, and any emitted resolution or
ambiguity metadata.

An explicit condition is not a pressure node. Render it as a condition terminal
or inspector relation row, not as an invented PR node.

If a target ID resolves ambiguously because multiple node occurrences carry
that ID, retain the relation and show an unresolved, branching, or interrupted
endpoint. Do not select an occurrence by file order, visual proximity, or
standing. If the model supplies no unique target, the graph supplies no unique
target.

No edge may be inferred from:

- shared terms or titles;
- similar or shared evidence;
- temporal adjacency;
- section grouping;
- Git adjacency;
- node proximity;
- visual continuity;
- likely causality.

### Layout

A layout algorithm may place nodes for readability, collision avoidance, and
viewport use. Placement is composition, not evidence. The initial layout
should favor stable, reproducible placement for the same JSON specimen so that
ordinary refreshes do not resemble semantic motion.

The map legend must include the statement:

> Position and proximity aid composition only. Relations exist only where an
> explicit normalized relation is rendered.

The earned runtime pipeline is not the map and must not replace it as the
homepage’s primary graph.

## 4. Universal pressure inspector

Selecting a pressure-node occurrence opens the universal inspector. Desktop
uses a persistent side panel; mobile uses a full-screen drawer. The inspector
keeps these sections in this order when data exists:

1. **ID / TITLE** — `id`, `title`.
2. **CURRENT STANDING** — exact `standing`, including raw/unknown status if
   represented.
3. **PRESSURE** — `pressure`.
4. **MISSING DISCRIMINATOR** — `missing_discriminator`.
5. **RESOLUTION SO FAR** — `resolution_so_far`.
6. **RESIDUE** — `residue`.
7. **BLOCKED BY** — `blocked_by` plus corresponding explicit normalized
   relations.
8. **UNLOCKS** — `unlocks` plus corresponding explicit normalized relations.
9. **RESOLUTION HISTORY** — ordered `resolution_history` entries, each with
   retained label, exact historical standing, summary, and provenance.
10. **EVIDENCE** — the node’s `evidence_ref_ids` resolved only against
    `evidence_refs`.
11. **PROVENANCE** — node and field provenance supplied by the model.
12. **DIAGNOSTICS** — diagnostics whose affected source, object, or field maps
    to this occurrence, without suppressing unmatched global diagnostics.

Current and historical standing must never collapse into a single success
summary. The required conceptual treatment is:

```text
CURRENT
BOUNDED_RESOLUTION

HISTORY
R0  BASIS_INSUFFICIENT
R1  BOUNDED_RESOLUTION
```

The R0 wound remains visible even when the current standing is bounded. If
history-like source material was retained only through an
`unsupported_structure` diagnostic, the inspector shows current standing and
the raw diagnostic residue separately. It must not promote the residue into
valid resolution history.

Evidence references are navigation, not proof badges. A `resolved` reference
means the target was resolvable under the adapter’s bounded rule; it does not
mean the target proves the displayed claim.

## 5. Constraints surface

The surface name is **CONSTRAINTS**. Do not introduce **DISTINCTIONS** or
**DISTINCTION ATLAS** as a label, object type, or navigation destination.

Render each object in `constraints` as conserved, non-authoritative
anti-collapse memory. The readable primitive is approximately:

```text
D-####

left
  relation
right

scope · basis · standing
note
provenance / evidence references
```

Expose the emitted `id`, `left`, `relation`, `right`, `scope`, `basis`,
`standing`, optional `note`, record provenance, adapter provenance, and
`evidence_ref_ids`. Preserve historical `D-*` identifiers.

The surface supports read-only search and filters over exact emitted fields.
It must preserve:

```text
constraint != local distinction event
```

It must not synthesize a distinction event, distinction history, semantic
graph, pressure direction, universal truth, or confidence measure. A malformed
registry row remains represented through diagnostics while valid neighboring
constraints remain available.

Constraints are specified here but may follow immediately after the first
plain observer rendering if the normalized surface proves straightforward.

## 6. Bounded lineage surface

The LINEAGE view answers the bounded question: **How did we get here?** It does
not claim a global causal history.

Legal v0 lineage material is limited to:

- a pressure node’s explicit `resolution_history` sequence;
- explicit objects in `pressure_relations`;
- navigable `evidence_refs` attached by normalized IDs;
- source and commit provenance already present on normalized objects.

Within a pressure node, the adapter-retained order of resolution-history
entries may be shown as declared history. Between pressure nodes, only explicit
normalized relations may connect them. Evidence references may branch to
source navigation, but reference existence is not causal or epistemic proof.

Git order must not be reconstructed by the browser or displayed as causal
dependency. When normalized data cannot establish
`pressure → experiment → result → next pressure`, render only the pieces and
relations actually available. Do not visually bridge gaps to complete the
story.

The view must state:

```text
visual continuity != causal lineage
```

## 7. Earned system surface

The desired long-term SYSTEM surface would explain the earned DME pipeline,
but the current normalized model does not emit an earned-system structure.
Therefore v0 chooses legal treatment **A: defer this surface until the adapter
explicitly projects it**.

Do not encode a pipeline diagram in frontend data, scrape it from Cockpit or
project documentation, or widen adapter scope from this specification. SYSTEM
must not appear as an enabled dynamic view in the first implementation. A
future implementation-stage decision may add it only after an authoritative
contract and normalized structure support it.

## 8. Projection horizon

HORIZON renders only `projection_documents`. It creates a conspicuous boundary:

```text
EARNED / OBSERVED TERRITORY
════════════════════════════════
PROJECTION HORIZON
════════════════════════════════
PROJECTED TERRITORY
```

Each projected document may expose only its emitted source path, title, source
commit, classification, explicit non-authority declaration, exact standing,
and provenance. The frontend must not parse the document body to build
components, relations, requirements, or state.

Projected objects use visibly weaker form than earned/observed objects and keep
their exact standing and non-authority declaration readable. Attractive
rendering does not promote projection into implementation.

Controller must remain visibly:

```text
PARKED
NON-AUTHORITATIVE
```

Displaying the Controller document does not create Controller authority,
behavior, controls, operations, or an implementation warrant.

## 9. Projection diagnostics

Diagnostics are a first-class page surface, not console output. The global
header and current-navigation strip always expose diagnostic status; a
dedicated panel exposes every object in `projection_diagnostics`.

For each diagnostic, show all available normalized fields, including:

- `kind`;
- `severity` as adapter-operational impact, not epistemic confidence;
- affected source, object, and field;
- message;
- safe retained raw value when supplied;
- provenance.

Expected kinds include `parse_failure`, `unsupported_structure`,
`missing_required_source`, `broken_reference`, `unknown_standing`,
`source_conflict`, `stale_projection_basis`, and
`duplicate_pressure_id`. The renderer must tolerate other exact kinds without
mapping them to a familiar category or dropping them.

When diagnostics exist, the page is visibly wounded. This requires all three:

- a persistent global interruption in the header/strip;
- a count and severity summary leading to the diagnostic panel;
- local wound marks on affected objects when association is available.

A clean-looking map with hidden diagnostics violates this specification.
Zero diagnostics may be shown as **0 reported** only when a valid
`projection_diagnostics` array is present. Missing or unreadable diagnostics
are **unavailable**, not zero.

## Visual semantic grammar

Semantics are defined before aesthetics. Color may reinforce a state but never
carry it alone. Exact standing text remains visible on the node or immediately
inspectable.

| Represented condition | Required form | Source boundary |
| --- | --- | --- |
| Bounded / earned standing explicitly mapped by the implementation | Solid, stable boundary | Exact normalized standing remains visible; no substring or nearest-status inference. |
| ACTIVE | Solid center with restrained motion | Only when `current_navigation.active_pressure` explicitly establishes activity. |
| OPEN | Open or incomplete boundary | Exact normalized standing. OPEN does not imply ACTIVE. |
| `BASIS_INSUFFICIENT` | Visible interruption or missing-coordinate form | Exact normalized standing or exact history entry. |
| `CANDIDATE_SURVIVED` | Solid inner structure with unresolved exterior | Exact normalized standing or history entry. |
| Projected document | Thin, ghosted, or dashed boundary beyond the horizon | `projection_documents[].classification` and explicit non-authority. |
| Historical entry | Reduced prominence but fully recoverable | Membership in `resolution_history`, not a guessed standing. |
| Diagnostic / wounded | Structural interruption plus textual marker | An emitted diagnostic or unavailable model state. |
| Unknown standing | Neutral interrupted form plus exact raw text | Exact unknown value; never nearest-known substitution. |

Other exact standings receive a neutral legible form until a documented visual
mapping is established. Do not infer semantics from token spelling alone.

No numerical confidence encoding is permitted. Do not invent percentages,
coherence scores, resolution scores, progress meters, or implied scalar ranking
among incomparable pressures.

### Geometry rule

> Visual geometry may not silently establish a relation absent from the
> normalized model.

Therefore:

```text
node proximity    != relation strength
node size         != importance
brightness        != truth
central placement != causal centrality
animation         != activity
```

A visual variable may carry semantic meaning only when it maps to an explicit
normalized field and that mapping appears in the page legend or inspector.
Otherwise it is composition only.

## Aesthetic direction

After usefulness survives, move toward:

```text
pearlescent scientific instrument
× astronomical atlas
× oscilloscope
× restrained sacred geometry
× brutal epistemic typography
```

Prefer a deep neutral background, large negative space, fine coordinate fields,
subtle chromatic refraction, thin relational traces, restrained luminous
structure, excellent explanatory typography, monospace identifiers/evidence,
quiet semantically justified motion, and austere evidence panels.

Avoid generic SaaS cards, crypto-dashboard styling, random neon cyberpunk,
glowing AI orbs, decorative complexity, fake realtime telemetry, gamification,
gratuitous 3D, and meaningless animation.

Beauty should increase inspectability. It must not increase apparent certainty.
The first implementation deliberately does not attempt this full aesthetic.

## Read-only interaction model

Permitted interactions are:

- select or inspect a normalized object;
- search and filter exact emitted fields;
- zoom and pan the map;
- follow an explicit normalized relation;
- follow an evidence reference;
- open a source reference for human inspection;
- switch among bounded views;
- close, pin, or resize an inspector locally;
- copy identifiers, standing text, commits, and source references.

Selection changes foreground only. Local viewport, filter, and panel state are
not repository or research state.

Do not implement editing, drag-to-rewrite graph behavior, new-pressure
creation, constraint creation, agent controls, experiment execution, Controller
invocation, mutation APIs, or write-back.

## View vocabulary

Use the smallest vocabulary supported by normalized data:

- **MAP** — primary pressure/resolution view;
- **CONSTRAINTS** — normalized constraint browser;
- **LINEAGE** — bounded explicit history/relation view;
- **HORIZON** — normalized projection documents beyond the visible boundary;
- **SOURCE** — evidence-reference and provenance inspection.

SYSTEM is withheld until an earned-system structure is explicitly normalized.
FRONTIER is not a separate destination; current navigation remains visible in
the observer shell. DISTINCTIONS and DISTINCTION ATLAS are prohibited labels.

These are modes of one dashboard, not independent sites with separate truth.
Views change foreground emphasis; they do not rewrite standing.

## Failure presentation

The visual layer reports failure and surviving content; it never repairs the
model.

| Condition | Page behavior |
| --- | --- |
| Projection `complete` | Render all supplied surfaces; show the exact status. Complete does not mean empirically true or generally reliable. |
| Projection `partial` | Render surviving normalized surfaces, keep a persistent wounded state, open diagnostics readily, and mark unavailable surfaces or fields. |
| Projection `failed` | Render a failure shell and diagnostics that are present. Do not present an older clean model as current. |
| JSON unavailable or unreadable | Show **PROJECTION UNAVAILABLE** with the load failure. Do not infer repository state and do not silently use cache. |
| Freshness `current` | Show exact source commit and observed tail; do not call evidence itself current. |
| Freshness `stale` | Prominent persistent stale boundary with both commits. An older projection may remain inspectable only as explicitly stale. |
| Freshness `unknown` or missing | Prominent unknown boundary. Do not infer current from successful page load or recent projection time. |
| `source_conflict` | Preserve all emitted competing values and provenance; show no selected winner unless the model explicitly supplies one. |
| Broken evidence | Keep the reference inspectable with broken status; do not drop it or show a proof/verified badge. |
| Unknown standing | Show exact raw standing with unknown form and diagnostic; do not coerce it. |
| Duplicate pressure identity | Keep every occurrence, mark lookup ambiguity, and avoid an invented canonical node. |
| Unsupported structure | Preserve supplied raw residue and wound location; do not parse it in the browser. |
| Unsupported history residue | Current standing may render; incomplete historical representation remains visibly wounded and separate from valid history. |

Cached data, if a later deployment adds caching, may be shown only with its own
source commit and explicit stale/unavailable status. It must never substitute
silently for a failed current projection.

## Responsive scope

Design desktop first. Mobile uses the same information architecture:

- header and diagnostic wound remain at the top;
- current navigation becomes a horizontally scrollable or stacked compact
  strip without changing semantics;
- map and bounded list share the foreground;
- universal inspector becomes a full-screen drawer;
- view vocabulary remains unchanged;
- dense provenance and history sections collapse visually but remain
  recoverable;
- no desktop-only relation is replaced by inferred mobile grouping.

Do not build a separate mobile truth surface or optimize the first
implementation around mobile.

## First implementation scope

After the Stage 4C gate is established by current repository evidence, the
first implemented UI is a deliberately plain observer specimen containing only:

1. repository/projection header;
2. current-navigation strip;
3. Pressure / Resolution Map;
4. universal pressure inspector;
5. first-class diagnostic visibility.

Its normalized JSON input still contains all seven top-level contract surfaces.
The first renderer directly uses `repository_state`, `pressure_nodes`,
`pressure_relations`, `evidence_refs`, and `projection_diagnostics`.
`constraints` and `projection_documents` remain valid normalized input and are
specified for the next bounded surfaces; they need not render in the first
commit. No frontend repository parsing is permitted to compensate for a
deferred surface.

Constraints may be added immediately afterward if the normalized data proves
straightforward. Lineage and Horizon remain specified but may be deferred.
SYSTEM remains deferred until the adapter explicitly projects an earned-system
structure.

The implementation progression is:

```text
normalized model
→ plain observer
→ usability / inference pressure
→ semantic visual grammar
→ richer Cockpit surfaces
→ aesthetic refinement
→ automatic deployment
```

Do not begin with the fully stylized pearlescent observatory.

## Technical implementation boundary

This specification does not choose a frontend framework. Framework and static
hosting choices belong to the implementation stage because the repository does
not currently force them.

The desired deployment shape is:

```text
push main
→ run adapter against the exact commit
→ generate normalized JSON
→ build frontend from that JSON
→ publish static Cockpit
```

V0 requires no persistent database, write backend, or API server. Introduce
none unless later deployment pressure forces it.

The build must bind visible source commit and freshness information to the
exact JSON specimen it consumes. A successful frontend build is not evidence
that projection parsing succeeded; `projection_status` and diagnostics still
govern the visible operational state.

## Acceptance checks for the first UI warrant

A later implementation may be called conformant to this page specification
only if all of the following hold:

- the Pressure / Resolution Map is the default primary visual object;
- the frontend loads one adapter JSON specimen and needs no repository access;
- all graph edges originate in `pressure_relations`;
- explicit none, missing, OPEN, ACTIVE, and selection remain distinct;
- current standing and resolution history remain separate and inspectable;
- duplicate pressure occurrences remain independent and ambiguous lookup is
  visible;
- evidence references navigate without becoming proof badges;
- diagnostics are globally persistent, locally associated when possible, and
  never console-only;
- stale and unknown freshness are prominent;
- projection documents remain beyond an explicit horizon;
- Controller is visibly parked and non-authoritative;
- the surface is named CONSTRAINTS and no Distinction Atlas is introduced;
- geometry and animation create no undocumented semantic relation;
- all interactions are read-only;
- the Stage 4C gate is checked from current repository evidence;
- no UI action changes repository or project standing.

The page succeeds when a competent user can recover where the Lab is, what is
open, resolved, wounded, evidenced, projected, stale, or conflicted faster than
manual reconstruction—without the page inventing new DME semantics, parsing,
authority rules, graph relations, standing categories, or Controller behavior.
