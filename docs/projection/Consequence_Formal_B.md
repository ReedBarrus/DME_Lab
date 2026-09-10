1. Primitive objects
I would start with three primitives.
Primitive	Required content
Semantic scope \(\sigma\)	Typed variables, their interpretation, admissible realizations \(X_\sigma\), and meaningful queries
Evidence terms \(E\)	Records and derivations supporting scoped claims, including their assumptions and dependencies
Transformation contracts \(f\)	Typed source and target scopes, validity conditions, an outcome relation, and rules for producing evidence


A realization \(x\in X_\sigma\) need only describe the distinctions relevant to that scope. It may include a short history, clock parameters, or capture coverage. It need not describe the entire world.
A configuration is constructed from these primitives:
\[
C=(\sigma,\Gamma,E),
\]where \(\Gamma\) contains explicit assumptions and constraints. Its compatible realizations are derived:
\[
K_C=
\{x\in X_\sigma:
x\models\Gamma
\text{ and the accepted constraints supported by }E\}.
\]The displayed state is another derived object: a query or projection of this configuration.
This construction is conditional on model adequacy. It cannot guarantee that reality lies in \(K_C\); capture fidelity, coordinate interpretation, and domain completeness are obligations of the chosen model.
Status: Sets, relations, satisfaction, and derivations are established mathematics. This selection and packaging are synthesis.
2. Configuration identity
A configuration is more than an endpoint because an endpoint need not determine either its possible histories or its legitimate continuations.
Consider:
\[
h_1=(0,0,0),\qquad h_2=(0,1,0).
\]Both end at \(0\). Complete observation can distinguish them. Endpoint capture cannot.
Moreover, two configurations can have the same \(K_C\) while possessing different evidence resources. One may retain an associated checkpoint; another may possess only its identifier. Their present answers can agree while their recovery capabilities differ.
Consequently, there are several useful equivalences:
- Display equivalence: the rendered values agree.
- Semantic equivalence: compatible realizations agree under a declared scope translation.
- Operational equivalence: permitted observations, transformations, evidence checks, and recovery operations cannot distinguish the configurations.
Only the last is a sufficient basis for merging configurations used in navigation.
This does not require retaining every historical detail. History belongs in configuration identity exactly when removing it changes a supported answer or an available continuation. The relevant query language and operation library therefore determine how aggressively configurations may be identified.
Status: Behavioral equivalence is established. Using it as the criterion for configuration merging is synthesis.
3. Transformation identity
Represent a transformation contract as
\[
f=(\sigma,\tau,G_f,R_f,\Pi_f),
\]with:
\[
G_f\subseteq X_\sigma,\qquad
R_f\subseteq X_\sigma\times X_\tau.
\]Here:
- \(G_f\) is the validity domain;
- \(R_f(x)\) contains all outcomes admitted by the contract;
- \(\Pi_f\) specifies required evidence and how output evidence is derived.
Require \(R_f(x)\neq\varnothing\) on the declared domain. Failure outcomes must be represented when possible; termination guarantees require their own justification.
A transformation record must bind its parameters and the versions of the semantics it uses. “Convert timestamp” is insufficient: conversion depends on clock identities, offset or drift constraints, units, and validity interval.
Three identities should remain distinct:
1. Contract identity: the same specified operation.
2. Execution identity: the same occurrence, inputs, dependencies, and resulting receipts.
3. Extensional equivalence: the same input/output relation within a stated domain.
Two executions can have extensionally identical results and different historical warrant.
This follows the established idea of specifying operations through assertions and correctness obligations. Hoare’s original formulation supplies that foundation; the evidence-bearing contract above is my synthesis.
4. Observer geometry
An observer is a transformation whose output is a record:
\[
O\subseteq X_\sigma\times Y_O.
\]An observed result \(y\) determines a compatibility set
\[
O^{-1}(y)=\{x:(x,y)\in O\}.
\]This inverse image is the observer’s resolution: it says which situations the observation cannot distinguish.
For a deterministic observer \(o\), observational equivalence is
\[
x\sim_o x'
\iff o(x)=o(x').
\]For a nondeterministic observer, the inverse images remain useful, but need not form equivalence classes.
The observer’s scope must specify its capture domain and coordinate basis. A result such as “missing during interval \(I\)” is a meaningful observation outcome with its own interpretation. It does not mean “the observed quantity was constant during \(I\).”
For two observers sharing an interpreted interface \(U\), let
\[
r_i:X_i\to U,\qquad r_j:X_j\to U.
\]Their compatible overlap is
\[
K_i\times_U K_j
=
\{(x_i,x_j)\in K_i\times K_j:
r_i(x_i)=r_j(x_j)\}.
\]Uncertain alignment replaces equality with an explicit compatibility relation.
This yields three distinct overlap results:
- Empty: the observations and alignment assumptions cannot jointly hold.
- Multiple possibilities: translation is ambiguous.
- Unique relevant correspondence: translation is determined for the stated query.
Pairwise compatibility does not guarantee global compatibility. For example, local constraints \(a=b\), \(b=c\), and \(a\neq c\) are pairwise satisfiable but jointly inconsistent.
A coordinate change deserves to be called exact only where it is bijective and preserves the declared query meanings. Otherwise it is a partial, ambiguous, or lossy translation.
Status: Inverse images, quotients, and fiber products are established. Treating their domain-and-overlap structure as the initial observational geometry is synthesis. A global atlas is not assumed.
5. Provenance
Provenance should answer:
Which premises and transformations make this claim available here?

Use a judgment such as
\[
\Gamma;E\vdash \phi
\]for a supported claim. A derivation records its premises, rule, scope, and assumptions.
Historical warrant has two effects:
1. It constrains present interpretation.
2. It determines which future checks, translations, or recoveries remain executable.
A capture receipt may establish that particular bytes were received. Inferring a physical event from those bytes additionally requires a capture interpretation. A historical association may bind a result to a ledger prefix while leaving source authenticity or completeness unresolved.
Dependencies must remain visible through composition. If a calibration assumption is withdrawn, conclusions depending exclusively on it lose their warrant. A conclusion supported by an independent derivation may survive.
This resembles established database provenance, where output annotations record how inputs contribute to results. Green, Karvounarakis, and Tannen provide one formal treatment. I would initially retain typed derivation graphs rather than choose a provenance algebra: temporal scope, invalidation, and missing evidence need their own semantics.
Status: Derivation tracking is established; its integration into configuration and navigation is synthesis. Selecting a minimal provenance encoding remains open.
6. Continuity and discontinuity
The minimal notion of continuation is contract-valid extension.
For a transformation guard \(G_f\):
\[
\begin{array}{ll}
K_C\subseteq G_f
& \text{valid throughout the compatible situations},\\[2mm]
K_C\cap G_f=\varnothing
& \text{invalid throughout them},\\[2mm]
\varnothing\neq K_C\cap G_f\neq K_C
& \text{validity remains unresolved}.
\end{array}
\]Treat \(K_C=\varnothing\) separately as inconsistency. It must not authorize every operation through vacuous implication.
An absent interval requires a transition relation describing what may have occurred across it. With no justified restriction on the missing evolution, that relation must retain all possibilities allowed by the surrounding model. Equal endpoint values do not establish an unchanged trajectory.
A calibration boundary or schema change requires an explicit bridge into another scope. Without that bridge, a continuation claim is unsupported.
This is not yet topological continuity. That term becomes mathematically available only after topologies are specified; then ordinary continuity can be tested. A transformation can be topologically continuous while losing information or crossing an evidential validity boundary.
Status: Guard semantics is established. Applying it to observational continuation is synthesis. A topology appropriate to DME remains unearned.
7. Uncertainty and information loss
Uncertainty is represented initially by compatible possibilities, without invented probabilities.
For an admitted transformation:
\[
K' = R_f[K_C]
=
\{y:\exists x\in K_C,\ (x,y)\in R_f\}.
\]An implementation may store a sound approximation \(\widehat K'\), provided
\[
R_f[K_C]\subseteq\widehat K'.
\]Extra possibilities sacrifice precision. Dropping a possible outcome invents certainty. This is the relevant established principle from abstract interpretation.
Crucially, uncertainty must preserve relevant dependencies.
Suppose
\[
t_A=k,\qquad t_B=k+1,\qquad k\in\{0,1\}.
\]The absolute times are uncertain, but \(t_A<t_B\) is certain. Replacing this joint constraint with independent sets
\[
t_A\in\{0,1\},\qquad t_B\in\{1,2\}
\]introduces the unsupported possibility \(t_A=t_B=1\).
For a query \(q:X_\sigma\to V\), its uncertainty is
\[
q(K_C)=\{q(x):x\in K_C\}.
\]A singleton supports a definite answer within the model. Multiple values remain unresolved.
A quantity survives a transformation when suitable source and target queries satisfy
\[
q_\tau(y)=q_\sigma(x)
\quad
\text{for every relevant }(x,y)\in R_f.
\]Information loss concerns distinctions between predecessor situations that the retained output can no longer resolve. It cannot generally be measured by comparing the sizes of source and target possibility sets.
“Unknowable” should also be relative: a query is unidentifiable within an observation system when possible realizations disagree on it yet remain indistinguishable under every admitted observation strategy.
Status: Possibility semantics and sound approximation are established. The operational treatment of residual and inaccessible distinctions is synthesis.
8. Reversibility and recoverability
These are distinct.
For a deterministic transformation \(f:X\to Y\), a semantic inverse on its image exists exactly when \(f\) is injective on the relevant domain.
Even then, operational reversal additionally requires an available, admissible operation that implements the inverse. A bijective description does not establish a physical undo mechanism.
Recoverability asks a different question. Given an output \(y\) and retained evidence \(e\), define the compatible predecessors:
\[
P_f(y,e)=
\{x\in K_C:
(x,y)\in R_f
\text{ and }x\text{ is compatible with }e\}.
\]Then:
\[
\text{exact predecessor recoverable}
\iff |P_f(y,e)|=1,
\]and, more generally,
\[
q\text{ recoverable}
\iff |q(P_f(y,e))|=1.
\]For example, projecting a sampled history onto its terminal value loses the intermediate samples. A correctly associated checkpoint can recover that prior record. Reading the checkpoint does not reverse the physical history.
Retaining a residual \(r(x)\) can make
\[
x\mapsto(f(x),r(x))
\]injective even when \(f\) alone is lossy. This recovers the modeled input only to the extent that the residual itself is preserved, interpretable, and correctly associated.
Status: These injectivity and fiber criteria are established elementary mathematics. Requiring operational availability and association evidence is synthesis.
9. Composition laws
For compatible scopes, relational composition is
\[
R_{g\circ f}
=
\{(x,z):
\exists y,\ (x,y)\in R_f\land(y,z)\in R_g\}.
\]This composition is associative.
However, existence of a favorable intermediate outcome is insufficient for warranted execution. Assuming each relation is nonempty on its guard, the composite guard is
\[
G_{g\circ f}
=
\{x\in G_f:R_f(x)\subseteq G_g\}.
\]Every possible intermediate outcome must satisfy the next operation’s requirements.
Legitimate composition additionally requires:
- compatible interpretations, or an explicit translation;
- jointly consistent assumptions;
- evidence produced by the first operation sufficient for the second;
- preserved dependencies where later conclusions require them.
Evidence derivations compose by substitution:
\[
\Pi_{g\circ f}=\Pi_g\circ\Pi_f,
\]when that substitution is well typed.
If only some outcomes permit \(g\), use an explicit branch with stated behavior for the remaining outcomes. Do not silently discard them.
For projections, the immediate obligation is
\[
K_C\subseteq\operatorname{Pre}_f(K_{C'}),
\qquad
\operatorname{Pre}_f(S)
=
\{x\in G_f:R_f(x)\subseteq S\}.
\]Thus the declared output configuration must cover every admitted result.
Status: Relational composition and universal preconditions are established. Combining them with evidence admission is synthesis.
10. Recursive structure
Descriptions of observers, transformations, and dependency graphs should be ordinary inspectable data.
That permits operations such as:
- calibrating an observer;
- translating a transformation contract between schemas;
- comparing two derivations;
- replacing or invalidating an evidence dependency.
But a description is not automatically an executable or trusted instance of what it describes. Interpretation requires an explicit checker or evaluator.
Use finite versioned levels:
\[
\text{observer description}
\longrightarrow
\text{checked contract}
\longrightarrow
\text{execution receipt}.
\]A calibration result can constrain later observations. It cannot provide its own sole evidential foundation.
This supports useful recursion without requiring a self-validating universe of objects. Dependencies between descriptions may be cyclic; a claim of warrant still needs a grounded derivation or a separately justified fixed-point interpretation.
Status: Reification and staged interpretation are established techniques. Their necessity here is limited to concrete tasks involving changed observers or contracts. Stronger reflective machinery remains speculative.
11. Navigation
Define the warranted next moves by
\[
\operatorname{Next}(C)=
\left\{
f:
\begin{array}{l}
K_C\neq\varnothing,\\
K_C\subseteq G_f,\\
\Pi_f\text{ accepts the available evidence and resources}
\end{array}
\right\}.
\]An executable checker may fail to establish a true inclusion. Its result should then be “not established,” with the unresolved obligation preserved.
An operation can be available even when its outcome is unknown. Acquiring another observation is a typical example: its acquisition contract may hold across \(K_C\), while its result separates the remaining possibilities.
A proposed assumption may also create a conditional branch. It must remain labelled as an assumption; it does not become evidence because it enables a desired move.
For goal-directed navigation, let \(T\) be a target set of configurations. In a finite model, configurations from which arrival can be guaranteed within \(n\) steps satisfy
\[
V_0=T,
\]\[
V_{n+1}
=
V_n\cup
\left\{
C:
\exists f\in\operatorname{Next}(C),\
\varnothing\neq\operatorname{Succ}_f(C)\subseteq V_n
\right\}.
\]This separates possible reachability from guaranteed reachability. Choosing among legitimate moves additionally requires objectives, costs, or preferences; those do not follow from observational geometry.
For cross-source navigation, timestamps alone should not supply an unsupported total order. The distinction between event precedence and imposed clock ordering has an established foundation in Lamport’s treatment.
Status: Guarded transition systems and reachability are established. Making warrant part of move admission is synthesis.
12. Minimal executable pressure
I created and ran a standalone [finite pressure fixture](C:/Users/Admin/Documents/Codex/2026-09-10/develop-an-independent-formal-composition-for/outputs/finite_observation_pressure.py). It uses no DME imports.
Its declared world has:
\[
h\in\{0,1\},\qquad
\text{sampled history}=(0,h,0),
\]and the shared clock uncertainty
\[
(t_A,t_B)=(k,k+1),\qquad k\in\{0,1\}.
\]Capture omits the middle sample. Every candidate has terminal value \(0\).
The competing representations produce:
Representation	Middle sample remained \(0\)?	\(A\) strictly precedes \(B\)?
One selected reconstruction	Yes—unsupported by the capture	Yes
Independent coordinate possibilities	Unresolved	Unresolved
Joint constraints	Unresolved	Yes


The same fixture projects away the hidden sample and then attempts recovery from a checkpoint. A checkpoint associated with the expected source and prefix recovers the prior modeled record. Substituting a checkpoint associated with a different prefix that shares the terminal value is rejected.
All 14 checks passed. They include the missing-interval distinction, shared timing uncertainty, guarded admission, relational associativity, inconsistency handling, and recovery without making the original projection injective.
The experiment discriminates concrete representation failures:
- Endpoint equality cannot determine legitimate inference.
- Separate uncertainty fields can discard useful dependencies.
- Recovery needs an association condition in addition to retained content.
It does not prove this formalism uniquely minimal. Another representation that preserves the same distinctions and obligations is an equally viable candidate. The fixture assumes trusted synthetic checkpoint statements; it does not test authentication or select a production association encoding.
The proposed seed would fail operationally if an admitted transformation produced an outcome outside its represented possibilities, or if an allegedly recoverable query had two compatible predecessors with different answers. A simpler implementation would displace it if it preserved the same warranted answers and continuations under those pressures.
The principal speculative claim is therefore narrow: scoped possibility constraints, guarded relations, and explicit warrant dependencies may be sufficient for the next layer. Metrics, smooth spaces, global observer agreement, calibrated probabilities, and self-modifying interpretation remain additional hypotheses.