EVIDENCE INSPECTED

Repository state was inspected at commit 6737d70d614106212511a1c1cc6ba8b7e7cfee9e (Implementation).

Exact evidence used:

PROJECT_STATE.md
WORKFLOW.md
PRESSURE_RESOLUTION_MAP.md, especially PR-001 and PR-006
docs/methods/Observation_Basis/NTSF_USN_observation_basis_proposal.md
docs/methods/Observation_Basis/Astra_Basis_Perturbation.md
docs/methods/Observation_Basis/Warrant_Synthesis_Chat.md
src/runtime/ntfs_usn_observation_basis_qualification.py
tests/runtime/test_ntfs_usn_observation_basis_qualification.py
traces/ntfs_usn_observation_basis_qualification_v0.json

The adjudication is based primarily on the committed trace plus executable behavior, as required by the supplied qualification warrant.

The trace records an elevated Windows run on NTFS volume C:, an already-existing journal, frozen V2/64-bit identity semantics, READ_USN_JOURNAL_DATA_V1, ReturnOnlyOnClose=1, ReasonMask=USN_REASON_CLOSE, SourceInfo == 0, and manual CLOSE + DATA_OVERWRITE conjunction.

WARRANT COMPLIANCE

PASS

No material violation of the frozen warrant was found.

The run satisfies the required coordinates:

NTFS qualification: trace reports filesystem NTFS.
Journal availability: FSCTL_QUERY_USN_JOURNAL succeeded before mutation.
Journal continuity: both arms retained the same UsnJournalID, same identified volume, and valid FirstUsn / LowestValidUsn relationships.
Independent intervals: AA used [26215184240,26215184432) while AB used [26215184720,26215184912). They were not one shared interval.
Exact S/E freezing: runtime takes S = before_journal.NextUsn, performs the controlled lifecycle, then obtains E = after_journal.NextUsn; reading happens afterward. There is no code path extending E to obtain a desired match.
Read cursor behavior: read_interval() advances from the returned continuation USN, explicitly rejects non-advancing cursors, and stops once the continuation reaches or exceeds frozen E.
Version constraint: V1 request fixes major version 2, parser rejects any returned non-V2 record.
Complete fileID64 association: runtime constructs the full unsigned high << 32 | low ID and record acceptance compares the complete value against FileReferenceNumber. The retained trace reports the same complete ID 0x002B00000002AA60 throughout both arms.
File continuity: baseline, writer, and final endpoint IDs agree.
Lifecycle: baseline observation handles are closed before S; the writer is opened after S with share mode 0, exactly one synchronous write is issued, buffers are flushed, and the writer closes before E.
Final-close behavior: accepted records carry both USN_REASON_CLOSE and USN_REASON_DATA_OVERWRITE.
Conjunction: acceptance tests the two bits independently; tests explicitly verify that CLOSE alone fails acceptance.
SourceInfo: both accepted records report 0, satisfying the predeclared fixture policy.
Endpoint observation: AA's final SHA-256 equals its A baseline; AB's final SHA-256 equals independently defined B and differs from A.
No semantic widening: runtime's explicit adjudication only reports a local operation-category basis and says the witness does not discriminate logical endpoint inequality.

One wording residue exists: the warrant used “reproducibly observed” in its success criterion, but did not specify repeated independent executions as a required replication schedule. The executable warrant defined one AA and one AB arm, and both were completed. That wording does not justify retroactively requiring another run.

AA ADJUDICATION

AA independently observed:

$$ A \rightarrow A $$

at the endpoint-content basis.

The baseline and final endpoint both have SHA-256:

6896d9ea3f73a4434f5832bc65714e7d066f177373f36f34dc8a6f735daa41b1

and both are recorded as 4096 bytes of A. The same complete file identity is preserved.

Inside AA's separately frozen journal interval, one V2 record for that complete file ID had:

$$ Reason = CLOSE \;|\; DATA\_OVERWRITE $$

with SourceInfo = 0, and every frozen acceptance check passed.

