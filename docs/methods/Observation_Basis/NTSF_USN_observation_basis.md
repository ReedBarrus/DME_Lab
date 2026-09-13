INPUT ARTIFACTS USED
Repository authority:
- PROJECT_STATE.md
- WORKFLOW.md
- PRESSURE_RESOLUTION_MAP.md
- docs/decisions/absent_interval_round_trip_pressure_v0.md
- docs/methods/Candidate_Pressure_Debate_Protocol_v0.md
- docs/projection/consequential_geometry_A.md
- docs/projection/Consequence_Formal_B.md
Completed debate artifacts:
- docs/methods/Debate_Content/Pass_1/Pass_1_Chat_Advocate.md
- docs/methods/Debate_Content/Pass_1/Pass_1_Astra.md
- docs/methods/Debate_Content/Pass_1/Pass_1_Codex_Experimentalist.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Astra_Advocation.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Codex_Experimentalist.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Chat_Adversary.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Codex_Null_Claim.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Chat_Null_Adversary.md
- docs/methods/Debate_Content/Pass_2/Pass_2_Astra_Final.md
The final A/B/Null experimental adjudication, identified by content, is docs/methods/Debate_Content/Pass_2/Pass_2_Astra_Final.md. It closes the candidate cycle, not PR-006, and recommends seeking a concrete observer basis.
Authoritative Microsoft documentation:
- Change Journals
- Change Journal Records
- Using the Change Journal Identifier
- Creating, Modifying, and Deleting a Change Journal
- FSCTL_QUERY_USN_JOURNAL
- USN_JOURNAL_DATA_V0
- USN_JOURNAL_DATA_V2
- FSCTL_READ_USN_JOURNAL
- READ_USN_JOURNAL_DATA_V0
- READ_USN_JOURNAL_DATA_V1
- USN_RECORD_V2
- [MS-FSCC] USN_RECORD_V2
- BY_HANDLE_FILE_INFORMATION
- FILE_ID_INFO
- Obtaining a Volume Handle for Change Journal Operations
- CreateFile volume-handle requirements
CANDIDATE NATIVE SOURCE
The candidate source is the NTFS filesystem implementation maintaining the per-volume USN Change Journal.
More precisely:
- Observed subject: the unnamed data stream of one selected NTFS file object.
- Native event generator and ordering regime: NTFS on the containing volume.
- Durable observation substrate: that volume’s current USN journal instance.
- DME role: reader and interpreter of returned journal records.
- Path: locator only, not object identity.
- SourceInfo: supplemental operation-source flags, not the selected source identity or reliable actor attribution.
NTFS appends records describing changes to filesystem objects to one journal stream per volume. The journal records a change category and affected object, not a reversible history. Microsoft’s journal overview
MINIMUM NTFS BASIS
The minimum qualified basis is:
confirmed NTFS volume identity
+ current UsnJournalID
+ start NextUsn
+ end NextUsn
+ retained-range continuity
+ supported USN record version
+ selected file ID
+ matching record FileReferenceNumber
+ qualifying Reason bit
+ interpreted SourceInfo
+ close/emission discipline
+ explicit invalid/unresolved states
Smallest native interface set:
1. Open the volume and use FSCTL_QUERY_USN_JOURNAL.
2. Retain at least UsnJournalID, FirstUsn, NextUsn, and LowestValidUsn.
3. Obtain the selected file ID from an open file handle.
4. Read with FSCTL_READ_USN_JOURNAL and a READ_USN_JOURNAL_DATA request containing StartUsn, ReasonMask, ReturnOnlyOnClose, and UsnJournalID.
5. Parse only supported USN_RECORD major versions.
6. Match the record’s FileReferenceNumber to the selected file ID.
USN_JOURNAL_DATA_V0 contains the required continuity coordinates. V2 additionally exposes supported record-version and range-tracking information and is useful when available. READ_USN_JOURNAL_DATA_V1 lets the caller constrain acceptable record major versions.
FSCTL_ENUM_USN_DATA, journal creation, journal deletion, and range tracking are not required for the first qualification.
JOURNAL IDENTITY
UsnJournalID is a 64-bit identifier for the current journal instance. NTFS assigns an identifier on creation and may stamp a new identifier when existing records are or may be unusable. Delete/recreate can restart USNs at zero; restamping can preserve the increasing USN sequence. Consequently, USN values alone do not establish continuity. Using the journal identifier
The bounded comparison regime is:
(volume identity, UsnJournalID)
Required continuity checks at the end of the interval:
- Same volume.
- Same UsnJournalID.
- Starting USN still readable: start >= current FirstUsn.
- Starting USN not below the current instance’s validity boundary: start >= current LowestValidUsn.
- No ERROR_JOURNAL_ENTRY_DELETED.
- No journal deletion or recreation in progress.
- Complete consumption of the requested retained interval.
FirstUsn is the earliest currently readable record. NextUsn is the USN for the next record to be written. LowestValidUsn can expose a journal discontinuity where changes may not be recorded. Journal trimming can advance FirstUsn beyond a previously saved start. USN_JOURNAL_DATA_V0 semantics
A reboot does not by itself prove discontinuity. The executor must re-query journal identity and continuity. The first specimen should exclude reboot, journal deletion, and journal recreation.
FILE IDENTITY
For a V2 journal record, FileReferenceNumber is the 64-bit file ID of the affected object. For record formats using 128-bit identifiers, the corresponding 128-bit representation must be used. The record’s declared major version must determine its parser and identity representation. [MS-FSCC] record semantics
For the first NTFS specimen:
- Obtain the file ID through its handle.
- Retain the containing volume serial or equivalent volume identity.
- Match that ID to the journal record’s FileReferenceNumber.
- Re-open after intervention and confirm the same file ID.
- Exclude delete, recreate, replace, rename, and hard-link manipulation.
On NTFS, a file normally retains its file ID until deletion. File IDs are not guaranteed unique forever and may be reused. ReplaceFile leaves the target path associated with the replacement file’s identity, not the original file object. BY_HANDLE_FILE_INFORMATION
Therefore:
path != file identity
same path after replacement != same file object
file reference != permanent universal identity
ORDERING SEMANTICS
A record’s USN is its position in the per-volume journal stream. New records are appended, and each record carries its own USN. Within one retained journal instance, USNs provide source-local journal ordering. Change Journal Records
A proposed frozen interval is:
S = initial NextUsn
E = final NextUsn
accepted record range = [S, E)
FSCTL_READ_USN_JOURNAL begins at StartUsn; the request structure does not carry the frozen upper bound. The future reader must therefore apply E client-side and accept only records satisfying:
S <= record.Usn < E
It must continue reading until that retained range is exhausted.
USN ordering does not establish:
- wall-clock simultaneity;
- physical write order;
- causal order;
- application-level transaction order;
- mutation count;
- cross-volume ordering;
- cross-source coherence.
TimeStamp is not needed for this bounded source-local discriminator.
RELEVANT-CHANGE SEMANTICS
For the smallest qualification specimen, narrow the predicate further to:
NTFS recorded an in-place, same-length overwrite operation on the unnamed data stream of the selected file object.

