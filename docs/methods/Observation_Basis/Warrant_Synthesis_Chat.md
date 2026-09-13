AUTHORITATIVE INPUTS

Repository artifacts used:

PROJECT_STATE.md
WORKFLOW.md
PRESSURE_RESOLUTION_MAP.md, especially PR-001 and PR-006
docs/decisions/absent_interval_round_trip_pressure_v0.md
docs/methods/Candidate_Pressure_Debate_Protocol_v0.md
all completed debate artifacts under docs/methods/Debate_Content/Pass_1/ and Pass_2/
docs/methods/Observation_Basis/NTSF_USN_observation_basis_proposal.md
docs/methods/Observation_Basis/Astra_Basis_Perturbation.md

The repository proposal identifies the intended basis as one selected NTFS file object's unnamed data stream, observed through the current per-volume USN Change Journal, and already narrows the positive claim to a bounded overwrite-category witness rather than logical-content change. Astra's adversarial pass accepts that basis only after sharpening file identity, lifecycle association, close-only reading, bounded acquisition, SourceInfo semantics, and operation-vs-state separation.

External Microsoft documentation actually consulted in this synthesis:

BY_HANDLE_FILE_INFORMATION: confirms the high/low file-index components and that file IDs are filesystem-specific and may be reused over time.
USN_JOURNAL_DATA_V0/V2: confirms UsnJournalID, FirstUsn, NextUsn, and LowestValidUsn, including the role of journal identity and possible discontinuity.
READ_USN_JOURNAL_DATA_V1: confirms ReturnOnlyOnClose, close-oriented behavior, and reason-mask semantics.
[MS-FSCC] USN_RECORD_V2: confirms the 64-bit FileReferenceNumber, accumulated Reason flags, final-close behavior, and SourceInfo interpretation.

The governing Lab workflow requires evidence boundaries to remain explicit, missing evidence not to be repaired by interpretation, and local sufficiency to remain distinct from global architectural necessity.

QUALIFICATION QUESTION

Under one deliberately bounded NTFS write lifecycle, does the selected USN observation basis reliably expose NTFS's unnamed-data overwrite operation category for the selected file object?

The qualification must simultaneously pressure:

Does that operation-category witness remain present for an identical-byte A → A overwrite as well as for a different-byte A → B overwrite?

The experiment qualifies a bounded operation witness. It does not test whether USN independently establishes logical byte inequality.

OBSERVED SUBJECT

The selected subject is:

the unnamed data stream of one explicitly selected NTFS file object.

Native observation generator:

NTFS on the identified containing volume.

Durable observation substrate:

that volume's current USN Change Journal instance.

DME's role:

bounded reader, parser, association checker, and interpreter of returned journal evidence.

The subject is not the repository as a whole, Git state, directory topology, Windows generally, or every filesystem event.

FROZEN BASIS

For one arm, the minimum admitted basis is:

$$ B= (V,J,S,E,F,R,M,L) $$

where:

\(V\): identified NTFS volume;
\(J\): identified journal instance via UsnJournalID;
\(S\): initial NextUsn;
\(E\): final NextUsn;
\(F\): selected file identity under the frozen V2/64-bit route;
\(R\): accepted V2 USN record associated with \(F\);
\(M\): declared read/emission semantics;
\(L\): fresh bounded write-lifecycle association.

The positive record predicate is:

$$ S \le R.Usn < E $$ $$ R.FileReferenceNumber = F $$ $$ (R.Reason \,\&\, USN\_REASON\_CLOSE)\neq0 $$ $$ (R.Reason \,\&\, USN\_REASON\_DATA\_OVERWRITE)\neq0 $$

under a successful bounded acquisition and unchanged admitted journal/file identity regime.

The interpretation is:

$$ \text{qualified USN evidence} \Rightarrow \text{NTFS recorded the selected unnamed-data overwrite category} $$

not:

$$ \text{qualified USN evidence} \Rightarrow \text{logical bytes became unequal}. $$
FILE IDENTITY CONTRACT

Freeze the first fixture to:

