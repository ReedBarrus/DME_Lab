# History Association Selection Adjudication v0

## Question and Starting Boundary

This pass independently asks what minimum additional association was sufficient
in bounded execution to connect a detached `current_result()` to recoverable
historical evidence, and whether current evidence selects among Astra's three
surviving encodings. It does not select or implement a production carrier.

After `git fetch origin main`:

- starting `HEAD` and `origin/main`:
  `cb8b916184d1e42e720834a62a68b4b4e0ace49c` (`Astra-Pass_2`);
- divergence: `0 0`;
- initial worktree: clean except for the untracked external
  `Working_Memory_Folder_Source/Astra_outputs/Pass_3/` handoff.

The investigator also began and ended at `cb8b916184d1e42e720834a62a68b4b4e0ace49c`
and reported no repository changes. Current remote main had not advanced.

## Investigator Evidence Boundary

Pass 3 remained external investigator evidence. The top-level artifacts and
verified SHA-256 values were:

- `history-association-report.md`:
  `4aefa68518c955938d66f701721424e04ae06fd7aa2b530a52f16749df74ff23`;
- `history-association-selection-trace.json`:
  `71a1c636ec8ea04350d6e6a67e5ac4c6e228189f21a7f6d16d13c542ad4a45db`;
- `history-association-adversarial-trace.json`:
  `c83427a3c3d9333f0ff5884ff2450932452577c0cd77fdfdc1fd3ce5077d081a`;
- `history-association-verification.json`:
  `3acab89317ca0e85de8fe9f531e7b1f43816efba1ba434bb05ecf77476e8a5b4`;
- `history-association-evidence.zip`:
  `2a0fa40e1a9257a70e45483db03d07bc4d7b6b5938d962004c8e9ece74b6c737`.

The archive contained 30 manifest-listed files plus its manifest. All member
byte lengths and hashes matched. It preserved 16 history files, both traces,
the pre-execution protocol, separately declared adversarial plan, experimental
public declaration and reader, generation scripts, tests, logs, report, and
verification record. No external file was copied into repository lineage.

## Repository Constraints

The audit read the current entry documents, bounded warrant, both prior consumer
adjudications, ledger/reconstruction/projection contracts, projection guidance,
ledger and continuity implementations, and relevant history-extent,
continuation, historical-relation, witness-content, provenance-recovery, and
operation-identity evidence.

Current semantics constrain this result:

- canonical replay sorts committed records by integer `commit_index`;
- valid bounded histories require unique IDs and dense, unique indices starting
  at one;
- each record digest is SHA-256 over canonical UTF-8 JSON of exactly
  `{record_id, commit_index, envelope}`, with sorted keys, compact separators,
  and unescaped Unicode;
- records are not hash-chained, so one terminal digest does not commit earlier
  records;
- `current_result().ledger.record_count` supplies the original extent N;
- valid append-only continuation preserves an earlier committed prefix;
- reconstruction and projection retain ledger-local record references but are
  not authoritative history.

## Independent Reproduction

Three separate checks were performed rather than adopting the report:

1. The archived 15-history, 9-candidate selection trace contains 135 cells; the
   adversarial trace adds `mixed4` and contains 48 cells across three finalists
   and 16 histories. Saved history hashes and trace bindings verified.
2. The nine archived handoff tests passed against the saved histories. A fresh
   scratch rerun of the external generator independently recreated 15 histories,
   135 selection cells, 48 finalist cells, functional finalist equivalence, and
   nine passing evidence tests.
3. A separately authored ephemeral pressure used current repository APIs to
   capture fresh healthy and degraded four-record histories, build changed,
   mixed, role-collision, truncation, copy, re-encoding, H4-to-H6,
   divergent-tail, and H14-to-H16 specimens, and evaluate every required weak
   candidate and finalist. All constructed histories passed current record
   schema, per-record integrity, and start-at-one continuity.

The fresh H4/D4 capture reproduced equal complete `current_result()` bodies.
H4 had a clean `main` branch, a present HEAD, empty status, and no capture
errors. D4 had null HEAD, branch, and status with three real Git command errors.
The canonical live ledger SHA-256 remained
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after every independent pressure.

## Candidate Eliminations

