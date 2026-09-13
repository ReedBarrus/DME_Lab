INPUT ARTIFACTS USED
- Candidate A: docs/projection/consequential_geometry_A.md
- Candidate B: docs/projection/Consequence_Formal_B.md
- Protocol: docs/methods/Candidate_Pressure_Debate_Protocol_v0.md
- Pass 1 artifacts:
  - docs/methods/Debate_Content/Pass_1/Pass_1_Chat_Advocate.md
  - docs/methods/Debate_Content/Pass_1/Pass_1_Astra.md
  - docs/methods/Debate_Content/Pass_1/Pass_1_Codex_Experimentalist.md
- Completed Pass 2 artifacts:
  - docs/methods/Debate_Content/Pass_2/Pass_2_Astra_Advocation.md
  - docs/methods/Debate_Content/Pass_2/Pass_2_Codex_Experimentalist.md — contains the Codex adversarial pass despite its filename.
  - docs/methods/Debate_Content/Pass_2/Pass_2_Chat_Adversary.md — contains the ChatGPT experimental adjudication despite its filename.
- docs/methods/Debate_Content/Pass_2/Pass_2_Codex_Null_Claim.md was not treated as completed evidence: it is currently an empty, pre-existing local modification and was left untouched.
- Authoritative PR evidence:
  - WORKFLOW.md
  - PRESSURE_RESOLUTION_MAP.md
  - docs/decisions/absent_interval_round_trip_pressure_v0.md
STRONGEST NULL CLAIM
For the single bounded question—
Did the selected repository source undergo at least one relevant source-relative change between endpoint captures?

—a persistent traversal-sensitive witness is sufficient in principle when one local contract preserves the exact source, scope, interval, association, validity, and coverage semantics needed to interpret it.
That contract may warrant YES, NO, or UNRESOLVED without instantiating shared consequence geometry, compatibility sets, observer inverse images, evidence graphs, or transformation contracts.
Null claims only:
No shared observational abstraction has yet earned implementation.

