# Constraint Registry Lineage Audit v0

## Scope and repository gate

This documentation and lineage audit asks what role the former Distinction
Registry actually performs. It creates no runtime machinery, formal operator,
ontology, symbolic grammar, task branch, or distinction-event store.

After `git fetch origin main`, local `main` and `origin/main` were identical at
`71c38f77e728781c50d6cff77816bbc107ddd278` (`Resolution Mapping`), divergence
`0/0`, with a clean worktree.

## Adjudication

The rename is warranted. All 46 registry rows have relation
`not_equivalent_to`; each conserves a reusable prohibition against collapsing
two coordinates under a named scope and evidence basis. The rows do not record
concrete applications with subjects, observations, comparison outcomes, or
occurrence identities. In current practice they function as scoped constraints
on admissible equivalence and inference, not as a log of local distinction
events.

The old name drifted because an early list of useful non-equivalences was called
a distinction registry, while later decisions repeatedly used the `D-*` rows
to prevent already-wounded interpretations from reappearing. The historical
IDs remain valid lineage and are not renumbered.

This interpretation is descriptive, not an operator definition:

```text
constraint = reusable scoped limit on equivalence or inference
             supported by declared basis and provenance

local distinction = discrimination produced when a constraint is applied
                    to concrete evidence under a declared basis
```

The rename does not retroactively convert all entries into empirically proven
facts. `supported` remains relative to each row's basis, provenance, and scope.

## Complete entry audit

Every entry was parsed, its provenance targets checked, and its later lineage
searched. The audit found 46 unique, contiguous `D-0001` through `D-0046` IDs,
46 `not_equivalent_to` relations, and 46 `supported` standings.

The character labels below mean:

- **executable empirical:** a deterministic fixture/assertion supports the
  scoped non-equivalence;
- **runtime empirical:** retained runtime specimens support it, without turning
  the result into a general law;
- **structural:** current implementation inspection supports it and must be
  revisited if that implementation changes;
- **imposed:** a project contract or decision intentionally prohibits the
  collapse; it is not an empirical discovery.

No row currently uses `structural_observation` or `semantic_inference` as its
basis. The absence of semantic-inference rows does not mean the registry is
free of interpretation; it means every conserved row declares a different
current support route.

### Deterministic-test constraints

| ID | Exact constrained pair | Character | Audit and later standing |
| --- | --- | --- | --- |
| D-0001 | commit order / event order | executable empirical | unchanged; scoped to the ordering-conflict fixture, not universal event chronology |
| D-0002 | ledger-record identity / envelope identity | executable empirical | unchanged; later detached-history work remains consistent with ledger-local identity |
| D-0007 | record integrity / history integrity | executable empirical | unchanged; continuity pressure supplies the discriminator |
| D-0008 | schema validity / integrity validity | executable empirical | unchanged; neither direction is generalized beyond the tested record boundary |
| D-0009 | per-record schema / ledger invariant | executable empirical | unchanged; scoped to tested duplicate IDs and indices |
| D-0010 | runtime possibility / schema validity | executable empirical | unchanged; describes the current append/schema mismatch only |
| D-0012 | snapshot / complete transformation history | executable empirical after later strengthening | basis changed from `design_constraint`; absent-interval alpha -> beta -> alpha pressure directly wounded endpoint equivalence as interval history |
| D-0016 | structural-state identity / observation-occurrence identity | executable empirical | unchanged; later acoustic uses are bounded correspondences, not cross-domain generalization |
| D-0017 | snapshot identity / content-change classification | executable empirical | unchanged; metadata-only fixture defines the narrow scope |
| D-0018 | retrospective Git history / contemporaneous filesystem history | executable empirical | unchanged; no later evidence supplies the missing contemporaneous observations |
| D-0022 | directory-level observation / leaf-level observation | executable empirical | unchanged; regional correspondence remains possible without equivalence |
| D-0023 | persisted observation / admission classification | executable empirical | unchanged; later pressures preserve rejected and unresolved evidence |
| D-0024 | rejected / deleted | executable empirical | unchanged; applies to the bounded admission ledger, not every rejection system |
| D-0025 | observation identity / admission classification | executable empirical | unchanged; multiple comparator records retain one subject |
| D-0026 | authoritative history / reconstructed representation | executable empirical | unchanged; later consumer work relies on rather than supersedes it |
| D-0027 | reconstruction / projection | executable empirical | unchanged; later projection pressures strengthen the exposure boundary |
| D-0029 | experiment trace / authoritative history | executable empirical | unchanged; later history-association work preserves the same authority split |
| D-0030 | history extension / history mutation | executable empirical | unchanged; complete-prefix preservation is the tested discriminator |
| D-0031 | internal continuity / witnessed history extent | executable empirical | unchanged; an external extent witness remains necessary for the scoped question |
| D-0032 | extent growth / historical conservation | executable empirical | unchanged; later carrier selection preserves prefix rather than whole-tail identity |
| D-0033 | record-ID sequence / record-content identity | executable empirical | unchanged; later role collisions and mixed histories strengthen the caution |
| D-0034 | witness-carrier survival / historical-relation recovery | executable empirical | unchanged; interpretation regime remains independently necessary |
| D-0035 | semantic label / recoverable semantic description | executable empirical | unchanged; the fixture tests withheld ambient meaning rather than language universally |
| D-0036 | token identity / semantic-operation identity | executable empirical | unchanged; mapped renaming and changed relation semantics provide the discriminator |
| D-0037 | implementation identity / operation identity | executable empirical | unchanged; equivalent bounded behavior does not define universal operation identity |
| D-0038 | behavioral-witness sufficiency / candidate-set-independent identity | executable empirical | unchanged but explicitly candidate-set-relative; later expansion is the strengthening evidence |
| D-0039 | operation-semantics difference / distinguishability on admissible history | executable empirical | unchanged; Chart 9 records which single constraints made the difference reachable |
| D-0040 | ordering resolution / relation resolution | executable empirical | unchanged; exact tie order stays unresolved while tested relation results are invariant |
| D-0041 | projection membership / admission resolution | executable empirical | unchanged; later degraded-source and consumer work preserve the same warning |
| D-0042 | coordinator lifetime / historical continuity | executable empirical | unchanged; later fresh-coordinator recoveries strengthen it without implying freshness |
| D-0043 | caller invocation outcome / durable history state | executable empirical | unchanged; retry policy remains consumer-dependent |
| D-0044 | same capture invocation / same world configuration | executable empirical | unchanged; scoped sequential acquisition does not become a global coherence claim |
| D-0045 | current derived history / current external configuration | executable empirical | unchanged; later consumer work remains historical rather than externally fresh |
| D-0046 | structural admissibility / source capture success | executable empirical | unchanged; consumer pressures strengthen its consequence without selecting a new projection |

