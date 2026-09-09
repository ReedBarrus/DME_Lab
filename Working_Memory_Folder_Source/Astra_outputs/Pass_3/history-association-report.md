# Detached result / historical evidence association: investigator result

Primary status: `multiple_history_association_candidates_remain`

Three carrier encodings survive the bounded tests. Each supplies an accessible evidence location and commits to the original result's complete committed prefix. The existing `result.ledger.record_count` supplies the prefix extent. The tests do not select a unique encoding, prove a universal minimum, or establish an association already supported by production. This is an investigator result awaiting independent adjudication.

## Standing and repository basis

Question: **What is the smallest public association sufficient to bind a detached `current_result()` to the authoritative historical evidence from which its record references derive, for the already-demonstrated Git-acquisition consumer question?**

The authoritative repository was refreshed into a separate checkout before experimentation. Starting and final HEAD and fetched `origin/main`: `cb8b916184d1e42e720834a62a68b4b4e0ace49c` (`Astra-Pass_2`). All repository references below refer to that commit. This does not assert that the remote cannot subsequently advance.

The required entry documents, bounded research method, both adjudications, projection and reconstruction contracts, and observability document were inspected. Further inspection covered ledger, continuity and schema implementation; coordinator recovery; capture and admission; reconstruction; existing consumer-acquisition reproduction; and earlier history-witness pressures.

The relevant earned constraints are:

- `docs/decisions/astra_consumer_pressure_adjudication_v0.md` preserves the complete-result acquisition counterexample and bounded recovery claim.
- `docs/decisions/public_history_association_adjudication_v0.md` establishes that the supplied public route did not associate the detached specimen with its intended ledger.
- `docs/contracts/ledger.md` preserves committed envelopes, canonical append order, integrity versus truth, and append-only continuation. Physical JSONL line order is not canonical replay order. Record integrity is not full-history integrity.
- `src/ledger/jsonl.py` commits each record with SHA-256 over canonical `{record_id, commit_index, envelope}`. It does not chain record hashes. `src/ledger/continuity.py` and the current schema supply the separate validity checks used here.
- `docs/contracts/projection.md`, `docs/contracts/reconstruction.md`, and `docs/projection/v0_observability.md` require recoverable references and missingness without promoting reconstruction into authoritative history or external-world proof.

`PROTOCOL.md` records the initial design. `ADVERSARIAL_PLAN.md` declares the later attacks before their execution. Their experimental interpretation is public in `PUBLIC_ASSOCIATION.md`; that document is an additional candidate declaration, not an adopted DME contract.

## What relation was actually tested?

Given a faithfully paired packet containing unchanged result R and association C, the reader opens C's declared local file URI, checks valid committed records, and compares the first N records against C, where N is R's existing record count. It then follows and checks R's observation and admission references and exposes the recorded Git payload.

The supported evidence context is **the original committed prefix available at the supplied location**. It is not a unique physical file, unique entire current history, or proof of the actual process that produced R. Two physical copies can contain the same prefix. Two different continuations can preserve that prefix and have different suffixes.

This choice follows the conservation and replay requirements and was pressured against exact-file alternatives: the historical question is answerable from H14 preserved inside valid H16. Requiring H16 to equal the entire old H14 file rejects a legitimate continuation. Accepting the old prefix does not attribute H16's tail to the old result. If “exactly one H” instead requires unique physical lineage or one entire current tail, these candidates do **not** establish it; the copy and divergent-tail constructions are counterexamples.

The packet's original pairing is a declared association, not authenticated authority. Because opposite histories produce identical R, replacing both C and its evidence consistently cannot be disproved from R alone. No source-trust or publisher-authentication mechanism was added. A matching commitment checks retained correspondence to the declared original prefix, under the existing hash assumptions; it does not prove causal derivation or historical truth.

## Candidate search and eliminations

Every executed locator candidate receives the same public interpretation and reference-role checks. Rejection by those shared checks is not credited to its commitment.