USN_RECORD_V2;
BY_HANDLE_FILE_INFORMATION;
complete unsigned 64-bit file ID:
$$ F= (\texttt{nFileIndexHigh}\ll32) \;|\; \texttt{nFileIndexLow}; $$
same identified NTFS volume;
compare \(F\) directly with V2 FileReferenceNumber.

Microsoft documents USN_RECORD_V2.FileReferenceNumber as the 64-bit file ID for the affected object. BY_HANDLE_FILE_INFORMATION exposes the corresponding high and low identifier components and volume serial information.

Do not substitute FILE_ID_INFO, truncate a 128-bit representation, zero-extend one representation into another, or infer equivalence between ID formats.

Require file identity to agree before and after the controlled write.

Preserve:

$$ \text{path}\neq\text{file identity} $$

and:

$$ \text{same path}\not\Rightarrow\text{same file object}. $$

Delete/recreate, replace, rename, cross-volume movement, and hard-link manipulation are excluded from this first qualification.

JOURNAL CONTINUITY CONTRACT

Before the controlled write, query the selected volume and retain at minimum:

volume identity;
filesystem type = NTFS;
UsnJournalID;
FirstUsn;
LowestValidUsn;
\(S=\texttt{NextUsn}\).

After the writing lifecycle has finalized, query again and retain:

same volume identity;
same UsnJournalID;
current FirstUsn;
current LowestValidUsn;
\(E=\texttt{NextUsn}\).

The admitted interval is:

$$ [S,E). $$

USN values alone do not establish continuity. UsnJournalID is a journal-instance integrity coordinate, and LowestValidUsn may expose a discontinuity where relevant changes may not be represented.

Every read request must use the frozen journal identity.

Follow the continuation USN returned by the read operation. Do not use the last matching record as the next cursor.

Records returned with:

$$ Usn\ge E $$

are overshoot and are excluded from the bounded claim, not treated as malformed evidence.

Treat as INVALID or UNRESOLVED, according to the exact failure:

journal ID change;
unreadable or trimmed retained range;
saved \(S\) falling below applicable readable/valid bounds;
journal acquisition failure;
unsupported record version;
malformed record layout;
cursor nonprogress or premature read termination;
inability to account for the intended frozen interval.

Successful interval consumption qualifies acquisition of that interval. It does not by itself establish complete detection of every possible NTFS mutation.

READ / EMISSION CONTRACT

Freeze:

request structure: READ_USN_JOURNAL_DATA_V1;
accepted record major version: 2;
ReturnOnlyOnClose != 0;
ReasonMask = USN_REASON_CLOSE;
BytesToWaitFor = 0;
frozen UsnJournalID;
start cursor initially \(S\).

Microsoft documents that nonzero ReturnOnlyOnClose, together with USN_REASON_CLOSE, requests notification associated with final close; accumulated change reasons are represented on close records.

A returned record is qualifying only if it independently passes the conjunctive acceptance test:

$$ CLOSE \land DATA\_OVERWRITE. $$

Do not interpret ReasonMask itself as logical conjunction.

Ordinary records that are:

for another file;
outside [S,E);
for nonqualifying reasons;

are NONMATCH, not INVALID.

Preserve the exact Reason bitmask and exact SourceInfo.

If a first-fixture inclusion policy requires SourceInfo == 0, that means only:

none of the documented special source flags represented by SourceInfo are present.

It does not identify the writer or prove an ordinary application actor. SourceInfo is documented as additional source-category information, and some documented source categories may explicitly correspond to operations that do not change application data.

LIFECYCLE CONTRACT

For each arm independently:

Establish the selected file with baseline content \(A\).
Record endpoint bytes/hash and selected file identity.
Finalize every prior controlled write lifecycle relevant to the fixture.
Query the current journal and freeze \(S=\texttt{NextUsn}\).
Only after \(S\), open the selected existing file for the controlled write.
Confirm the frozen file identity route still identifies the selected object.
Perform exactly one declared same-length overwrite.
Complete the write synchronously.
Close the relevant writing handle.
Ensure no controlled observer-held or writing handle defeats the intended final-close emission.
Query the journal and freeze \(E=\texttt{NextUsn}\).
Read from \(S\), admitting only V2 records with Usn < E.
Re-observe endpoint bytes/hash.
Re-observe file identity and require continuity of the selected file object.