The qualifying reason is:
USN_REASON_DATA_OVERWRITE = 0x00000001
The broader in-place file-data family is:
USN_REASON_DATA_OVERWRITE   0x00000001
USN_REASON_DATA_EXTEND      0x00000002
USN_REASON_DATA_TRUNCATION  0x00000004
Named-stream variants are outside the first scope. Metadata, rename, security, create/delete, and directory reasons are also excluded. Documented reason meanings
The initial controlled fixture should expect ordinary SourceInfo == 0. Records marked as auxiliary or data-management activity require separate interpretation because Microsoft documents cases where filesystem writes do not change application data.
A qualifying reason supports:
NTFS recorded an operation in the declared unnamed-data change category.

It does not alone support:
The logical byte sequence necessarily became different.

An overwrite of identical bytes may still produce USN_REASON_DATA_OVERWRITE.
RECORD-EMISSION SEMANTICS
Reason flags accumulate from the opening of a file until final close. A new reason type can generate another journal record, but repeated operations of a reason type already present may not create additional records. The final close record adds USN_REASON_CLOSE; it summarizes accumulated reasons without preserving their order. Microsoft’s accumulation example
Consequences:
- Several writes may collapse into one overwrite indication.
- One mutation may contribute to multiple records.
- Record count does not equal mutation count.
- The close summary does not encode operation order.
- A record is a partial traversal witness, not a hidden path.
Smallest clean discipline:
1. Establish baseline contents and close every known handle.
2. Freeze the starting NextUsn.
3. Open the file once.
4. Perform one same-length overwrite.
5. Close the writing handle.
6. Query the ending NextUsn only after close.
7. Read the frozen interval.
ReturnOnlyOnClose != 0 may be used with USN_REASON_CLOSE included in ReasonMask to request finalized close records. Alternatively, non-close-only reading can observe the first logged change. The qualification should choose one mode in advance and not mix their interpretations. READ_USN_JOURNAL_DATA close semantics
The cleanest first fixture uses the finalized close summary.
POSITIVE WARRANT
The following evidence would support YES:
1. Endpoint capture C0 completed.
2. The selected object’s file ID and containing volume identity were recorded.
3. Query J0 returned active journal identity J and S = J0.NextUsn.
4. The same file object was overwritten in place and the writing handle closed.
5. Query J1 returned the same journal identity and E = J1.NextUsn.
6. The interval beginning at S remained readable and valid.
7. An accepted record had:
   - a supported major version;
   - S <= Usn < E;
   - FileReferenceNumber equal to the selected file ID;
   - Reason containing USN_REASON_DATA_OVERWRITE;
   - no unresolved SourceInfo qualification.