| Candidate | Observation and disposition |
|---|---|
| No association; source/root; DME repository revision | H4 and D4 share the source path and implementation revision and have identical complete R but different recorded Git outcomes. These coordinates do not discriminate them. |
| Trace name, source identity, capture invocation, reconstruction provenance | No already-exposed, publicly resolvable history association was found in this basis. Reopened R has no usable capture-round coordinate. A trace label needs its own binding declaration; local provenance references already suffer the disputed association. This is inspection evidence, not an exhaustive impossibility proof for future coordinates. |
| Locator alone; locator + extent; locator + complete local IDs | Each accepts D4 when supplied with the unchanged H4 packet and the evidence location is replaced. Same IDs and count do not bind their underlying records. |
| Locator + terminal record digest | Also accepts D4. The terminal admission is unchanged and does not commit to earlier observation content. |
| Locator + target Git record digest | Rejects the opposite Git observation, but accepts changed original context elsewhere. The mixed-history attack preserves the Git and terminal records while replacing the filesystem observation. This carrier supports the weaker target-content question, not association with the complete originating prefix required here. |
| Digest without a location | Can compare content once supplied, but provides no public route for obtaining it. Removing the URI leaves unresolved location; no digest lookup service is assumed. |
| Locator + exact available-file byte digest | Discriminates replacements but rejects H4→H6, H14→H16, and harmless physical re-encoding. It can still address a separately retained exact snapshot; that adds a retention/access basis not demonstrated for every detached specimen here. |
| Immutable repository revision + artifact path | A possible exact-snapshot route when the actual original history is committed and publicly reachable. Temporary coordinator histories are not made into repository artifacts automatically. No generic operational support or lower cost was established; not claimed experimentally refuted. |
| Locator + full prefix records | Executed as a content control; succeeds on the tested prefix relation. Carries complete envelopes where the digest candidates retain the same tested discrimination under hash assumptions. Not selected as minimal. A separately embedded history would additionally move evidence into the packet. |
| Locator + ordered list of all prefix record digests | Survives selection. Its separately serialized ordering is unnecessary on the tested valid histories: each digest already commits to `commit_index`. Weakened to a set during the adversarial pass. |
| Locator + complete digest set; locator + ordered-prefix aggregate digest; locator + digest-set aggregate digest | Three surviving encodings. They agree on every history in the final matrix. None has an earned overall necessity advantage. |

These eliminations do not mean that every changed envelope changes the Git answer. The single-position metadata changes deliberately preserve the whole result and source observations. They distinguish **binding the original committed context** from merely retrieving sufficient target payload content. No stronger acquisition difference is attributed to those controls.

## Executable evidence

The selection pass created 15 valid histories and evaluated 9 encodings against each: 135 cells. The adversarial pass added one valid mixed history and evaluated the three finalists against all 16: 48 cells. All histories passed current schema, per-record integrity, and dense start-at-one continuity checks. Alternate histories were independently committed; the authoritative original ledger was not silently amended.

| Specimens | Pressure |
|---|---|
| H4, D4 | Real bounded capture before/after Git initialization at the same temporary root, in independent ledgers. Complete reopened R is equal; the Git records differ. D4 retains three command errors and null fields; H4 retains fields with no capture errors. |
| roles4 | Same four local IDs; `rec-000002` is an admission instead of the H4 Git observation. All finalists reject replacement; shared reference checks also reject even if the commitment is changed to match roles4. |
| copy_H4 | Same committed content at another location; demonstrates absence of physical-store uniqueness. |
| changed_1 through changed_4 | One independently committed envelope annotation at each prefix position; complete R stays equal. Tests sparse coverage and component removal. |
| renamed4 | Different local IDs and corresponding admission references, unchanged source observation. Its own association recovers the source evidence; the original H4 association rejects it. The executed own-association checks used the original ordered-list and ordered-aggregate candidates. |
| H6, H6_other_tail | Two valid but different continuations of H4. Both retain the original prefix; neither establishes a unique current tail. |
| H3 | Truncated original prefix; insufficient extent. |
| H14, H16 | Copied canonical repository ledger and valid two-record continuation. Old N=14 evidence remains recoverable with 16 available records. |
| reencoded_H4 | Reversed physical JSONL lines, whitespace changes, and CRLF; replayed committed content stays equal. |
| mixed4 | D4 filesystem observation combined with H4's remaining records in a separate valid history. Complete R, target Git record, and terminal record remain H4-equal; full-prefix candidates reject it. |

Every specimen is reopened through the coordinator with an unavailable source root and no appended bytes. The saved records can be recommitted through the existing ledger API and reproduce their complete saved results. Six initial and nine final detached JSON packets were read in new processes by `public_reader.py`, which imports no DME implementation. The nine finalist reads cover H4, D4, and H14 through H16 and preserve ledger bytes. Nine explicit finalist extension cases recover the original prefix while reporting the larger available count.

The reader reports recorded field availability or recorded capture errors, with `current_external_state: unobserved`. It never converts admission or matching commitment into source success. This is an executable demonstration of the additional public declaration's interpretability, **not** a new unfamiliar-human or LLM navigation trial, cross-host transport trial, or generalized malformed-input security audit.

## Falsification and minimality

The initial preference was the existing ordered record-digest witness plus a locator. The adversarial mixed history defeated its sparse target/terminal alternatives but not full coverage. Reversing witness serialization after removing the ordering requirement preserved discrimination. Consequently, a claim that a separately ordered witness is minimal was falsified.

For the resulting digest set, omit each of its four distinct members and allow the weakened subset comparison. In all four cases, the corresponding independently changed history is accepted even though it is a different original prefix and full R is equal. Restoring the complete set rejects it. This demonstrates the need for each member **within this tested representation and full-prefix question**, not bit-level or universal minimality.

