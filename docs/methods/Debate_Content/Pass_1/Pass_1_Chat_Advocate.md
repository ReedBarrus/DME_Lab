STRONGEST LOCAL A CLAIM

For PR-006 as narrowed to hidden traversal, Candidate A needs only this claim:

Endpoint configuration and evidence of intervening source-relative change are distinct observational coordinates. If a bounded witness is defined so that a relevant change to the selected repository source persists across return to the same endpoint configuration, then that witness can distinguish true stasis from A → B → A without representing the hidden path itself.

Formally, for endpoint observations \(E_0=E_1=A\), let \(w\) be a source-relative persistent change witness over the interval. The required discrimination is only:

$$ w(A\rightarrow A)=0 $$

and

$$ w(A\rightarrow B\rightarrow A)>0. $$

Nothing stronger follows.

This is consistent with Candidate A's core distinction that configuration is not projection and endpoint equivalence does not imply consequential equivalence, while discarding its broader machinery as locally unnecessary.

The repository has already established the wound: C0 true stasis and S1 hidden alpha → beta → alpha produced equivalent captured filesystem and Git configurations, while DME could not distinguish the interval predicate.

MINIMUM A MECHANISM

A persistent source-relative change witness spanning the interval between the two endpoint captures.

Examples could include a monotonic source version, append-only change occurrence, source change counter, or equivalent irreversible activity coordinate, provided that the witness:

remains unchanged during true stasis;
changes on every relevant source-relative mutation within its declared scope;
does not revert merely because the source configuration returns to its original endpoint;
can be associated with the two endpoint captures being compared.

Candidate A does not locally require:

$$ (A,R,U,V,K), $$

a consequential-geometry object, transformation graph, observer atlas, singularity model, consequence debt, reversibility, recoverability, or navigation structure.

Those are global/compositional concepts, not requirements of this binary pressure. Candidate A itself is explicitly a conceptual projection rather than an implementation mandate.

REQUIRED SEMANTICS

The witness needs only enough semantics to make its binary claim interpretable.

Source: Which repository source the witness observes. A filesystem witness cannot silently establish a Git-source mutation, and vice versa.

Scope: What counts as a relevant change. For example, selected path/content changes versus every filesystem metadata mutation.

Observation basis: The witness semantics must specify what events can affect it and what relevant events it may miss.

Association: The before and after witness values must belong to the endpoint interval under examination.

Provenance: Only enough provenance is required to warrant that association and interpretation. Candidate A does not require a generalized provenance object if source, scope, witness identity, and endpoint association are fixed by construction.

The existing PR-006 map already identifies the missing basis as a selected event/change source, scope, clock, attribution rule, and consumer question. It also explicitly warns that change notification alone would not establish complete history or semantic consequence.

For this narrower collision, even “clock” may be unnecessary if the interval association is structurally fixed—for example, read witness before capture 1 and again before capture 2 from the same persistent source coordinate.

SUPPORTED CLAIMS

If the witness differs across the interval under its declared source and scope, Candidate A would support:

At least one relevant source-relative change represented by this witness occurred between the associated endpoint observations.

For the two specimens:

A --------> A
A -> B -> A

the intended witness can therefore discriminate:

stasis:           no witnessed relevant change
hidden traversal: at least one witnessed relevant change

It also supports the already-earned distinction:

endpoint state != traversal evidence

The PR-001 evidence specifically established that occurrence timestamps and different ledger records did not supply this interval distinction; source-relative endpoint configurations remained equivalent in C0 and S1.

UNSUPPORTED CLAIMS

The witness would still not establish:

the complete hidden path;
whether exactly one change occurred;
the intermediate state \(B\), unless independently captured;
why the mutation occurred;
causal mechanism;
semantic consequence;
cross-source simultaneity;
another source's state during the interval;
current external freshness generally;
reconstruction correctness generally;
caller acknowledgement;
recurrence semantics beyond the witnessed predicate;
absence of every kind of change outside the witness scope.

Even if the witness remains unchanged, the strongest legitimate statement is:

