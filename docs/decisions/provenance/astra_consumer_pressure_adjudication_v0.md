# Astra Consumer Pressure Adjudication / Reproduction v0

## Scope and Repository Boundary

This pass audits Astra's `Consumer Git Acquisition Pressure v0` as external
experimental evidence and independently reproduces its central claim against
current authoritative `main`. Astra's patch was not applied and its files were
not copied into Lab lineage.

After `git fetch origin main`:

- starting `HEAD` and `origin/main`:
  `b9ef1361e87690af03cc8e536c406d8152fd0164`
  (`Source-Coordinate Witness Selection`);
- divergence: `0 0`;
- initial worktree: no tracked changes; the user-supplied untracked
  `Working_Memory_Folder_Source/` was present and treated as read-only external
  evidence.

The only changes between Astra's base
`2618453d233a5867757c22ff732459f701834372` and current `main` are
`PROJECT_STATE.md` and the acoustic witness-selection decision. No production,
coordinator, reconstruction, projection, ledger, or Git-observer semantics
changed. The acoustic frontier is orthogonal and was not reopened.

## External Artifact Audit

The supplied directory contained a report, JSON trace, patch, ZIP bundle, and
verification manifest. Their SHA-256 values were recorded before inspection.
The manifest's patch hash and per-file hashes matched the supplied files; the
ZIP contained the five proposed repository files, two navigator answer records,
the manifest, and the patch. The navigator answer hashes in the trace matched
the ZIP entries.

Astra's patch proposed exactly:

- one pressure-only runtime module;
- three evidence tests;
- one execution trace;
- one decision record;
- two short `PROJECT_STATE.md` additions.

It invoked the unchanged foreground coordinator, JSONL ledger, admission
reconstruction, the existing clean-Git fixture initializer, and the existing
real Git observer. It added no production abstraction, comparator behavior,
projection field, or registry entry.

The fixtures were one deterministic clean Git repository and one ordinary
directory without `.git`, each captured into its own temporary four-record
ledger. A fresh coordinator then called the complete `current_result()` surface.
The case labels were external handles; neither label nor fixture identity was
inserted into the result body.

Before its first answer, Astra's navigator saw only case A's full result and the
question. Before its paired answer, it saw both full results and their equality.
It intentionally withheld raw observations, ledger bytes, reconstruction,
fixture mapping, Git fields, errors, and the immediate capture return until the
audit. The navigator was the same assistant that designed the experiment,
already knew D-0046 and the implementation, and was restricted procedurally,
not technically.

The compared value was the entire `current_result()` Python object. Astra also
serialized each object with sorted keys and compact separators. No fields were
deleted, masked, renamed, or normalized. Its trace contains different complete
ledger JSONL bytes and identical visible bodies with SHA-256
`58b08aba3a774d6f508b0a8a06b752476ff7a3f91664ffbeb52fc87ce86e16a9`.

Astra's three tests check fixture outcomes, whole-body equality, append-free
historical recovery, and replay of the recorded specimen ledgers. They do not
test whether the navigator prose is semantically correct. The no-overclaim
finding is a manual audit of one recorded knowledgeable consumer response.

## Independent Reproduction

The reproduction was authored from current repository APIs rather than Astra's
patch. It created fresh clean-Git and non-Git fixtures, captured each through
the unchanged coordinator, closed the writer, opened a fresh coordinator, and
compared the complete unmodified `current_result()` values.

The result reproduced exactly:

| Evidence | C0 | S1 |
| --- | --- | --- |
| fixture | clean Git repository | ordinary non-Git directory |
| historical `head_sha` | `46a865676f52e115b1d9319ddef62f4f42433453` | null |
| historical branch | `main` | null |
| historical status | empty list | null |
| historical `capture_errors` | empty list | three real command failures |
| admission | admitted | admitted |
| complete `current_result()` | exactly equal to S1 | exactly equal to C0 |

Both complete bodies independently reproduced Astra's digest
`58b08aba3a774d6f508b0a8a06b752476ff7a3f91664ffbeb52fc87ce86e16a9`.
Python object equality and canonical serialized-byte equality were both true.
No normalization was applied. The temporary ledger hashes differed, as did
their raw and reconstructed Git payloads.

Separate ledgers legitimately reuse `rec-000001` through `rec-000004`; record
identity is ledger-local. Those record IDs are part of the public body and were
not changed to manufacture equality. The declared consumer surface does not
include root or ledger identity. An external caller must retain the associated
ledger context to follow `rec-000002`; whether a consumer can discover that
context without prior knowledge is question 5 and was not tested here.

The collision follows directly from current `_result()` construction:
`current_result()` supplies no new records or captures, exposes ledger and
derived health/counts, and projects record/source relationships without nested
Git payloads. Opposite source-acquisition outcomes can therefore share every
exposed field when their ledger shapes and decisions agree. This is not a
serialization artifact.

## Historical Recovery