8. Endpoint capture C1 occurred after E.
This supports only:
NTFS recorded at least one qualifying same-file unnamed-data overwrite operation after C0 and before C1.

It does not identify the writer, prove the intended bytes were written, or reconstruct the intermediate state.
NEGATIVE WARRANT
NO is not presently authorized by this documentation-only qualification pass.
A future scoped negative would require:
- the exact relevant-change class to be closed;
- documented and locally verified detection coverage for that class;
- the entire endpoint interval to be associated with the journal window;
- same volume and UsnJournalID;
- S retained through the completed read;
- no FirstUsn or LowestValidUsn discontinuity;
- all accepted record versions understood;
- the complete [S,E) range consumed;
- correct reason mask;
- all relevant file handles finalized as required;
- no reset, rollover, recreation, acquisition failure, or malformed record;
- confirmed continuous file identity;
- no unresolved SourceInfo case;
- no boundary gap permitting mutation between endpoint capture and USN freezing.
For a future negative-control fixture, exclusive file handles could close the sequential boundary gaps: hold the file against writers while relating C0 to S, and again while relating E to C1.
Only after those conditions survive local pressure could absence support:
No NTFS-recorded operation in the declared same-file data-change class occurred during the bounded interval.

Even then, it would not establish complete physical or semantic stasis.
INVALID / UNRESOLVED CONDITIONS
Return INVALID or UNRESOLVED rather than NO when any of these occurs:
- Volume is not NTFS.
- No active journal exists.
- Volume handle or journal query/read fails.
- UsnJournalID changes.
- Journal deletion is in progress.
- Saved start is below FirstUsn.
- Saved start is below the applicable LowestValidUsn.
- ERROR_JOURNAL_ENTRY_DELETED occurs.
- Read ends before the frozen interval is exhausted.
- Record major version is unsupported.
- Record length or layout is malformed.
- Record USN lies outside [S,E).
- File reference does not match.
- File was deleted, recreated, or replaced.
- Only named-stream, metadata, rename, or other out-of-scope reasons appear.
- SourceInfo makes application-data interpretation ambiguous.
- The change handle remains open and expected close emission is unavailable.
- Endpoint-to-journal boundary association is ambiguous.
- No record is found while completeness remains unqualified.
PERMISSION / ENVIRONMENT REQUIREMENTS
The containing volume must be NTFS, and a journal must already exist. Journals are not necessarily created at startup. Creating, resizing, deleting, or re-creating one is an administrator operation and is outside this qualification. Journal lifecycle documentation
Microsoft documents administrator privileges for change-journal operations. A later executor should use an elevated process to open the volume as \\.\X: with OPEN_EXISTING and an appropriate sharing mode, then call DeviceIoControl. Volume-handle requirements
No normal-user route is assumed or qualified.
Read-only environment inspection established:
- Workspace volume C: is NTFS.
- C: is a fixed, healthy volume.
- The present process has an elevated administrator token.
The journal’s existence, identity, retained range, and readability were deliberately not queried. No journal experiment was run.
MINIMUM QUALIFICATION FIXTURE
Do not execute yet.
1. Select a disposable file on confirmed NTFS volume C:.
2. Create same-length baseline bytes A; close the creation handle.
3. Open the file, capture:
   - content hash A;
   - volume serial/identity;
   - file ID;
     then close it.
4. Query the current journal:
   - UsnJournalID;
   - FirstUsn;
   - LowestValidUsn;
   - S = NextUsn;
   - supported record versions if available.
5. Open the same existing file without truncate/create semantics.
6. Confirm its file ID is unchanged.
7. Overwrite the unnamed stream with different same-length bytes B.
8. Close the writing handle.
9. Query the journal again and freeze E = NextUsn.
10. Require:
    - unchanged volume identity;
    - unchanged UsnJournalID;
    - S >= FirstUsn;
    - S >= LowestValidUsn.
11. Read from S using the frozen journal ID and supported record-version range.
12. Inspect only records with Usn < E.
13. Require one record matching:
    - selected file ID;
    - USN_REASON_DATA_OVERWRITE;
    - predeclared acceptable SourceInfo;
    - finalized close discipline.