This sequencing is necessary because a close record inside [S,E) can summarize reasons accumulated before \(S\) if an earlier changed lifecycle remained open. Astra's adversarial review identifies exactly this temporal hazard and requires a fresh write lifecycle before making a bounded operation-occurrence claim.

Do not extend \(E\) until a desired record appears.

If lifecycle isolation or final-close association is not established, withhold the operation-timing inference.

ARM AA — A → A

Initial content:

$$ A. $$

Controlled intervention:

overwrite the selected file's unnamed stream once with the same-length byte sequence \(A\).

Required endpoint observation:

$$ A. $$

Purpose:

determine whether the selected NTFS USN operation-category witness can be present even when independently observed logical endpoint content remains equal.

A qualifying record in this arm supports the operation-category witness.

It directly defeats the stronger interpretation:

$$ DATA\_OVERWRITE \Rightarrow \text{logical byte inequality}. $$

It does not defeat the candidate USN basis itself.

ARM AB — A → B

Initial content:

$$ A. $$

Controlled intervention:

overwrite the same selected file object's unnamed stream once with a same-length byte sequence \(B\), where \(B\neq A\).

Required endpoint observation:

$$ B. $$

Purpose:

determine whether the selected local write/read discipline reproducibly produces the same qualified NTFS overwrite-category witness when an independent byte observation establishes actual endpoint inequality.

This arm receives its own independently frozen journal interval.

The AA and AB arms must not share one [S,E) interval.

POSITIVE WARRANT

A qualifying record licenses only:

In journal instance \(J\) on identified NTFS volume \(V\), a valid V2 record at USN \(u\in[S,E)\), associated with selected file object \(F\), contained both USN_REASON_CLOSE and USN_REASON_DATA_OVERWRITE under the declared read regime.

With the lifecycle contract successfully established, this additionally licenses:

NTFS recorded at least one operation in the selected unnamed-data overwrite category during the bounded controlled lifecycle.

The journal evidence is the observation being qualified.

Experimenter knowledge that an overwrite command was issued is not a substitute for locating and associating the qualifying USN record.

UNAUTHORIZED INFERENCES

The qualification does not license:

logical byte inequality from DATA_OVERWRITE alone;
exact written bytes;
exact offset;
exact write length from USN;
intermediate byte state;
exact operation count;
one record = one mutation;
actor identity;
causal intent;
persistence to physical media;
complete hidden history;
hidden A → B → A;
repository semantic change;
Git semantic change;
cross-source simultaneity;
wall-clock or causal ordering;
generalized NTFS observation;
generalized Windows observation;
stasis from absence of a qualifying record.

The claim ladder remains separated:

$$ L3=\text{NTFS operation-category evidence} $$

does not entail:

$$ L4=\text{logical bytes changed}, $$

nor:

$$ L5=A\rightarrow B, $$

nor:

$$ L6=A\rightarrow B\rightarrow A. $$

The warrant targets Level 3 only.

NEGATIVE / ABSENCE SEMANTICS

For this qualification:

$$ \text{no qualifying record} \not\Rightarrow \text{no relevant source change}. $$

If the controlled intervention is independently verified but no qualifying associated record appears, classify the outcome as:

candidate basis weakened;
acquisition/emission discipline unresolved;
or qualification failed;

depending on the observed failure.

Do not call it stasis.

Unrelated records and nonqualifying reasons are NONMATCH.

Use INVALID only when the integrity of acquisition, parsing, identity, continuity, bounded association, or the declared lifecycle is broken.

Use UNRESOLVED when the evidence remains valid as evidence but cannot warrant the intended claim—for example, ambiguous lifecycle association or uninterpretable SourceInfo under the declared inclusion policy.

No scoped negative completeness is being qualified in this pass.