No relevant change represented by this witness was observed across this associated interval.

It cannot silently become:

Nothing happened.

That restriction is directly consistent with PR-001's finding that the hidden transformation lay outside the then-current observation basis rather than representing corruption or lost captured evidence.

LOCAL SUFFICIENCY

Yes.

If the chosen witness has the declared persistent-change property, it directly answers:

Did the selected repository source undergo at least one relevant source-relative change between endpoint captures?

No richer Candidate A structure is necessary for that binary discrimination.

The current endpoint-only basis is insufficient because PR-001 empirically showed identical relevant endpoint configurations for true stasis and hidden round trip.

Adding one persistent change coordinate is sufficient if and only if its defined observation basis actually separates those two specimens.

COMPOSITIONAL COMPATIBILITY

To avoid destroying distinctions useful later, the retained record should preserve only the minimal facts already intrinsic to interpreting the witness:

witness identity
source identity
scope / relevant-change semantics
before value
after value
association with the compared endpoint occurrences

If uncertainty or acquisition failure occurs, that condition must remain distinguishable from “no change witnessed.”

Those retained semantics can later participate in stale-history detection, reconstruction, provenance, recoverability, or cross-source comparison without requiring any of those systems now.

Candidate A would specifically resist collapsing:

endpoint configuration

and:

persistent change witness

into one coordinate, because PR-001 already demonstrates that the former cannot reconstruct the latter. But future compositional usefulness does not justify introducing the full Candidate A tuple today.

NULL-CANDIDATE CHALLENGE

Yes.

A simple persistent source-relative change witness can satisfy the strongest local Candidate A claim if source, scope, semantics, and interval association are fixed or unambiguous by construction.

Under that condition, Candidate A does not require an explicit:

source/scope/basis
+ provenance object
+ transformation object

in runtime representation merely to repeat information guaranteed by construction.

What remains distinctive about Candidate A is therefore interpretive rather than executable:

the witness is a separate consequence-bearing observational coordinate and must not be conflated with endpoint configuration or promoted beyond its warranted scope.

But the Null Candidate already accepts the essential behavioral restriction for this collision: a persistent witness answers the binary change question without establishing complete history. The debate protocol explicitly frames this as the live possibility and requires equivalence to be recorded if no distinct prediction remains.

So this distinction does not currently earn additional machinery.

COMPARISON WITH B

Candidate A currently makes no distinct executable prediction from Candidate B for this pressure.

Both accept a bounded source-relative observation that separates:

A --------> A

from:

A -> B -> A

while refusing to infer the complete hidden history.

Candidate B expresses the result through semantic scope, observer relations, compatible realizations, and evidence terms. Candidate A expresses it through distinction between configuration/projection and provenance-warranted traversal evidence.

For this binary consumer question, those formalisms collapse onto the same executable discriminator unless one candidate can identify an additional retained coordinate whose absence changes the observed result. No such coordinate is currently established.

FALSIFIER

Candidate A's local sufficiency claim is weakened or refuted by a bounded specimen in which:

C0: A --------> A
S1: A -> B -> A

contains a relevant source-relative change under the witness's own declared scope, yet the proposed persistent witness produces the same valid associated result for C0 and S1.

That would show that the proposed coordinate does not actually preserve the traversal distinction Candidate A claims it can represent.

A second failure mode would be a witness changing during verified true stasis under the same semantics, because then witness difference would not warrant the claim “at least one relevant source-relative change occurred.”

ADVOCATE VERDICT

EQUIVALENT TO NULL UNDER CURRENT PRESSURE

The strongest defensible local Candidate A reduces to a persistent source-relative change witness with sufficiently fixed semantics to prevent overclaiming. PR-006 does not presently require Candidate A's broader configuration, transformation, provenance, residue, uncertainty, reversibility, recoverability, or navigational machinery.

Candidate A remains compositionally compatible and supplies useful language for protecting distinctions, but it currently earns no additional executable mechanism over the Null Candidate for the hidden-traversal question.