Therefore AA establishes, for this bounded fixture:

NTFS recorded its selected unnamed-data overwrite operation category during a controlled overwrite for which independently observed endpoint logical content remained A.

This directly falsifies the bounded implication:

$$ DATA\_OVERWRITE \Rightarrow \text{logical endpoint inequality}. $$

It does not establish that every identical-byte write always generates this record, nor does it establish anything about arbitrary NTFS write regimes.

AB ADJUDICATION

AB contains two independent evidential coordinates.

Endpoint-content evidence establishes:

$$ A\rightarrow B $$

because the baseline endpoint hashes to A and the final endpoint hashes to the independently frozen B value:

725bcd6c66d02acf6ebeab9c92410e010ea22e336876256aaf05a211f4ce1902

while file identity and length remain constant.

USN evidence independently establishes that, inside AB's frozen interval, the same selected file ID had a valid V2 record with CLOSE + DATA_OVERWRITE, SourceInfo = 0, and all acceptance predicates satisfied.

Thus:

$$ \text{endpoint basis} \Rightarrow A\rightarrow B $$

while separately:

$$ \text{USN basis} \Rightarrow \text{recorded overwrite-operation category}. $$

The fact that the experiment intentionally issued B is not doing the epistemic work of the native observations; both endpoint content and USN operation evidence are actually retained in the trace.

CROSS-ARM ADJUDICATION

The strongest joint inference is:

$$ \boxed{ DATA\_OVERWRITE \text{ occurred as qualified USN evidence in both } A\rightarrow A \text{ and } A\rightarrow B } $$

under the two independently bounded controlled lifecycles.

The committed cross-arm adjudication itself reports:

LOCAL BASIS QUALIFIED

and:

DATA_OVERWRITE was observed for both A->A and A->B; the operation-category witness does not discriminate logical endpoint inequality in this fixture.

That inference is warranted by the underlying records, not merely by the summary label.

QUALIFIED BASIS

The minimum basis actually earned is:

$$ \boxed{ \begin{aligned} &\text{identified NTFS volume}\\ +&\text{identified current USN journal instance}\\ +&\text{frozen source-local }[S,E)\text{ interval}\\ +&\text{complete V2 64-bit file-reference association}\\ +&\text{fresh isolated controlled write lifecycle}\\ +&\text{completed bounded V2 acquisition}\\ +&\text{associated CLOSE + DATA\_OVERWRITE record}\\ \Rightarrow& \text{bounded NTFS overwrite-operation-category evidence}. \end{aligned} } $$

The exact SourceInfo == 0 policy was part of this qualification realization and should remain part of its empirical scope, even though it is not intrinsic to the abstract meaning of DATA_OVERWRITE.

The qualified basis is not:

content-transition observation;
all NTFS event observation;
general filesystem change observation;
Windows observation;
repository semantic observation.
REFUTED OR FAILED STRONGER CLAIM

REFUTED UNDER THE QUALIFIED FIXTURE:

$$ \boxed{ DATA\_OVERWRITE \Rightarrow \text{logical endpoint byte inequality} } $$

This is stronger than merely “not supported.”

AA is a direct counterexample within the admitted regime:

$$ \text{DATA\_OVERWRITE}=true $$

while:

$$ A_{\text{endpoint before}} = A_{\text{endpoint after}}. $$

Therefore DATA_OVERWRITE cannot be used as a discriminator of endpoint inequality in this fixture.

The broader universal claim about every possible NTFS regime is not adjudicated.

REPEATABILITY STATUS

useful residue

Repeat-run stability under another independent execution of the exact frozen fixture is not established.

It is also not a blocker to accepting this qualification.

The frozen warrant asked whether the basis could be successfully realized under the declared AA/AB qualification and did not predeclare an \(n>1\) replication requirement. The current run supplies one complete realization of each prescribed arm, with the operation-category witness occurring in both.