For each case, fresh `JsonlLedger.replay()` followed by
`reconstruct_admission_relationships()` located the
`repository_git_state` observation at `rec-000002`. Its nested signal payload
exactly matched the original raw Git observation:

- C0 recovered HEAD, branch, empty status, and no errors;
- S1 recovered null HEAD/branch/status and all three command failures.

The ledger bytes were unchanged by `current_result()` and reconstruction.
Thus the representation is insufficient for the selected acquisition-success
question, but the distinguishing information was not destroyed. Existing
reconstruction is the valid historical recovery route. There is no generalized
navigator or index, so consumer discovery of that route is not claimed.

## Consumer-Basis Adjudication

The five questions remain separate:

1. **Did Astra overclaim?** No overclaim appears in the recorded responses. The
   navigator explicitly declined to summarize Git state and requested the
   nested historical observation.
2. **Could `current_result()` distinguish the cases?** No. The complete bodies
   are exactly equal while the selected historical outcomes differ.
3. **Does the representation prevent overclaim?** Not established. It omits the
   answer and marks itself non-authoritative, but supplies no enforcement
   mechanism. One knowledgeable consumer's restraint is not representation
   safety.
4. **Is the evidence recoverable?** Yes, from each associated ledger through
   existing reconstruction.
5. **Can an uninformed consumer discover the route?** Not tested and not
   inferred from Astra's procedurally restricted, implementation-aware run.

The model prose adds one bounded consumer observation, not a general consumer
reliability result. The executable contribution is the exact whole-surface
collision and recovery check.

## Canonical-History Hash Discrepancy

The reported hashes describe checkout-byte representations, not different
logical history:

| Representation | Bytes / line endings | SHA-256 |
| --- | --- | --- |
| current working file | 65,970 bytes; 12 CRLF and 2 LF terminators | `0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0` |
| Astra working file | inferred 65,972 bytes; 14 CRLF terminators | `35107048c6cbdbef7276d7aec2960456dbe17125b1ec80880d88da923ab26eb6` |
| Git blob at Astra base/current lineage | 65,958 bytes; 14 LF terminators | `2a2b4adb673df0a87855f075e464796d8ca49e2e0e59b74ea8be579ec815f03f` |

Converting the Git blob to all CRLF produces Astra's exact hash. Normalizing the
current working file to LF produces the exact Git blob and blob hash. Git
reports the canonical history path unchanged. The discrepancy is line-ending
checkout representation, not alternate or mutated history; no distinction is
forced.

## Relation to Existing Evidence

D-0046, `structural_admissibility != source_capture_success`, remains
sufficient. D-0041 prohibits reading projection membership as resolved truth;
D-0042 supports recovery across coordinator lifetimes; D-0045 separates a
derived historical view from current external configuration. The reproduced
collision is a new operational consequence and consumer-pressure specimen for
those existing boundaries, not a new distinction.

No production change is justified. Adding errors or source-quality summaries
to `current_result()` would change a deliberately bounded projection because
one consumer question requires deeper evidence. Existing reconstruction already
answers the historical question.

## Required Standing

```text
astra_pressure_reproduced
```

All three required components reproduced on current `main`: opposite relevant
historical Git acquisition outcomes, identical complete declared
`current_result()` bodies without normalization, and append-free recovery of
the underlying difference through existing history.

## Lineage and Verification

The exact whole-body collision was not previously asserted by an executable
test, so the bounded specimen merits lineage. Astra's patch and prose remain
external. Lab lineage contains an independently authored pressure module,
three evidence tests, an independently executed trace, this adjudication, and
one state pointer. No Astra-specific runtime abstraction or navigator framework
is added.

Tests:

- baseline full suite: 469/469 passed;
- focused new pressure: 3/3 passed;
- final full suite: 472/472 passed;
- runner: `python -m unittest discover -s tests -v`; no audio or
  hardware-dependent pressure executed.

Canonical live history remained unchanged at working-file SHA-256
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`
before and after execution. Its normalized Git blob remained
`2a2b4adb673df0a87855f075e464796d8ca49e2e0e59b74ea8be579ec815f03f`.

Files changed for Lab lineage:

- `src/runtime/consumer_git_acquisition_pressure.py`;
- `tests/runtime/test_consumer_git_acquisition_pressure.py`;
- `traces/consumer_git_acquisition_pressure_v0.json`;
- this decision record;
- `PROJECT_STATE.md`.

No production module, contract, registry entry, prior trace, or canonical
history was changed. Final `HEAD` and `origin/main` remain
`b9ef1361e87690af03cc8e536c406d8152fd0164` with divergence `0 0`. The supplied
`Working_Memory_Folder_Source/` remains untracked and unmodified. During final
verification, an unrelated concurrent `README.md` modification and untracked
`docs/contracts/Bounded_Research_Warrant.md` appeared. They were not created,
altered, audited, or attributed to this pressure. Apart from those preserved
external changes, the worktree contains exactly the five scoped lineage changes
above.