Removing commitment checking allows D4 substitution. Removing location leaves no legitimate acquisition route. Removing the supplied interpretation makes the experimental reader stop. That last test is a deliberate parser guard: it is **not** proof that every profile word or metadata field is irreducible. N is reused from R rather than duplicated in C.

The two aggregate digests survive the same attacks. Each compresses the coverage declaration to one hash but introduces an additional commitment boundary. No tested observation distinguishes whether that new boundary is necessary or preferable to carrying the existing per-record commitments. No SHA-256 collision was constructed; collision resistance remains an assumption rather than an empirical theorem.

## Finalist comparison vector

Let S be the set of recomputed record digests for the first N committed records. All three include the declared URI, encoding interpretation, and unchanged R. Canonical JSON and SHA-256 meanings are explicitly supplied.

| Dimension | A: URI + S | B: URI + hash of ordered prefix-digest array | C: URI + hash of lexicographically sorted S |
|---|---|---|---|
| Sufficiency | Recovers exactly the tested original prefixes, then referenced evidence | Same tested acceptance/recovery | Same tested acceptance/recovery |
| Ambiguity | Rejects replaced prefixes; copies and different suffixes remain compatible | Same; additional aggregate hash assumption | Same; additional aggregate hash assumption |
| Minimality | Each of four witness members needed under tested weakening; extra serialization order removable | Removing commitment loses discrimination; no universal minimum established | Same; no necessity advantage over A or B established |
| Persistence | Reopen and detached same-host process pass while URI remains accessible | Same | Same |
| Consumer discoverability | New explicit public declaration makes opening and verification executable; no production export or usability result | Same, plus aggregate boundary | Same, plus set canonicalization boundary |
| Coupling | Host/file access, original extent, existing commit hash semantics; hash already includes commit index | Same, plus ordered aggregation | Same, plus sorted-set aggregation |
| Claim inflation | Must limit match to original committed prefix, not freshness, success, truth, or physical uniqueness | Same; compact hash must not be read as complete current-history identity | Same |
| Representation cost | N existing digest values; new association declaration; no new digest primitive | One new aggregate value using existing SHA-256; additional boundary semantics | One new aggregate value using existing SHA-256; additional boundary semantics |
| Implementation cost | Future consistent result/association export and stable evidence access; verify full prefix | Same, plus aggregate calculation/verification | Same, plus set canonicalization and aggregate calculation/verification |

All require retained pairing and access obligations; none requires new mutable coordinator state in this experiment. Eventual production export must pair R and its commitment from the same evidence extent. Concurrency, retention policy, portable location design, and export atomicity were not implemented or established. No scalar score is assigned. Reusing existing commitments and carrying fewer values are different tradeoffs; choosing between them now would add a preference the evidence has not earned.

## Stop, verification, and handoff

Stop condition reached: more than one carrier survives and current evidence does not discriminate relative necessity. No production recommendation or new distinction is admitted. The smallest supported shape has two roles—**reach the declared evidence and discriminate its original committed prefix**—without claiming two mandatory fields or a unique minimal encoding.

Not established: current-world freshness, historical truth, source trust, global record identity, unique physical lineage, capture simultaneity, source success from association alone, general navigability, cross-host availability, permanent hash/canonicalization semantics, or production support. A content association cannot authenticate a maliciously replaced original packet. A moved or missing evidence location remains unavailable.

Validation: baseline full repository suite passed 472 tests; final full suite passed 472 tests in 16.234 seconds. Nine external evidence tests passed, checking valid replay and complete-result reproduction, the full-record equality oracle, acquisition collisions, ablations, extensions, detached recovery, role mismatch, missing associations, and trace binding. The original canonical ledger's before/after SHA-256 is equal. Final checkout is clean on `main...origin/main`; `git diff --check` is empty. No repository files were changed, committed, or pushed in this investigation.

External files: `PROTOCOL.md`, `PUBLIC_ASSOCIATION.md`, `ADVERSARIAL_PLAN.md`, `run_pressure.py`, `public_reader.py`, `adversarial_pressure.py`, `test_pressure.py`, both JSON traces, this report, reproduction instructions, test logs, and packaging/verification artifacts. The evidence archive preserves all 16 specimen histories, exact trace bytes, and a SHA-256 manifest. Temporary fixture locations in traces document the executed run and are not still-live evidence endpoints; the archive supplies the records for replay.

The next reviewer can reconstruct candidate → pressure → evidence → elimination → surviving relation without trusting the narrative, using the saved fixtures and executable checks. No additional warrant was needed to reach this stop. Selecting or adopting an encoding would need a separately stated criterion or new discriminating pressure, followed by independent adjudication; it is not silently delegated to production work.
