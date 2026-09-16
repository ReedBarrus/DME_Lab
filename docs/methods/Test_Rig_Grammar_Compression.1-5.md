Rig 0 — establish the cost curve

Don't start with clever compression. Establish stupid baselines.

Take the same bounded repository task and run four conditions:

Condition	Model	State delivery
A	Codex / strongest available	ordinary large-context reconstruction
B	Qwen	ordinary large-context reconstruction
C	Qwen	explicit grammar + compact continuation packet
D	Qwen	grammar + distinction packet + on-demand resolution

Then compare actual consequence.

Not vibes.

Record at minimum:

task success
semantic correctness
tests passed
wall time
input tokens/context bytes
output tokens
tool calls
repo searches
files reopened
repeated questions
wrong assumptions
scope violations
human corrections
reconstruction time
continuation success

The hypothesis isn't even that D wins immediately.

The hypothesis is:

$$ \boxed{ \text{better retained structure} \Rightarrow \text{less reconstruction burden} } $$

If reality goes:

nah, normal summaries are already basically optimal

beautiful. We learn that cheaply.

If the curve bends hard, hello money goblin.

Rig 1 — packet before distinction magic

I'd first test a plain operational continuation packet.

Something like:

{
  "task_id": "QWEN-001",
  "basis": {
    "repo": "DME_Lab",
    "commit": "abc123"
  },
  "pressure": "One failing test exposes X.",
  "authority": [
    "READ_REPO",
    "EDIT_DECLARED_FILES",
    "RUN_TESTS"
  ],
  "forbidden": [
    "WIDEN_SCOPE",
    "ALTER_UNRELATED_STATE"
  ],
  "contract": {
    "target": "Make test X pass without changing Y.",
    "success": "Focused test passes and existing invariant Z remains."
  },
  "known_distinctions": [
    "mechanical_pass != semantic_correctness",
    "capability != authority"
  ],
  "open_residue": [],
  "return_required": [
    "files_changed",
    "tests_run",
    "result",
    "remaining_uncertainty"
  ]
}

We can measure how much reconstruction that eliminates before inventing the clever registry.

If Qwen still spends seventeen tool calls asking what planet it's on, that's evidence.

Rig 2 — actual distinction ablation

Then we get mean.

Same task, same packet, but deliberately remove one distinction.

Example:

FULL:
current specification != commitment identity

ABLATION:
those states are conflated

Then compare the consequence signature.

Maybe task correctness stays identical but it:

edits the wrong record,
uses more searches,
reconstructs lineage incorrectly,
damages future continuation,
or requires human repair.

That gives us:

$$ \Sigma_D $$

for a real software distinction.

This is where Distinction Dynamics stops being us smoking topology crack and becomes an experiment.

And we should absolutely include distinctions that we expect not to matter.

Otherwise we'll unconsciously manufacture evidence for every precious baby distinction.

Rig 3 — progressive compression

Once a packet works, shrink it.

Say the full operational state starts at 20 KB.

Try:

20 KB
10 KB
5 KB
2 KB
1 KB
500 B
200 B + retrieval
handle only + shared substrate

At every stage measure the same task consequences.

We're trying to locate a phase transition:

compression ↑
cost ↓
performance stable
performance stable
performance stable
OH GOD IT FORGOT WHAT AUTHORITY MEANS

😂

That transition is incredibly valuable.

Call it something like a semantic compression boundary:

$$ \boxed{ K^* = \text{smallest retained representation before consequence signature materially degrades} } $$

Not universal—task/model/basis dependent.

But measurable.

Rig 4 — reconstruction depth

Then test your three compression regimes directly.

Self-contained bundle

Everything needed locally.

No substrate dependency.

Portable distinction packet

Definitions + provenance + standing + refs sufficient for bounded reconstruction.

Symbolic handle
D-184

plus engine lookup.

Then we measure where the work goes.

I expect something like:

bundle:
network low
transport high
local reconstruction medium

packet:
network medium
transport low
reconstruction medium

handle:
transport almost zero
network/query dependence high
substrate dependence high

Now we have an actual engineering trade space instead of “memory but better.”

Rig 5 — cross-model conservation

This one might be the killer demo.

Have Agent A do work.

Retain only structured state.

Kill Agent A.

Start a different model family.

Give it the packet.

Then ask it to continue.

Something like:

Codex
→ retained state
→ Qwen

Qwen
→ retained state
→ ChatGPT

ChatGPT
→ retained state
→ Qwen

We aren't asking:

did they write similarly?

We're asking:

did identity, authority, unresolved pressure, prior consequence, and executable continuation survive the cognitive-substrate change?

That's a much stronger claim.

If it works:

$$ \boxed{ \text{continuity is increasingly located in externalized structure rather than model instance} } $$

That's the demonstration I would show people.

And we should build the harness stupidly small

I can already see the repo shape:

experiments/
  local_model_memory/
    README.md
    fixtures/
      task_001/
      task_002/
    packets/
    ablations/
    runs/
    reports/

src/
  experimental/
    packet_loader.py
    distinction_registry.py
    context_builder.py
    trace_recorder.py
    consequence_compare.py

No network.

No distributed memory service.

No investor-grade API.

No black hole. 😭

Just:

fixture
→ construct condition
→ invoke model
→ retain trace
→ evaluate
→ compare

And because we're DME goblins, the harness itself gets append-only run evidence.

Every run should know:

run_id
model
model_version
task
basis revision
packet revision
distinctions included
distinctions ablated
context size
timestamps
outputs
tool trace
test results
grader result

Then six months from now we can actually reproduce a claimed win.

I also want one hostile null condition

Something like:

generic competent summary of equal byte length.

Because that is probably the strongest cheap competitor.

If:

DME packet = 1 KB
normal summary = 1 KB

and they perform identically, we have not earned semantic machinery.

If the distinction packet wins reliably, then we can start asking why.

That ties directly back to the earlier Resolution Lineage countermodel: organizing description is not demonstrated capability.

Perfect pressure.

And then the business proposal practically writes itself after evidence.

The first claim shouldn't be:

revolutionary AI memory infrastructure.

It should be brutally boring:

We reduce the amount of context and model capability required to reliably continue stateful agent work.

Then show:

Baseline:
34k tokens
frontier model
$X
17 tool calls
92% success

Structured continuation:
3.1k tokens
local model
$Y
8 tool calls
91–93% success

If we ever get numbers like that repeatedly, nobody needs the Warhammer lore.