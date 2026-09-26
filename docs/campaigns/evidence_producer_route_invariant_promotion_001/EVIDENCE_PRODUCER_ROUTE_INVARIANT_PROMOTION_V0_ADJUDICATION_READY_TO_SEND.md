# EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_001 — Independent Promotion Adjudication

PRESSURE_ID:
EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_V0_ADJUDICATION

ROLE:
FRESH_INDEPENDENT_INVARIANT_PROMOTION_ADJUDICATOR

MODE:
READ_ONLY
+
NO_LIVE_CHAT_CONTEXT
+
NO_REDESIGN
+
NO_REPAIR
+
NO_LEDGER_MUTATION
+
NO_PRODUCER_ROUTE_MUTATION
+
NO_CONSUMER_ROUTE_MUTATION
+
NO_GENERIC_INTAKE_ROUTER
+
NO_REFERENCE_REWRITE
+
NO_ARCHIVE_POLICY
+
NO_COLD_STORAGE_ADMISSION
+
NO_SOURCE_DELETION
+
NO_PLANNING
+
NO_AUTHORITY
+
NO_EXECUTION
+
NO_GLOBAL_INVARIANCE
+
NO_GLOBAL_ECOLOGY
+
NO_ECONOMIC_WEIGHTING
+
NO_SCIENTIFIC_PROMOTION

GOVERNING_LEDGER:
docs/methods/EARNED_MEMORY_INVARIANTS_v0.md

GOVERNING_LEDGER_BLOB:
1b28599b0e69844617f76cee47dabf5577c6baed

GOVERNING_PROMOTION_RULE:

candidate relation
→ pressure
→ consequential failure or repeated reconstruction requirement
→ bounded qualification
→ ledger entry

FROZEN_G18_ADJUDICATION_RESULT:

docs/campaigns/evidence_producer_route_alignment_001/pressure_runs/
EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_ADJUDICATION_RESULT_001.md

blob:
9dfa683c03420d793d100fcc90ca05bb81c14640

FROZEN_G18_PRESSURE_RESULT:

docs/campaigns/evidence_producer_route_alignment_001/pressure_runs/
EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_PRESSURE_RESULT_001.md

blob:
f22975d051a63056c8101b45c6f852ca491492f1

FROZEN_G18_WITNESS:

docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json

blob:
9d6e627401c3c51b9cc30449d80f6c94a99711d7

G18_REQUIRED_STANDING:

EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_MATCHED

G18_EARNED_RELATION:

For the exact tested producer:

tools/observe_horizon_gap_selector_v0.py

the historical observation had been relocated from:

horizon_gap_selector_v0_observation.json

to:

docs/evidence/for_planner/horizon_gap_selector_v0_observation.json

while the unchanged producer still declared:

ROOT / "horizon_gap_selector_v0_observation.json"

One bounded fresh execution then established:

PRODUCER_EXIT_CODE = 0
OLD_ROOT_OUTPUT_CREATED = true
GENERATED_ROOT_BLOB_NE_HISTORICAL_BLOB = true
RELOCATED_HISTORICAL_BLOB_PRESERVED = true
PRESSURE_CLEANUP_COMPLETE = true
PRODUCER_OUTPUT_ROUTE_MIGRATED = false
STORED_EVIDENCE_RELOCATION_NE_PRODUCER_OUTPUT_ROUTE_MIGRATION = YES

TARGET:

Adjudicate only whether the exact G18 basis satisfies the existing
earned-memory invariant promotion rule strongly enough to admit the bounded
proposed EMI-016 entry below.

Do not mutate the ledger.

Also adjudicate whether the wording remains strictly inside the earned G18
claim ceiling and does not become a generic evidence intake/routing rule,
archive policy, cold-storage policy, or authority to repair producer/consumer
routes.

PROPOSED_LEDGER_ENTRY:

## EMI-016 — Stored evidence relocation is not producer output route migration

```text
historical evidence relocated
!=
unchanged producer output route migrated
```

for the tested producer:

`tools/observe_horizon_gap_selector_v0.py`.

For the exact G18 specimen, the historical
`horizon_gap_selector_v0_observation.json` had been relocated to
`docs/evidence/for_planner/horizon_gap_selector_v0_observation.json`,
with its historical blob preserved.

