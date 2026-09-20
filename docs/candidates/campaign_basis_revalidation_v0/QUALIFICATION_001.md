# CAMPAIGN_BASIS_REVALIDATION_001 — QUALIFICATION_001

## Status

\`\`\`text
BOUNDED MECHANICAL QUALIFICATION
QUALIFIED AT RECORDED IMPLEMENTATION HEAD
CAMPAIGN ADOPTION: NONE
DOGFOOD RETRY: NO
MERGE: NOT AUTHORIZED
\`\`\`

## Frozen contract basis

\`\`\`text
contract PR:
#48

contract branch:
campaign-basis-revalidation-contract-v0

contract head:
3c3344bc1366596832f47b3fb627b5eaad486017
\`\`\`

The implementation does not modify either frozen contract document.

## Executed implementation basis

\`\`\`text
implementation branch:
campaign-basis-revalidation-v0

executed implementation head:
0d9f0c7b322345fadb570eaa4b51d2058b1e2550

implementation PR:
#49
DRAFT
UNMERGED
\`\`\`

## Exact apparatus identities

\`\`\`text
tools/campaign_basis_revalidation_v0.py
251e5b7dafbba1168af2c077a3eec0d831bbe2fd

tests/runtime/test_campaign_basis_revalidation.py
bb1aef3d22e2daf979e6eeb510cacef24abf211d

.github/workflows/campaign-basis-revalidation-001.yml
32682da0955bf15c4dcd3eeb2344c8c435464a12
\`\`\`

The primary historical specimen remained:

\`\`\`text
COCKPIT_OPERATING_SPACE_001
\`\`\`

with its exact historical qualification artifact independently resolved as the
Git blob:

\`\`\`text
docs/candidates/wake_source_v0/QUALIFICATION_001.md
ee721faebb5f2a3e6780d20b7a558043e164a5b3
\`\`\`

The historical \`@ee721...\` coordinate is a Git blob identity, not a commit
identity. The apparatus preserves that distinction.

## Requirement-derivation mechanism

The first apparatus derives requirements only from exact coordinates that the
historical campaign itself already grounds:

1. each \`qualification:<path>@<git-blob-sha1>\` entry in historical
   \`basis_refs\`;
2. each exact \`NO_<EFFECT>\` entry in
   \`explicit_non_authorizations\`.

The caller cannot supply or reduce the derived requirement set.

For a qualification requirement the apparatus independently computes the Git
blob identity of raw supplied artifact content and checks whether the candidate
basis declares that exact content-addressed artifact.

For a non-authorization requirement the caller supplies raw event references;
the apparatus independently evaluates whether the observed event count is zero.

No input field accepts:

\`\`\`text
campaign_currently_applicable
surface_compatible
requirement_passed
dependency_still_valid
semantic_equivalence
\`\`\`

## Raw evidence shapes

The bounded v0 raw evidence membrane accepts only:

\`\`\`text
campaign_artifact_evidence_v0
- artifact_ref
- raw text content
\`\`\`

and:

\`\`\`text
campaign_effect_trace_v0
- effect
- raw event_refs[]
\`\`\`

Storage/history annotations such as \`_seq\` are excluded before durable
evidence identity is computed.

## Dedicated store

The implementation uses only:

\`\`\`text
campaign_basis_revalidations
\`\`\`

inside a dedicated SQLite revalidation store.

The store retains:

\`\`\`text
revalidation_id
result_sha256
campaign_id
campaign_sha256
candidate_current_basis_sha256
disposition
exact result_json
\`\`\`

The SQLite sequence is retrieval metadata and is not part of the durable
revalidation object.

Replay behavior observed:

\`\`\`text
same revalidation_id + exact same durable bytes
→ idempotent replay

same revalidation_id + changed durable bytes
→ REJECT
\`\`\`

## Executed workflow evidence

\`\`\`text
workflow:
CAMPAIGN_BASIS_REVALIDATION_001

run:
35511635228

job:
106080435898

executed head:
0d9f0c7b322345fadb570eaa4b51d2058b1e2550

conclusion:
SUCCESS
\`\`\`

The focused pressure command was:

\`\`\`text
python -m unittest tests.runtime.test_campaign_basis_revalidation -v
\`\`\`

Observed:

\`\`\`text
Ran 17 tests in 0.146s
OK
\`\`\`

## R1–R10 observed results

\`\`\`text
R1  exact same basis
    CURRENTLY_APPLICABLE
    exact replay idempotent
    campaign bytes unchanged
    PASS

R2  basis moved / every grounded requirement established
    CURRENTLY_APPLICABLE
    removing required qualification evidence becomes INSUFFICIENT_BASIS
    Git movement alone does not pass
    PASS

R3  required qualification artifact changed
    replacement lacks an independently qualified continuity relation
    INSUFFICIENT_BASIS
    PASS

R4  raw forbidden-effect trace contains a grounded violating event
    NOT_APPLICABLE
    standing effect remains NONE
    PASS

R5  content-addressed unrelated basis coordinate added
    deterministic campaign-grounded requirement set unchanged
    all grounded requirements established
    CURRENTLY_APPLICABLE
    PASS

R6  same campaign_id label / different valid campaign bytes
    prior revalidation does not transfer
    independent campaign identity required
    PASS

R7  successful revalidation
    adoption NONE
    selection NONE
    standing NONE
    authority NONE
    execution NONE
    priority NONE
    scheduler NONE
    PASS

R8  later failure
    prior result retained
    historical campaign bytes unchanged
    no destructive rewrite
    PASS

R9  success against B2 / query against B3
    B2 result remains historical
    B3 applicability NOT_ESTABLISHED
    PASS

R10 answer-key fields at request or evidence boundary
    REJECT
    PASS
\`\`\`

## Additional adversarial results

\`\`\`text
A1
same exact campaign input
→ deterministic requirement derivation
PASS

A2
derived result with one grounded requirement omitted
→ store validation rejects
PASS

A3
raw evidence ordering reversed
→ identical durable result
PASS

A4
storage metadata _seq added to raw evidence / history row
→ durable identity unchanged after metadata stripping
PASS

A5
same revalidation_id + changed durable result
→ rejected
PASS

A6
git:HEAD or other non-content-addressed candidate basis
→ rejected

explicit 40-hex Git basis
→ accepted
PASS

A7–A10
dedicated revalidation write executed while campaign,
selection, preparation, assignment, reentry, wake,
and controller stores were independently hashed

all operational store bytes:
UNCHANGED
PASS
\`\`\`

## Inherited regressions observed on the same workflow run

Every step completed successfully:

\`\`\`text
DEVELOPMENT_CAMPAIGN_001 regression
PASS

ENVELOPE_SELECTION_001 regression
PASS

PREPARATION_001 regression
PASS

PREPARATION_ASSIGNMENT_001 regression
PASS

WAKE_SOURCE_001 regression
PASS

BOUNDED_REENTRY_001 regression
PASS

COCKPIT_CONTROL_ADAPTER_001 regression
PASS

Cockpit control UI regression
PASS
\`\`\`

The development-campaign regression specifically retained:

\`\`\`text
basis drift
→ STALE
without rewriting campaign
\`\`\`

The new revalidation relation exists beside that conservative baseline; it does
not weaken or replace \`CampaignStore.snapshot(...)\`.

## Failures encountered

\`\`\`text
EXECUTED PRESSURE FAILURES:
NONE

CI FAILURES:
NONE
\`\`\`

Pre-implementation source inspection did catch one identity-classification rake:

\`\`\`text
qualification:...@ee721fae...
!=
Git commit coordinate

ee721fae...
=
exact Git blob identity
\`\`\`

No contract repair was required.

## Repairs made

\`\`\`text
NONE
\`\`\`

No implementation repair was required after the first executed CI pass.

## Claim ceiling

This qualification supports only:

\`\`\`text
ONE EXACT HISTORICAL CAMPAIGN

CAN RECEIVE ONE DURABLE,
BASIS-RELATIVE CURRENT-APPLICABILITY JUDGMENT

AGAINST ONE EXACT CURRENT BASIS

FROM REQUIREMENTS DETERMINISTICALLY GROUNDED
IN THAT HISTORICAL CAMPAIGN'S
PINNED QUALIFICATION ARTIFACTS
AND EXPLICIT NON-AUTHORIZATIONS,

USING RAW INSPECTABLE ARTIFACT CONTENT
AND RAW EFFECT-EVENT REFERENCES,

WITHOUT REWRITING HISTORY
OR CREATING:

ADOPTION
SELECTION
ASSIGNMENT
PRIORITY
STANDING
AUTHORITY
SCHEDULER
WAKE
OR EXECUTION.
\`\`\`

## Known residue

The v0 apparatus does **not** establish general semantic equivalence.

In particular:

\`\`\`text
changed required qualification blob
!=
semantically equivalent replacement
\`\`\`

A changed required qualification surface with no independently admitted
replacement continuity proof yields:

\`\`\`text
INSUFFICIENT_BASIS
\`\`\`

not optimistic applicability.

The positive R2/R5 cells establish only the narrower tested relation:

\`\`\`text
repository / world basis may move

WHILE

every campaign-grounded qualification artifact
retains exact content identity

AND

every campaign-grounded non-authorization
has a mechanically empty raw effect trace

→
basis-relative CURRENTLY_APPLICABLE
may be retained
\`\`\`

This does not establish:

\`\`\`text
general code-impact analysis
general semantic-equivalence checking
general campaign portability
campaign adoption
autonomous development
scheduler safety
or DOGFOOD_001 continuation
\`\`\`

## Effect boundary

\`\`\`text
CAMPAIGN MUTATION:
NO

CAMPAIGN ADOPTION:
NONE

SELECTION:
NONE

ASSIGNMENT:
NONE

BELL:
NONE

WAKE:
NONE

STANDING EFFECT:
NONE

AUTHORITY EFFECT:
NONE

EXECUTION EFFECT:
NONE

PRIORITY EFFECT:
NONE

SCHEDULER EFFECT:
NONE

DOGFOOD RETRY:
NO

MERGE:
NO
\`\`\`