PREDECLARED OUTCOME TABLE
AA	AB	Predeclared interpretation
qualifying record	qualifying record	Local operation-category basis survives. DATA_OVERWRITE does not discriminate logical endpoint inequality; operation occurrence and byte-value difference remain distinct observation bases.
no qualifying record	qualifying record	Local asymmetry observed. Do not infer general NTFS content sensitivity. The basis may qualify for the AB controlled regime only; no stronger semantics are earned.
qualifying record	no qualifying record	Qualification does not pass cleanly. Expected basis behavior is unstable or fixture/acquisition discipline differs between arms; preserve discrepancy.
no qualifying record	no qualifying record	Basis not qualified. The local USN basis or acquisition/emission discipline failed to expose the expected controlled operation.
identity, journal, format, acquisition, or lifecycle fracture in either arm	any	INVALID or UNRESOLVED according to the exact failure; do not repair by widening scope or moving \(E\).
SUCCESS CRITERION

The basis qualifies locally only if all of the following survive execution:

the selected volume is confirmed NTFS;
an active readable USN journal can be queried and bounded;
the same journal instance remains valid for the admitted interval;
the selected file's 64-bit V2 identity relation is established and preserved;
bounded acquisition completes under the frozen cursor and [S,E) discipline;
a valid associated CLOSE + DATA_OVERWRITE V2 record is reproducibly observed in at least the changed-byte AB regime;
the operation record is successfully associated with the fresh controlled write lifecycle;
interpretation remains at the documented NTFS overwrite-category level;
missingness, discontinuity, malformed evidence, and identity failure remain visible;
the AA arm either demonstrates that identical-byte overwrite can also produce the operation witness or cleanly exposes a narrower regime without semantic strengthening.

This is only local qualification of the selected NTFS operation-category observation basis.

It does not resolve PR-006.

FAILURE / FALSIFICATION CRITERION

Qualification fails or is withheld if any of the following occurs:

selected filesystem is not NTFS;
required active/readable journal is unavailable;
journal identity changes;
[S,E) cannot be retained/read completely under the declared acquisition procedure;
unsupported or malformed record version/layout is encountered where required for the claim;
64-bit selected file identity cannot be safely matched to V2 FileReferenceNumber;
selected file identity changes during the arm;
fresh controlled lifecycle cannot be isolated;
final-close emission cannot be associated with that lifecycle;
the AB controlled overwrite repeatedly produces no qualifying associated record under otherwise verified fixture conditions;
the positive inference requires undocumented reason semantics;
the reader must move \(E\) or otherwise alter the frozen fixture to obtain the desired evidence.

A positive AA record is not basis falsification.

It falsifies only:

$$ DATA\_OVERWRITE \Rightarrow \text{logical endpoint inequality}. $$
PRESERVED RAW DISTINCTIONS

Retain only:

volume identity;
filesystem type;
UsnJournalID;
FirstUsn;
LowestValidUsn;
initial and final NextUsn;
frozen \(S\) and \(E\);
record major/minor version;
record Usn;
complete 64-bit FileReferenceNumber;
exact endpoint file IDs;
exact endpoint hashes/bytes used for AA/AB interpretation;
full Reason mask;
exact SourceInfo;
read request parameters;
returned continuation cursors;
scan completion/failure state;
lifecycle-open/close association evidence;
acquisition errors;
continuity result;
record-match versus ordinary nonmatch versus invalidity;
arm identity.

Do not promote these into generalized observer/provenance infrastructure during qualification.

LOCAL / GLOBAL AUDIT

LOCAL-ONLY SURVIVOR

The NTFS USN tuple:

$$ \text{volume} + \text{journal instance} + [S,E) + \text{file identity} + \text{qualifying V2 record} + \text{bounded lifecycle} $$

is the candidate local mechanism being qualified.

LOCALLY + COMPOSITIONALLY EARNED

Already-earned constraints that this warrant preserves:

endpoint state and traversal evidence remain distinct;
operation-category evidence and logical-content evidence remain distinct;
source, identity, interval, and association must remain explicit;
missingness and invalidity cannot be collapsed into negative evidence;
positive and negative claims carry different warrant burdens.

COMPOSITIONALLY COMPATIBLE

Retaining the raw source-relative coordinates above leaves future provenance, reconstruction, recoverability, or broader observation work possible without requiring any of those systems now.

BASIS INSUFFICIENT

Before execution, actual local USN emission/read behavior, file-ID correspondence on the fixture, and acquisition reliability remain empirically unqualified.

OVERBUILT

Not justified here:

