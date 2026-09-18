# MM-003 Targeted Repair Verification 001

You are an independent observer testing a specific repair to a compressed
deliberation-memory carrier.

Use only the supplied contents of:

1. `traces/multi_round_deliberation_001_checkpoint.json`
2. `MM002_CHECKPOINT_BASIS_ENVELOPE_v0.md`
3. `MM002_COUNCIL_CAUSAL_LINEAGE_ENVELOPE_v0.md`
4. `MM003_CONTINUITY_DEPENDENCY_BASIS_ENVELOPE_v0.md`

Do not browse the repository.
Do not inspect raw source artifacts.
Do not use prior conversation or prior observer conclusions.
Do not repair the carrier.

This test asks only whether the cold-audit dependency-basis wound has been
closed.

Determine:

1. Which immutable historical basis governs the Council's operational
   continuity dependencies?
2. Which exact historical `AGENT_CONTEXT.md` version belongs to that basis?
3. What artifact owns the detailed synchronization ritual, and is its exact
   source identity recoverable?
4. What minimum ritual relation is preserved hot?
5. Are the event stream and both Council-relevant cursor versions exactly
   recoverable?
6. May the later transplant version of `AGENT_CONTEXT.md` substitute for the
   frozen source version merely because the path is the same?
7. Does the older MM-002 transplant coordinate remain valid for the checkpoint
   and four Council rounds it explicitly pinned?
8. Does this repair require claiming a generalized dependency graph,
   generalized semantic continuity checker, or source deletion authority?

Fail if correct answers require guessing a historical dependency version or if
the carrier still silently allows the post-handoff `AGENT_CONTEXT.md` to stand
in for the source version.

Do not fail merely because exact raw prose remains omitted when the required
relation is preserved hot and an exact immutable route to the raw source is
present.

Finish with exactly one of:

`MM003 DEPENDENCY REPAIR PASSES`

or

`MM003 DEPENDENCY REPAIR FAILS`

If FAIL, name the single smallest remaining consequential loss.