### Runtime-observation constraints

| ID | Exact constrained pair | Character | Audit and later standing |
| --- | --- | --- | --- |
| D-0011 | filesystem observation / Git observation | runtime empirical | unchanged; one bounded repository regime with distinct payloads, scopes, and times |
| D-0013 | observation interval / event time | runtime empirical | unchanged; event time was unavailable in the inspected envelope |
| D-0014 | shadow-schema comparison / admission decision | runtime empirical | unchanged within the pre-admission live-handshake scope; later admission machinery does not rewrite that history |
| D-0015 | filesystem scope / Git scope | runtime empirical | unchanged; its note already preserves the earlier narrowing from directory mismatch to regional correspondence |
| D-0019 | working-tree state / committed state | runtime empirical | unchanged; restricted to the compared transition and Git evidence basis |
| D-0021 | invocation path / stable source identity | runtime empirical | unchanged; the empty-name `.` specimen shows insufficiency, not a general identity solution |
| D-0028 | capture sequence / ledger commit order | runtime empirical | unchanged; they are different coordinates even where a specimen's relative order agrees |

### Code-inspection constraints

| ID | Exact constrained pair | Character | Audit and later standing |
| --- | --- | --- | --- |
| D-0004 | runtime trace / test verdict | structural | unchanged; current runner and assertion locations differ, but this is not a runtime theorem |
| D-0005 | scenario executed / guarantee verified | structural | unchanged; dedicated assertions remain necessary under the named runner |
| D-0006 | canonical replay order / physical file order | structural | unchanged; current replay sorts by `commit_index`; later re-encoding work is consistent but does not broaden the scope |

### Design constraints

| ID | Exact constrained pair | Character | Audit and later standing |
| --- | --- | --- | --- |
| D-0003 | integrity / truth | imposed | unchanged; `supported` means the contract deliberately refuses the inference, not that truth was empirically measured |
| D-0020 | raw observation / derived comparison | imposed | unchanged; the pressure deliberately kept derived deltas outside raw ingest |

## Counts and registry changes

Starting basis counts:

| Basis | Count |
| --- | ---: |
| `deterministic_test` | 33 |
| `runtime_observation` | 7 |
| `code_inspection` | 3 |
| `design_constraint` | 3 |
| `structural_observation` | 0 |
| `semantic_inference` | 0 |

After the audit:

