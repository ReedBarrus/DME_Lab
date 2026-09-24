# Operative Surface Map

Primary current map of **what DME_Lab can actually do, where it lives, what
authority it has, and what risk it carries**.

This file is a navigation and development-control projection. It does not
promote candidate machinery or create scientific standing. If this map
conflicts with implementation, policy, tests, adjudicated evidence, or
PROJECT_STATE.md, repair this map.

## State vocabulary

- **LIVE** — current governing / active surface.
- **OPERABLE_V0** — implemented and usable inside a bounded declared regime.
- **QUALIFIED_BOUNDED** — survived the named tested scope; not generalized.
- **CANDIDATE** — addressable / inspectable but not admitted as authoritative.
- **PARKED** — retained but intentionally non-authoritative.
- **UNAUTHORIZED** — capability may be imaginable or partially implemented but
  is not permitted for operational use.

## Operative surfaces

| Surface | Repository location | Current state | Main leverage | Current authority / access | Primary risk / limitation |
|---|---|---|---|---|---|
| Project-state projection | `PROJECT_STATE.md` | LIVE projection | Fast current-standing recovery | Read-only descriptive projection | Can become stale; projection != evidence |
| Development pressure map | `DEVELOPMENT_PRESSURE_MAP.md` | ACTIVE_CONSTRUCTION | Navigates development questions | No execution authority | Map != resolution |
| Scientific pressure map | `PRESSURE_RESOLUTION_MAP.md` | LIVE navigation | Navigates open scientific questions | No execution authority | Map != evidence/adjudication |
| Repository capture / ingest / ledger / replay / reconstruction / projection | `src/capture/`, runtime/projection surfaces | OPERABLE_V0 in declared regimes | Reconstructable repository-state lineage | Bounded repository observation only | Not generalized OS/world observation |
| Cockpit projection / observer | `src/cockpit/` | OPERABLE_V0 / bounded projection | Human-readable navigation and read-only observation | No scientific admission or external action authority | Projection can be mistaken for source truth |
| Action surface | `src/cockpit/action_surface.py`, `docs/candidates/action_surface_v0/` | CANDIDATE / bounded implementation | Explicit action representation | Not generalized execution authority | Representation/action boundary must stay explicit |
| Continuity tooling | `tools/continuity.py` and continuity artifacts | OPERABLE/CANDIDATE by sub-surface | Continuity inspection and reconstruction support | Local bounded tooling | Must not be treated as generalized memory |
| Branch registry | `tools/branch_registry.py` | OPERABLE_V0 | Durable addressed branch/participant bookkeeping | Registry semantics only | Registration != truth/authority |
| Lab conductor | `tools/lab_conductor.py` | BOUNDED LOCAL TOOL | Coordinates declared lab operations | Local process/tool scope only | Conductor != autonomous governance |
| Labboib seat utility | `tools/labboib_seat.py` | BOUNDED / EXPERIMENTAL | Seat-specific local workflow support | No generalized seat authority | Seat utility != formal seat standing |
| Two-lane coordination | `tools/two_lane_coordination_v0.py`, `v1.py` | BOUNDED / EXPERIMENTAL | Pressure on lane coordination | Declared test scope only | Coordination result != generic multi-seat regime |
| Lifecycle disposition apparatus | `tools/lane_lifecycle_disposition_v0.py`, oracle/pressure tools | QUALIFIED in tested cells | Tests lifecycle state / disposition laws | Test apparatus only | Apparatus law scope is bounded |
| Succession / fencing apparatus | `tools/legacy_lane_succession_fencing_v0.py`, successor engagement tools | EXPERIMENTAL / BOUNDED | Pressures predecessor/successor continuity and anti-zombie behavior | No generalized actor authority | Temporal succession != lawful authority succession |
| Local LM Studio bridge | `tools/local_lmstudio_bridge_v0.py` | OPERABLE_V0 transport | Fresh local model invocations from immutable Git-addressed requests | Localhost model call only; no model tools/repo/network/connectors; human `y` required | Referenced evidence is not automatically delivered to model; result publication is manual |
| LM Studio bridge policy | `bridge/policy_v0.json` | LIVE V0 policy | Hard bounds on models, prompt prefixes, size, temperature, tokens, authorization | Human approval required; result push disabled | Policy change is authority-relevant |
| Bridge request queue | `bridge/requests/` | OPERABLE_V0 | Declarative invocation proposals | Proposal only; remote request != local authorization | Duplicate/replay semantics still need pressure |
| Bridge result witnesses | `bridge/results/` | OPERABLE_V0 local witness | Binds request, prompt hash, model, request/response hashes, timestamps, assistant text | Local result only; no automatic Atlas settlement | Witness != scientific standing; local file not auto-published |
| Atlas planner-seat contract | `docs/campaigns/semantic_continuity_operative_atlas_001/ATLAS_RELATIONAL_HORIZON_PLANNER_SEAT_CANDIDATE_V0.md` | CANDIDATE; contract fidelity qualified in tested scope | Bounded horizon reconstruction / next-pressure proposal | No execution, routing, or formal seat authority | Planner output != admitted topology |
| Atlas planner state frames | `docs/campaigns/semantic_continuity_operative_atlas_001/ATLAS_PLANNER_STATE_FRAME_*.md` | CANDIDATE state-carrier family; continuity qualified boundedly | Carries target, trajectory, horizon, unresolved load across fresh occupants | Environmental state only | State frame != persistent occupant identity |
| Atlas planner continuity | `ATLAS_PLANNER_CONTINUITY_QUALIFIED_V0.md` | QUALIFIED_BOUNDED | Fresh occupant can recover bounded planner state without chat memory | No autonomy / no formal seat admission | Tested specimen family only |
| Metabolic compression cells | `ATLAS_METABOLIC_COMPRESSION_CELL_*` | Cell 001 QUALIFIED_BOUNDED; later variants experimental | Tests representation reduction while preserving consequence-bearing relations | No automatic compression/admission | Compression success is specimen-local |
| Authority membrane candidates | `docs/campaigns/authority_membrane_security_001/` and bounded candidates | EXPERIMENTAL / CANDIDATE | Pressure on approval, consumption, invocation, fencing | Not yet generalized as live system membrane | Highest-risk future surface; authority ≠ evidence |
| Execution stop / latch candidate | `lab/ops/candidates/execution_stop_latch_001/` | CANDIDATE | Future bounded stop semantics | Not generalized run/stop control | STOP != state destruction; requires pressure |
| Primary ecology / coordination prototypes | `tools/primary_ecology_v0.py` and related campaign artifacts | EXPERIMENTAL | Tests ecology/coordination structures | No autonomous ecology standing | Easy to over-read as autonomy |
| External write / CLI / network authority for model seats | none admitted | UNAUTHORIZED | Future developmental leverage | NONE | High consequence surface; requires membrane, warrants, logging, replay resistance, stop control |
| Automatic result publication | bridge policy currently disables | UNAUTHORIZED | Could reduce human transport | NONE | Publication is a distinct authority edge |
| Autonomous scheduling / heartbeat / clock-driven execution | no admitted generalized surface | UNAUTHORIZED | Future active-loop leverage | NONE | CLOCK != AUTHORITY; heartbeat != permission |
| Multi-seat autonomous regime | no admitted generalized surface | UNAUTHORIZED | Future parallelized development/science | NONE | Requires stable single-seat lifecycle + membrane + coordination pressure |