14. Re-open the file and confirm:
    - same file ID;
    - endpoint hash B.
Qualification outcomes:
matching record found       → positive basis observed
no record                   → basis weakened; not NO
identity/journal break      → INVALID
unsupported record format   → INVALID
ambiguous reason/source     → UNRESOLVED
This is an A → B qualification only. It does not execute A → B → A or activate PR-006.
CLAIMS THIS BASIS WOULD NOT SUPPORT
The basis would not establish:
- exact intermediate bytes;
- complete hidden history;
- mutation count;
- actor identity;
- intent or cause;
- semantic consequence;
- caller acknowledgement;
- persistence to physical media;
- cross-source simultaneity;
- wall-clock or causal ordering;
- cross-volume ordering;
- repository or Git semantic change;
- file identity from path alone;
- permanent universal file identity;
- absence of change outside the declared reason scope;
- stasis from missing records without completeness;
- journal continuity forever;
- DME interpretation as native source truth.
Explicitly:
same endpoint bytes != same traversal history
USN advancement != semantic consequence
USN record != complete hidden path
USN reason bits != cause
journal association != physical truth
native subsystem event != DME interpretation
LOCAL SUFFICIENCY AUDIT
LOCALLY + COMPOSITIONALLY EARNED from prior evidence:
- Endpoint state and traversal evidence must remain distinct.
- Missingness, discontinuity, and invalidity must remain visible.
- Positive and negative claims have different warrant burdens.
LOCAL-ONLY SURVIVOR:
- The proposed tuple of volume, journal ID, USN interval, file ID, and data-reason record appears sufficient for the bounded positive question.
BASIS INSUFFICIENT:
- Actual journal availability and record behavior on this machine remain unobserved.
- Scoped negative completeness remains unqualified.
- Logical byte-value transition is not established by an overwrite reason alone.
OVERBUILT:
- General Windows observer framework.
- General event architecture.
- Cross-subsystem clock.
- Provenance graph.
- Compatibility engine.
- Observational geometry.
- Controller integration.
COMPOSITIONAL COMPATIBILITY AUDIT
Retain only these raw distinctions for possible later composition:
- volume identity;
- filesystem type;
- journal ID;
- FirstUsn, NextUsn, and LowestValidUsn;
- record major/minor version;
- record USN;
- file reference number and its width;
- parent file reference, if captured;
- exact reason mask;
- exact SourceInfo;
- endpoint identities and hashes;
- half-open interval bounds;
- read completion state;
- close/emission mode;
- acquisition errors;
- continuity and validity result;
- file identity before and after.
Do not generalize them into a reusable event ontology, provenance graph, cross-source clock, or observational geometry.
QUALIFICATION VERDICT
QUALIFICATION READY
Microsoft’s documented NTFS surface is concrete enough to define a bounded candidate basis for adversarial review:
same NTFS volume
+ same UsnJournalID
+ retained [S,E) USN interval
+ same selected file ID
+ supported record
+ qualifying data reason
→ scoped positive NTFS traversal evidence
This verdict qualifies the basis definition only. It does not establish local journal availability, validate the observer empirically, authorize a scoped NO, execute hidden traversal, or activate PR-006.
ASTRA ADVERSARY HANDOFF
STRONGEST BASIS CLAIM: Within one retained NTFS journal instance, a supported USN record in a frozen half-open USN interval, matching the selected file ID and carrying USN_REASON_DATA_OVERWRITE, supports the scoped claim that NTFS recorded at least one same-file unnamed-data overwrite operation between endpoint captures.
WEAKEST SEMANTIC POINT: A USN data-reason flag describes an NTFS operation category; it does not prove that the logical byte value became different or identify the intermediate contents.
MOST DANGEROUS OVERCLAIM: No matching retained record means stasis, or a matching overwrite record proves an actual A → B content-value transition.
SMALLEST COUNTEREXAMPLE TO TRY: Overwrite the selected file in place with identical bytes, close it, and test whether NTFS emits USN_REASON_DATA_OVERWRITE. A positive record would demonstrate that the reason supports an overwrite operation but not byte-value inequality.
MISSING DOCUMENTATION OR EMPIRICAL FACT: The current volume’s active journal identity, retained range, supported record format, actual file-ID correspondence, close-emission behavior, and reason output for the controlled write remain locally unobserved; complete endpoint-to-journal coverage needed for NO also remains unqualified.
WHAT MUST NOT BE GENERALIZED: One volume, file, journal epoch, reason mask, or successful fixture must not become a general Windows observer, complete event history, cross-source clock, provenance architecture, observational geometry, or Controller warrant.