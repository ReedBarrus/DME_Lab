# Public History Association Adjudication v0

## Scope and Repository Gate

This pass adjudicates Astra Pass 2's bounded consumer-navigation result against
the complete materially relevant public DME_Lab surface. The sole question is
whether that surface binds the supplied historical `current_result()` specimen
to the authoritative history containing its referenced records. It does not
test general navigability, consumer reliability, or a proposed remedy.

After `git fetch origin main`:

- starting `HEAD` and `origin/main`:
  `55cc382e2175c57819b35c622419a9ee9d8a677b`
  (`Altered warrant position and content`);
- divergence: `0 0`;
- initial worktree: the user's tracked Astra files had been moved from the flat
  `Working_Memory_Folder_Source/Astra_outputs/` directory into untracked
  `Pass_1/` and `Pass_2/` subdirectories, appearing as five tracked deletions
  plus the two untracked directories. That reorganization was preserved.

No audio, WASAPI, hardware, or acoustic inquiry was performed.

## External Artifact Audit

Pass 1 was used only to establish specimen lineage. Its report, trace, patch,
ZIP, and verification manifest were inspected. Their SHA-256 values were,
respectively:

- `efda36e4cc460524102f758fa93888afbcf2d263a0e7e4d87dea2abe77ff406b`;
- `53ce285100d767dff51180cdc06721a0646a804d7d56975d658b5f23e5481783`;
- `798b6459720734cbfef35f7af909d18ade8b1bde2dfd307734a5befdd659c7da`;
- `3fff0aa211a591f23108d795ee4cb7d6c73b418cb27e67b1ee3083f20b2d6f6f`;
- `cd95c154dcf49bd0b199dc272da4b9bb3dd7534830007a1ab78c88de37154b8f`.

Pass 2's report, trace, manifest, and evidence ZIP were inspected directly.
Their SHA-256 values were:

- report: `3a3d10464f1a24934b3fa7e776f6f2c1152fe9e4ed6339f8eabbe449ef142a6f`;
- trace: `0a0b62c7640f528c09cf4551b1e4dfa2bdfd296cd950f7e7bc477c7841810c4b`;
- manifest: `42c32590c3be455c52c91f744c5df5fbefcee9661f86147ebdf6277b497090d0`;
- ZIP: `11528e0903df392218fb19dc93b08dd56a02b2cb4d09b4eb7dd8689854be78c7`.

The ZIP contained the packet, request, broker response, final consumer answer,
delivered public ledger, navigation delivery, withheld binding, report, trace,
and manifest. Every manifest-listed member matched its declared hash. The
external prose was not treated as repository authority.

## Revisions and Specimen Identity

The consumer-visible specimen S was Pass 1 case B's saved, complete
`current_result()` body, produced at
`2618453d233a5867757c22ff732459f701834372`. It was relabeled S outside the
body. The body has SHA-256
`58b08aba3a774d6f508b0a8a06b752476ff7a3f91664ffbeb52fc87ce86e16a9`,
reports four records, and identifies `rec-000002` as its Git observation and
`rec-000004` as the corresponding admission.

The three supplied public documents and requested public ledger came from
`55cc382e2175c57819b35c622419a9ee9d8a677b`, which is also current
authoritative `main`. Comparison from the specimen-producing revision to
current main found no change to `current_result()` structure, foreground
coordinator behavior, reconstruction code, ledger code, or the three supplied
projection/reconstruction documents. Later public prose makes the need to
retain associated ledger context explicit, but adds no binding for S.

The temporal mismatch therefore matters but does not explain away the result:
S is an older detached specimen queried through later documentation, and the
later canonical evidence reference is not declared to be S's history. The
relevant representation and record-reference semantics did not change in the
interval.

## Actual Specimen History

The withheld Pass 2 binding identifies S with Pass 1 case B's four-record
ledger. Direct reconstruction verified that ledger's saved SHA-256
`4a69685c48b2012692a74031156945181beb1fbd8f9e6ef649842dfe0106417b`,
all four record-integrity digests, and the fixture relation.

Its `rec-000002` is a `repository_git_state` observation. `head_sha`, `branch`,
and `status_porcelain` are null, while both nested signal payload and nested
observation provenance retain three real Git command failures. Reconstruction
recovers that observation unchanged and append-free. Thus the authoritative
historical outcome is degraded Git acquisition with three command failures;
the evidence is recoverable once the correct history is supplied.

The same complete S body also equals Pass 1 case A's body, whose associated
four-record history records successful clean-Git acquisition. Current Lab
trace `traces/consumer_git_acquisition_pressure_v0.json` independently contains
the same whole-body collision across newly executed healthy and degraded
histories. Body equality therefore cannot select the intended history even if
both candidate histories are available.

## Astra's Public Route

The consumer received S and these complete public documents at the later
revision:

- `docs/contracts/projection.md`;
- `docs/contracts/reconstruction.md`;
- `docs/projection/v0_observability.md`.

Both contracts legitimately name `traces/live_ingest_ledger_v0.jsonl`, so the
consumer's single evidence request was warranted. The broker returned that
entire 65,958-byte Git-blob representation with SHA-256
`2a2b4adb673df0a87855f075e464796d8ca49e2e0e59b74ea8be579ec815f03f`.
It supplied no additional association to S.

The resulting comparison is:

| Coordinate | Specimen S | Public canonical ledger |
| --- | --- | --- |
| record count | 4 | 14 |
| `rec-000002` | Git observation | admission |
| `rec-000003` | filesystem admission | Git observation |
| declared relation to S | representation-local reference | none |

The current checkout byte hash of that canonical ledger is
`0d877151c73cb2154417065387dc286a1277e80f3838c40874832a7061c17dd0`;
the difference from the delivered Git-blob hash is the already adjudicated
line-ending representation difference, not a different logical history. The
canonical ledger remained unchanged in this pass.

## Public Surface Search

The audit read the current `PROJECT_STATE.md`, `README.md`, `WORKFLOW.md`,
`AGENT_CONTEXT.md`, `docs/methods/Bounded_Research_Warrant.md`, the ledger,
ingest, projection, and reconstruction contracts, projection observability
guidance, the relevant admission/source-quality/current-result decisions, the
prior Astra adjudication, the trace index and contract map, and relevant
identity/navigation entries in the distinction registry. Repository-wide
documentation searches covered ledger/history identity, paths, roots, record
identity, canonical history, `current_result()`, and navigation/resolution
language.

The candidate routes ended as follows:

| Candidate route | Standing | Warrant boundary |
| --- | --- | --- |
| S's `observation_record_id` and `subject_record_id` | legitimate ledger-local coordinates | S carries no ledger path, root, trace, or history identity |
| contracts to `live_ingest_ledger_v0.jsonl` | legitimate public evidence discovery | no declaration binds that ledger to S; its record roles contradict such a substitution |
| README / `PROJECT_STATE.md` navigation prose | legitimate general guidance | describes navigation from supplied recorded history, but does not supply S's history |
| prior Astra adjudication | legitimate and explicit boundary | says an external caller must retain associated ledger context; it does not recover missing context |
| canonical-history language | legitimate only for the named canonical bounded trace lineage | does not make every detached `current_result()` a view of that ledger |
| Pass 1 external files or Pass 2 withheld binding | sufficient for the auditor | external experiment context, not the declared public consumer surface |
| implementation constructor/root/ledger state | sufficient for an auditor holding the coordinator | implementation knowledge is excluded and cannot infer an absent binding from S |
| bare string equality of record IDs | unsupported | record IDs are ledger-local and collide across the compared histories |
| record count or role mismatch | legitimately rejects the proposed canonical ledger as S's exact four-record history | rejection does not identify the correct history |

The public coordinates are useful only after an associated history has already
been supplied. They do not narrow, select, or authenticate a history for this
detached S. For that reason this is not classified as partially resolvable:
there is no publicly connected partial route toward the actual specimen
history, only a valid within-history route whose required starting association
is external.

## Four Separations

The evidence requires these statements to remain separate:

```text
identifier equality
!= record identity
!= history association
!= evidence recovery
```

The matching string `rec-000002` has different record roles in different
histories. A record reference becomes actionable only inside an already chosen
history. The auditor can recover S's historical evidence from its actual
ledger, but that recovery does not retroactively make the hidden association
public.

## Consumer Standing

Astra's consumer made a legitimate request, explicitly declined to infer that
the returned ledger belonged to S, identified the role/count mismatch, and
stopped with Git acquisition success unresolved. The audited response contains
no overclaim.

The consumer inherited a general DME memory summary and operated under
procedural rather than technical isolation. Therefore:

```text
strict unfamiliar consumer behavior = unresolved
```

No new model trial is needed for this repository-surface adjudication.

## Distinction Standing

No new distinction is forced. D-0002 keeps ledger record identity separate
from envelope identity; D-0026 keeps authoritative history separate from its
reconstructed representation; D-0029 prevents an experiment trace from being
substituted for authoritative history; D-0033 prevents record ID/index
sequences from establishing content identity; and D-0046 keeps structural
admissibility separate from source capture success.

Together they conserve the observed failure without promoting explanatory
phrases such as `reference != association` into the registry. This is a new
bounded operational consequence of existing distinctions, not a new
distinction or a demonstrated production defect.

## Required Outcome

```text
public_history_association_not_resolvable
```

The underlying evidence is recoverable to the auditor, but no current public
route establishes which history belongs to S. The result does not assert that
evidence was destroyed, that every navigation problem fails, or that a resolver
must be built.

## Lineage and Verification

Existing artifacts and deterministic comparisons were sufficient. No new
fixture, runtime, test, or trace was needed. This independently authored
decision and one `PROJECT_STATE.md` pointer are the complete scoped lineage.

Tests:

- baseline full suite: 472/472 passed;
- final full suite: 472/472 passed in 16.366 seconds;
- runner: `python -m unittest discover -s tests -v`;
- no audio or hardware-dependent pressure executed.

Files changed by this pass:

- this decision record;
- `PROJECT_STATE.md`.

No production module, contract, registry entry, existing trace, canonical
history, or Astra artifact was changed. The final repository gate and worktree
remain `HEAD == origin/main == 55cc382e2175c57819b35c622419a9ee9d8a677b`
with divergence `0 0`. In addition to this untracked decision and the scoped
`PROJECT_STATE.md` modification, the final worktree retains exactly the user's
initial five tracked Astra-output deletions and untracked `Pass_1/` and
`Pass_2/` directories. No trace was produced. No navigation experiment or
remedy is selected here.