Under the Lab workflow, evidence earns only its bounded scope; unresolved recurrence can remain residue rather than being retroactively converted into a failed success condition. The workflow explicitly allows bounded resolution while preserving what remains unknown.

Thus the present standing is:

one bounded local realization on this machine, volume, journal instance, selected file object, and execution.

OPERATION / CONTENT BASIS SEPARATION

Empirically earned within the fixture.

The experiment now contains two independently observed coordinates:

$$ \text{CONTENT BASIS} = \text{endpoint bytes/hash} \rightarrow \text{logical endpoint state} $$

and:

$$ \text{USN BASIS} = \text{journal + file identity + reason} \rightarrow \text{NTFS overwrite-operation category}. $$

AA is the decisive separation specimen:

$$ \text{content basis}: A=A $$

while:

$$ \text{operation basis}: DATA\_OVERWRITE=true. $$

So the distinction is no longer merely conceptual.

Their blind spots differ.

The endpoint-content basis cannot expose a departure that returns before the next endpoint observation:

$$ A\rightarrow B\rightarrow A $$

may still appear as \(A,A\).

The USN operation basis can expose a qualifying overwrite-category occurrence but cannot establish what intermediate bytes were, whether bytes became unequal, or whether a hidden content excursion occurred.

Neither basis is complete.

PR-006 BLOCKER AUDIT

The second PR-006 blocker is now partially removed for the bounded operation-category question.

The map at the inspected commit still says PR-006 is OPEN and blocked by:

concrete consumer need and a separately justified bounded observation basis.

This experiment supplies an independently justified bounded observation basis for:

did the selected file undergo at least one qualifying NTFS unnamed-data overwrite-category operation under the qualified regime?

It does not supply a basis sufficient for:

did the selected file's logical content depart from A and later return to A?

Therefore:

bounded NTFS operation basis: now empirically justified;
exact PR-006 consumer selection: still needs freezing;
content-traversal observation: unresolved;
PR-006 itself: still unresolved and must not be activated or marked resolved by this adjudication.
NEXT CONSUMER FORK

Q_OPERATION:

Between equivalent endpoint captures, did the selected file undergo at least one qualifying NTFS unnamed-data overwrite-category operation?

Current USN basis: sufficient to pressure this question, within the exact qualified volume/journal/file/lifecycle semantics.

Q_CONTENT:

Between equivalent endpoint captures, did the selected file's logical content actually depart from A and later return to A?

Current USN basis: insufficient by itself.

The exact missing distinction is:

$$ \boxed{ \text{overwrite-category occurrence} \neq \text{logical content departure}. } $$

AA demonstrates why. The USN basis can report DATA_OVERWRITE even though independent endpoint observations remain \(A,A\). Therefore it cannot tell whether the operation was:

$$ A\rightarrow A $$

or involved some logically distinct intermediate content.

The current evidence does not authorize inventing the sensor or basis that would close that distinction.

FIRST STITCHING RESIDUE

Combining:

$$ \text{endpoint content evidence} + \text{qualified USN operation evidence} $$

can recover something neither alone provides:

equal endpoint content together with evidence that at least one qualifying overwrite-category operation occurred during the bounded interval.

That is already a meaningful stitched distinction:

$$ A\;[\text{endpoint}] \quad+\quad \text{overwrite occurred} \quad+\quad A\;[\text{endpoint}] $$

versus endpoint-only apparent stasis.

But the combination still cannot distinguish:

$$ A\rightarrow A $$

from:

$$ A\rightarrow B\rightarrow A. $$

Both can be compatible with:

$$ \text{endpoint }A,A + \text{at least one DATA\_OVERWRITE-category operation}. $$

Thus the smallest unresolved stitching distinction is:

$$ \boxed{ \text{operation during equal endpoints} \neq \text{logical hidden content excursion}. } $$

Another basis would be required to discriminate those histories, but this adjudication does not select or design it.

LOCAL / GLOBAL AUDIT

Bounded NTFS operation-category basis — LOCAL-ONLY SURVIVOR