The unchanged producer still declared:

```text
OUT = ROOT / "horizon_gap_selector_v0_observation.json"
```

A bounded fresh execution then produced:

```text
OLD_ROOT_OUTPUT_CREATED = true
PRODUCER_OUTPUT_ROUTE_MIGRATED = false
RELOCATED_HISTORICAL_BLOB_PRESERVED = true
```

and the fresh output had a different Git blob from the relocated historical
artifact.

**Earned by:** G18 /
`EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_PRESSURE_001`.

Frozen G18 adjudication result:
`docs/campaigns/evidence_producer_route_alignment_001/pressure_runs/EVIDENCE_PRODUCER_ROUTE_ALIGNMENT_V0_ADJUDICATION_RESULT_001.md`
(blob `9dfa683c03420d793d100fcc90ca05bb81c14640`).

Runtime G18 witness:
`docs/evidence/for_planner/evidence_producer_route_alignment_v0_observation.json`
(blob `9d6e627401c3c51b9cc30449d80f6c94a99711d7`).

**Consequence:** for this tested producer, relocating preserved historical
evidence does not redirect future evidence production. Without a separate
producer-route change, a fresh execution can reoccupy the old output path
while the relocated historical artifact remains intact.

This does not establish producer repair authority, consumer repair authority,
a generic evidence intake router, automatic reference rewriting, archive
policy, cold-storage admission, deletion permission, planning, authority,
execution, global invariance, global ecology coverage, economic weighting,
or scientific standing.

REQUIRED_NONCOLLAPSES:

STORED_ARTIFACT_RELOCATION != PRODUCER_ROUTE_MIGRATION
OLD_PATH_REOCCUPATION != HISTORICAL_EVIDENCE_OVERWRITE
NEW_OUTPUT != HISTORICAL_ARTIFACT
ONE_PRODUCER_PRESSURE != ALL_PRODUCERS
PRODUCER_ROUTE_RESULT != PRODUCER_REPAIR_AUTHORITY
LEDGER_PROMOTION != GENERIC_INTAKE_ROUTER
LEDGER_PROMOTION != ARCHIVE_POLICY

ALLOWED_DISPOSITIONS:

EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_V0_MATCHED
EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_V0_PARTIAL
EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_V0_FRACTURED
EVIDENCE_PRODUCER_ROUTE_INVARIANT_PROMOTION_V0_UNRESOLVED

RETURN_ONLY:

PRESSURE_ID
GOVERNING_LEDGER_BLOB_MATCHED
G18_MATCHED
G18_ADJUDICATION_RESULT_BLOB_MATCHED
G18_PRESSURE_RESULT_BLOB_MATCHED
G18_WITNESS_BLOB_MATCHED
CANDIDATE_RELATION
PRESSURE_REQUIREMENT_SATISFIED
CONSEQUENTIAL_FAILURE_OR_REPEATED_RECONSTRUCTION_REQUIREMENT_SATISFIED
BOUNDED_QUALIFICATION_SATISFIED
PROMOTION_RULE_SATISFIED
PROPOSED_ENTRY_CLAIM_CEILING_PRESERVED
PROPOSED_ENTRY_GLOBAL_WIDENING
LEDGER_ENTRY_ELIGIBLE
LEDGER_MUTATION_EFFECT
PRODUCER_REPAIR_EFFECT
CONSUMER_REPAIR_EFFECT
GENERIC_INTAKE_ROUTER_EFFECT
AUTOMATIC_REFERENCE_REWRITE_EFFECT
ARCHIVE_POLICY_EFFECT
COLD_STORAGE_ADMISSION_EFFECT
DELETION_PERMISSION_EFFECT
PLANNING_EFFECT
AUTHORITY_EFFECT
EXECUTION_EFFECT
GLOBAL_INVARIANCE_EFFECT
GLOBAL_ECOLOGY_EFFECT
ECONOMIC_WEIGHTING_EFFECT
SCIENTIFIC_STANDING_EFFECT
DISPOSITION
UNRESOLVED
CLAIM_CEILING
STOPPED
