# DME_Lab — Bounded Research Warrant

## Status

**Adopted working method.**

This document defines the operating boundary for a research investigation that
explicitly invokes a Bounded Research Warrant.

Its authority is methodological, not evidentiary.

A warrant governs how an authorized question may be investigated. It does not:

- establish that a claim is true;
- authorize an investigation merely by existing;
- promote a candidate result into repository standing;
- override current repository evidence;
- override a more specific experimental constraint;
- expand the authority of the participant conducting the work.

Repository state, executed evidence, traces, reconstruction, and admitted
decision records remain authoritative for empirical claims according to the
current DME_Lab authority order.

This method remains amendable under pressure.

---

## Purpose

A Bounded Research Warrant gives a capable participant substantial freedom to
investigate one standing uncertainty without requiring repeated approval for
routine experimental choices.

The governing distinction is:

```text
changing a hypothesis
!=
changing the research question

Hypotheses may change freely when evidence requires it.

Changing the question, intervention class, source domain, or research objective
changes the warrant and requires separate standing.

The purpose of greater autonomy is not to accumulate conviction.

It is to create more opportunities for the investigator's current account to
fail under evidence.

Warrant
QUESTION

[State the specific uncertainty this investigation is authorized to address.]

The question should be narrow enough that execution can produce:

a supported bounded answer;
a counterexample;
a demonstrated evidence limit; or
a precise reason that the question cannot yet be discriminated.
WHY NOW

[State what gives this question standing.]

Examples may include:

an unresolved result from an existing pressure pass;
a concrete consumer demand;
a contradiction;
a missing observation boundary;
an independently reproduced ambiguity;
a failure of an existing representation to discriminate a required case.

Interest alone is not sufficient standing.

STARTING EVIDENCE

[Identify the repository ref and the minimum relevant contracts,
implementations, decisions, tests, traces, or reconstruction evidence.]

Treat current repository evidence as authoritative.

Preserve the scope, missingness, and provisional status of prior findings.

Do not silently inherit claims from conversation, model interpretation, or
older documents when current repository evidence does not support them.

TYPE OF INVESTIGATION

Declare one basis before execution.

Exploratory

Use when the question is:

What is observable, measurable, or discriminable here?

Before execution, declare:

the observation boundary;
what the instrument is intended to observe;
what would make the observation meaningful;
what the instrument cannot establish.

Patterns discovered during exploration remain candidate structure.

Exploratory evidence may formulate a later hypothesis.

It does not independently confirm that hypothesis.

Confirmatory

Use when the question is:

Does a specified relation survive, fail, or change under a specified pressure?

Before execution, declare:

the candidate relation;
the transformation or pressure;
the expected preservation or change;
the failure criterion.

Evidence used to formulate the prediction is not independent confirmation of it.

Transition rule

Moving from exploration to confirmation requires a separately declared test.

Do not discover a pattern and treat the same observation as confirmation of the
pattern.

PERMITTED INTERVENTIONS

[Declare what may be inspected, created, changed, executed, captured, or
externally affected.]

Include applicable boundaries such as:

files or modules that may be modified;
source systems that may be observed;
whether hardware may be actuated;
whether network access is permitted;
whether dependencies may be installed;
whether external services may be changed;
whether persistent artifacts may be created;
compute, time, storage, attention, privacy, or safety limits.

Routine reversible implementation decisions inside these boundaries do not
require repeated approval.

FORBIDDEN PROMOTIONS

[Declare claims this investigation cannot license.]

At minimum:

implementation
!= evidence

interpretation
!= observation

admission
!= source truth

bounded result
!= general guarantee

Do not promote:

a working instrument into proof of what it measures;
a model's explanation into observed fact;
a correlation into causation without pressure that establishes it;
a source-relative result into a global state claim;
a consumer's restraint into representation safety;
a candidate correspondence into an earned invariant;
one successful experiment into generalized architecture.
AUTONOMY

The investigator owns experimental design, implementation, debugging, control
selection, verification, and routine reversible choices within this warrant.

The investigator may:

reject the initial hypothesis;
introduce competing explanations;
tighten a control;
change implementation strategy;
preserve an unexpected result;
stop early when the evidence resolves the question;
conclude that the available basis is insufficient.

The investigator should build only the instrumentation necessary to discriminate
the authorized question.

Negative results and failures remain evidence when their provenance and scope
are preserved.

EVIDENCE EXPOSURE

When a consumer, navigator, reviewer, or other participant is part of the
experiment, declare before interpretation:

evidence visible to that participant;
evidence intentionally withheld;
relevant prior context;
whether separation is procedural or technically enforced.

Record the participant's interpretation or proposed action before revealing
withheld evidence when that ordering matters to the experiment.

Do not claim independence merely because two different models, agents, or role
labels are used.

Review independence is strengthened when a participant reconstructs a result
from declared artifacts without inheriting the investigator's interpretation.

QUESTION-CHANGE RULE

Stop dependent work when progress requires changing the authorized question.

A question change includes materially expanding into:

a different research objective;
a new source domain not covered by the warrant;
a new intervention class outside the permitted boundary;
a substantially stronger claim target;
an external action whose consequences were not authorized.

Changing a hypothesis inside the existing question is ordinary investigation
and does not require a new warrant.

When the question boundary is reached, report:

what changed;
why the current warrant is insufficient;
what evidence produced the need;
the smallest additional warrant that would permit further work.

Do not perform that additional work under the old warrant.

STOP CONDITIONS

Stop when any of the following occurs:

Supported bounded answer

The declared question has an evidence-supported answer within its stated scope.

Counterexample

Execution defeats the tested claim or relation.

Evidence limit

The available basis cannot discriminate the relevant alternatives.

Warrant boundary

Further discrimination requires a different question or unauthorized
intervention.

Non-informative continuation

Further work inside the same warrant is not expected to produce additional
discrimination.

Do not manufacture additional activity merely to produce a positive result.

If the result remains inconclusive, state exactly what remains unresolved.

DURABLE OUTPUT

Preserve enough evidence for another participant to reconstruct and challenge
the conclusion without trusting the investigator's prose.

At minimum record:

authorized question;
why it had standing;
starting repository/evidence boundary;
exploratory or confirmatory basis;
competing interpretations or hypotheses;
permitted interventions;
executed intervention;
observed evidence;
comparison or discrimination performed;
bounded result;
remaining alternatives;
claims explicitly not established;
files changed;
tests, traces, or verification performed;
final repository/worktree standing.

Where applicable, preserve raw or minimally transformed evidence strongly enough
that later interpretation can be challenged.

REVIEW AND INTEGRATION

The investigator's result is a candidate finding until it passes the applicable
repository integration boundary.

A durable artifact should preserve the difference between:

investigator conclusion
        ↓
candidate result

independent reconstruction / review
        ↓
surviving result

repository admission
        ↓
current project standing

Independent review should prefer reconstructing the result from evidence over
reviewing the investigator's reasoning alone.

Do not import an external participant's patch merely because its conclusion was
accepted. Reproduce or independently author the minimum repository artifact when
that materially strengthens provenance.

A reproduced result does not automatically require:

a new distinction;
a production change;
a new abstraction;
another experiment.

The smallest justified repository consequence may be only a pressure specimen,
trace, decision record, amendment, or explicit stop.

Relationship to DME_Lab workflow

This warrant operates inside the existing DME_Lab pressure discipline:

establish minimal working regime
→ apply pressure
→ observe what separates
→ preserve the distinction when necessary
→ tighten the constraint surface
→ repeat

The warrant does not replace WORKFLOW.md.

It supplies an execution boundary for investigations whose scope or duration is
large enough that repeated step-by-step authorization would otherwise obscure
the experimental question.

Core rule

Additional autonomy should produce additional opportunities to discover that
the investigator's account is wrong.

Longer investigation is valuable when it increases discrimination, exposes
alternatives, preserves provenance, and narrows the surviving claim.

It is not valuable merely because it produces a more coherent explanation.