| Candidate | Independent result | Preserved relation |
| --- | --- | --- |
| location alone | accepted H4 and opposite-outcome D4 | reachability only |
| location + extent | accepted D4 because both have N=4 | reachability and size lower bound |
| location + record IDs | accepted D4 and same-ID changed histories | ledger-local labels only |
| location + terminal digest | accepted D4 and changes at positions 1-3 | terminal committed record only |
| location + target Git-record digest | rejected D4, but accepted `mixed4` and non-target prefix changes | target payload recovery, not complete originating-prefix association |
| location + exact file-byte digest | accepted an exact copy, but rejected valid continuation and replay-equivalent whitespace/line-order/CRLF changes | one byte representation of one retained file |
| location + full prefix records | accepted the required prefix relation | complete embedded control, not a smallest digest carrier under current hash assumptions |
| location + ordered prefix record digests | accepted the required prefix relation | order metadata in the carrier proved redundant on current valid histories |

The `roles4` specimen retained the same local ID strings while assigning the
referenced Git observation ID to an admission record. Reference-role checks
failed even when a matching commitment to `roles4` was supplied. Bare ID
equality therefore did not become association.

`mixed4` retained H4's Git target record, terminal admission, complete result
shape, and record IDs while replacing another record inside N. Target and
terminal commitments recovered the selected Git payload but did not bind the
complete committed context from which all result references derive. That
narrower payload-recovery sufficiency is preserved rather than mislabeled as
whole-result historical association.

## Functional Requirement

The surviving bounded relation has two functional roles:

```text
reachable evidence location
+
discrimination of every committed record boundary in the original prefix of N
```

Removing the location left no current public mechanism to obtain evidence from
a commitment. No digest resolver, search service, or index exists. An immutable
content-addressed location could eventually combine both roles in one carrier,
but current temporary histories are not automatically exported to one; this is
not a fourth executed finalist or evidence for two mandatory production fields.

Removing sufficient commitment let the declared location be substituted with
D4 while the complete result and weak coordinates remained compatible. Removing
each one of H4's four digest-set members in turn let the corresponding valid
single-position replacement pass the weakened subset rule; restoring the member
rejected it. This supports complete coverage within the tested digest
representation and full-prefix question, not universal or bit-level minimality.

## Continuation, Copies, and Tails

All finalists accepted H4's original N=4 prefix in H6 and in a second valid H6
with a different two-record suffix. They also accepted H14's original N=14
prefix in H16. Truncated H3 failed extent. The tested relation is preserved
original committed prefix, not exact whole-current-history equality.

An exact physical copy at another location and a replay-equivalent file with
reversed JSONL line order, whitespace changes, and CRLF encoding both retained
the committed replay content and were accepted after an appropriate reachable
location was supplied. Neither physical location nor byte representation is the
associated identity. Different compatible suffixes do not become part of the
old result and no unique current tail or physical lineage is established.

## Finalist Semantics

Let S contain the recomputed lowercase hexadecimal record digests for the first
N valid replayed records.

### A: reachable location plus complete digest set

The commitment is mathematical set S. Serialization order is irrelevant. Each
member is an existing record commitment; A adds no aggregate hash boundary.

### B: reachable location plus ordered-prefix aggregate

The commitment is SHA-256 over canonical JSON of the array of N digest strings
in canonical replay order. It adds an aggregate commitment and array
canonicalization boundary. Changing compact JSON to spaced JSON changed the
aggregate, as declared.

### C: reachable location plus canonical-set aggregate

The commitment is SHA-256 over canonical JSON of the lexicographically sorted
distinct members of S. It adds an aggregate boundary plus lowercasing, set, and
sorting semantics. Changing aggregate JSON canonicalization changed the hash.

Under current full validity, two distinct committed record boundaries cannot
produce the same digest without a SHA-256 collision: `commit_index` is inside
the digest boundary and valid histories require unique dense indices. Physical
encodings of the same boundary are not distinct committed content. The current
schema also fixes stored algorithm and boundary labels. `JsonlLedger.verify()`
alone does not enforce those labels, but label drift fails the current schema
and none of A, B, or C commits integrity metadata outside the declared record
boundary. Thus set multiplicity loss does not separate A and C on the current
valid-history basis; SHA-256 collision resistance remains an assumption, not an
executed proof.

## Non-Scalar Comparison