It solves the qualification question locally. Broader recurrence and portability remain unresolved.

Operation \(\neq\) logical content inequality — LOCALLY + COMPOSITIONALLY EARNED

The AA counterexample directly establishes this boundary, and preserving it prevents future semantic strengthening.

Repeat-run stability — BASIS INSUFFICIENT

A second independent execution has not been observed. This is useful residue, not a qualification blocker.

Operation/content basis distinction — LOCALLY + COMPOSITIONALLY EARNED

AA and AB empirically separate operation-category evidence from endpoint-content evidence.

Possible content + operation composition — COMPOSITIONALLY COMPATIBLE

The retained evidence can be combined without flattening either coordinate, and the combination exposes “activity despite equal endpoints.” No generalized composition machinery is locally required.

Generalized Windows event observer — OVERBUILT

Nothing in this fixture earns Windows-wide event capture.

Shared observational geometry — OVERBUILT

The experiment earns two distinct bounded evidence regimes and a legitimate question about their combination; it does not earn an atlas, transition system, or generalized geometry.

This follows the Lab's explicit rule:

$$ \text{global compatibility}\not\Rightarrow\text{local necessity} $$

and:

$$ \text{local sufficiency}\not\Rightarrow\text{global architecture}. $$
QUALIFICATION ADJUDICATION VERDICT

QUALIFICATION ADJUDICATION PASSES

The completed experiment legitimately establishes the bounded local basis claimed by the frozen warrant.

The phrase:

LOCAL BASIS QUALIFIED

is warranted.

Its exact epistemic scope is:

On this bounded realization, under the frozen NTFS volume, journal, file-identity, interval, lifecycle, read, and acceptance semantics, the USN basis successfully exposed the selected file's NTFS unnamed-data overwrite operation category.

It does not resolve PR-006.

REPOSITORY UPDATE HANDOFF

QUALIFIED OBSERVATION BASIS: Identified NTFS volume + identified USN journal instance + independently frozen [S,E) interval + complete V2 64-bit selected-file identity association + fresh controlled lifecycle + valid completed V2 acquisition + associated CLOSE + DATA_OVERWRITE record under the frozen SourceInfo == 0 policy → bounded NTFS unnamed-data overwrite-operation-category evidence.

EMPIRICALLY SEPARATED DISTINCTION: Endpoint logical-content state and NTFS overwrite-operation-category evidence are distinct observation coordinates; AA retained endpoint A while independently yielding a qualifying DATA_OVERWRITE + CLOSE record.

REFUTED STRONGER CLAIM: Within the qualified fixture, DATA_OVERWRITE → logical endpoint byte inequality is directly refuted.

REPEATABILITY RESIDUE: Repeat-run stability of the identical frozen qualification remains untested; it is useful residue, not a prerequisite for accepting this one bounded realization.

PR-006 BASIS BLOCKER: The separately justified bounded-basis blocker is removed for the qualified NTFS operation-category consumer question, but remains unresolved for logical hidden-content traversal; PR-006 itself remains OPEN.

Q_OPERATION: Between equivalent endpoint captures, did the selected file undergo at least one qualifying NTFS unnamed-data overwrite-category operation? Current qualified USN basis is fit to pressure this question.

Q_CONTENT: Between equivalent endpoint captures, did the selected file's logical content actually depart from A and later return to A? Current USN basis is insufficient by itself.

SMALLEST UNRESOLVED STITCHING DISTINCTION: Equal endpoint content + qualifying overwrite occurrence still cannot discriminate A → A from logical hidden A → B → A.

AUTHORIZED NEXT ACTION: Preserve this adjudication as bounded evidence and explicitly choose/freeze the next consumer question before any further experimental pressure.

UNAUTHORIZED NEXT ACTIONS: Do not mark PR-006 resolved or active automatically; do not run A → B → A; do not introduce another sensor/basis; do not generalize to NTFS/Windows event observation; do not create observational geometry; do not modify runtime or schemas on the authority of this adjudication alone.