| Basis | Count |
| --- | ---: |
| `deterministic_test` | 34 |
| `runtime_observation` | 7 |
| `code_inspection` | 3 |
| `design_constraint` | 2 |
| `structural_observation` | 0 |
| `semantic_inference` | 0 |

D-0012 is the only modified row. Its `basis`, provenance, and note now record
the later deterministic strengthening without changing its ID, constrained
pair, original scope, standing, or historical origin. Forty-five rows are byte
changed only by the file move, not semantically edited. No row was downgraded,
deleted, contradicted, or superseded.

Potential misreadings remain rather than suspicious unsupported entries:

- D-0003 and D-0020 are imposed constraints, not discoveries;
- D-0004 through D-0006 depend on current implementation inspection;
- D-0011, D-0013 through D-0015, D-0019, D-0021, and D-0028 are bounded runtime
  observations, not universal source laws;
- every apparently broad left/right phrase is limited by its `scope`, `basis`,
  provenance, and note.

No current evidence requires a standing downgrade. A future contradiction must
be recorded as lineage rather than silently repaired here.

## Where concrete distinction events are represented

There is no explicit persistent distinction-event representation today.

Concrete local discriminations live mainly in:

1. **traces**, which retain scenario observations and derived comparison
   surfaces;
2. **decision records**, which state the applied comparison, bounded result,
   and residue;
3. **tests**, which deterministically assert many discriminations and failure
   boundaries;
4. **comparison outputs** embedded in traces and decisions.

Reconstruction artifacts preserve observations, admissions, identifiers, and
relations used by later comparisons. They do not currently persist a general
distinction event. The Constraint Registry remains summary memory over those
evidence surfaces, not a new store.

## Human/agent process audit

The repository repeatedly exhibits the following descriptive operations:

| Name | Classification | Current evidence and boundary |
| --- | --- | --- |
| observe | recurring observed operation | capture modules and traces retain bounded source observations |
| compare | recurring observed operation | pressure runners, tests, and decision matrices compare declared coordinates |
| transform | recurring observed operation | controlled repository and acoustic interventions vary a declared basis |
| constrain | candidate reusable operation | D-* memory is repeatedly consulted to reject unsupported equivalence, but no formal application operator exists |
| distinguish | candidate reusable operation | local comparisons produce discriminations, but no persistent distinction-event type exists |
| project | recurring observed operation | bounded reconstruction and admitted projection code select exposed relations |
| integrate | recurring observed operation | decisions, project state, and the Pressure / Resolution Map preserve bounded outcomes |
| adjudicate | recurring observed operation | decision records select exact statuses while preserving residue |

These names describe practice. They do not define signatures, composition,
closure, order, a symbolic grammar, or formal operational semantics. `WORKFLOW.md`
receives only that guard. No pressure-map node is needed: the audit is complete,
no experimental pressure is active, and no new branch of work is selected.

## Rename and historical residue

The current navigational files are now:

- `docs/constraints/README.md`;
- `docs/constraints/registry.jsonl`.

Current documentation and executable test references use the new path and
name. Old path/name strings inside committed traces and external investigator
artifacts remain historical captured bytes; rewriting them would mutate
evidence rather than repair navigation. Those residual strings do not indicate
a live path.

## Boundaries

This audit adds no formal operators, runtime or schema, constraint engine,
distinction engine, ontology, grammar, projection, persistent distinction
store, chart, or new D-* entry. It does not select research direction.

Validation is documentation/reference focused. The four tests whose registry
path literals changed are run as a focused compatibility check; the full suite
is not required because production code and runtime behavior are unchanged.

The first focused run passed 107/110 checks and failed three protection checks
because a terminology-only edit had touched
`docs/projection/Persistent_Ecology.md`. That edit was withdrawn. This is direct
repository evidence that the older projection text is protected historical
lineage rather than a current navigation reference to rewrite. The final
focused run passed 110/110. No test logic changed beyond the four required
registry-path literals.

Final checks:

- all 46 JSONL rows parsed; IDs were unique and contiguous; every relation
  remained `not_equivalent_to` and every standing remained `supported`;
- all provenance file paths and named test symbols resolved;
- the new README, registry, and this audit record exist; the empty old directory
  was removed;
- current entry/navigation documents contain no old path or live old-name
  reference;
- exact old-path strings remain in eight historical artifacts: two external
  investigator traces, five committed repository traces/ledgers, and the
  transition decision's historical path list;
- `git diff --check` passed;
- production source, schemas, traces, canonical history, and the Pressure /
  Resolution Map were unchanged;
- final committed `HEAD` and `origin/main` remained
  `71c38f77e728781c50d6cff77816bbc107ddd278`, divergence `0/0`;
- no commit or push was made.