generalized Windows observer;
ETW;
ReadDirectoryChangesW;
event ontology;
cross-source clock;
provenance graph;
observational geometry;
Controller integration;
generalized filesystem observation.

This follows the Lab rule that local sufficiency does not imply global architecture and global compositional compatibility does not imply local necessity.

EXECUTABLE WARRANT
SOURCE:
NTFS on one explicitly identified volume, using that volume's current USN
Change Journal instance as the durable observation substrate.

SUBJECT:
The unnamed data stream of one selected existing NTFS file object.

QUESTION:
Under a fresh bounded write lifecycle, does the frozen USN observation basis
reliably expose NTFS's unnamed-data overwrite operation category for the
selected file object, and does that witness remain distinct from logical
byte-value inequality?

ARM AA:
Establish content A.
Freeze journal start S.
Open the selected same file object only after S.
Perform exactly one synchronous same-length overwrite A -> A.
Close the relevant writing handle.
Freeze journal end E.
Read [S,E).
Re-observe endpoint bytes and file identity.

ARM AB:
Independently establish content A.
Freeze a new journal start S.
Open the selected same file object only after S.
Perform exactly one synchronous same-length overwrite A -> B where B != A.
Close the relevant writing handle.
Freeze a new journal end E.
Read that independent [S,E).
Re-observe endpoint bytes B and file identity.

IDENTITY:
Accept USN_RECORD_V2 only.
Obtain file identity via BY_HANDLE_FILE_INFORMATION.
Construct:
    fileID64 = (nFileIndexHigh << 32) | nFileIndexLow
using unsigned 64-bit composition.
Require the same identified NTFS volume.
Compare the complete fileID64 with V2 FileReferenceNumber.
Require file identity continuity across each arm.
Do not use FILE_ID_INFO interchangeably.

JOURNAL:
Before each arm retain:
    volume identity
    filesystem = NTFS
    UsnJournalID
    FirstUsn
    LowestValidUsn
    S = initial NextUsn

After controlled final close retain:
    same volume
    same UsnJournalID
    current FirstUsn
    current LowestValidUsn
    E = final NextUsn

Accepted interval:
    [S,E)

Use frozen journal identity on reads.
Follow returned continuation USNs.
Do not use last matching record as scan cursor.
Exclude records with Usn >= E.
Do not infer continuity from USN values alone.

READ MODE:
READ_USN_JOURNAL_DATA_V1
accepted major version = 2
ReturnOnlyOnClose != 0
ReasonMask = USN_REASON_CLOSE
BytesToWaitFor = 0
frozen UsnJournalID

QUALIFYING RECORD:
A parsed valid USN_RECORD_V2 satisfying:
    S <= Usn < E
    FileReferenceNumber == selected fileID64
    Reason contains USN_REASON_CLOSE
    Reason contains USN_REASON_DATA_OVERWRITE
    SourceInfo satisfies the predeclared inclusion policy
and whose close/lifecycle association is established.

ReasonMask matching is not conjunction.
The conjunction is enforced during record acceptance.

SUCCESS:
Local basis qualifies if journal acquisition and continuity remain valid,
file identity is explicitly matched and preserved, bounded acquisition
completes, and a qualifying associated CLOSE + DATA_OVERWRITE record is
reproducibly observed at minimum in ARM AB while interpretation remains
strictly at NTFS operation-category level.

ARM AA additionally determines whether the same operation-category witness
can occur without logical endpoint inequality.

UNRESOLVED:
No qualifying record despite otherwise valid evidence;
unestablished lifecycle timing;
ambiguous SourceInfo under the declared policy;
or any valid evidence that does not warrant the Level-3 operation claim.

Absence is not stasis.

INVALID:
Non-NTFS source;
journal unavailable where required;
journal-instance discontinuity;
retained range lost or unreadable;
malformed or unsupported record format;
file identity cannot be safely matched;
file object identity changes;
bounded acquisition cannot complete;
or lifecycle/association integrity is broken.

DO NOT INFER:
logical byte inequality from DATA_OVERWRITE alone;
exact bytes, offset, length, mutation count, actor, cause, physical-media
persistence, complete hidden history, A -> B -> A, repository semantics,
Git semantics, cross-source timing, or generalized Windows/NTFS observation.