## Local LM Studio bridge: exact current contract

Current V0 flow:

```text
REMOTE DECLARATIVE REQUEST
→ bridge fetches fixed branch
→ immutable source_ref + input_path + input_sha256 check
→ local human approval
→ one LM Studio chat-completion invocation
→ local witnessed JSON result
```

Current model-visible capabilities:

```text
prompt text supplied by bridge
+
model weights / local inference
```

Explicitly absent:

```text
repo access
filesystem access
tools
connectors
network
previous-response state
automatic result publication
execution authority
```

Important current wound:

```text
PACKET REFERENCES EVIDENCE FILES
!=
MODEL RECEIVES THOSE EVIDENCE FILES
```

Self-contained packets work. Reference-only adjudication packets do not yet
work through the bridge unless the referenced evidence is assembled into the
model-visible prompt first.

## Near-term bridge evolution

The next useful bridge layer is a **bounded evidence-bundle assembler**, not
general repository access.

Target:

```text
manifest
→ exact evidence coordinates
→ bridge resolves immutable blobs
→ verifies identities
→ assembles deterministic evidence bundle
→ hashes final bundle
→ human approves
→ model receives only that bundle
→ result witness binds bundle hash
```

This would provide modular evidence leverage while preserving:

```text
EVIDENCE ACCESS
!=
REPOSITORY ACCESS

MODEL COGNITION
!=
OPERATIVE AUTHORITY
```

## Single-seat stabilization horizon

Before multi-seat or autonomous regimes, pressure until boring:

1. state recovery;
2. target / trajectory / horizon continuity;
3. qualified-vs-candidate separation;
4. bounded next-pressure selection;
5. occupant succession;
6. immutable invocation request binding;
7. deterministic evidence-bundle delivery;
8. result-witness binding;
9. one-shot human authorization;
10. duplicate / replay resistance;
11. malformed / missing evidence failure legibility;
12. result settlement into candidate Atlas state;
13. pause / resume without state loss;
14. local model swap while preserving seat contract;
15. explicit stop behavior.

Only after those surfaces are pressureable should development move into
multi-seat coordination, write/tool authority, CLI/network access, clock-driven
operation, or autonomous regimes.

## Maintenance rule

When a new operationally consequential tool, seat, bridge, gate, adapter,
observer, writer, scheduler, or authority surface appears:

1. add it here;
2. state its current standing;
3. state exactly what it can read/write/execute;
4. state its authorization boundary;
5. state its highest known leverage;
6. state its highest known risk;
7. link the qualifying evidence or mark it candidate/unresolved.

The purpose is to keep **available leverage and available danger equally
legible**.