| Dimension | A | B | C | Classification now |
| --- | --- | --- | --- | --- |
| sufficiency | accepts exactly tested preserved prefixes | same | same | experimentally equivalent |
| ambiguity | copies and divergent tails remain | same | same | experimentally equivalent |
| minimality | every member needed under tested ablation | one aggregate value, but extra boundary | one aggregate value, but extra set boundary | no overall necessity order |
| persistence | survives H4-to-H6 and H14-to-H16 | same | same | experimentally equivalent |
| public interpretability | needs set and record-digest rules | needs ordered-array aggregate rules | needs set/sort aggregate rules | contractual representation difference |
| coupling | current per-record digest semantics | same plus aggregate canonicalization | same plus set/sort canonicalization | contractually different, not selecting |
| claim inflation | must remain prefix correspondence | aggregate must not imply whole-history identity | same | equal bounded risk |
| representation cost | N digest values | one digest value | one digest value | merely representational absent a budget |
| implementation obligations | member verification permits position/member diagnostics | aggregate recomputation | set construction, sorting, aggregate recomputation | future operational pressure |
| assumptions | faithful pairing, reachable location, current digest semantics and collision resistance | same plus aggregate boundary | same plus aggregate/set boundary | explicit, not selecting |

A exposes individual members and can support partial diagnostics, while B and C
are opaque until their aggregates are recomputed. B may be accumulated in replay
order; C requires canonical set construction and sorting. These are observable
implementation/representation differences, but current contracts impose no
transport budget, incremental verification, partial-retention, diagnostic,
cross-host, concurrency, or export-atomicity requirement. Using those future
pressures to rank the finalists now would be unsupported preference.

Missing or deleted evidence makes all three unavailable. Moving evidence
requires an updated reachable locator. Re-encoding or copying committed content
does not change any commitment. No newly discovered valid history separated
their acceptance pattern.

## Pairing and Claim Boundary

All three accepted an opposite-outcome D4 history when R, the commitment, and
the evidence location were consistently paired to D4. The experiment therefore
assumes faithful original pairing. It checks retained correspondence to a
producer-declared committed prefix; it does not authenticate the producer or
prove that execution causally derived R from that history.

Historical association here remains distinct from freshness, source success,
historical truth, unique physical lineage, unique current tail, and authenticated
causal derivation. Matching a commitment does not strengthen structural
admission into source success.

## Finalist Standing

- **A:** survives on the current tested basis; not preferred.
- **B:** survives on the current tested basis; not preferred.
- **C:** survives on the current tested basis; not preferred.

The three are functionally equivalent for the executed association relation.
Their present asymmetries concern representation and additional semantic
boundaries, not a current executable or contractual requirement that selects
one.

## Distinction Standing

No new distinction is forced. D-0032 preserves prefix conservation against
mere extent growth; D-0033 defeats ID/index-only content identity; D-0034 keeps
a carrier separate from recoverable interpretation; D-0026 keeps reconstruction
separate from authoritative history; D-0029 prevents an experiment trace from
becoming that history; and D-0046 keeps association/admission from implying
source capture success.

These existing distinctions conserve the bounded result and its limits. No
registry entry was added.

## Primary Adjudication Status

```text
history_association_selection_reproduced
```

Weak-candidate eliminations materially survive; reachability plus complete
original-prefix discrimination survive as functional roles; A, B, and C remain
equivalent on the current valid-history basis; and no current contract or
executable pressure selects among them.

## Repository Consequence and Verification

The smallest warranted integration is this independently authored decision and
one factual `PROJECT_STATE.md` update. No production history ID, locator,
digest-set field, aggregate digest, resolver, namespace, navigation graph,
cross-host mechanism, runtime, contract, test, trace, or new distinction was
added. Astra's external files remain untracked and unchanged.

Verification performed:

- baseline repository suite: 472/472 passed in 15.465 seconds;
- saved external handoff tests: 9/9 passed in 0.354 seconds;
- fresh external scratch generation: 15 histories, 135 selection cells, 48
  finalist cells, with 9/9 tests passing in 0.338 seconds;
- independent ephemeral matrix: fresh H4/D4 plus 12 adversarial four/six-record
  histories, four member ablations, H14-to-H16 continuation, aggregate
  canonicalization, role, copy, re-encoding, and faithful-pairing checks passed;
- final repository suite: 472/472 passed in 16.452 seconds.

No audio or hardware work occurred. Canonical history was not mutated. No
production carrier or next navigation experiment is selected.