It does not claim that interpretation can be omitted or that abstraction will never become necessary.
MINIMUM NULL MECHANISM
One bounded association tuple:
(
  witness identity and semantics,
  before value/status,
  after value/status,
  selected source,
  endpoint interval,
  relevant-change predicate,
  source/interval association,
  positive soundness condition,
  coverage/completeness condition,
  retention condition,
  reset/rollover interpretation,
  acquisition/validity state,
  sufficient local provenance
)
These elements may be fixed unambiguously by construction or carried directly with the observation. They need not become independent global primitives.
The mechanism must distinguish:
- valid advancement;
- valid unchanged value;
- missing acquisition;
- detected reset;
- rollover;
- malformed state;
- conflicting observations;
- wrong-source association;
- ambiguous interval association.
The tuple is occurrence-local. Fields from separate observations may not be recombined to manufacture a valid association.
RESULT SEMANTICS
YES:
A valid witness advancement is jointly associated with the selected source and target interval, and the declared witness semantics establish that accepted advancement entails at least one relevant change within scope.
NO:
The witness is valid and unchanged, and independently warranted conditions establish complete detection over the entire interval, complete coverage of the declared relevant-change class, valid retention, sound reset/rollover handling, correct association, and no unresolved conflicting evidence.
UNRESOLVED:
The available observation cannot warrant either answer. This includes incomplete coverage, missing acquisition, unknown reset or rollover effects, conflict without an earned precedence rule, wrong-source evidence, or ambiguous interval association.
INVALID:
The observation violates its local contract—for example, malformed values, impossible transitions, failed acquisition represented as data, or a known-broken association. Invalid evidence cannot yield YES or NO; the consumer remains unresolved with the invalidity visible.
DEPENDENCY PRESERVATION
Null preserves dependency through one occurrence-local association:
(witness observation, source, interval, relevance semantics)
The relation is part of the bounded record or its immutable enclosing context. It is not reconstructed from detached fields.
For example:
- an advancement for the selected source outside the interval; and
- an advancement inside the interval for another source
cannot be combined into evidence of a selected-source change during the interval.
This requires tuple-level dependency, not a provenance graph. It remains local because it binds one observation to one bounded claim and supplies no reusable cross-observer traversal, derivation, or navigation system.
UNCERTAINTY HANDLING
Null uses explicit validity and result states rather than enumerated possible histories:
unchanged + incomplete coverage       → UNRESOLVED
reset + unknown reset semantics       → UNRESOLVED
conflict + no precedence rule         → UNRESOLVED
missing or ambiguous association      → UNRESOLVED
malformed observation                 → INVALID
This preserves the uncertainty consequential to the current predicate without claiming which hidden history occurred.
A compatibility engine would become locally necessary only if two observations with the same complete local contract required different warranted verdicts because of a relation among possible histories that the bounded contract could not express.
No such case has been established.
NEGATIVE VERDICT
NO RELEVANT CHANGE requires all of the following:
- the relevant-change class is explicitly bounded;
- every relevant change in that class would affect the witness;
- coverage spans the complete endpoint interval;
- no undetected observation gap exists;
- witnessed change cannot disappear before the final read;
- reset and rollover are absent or completely accounted for;
- both acquisitions are valid;
- the observation is jointly bound to the selected source and interval;
- the witness is unchanged;
- no unresolved conflicting evidence defeats the negative inference.
A local contract can represent these conditions and their warrant status. A first-class observer-completeness abstraction would only rename them unless multiple observation regimes require shared comparison or composition.
WHAT NULL DOES NOT PROVIDE
Null deliberately does not generalize:
- reusable observer identity;
- cross-witness comparison or precedence;
- compatibility reasoning over modeled histories;
- translation between observation regimes;
- generalized provenance composition;
- global semantic scopes;
- transformation composition;
- cross-source timing or simultaneity;
- stale-history reconstruction;
- recoverability calculus;
- consequence navigation;
- observer charts or atlas structure.
These remain future compositional opportunities. Their absence is not a local PR-006 defect unless one becomes necessary to determine the bounded verdict.
ATTACK ON A NECESSITY
Null already preserves A’s locally consequential distinctions:
endpoint state != traversal evidence
association != source truth
witness advancement != complete history
It also preserves source, scope, basis limits, association, validity, and sufficient local provenance.
The following A components do not change the current verdict:
- situated configuration objects;
- transformation objects;
- A/R/U/V/K tuples;
- consequence debt;
- observer charts;
- atlas structure;
- residue geometry;
- reversibility and recoverability structure;
- navigation machinery.
No A-specific distinction has been shown that Null cannot preserve locally. A’s richer provenance and consequence structure remains compositionally interesting, not locally necessary.
ATTACK ON B NECESSITY
Null produces the same verdict rule as B:
sound associated advancement          → YES
complete valid unchanged              → NO
mixed, incomplete, or invalid basis   → UNRESOLVED
It can do so without:
- represented compatibility sets;
- observer inverse-image machinery;
- evidence-term graphs;
- transformation contracts;
- global semantic-scope objects;
- general dependency graphs.
B’s model-adequacy warning can be retained as a local coverage assumption. Its dependency-preservation requirement can be retained as an occurrence-local tuple.
No locally consequential B distinction remains unavailable to Null.
LOCAL SUFFICIENCY
Yes, in principle.
The bounded contract completely supports the declared YES | NO | UNRESOLVED result space while preserving invalidity separately.
This does not establish that a real repository witness satisfying the contract has been acquired or validated. PR-006 therefore remains OPEN, and actual observer adequacy remains BASIS INSUFFICIENT.
Workflow classification:
- Bounded contract: LOCAL-ONLY SURVIVOR
- Lossless occurrence-local association: COMPOSITIONALLY COMPATIBLE
- Actual PR-006 observer realization: BASIS INSUFFICIENT
- Shared A/B runtime machinery: OVERBUILT
COMPOSITIONAL COMPATIBILITY
The bounded mechanism can remain compositionally available if it retains, without flattening:
- witness identity and realization semantics;
- raw before/after values and statuses;
- selected source;
- exact relevance predicate;
- endpoint identities;
- source/interval/witness association;
- coverage and completeness status;
- reset, rollover, and retention conditions;
- missingness, invalidity, and conflict;
- the basis for its local provenance claim.
Later systems may translate or incorporate this record into richer observer, provenance, reconstruction, or recovery structures.
This is compatibility, not proof that those structures are already earned. Null must preserve the raw distinctions and avoid encoding assumptions that make future composition impossible.
IS NULL ACTUALLY SMALLER?
REPRESENTATIONALLY SMALLER ONLY
Null does not eliminate the semantic obligations identified by A and B. It packages the locally necessary subset into one bounded contract instead of promoting those obligations into reusable global objects.
Its advantage is therefore restraint in representation and authority, not a smaller information requirement or a distinct observational theory.
NULL FALSIFIER
Null is defeated if two observations contain the same complete, valid local contract yet require different warranted PR-006 verdicts because of an additional reusable relation that cannot be represented occurrence-locally.
The smallest exposing pressure would use two individually valid witnesses over the same source and interval whose conflict can be correctly adjudicated only through shared observer lineage, dependency, or compatibility semantics.
If YES, NO, or UNRESOLVED cannot be determined correctly without that cross-record structure, Null may not rescue itself by appending arbitrary global metadata to the local tuple. The shared abstraction would then be locally necessary.
DISTINCT NULL COMMITMENT
No shared observational-geometry abstraction should be implemented or formally promoted solely to answer PR-006 while the complete warranted verdict can be preserved by one occurrence-local contract.
This is an implementation and conservation commitment, not a distinct prediction about source behavior.
ADVOCATE VERDICT
NULL SURVIVES ONLY AS IMPLEMENTATION RESTRAINT
ADVERSARY HANDOFF
- Strongest Null claim: one occurrence-local witness contract preserves every distinction required for the bounded YES | NO | UNRESOLVED verdict.
- Weakest point: Null carries nearly the same semantic information as local A/B and is only representationally smaller.
- Exact place A or B might still be necessary: adjudicating valid cross-witness conflict or context-dependent verdicts that cannot be represented within one bounded association tuple.
- Smallest pressure that could expose that necessity: two locally complete witness records requiring different verdicts depending on a shared observer-lineage, dependency, or compatibility relation unavailable to either local contract.