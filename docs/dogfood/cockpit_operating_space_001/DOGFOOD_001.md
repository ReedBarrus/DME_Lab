# COCKPIT_OPERATING_SPACE_001 — DOGFOOD_001

## Status

DOGFOOD: BLOCKED
STOP CONDITION: DOGFOOD_BLOCKED_BASIS
REAL OPERATING LOOP: NOT EXECUTED
MERGE: NO

This is a failure-legible blocked dogfood receipt under WORKSHOP_EXECUTION_PACKET_001.

## EXPECTED

Target campaign: COCKPIT_OPERATING_SPACE_001
Primary relation: COS-R2 — HUMAN_READABLE_ASSIGNMENT_DISPLAY != QUEUE_SEMANTICS
Intended current dogfood Git basis: 621f840709fc64c3b3947dcda945be9f5f14f399

The authorized packet required the checked-in campaign packet to be used without silently replacing its historical basis refs.

Intended bounded chain if current applicability existed:
campaign → execution_envelope_request_v0 → FOCUS → envelope_selection_v0 → ASSIGN → MAYA / RESOLVE_REFS → RING → manual_bell_v0 → wake_opportunity_v0 → external BOUNDED_REENTRY_001 → one preparation receipt → one successor → MAYA AVAILABLE → optional assignment satisfaction.

## OBSERVED

Checked-in campaign packet:
docs/campaigns/candidates/COCKPIT_OPERATING_SPACE_001.json

Retained historical basis:
- git:2ee939453651da741769ea07210fcdeaec9da971
- qualification:docs/candidates/wake_source_v0/QUALIFICATION_001.md@ee721faebb5f2a3e6780d20b7a558043e164a5b3

Currently authorized Cockpit candidate head:
621f840709fc64c3b3947dcda945be9f5f14f399

Inspection of actual CampaignStore and SelectionStore APIs found:

- CampaignStore.post_campaign(...) retains exact campaign bytes and has no campaign-adoption or basis-rewrite effect.
- CampaignStore.snapshot(..., current_basis_refs=...) reports CURRENT iff current_basis_refs == campaign['basis_refs']; otherwise STALE.
- SelectionStore.projection(...) maps stale campaign basis to request_applicability=STALE and preparation=BLOCKED_PENDING_REVALIDATION.

The development-campaign regression at the authorized final head passes:
test_c8_basis_drift_marks_projection_stale_without_rewriting_campaign

PreparationStore.append(...) requires the selected request to already be ELIGIBLE_FOR_PACKET_PREPARATION before a preparation receipt can be appended.
Therefore REVALIDATE_BASIS as a preparation kind does not provide an admitted v0 transition that can make this stale campaign currently applicable before preparation eligibility.

## BLOCKED

Exact missing relation:
HISTORICAL CAMPAIGN BASIS → CURRENTLY ADMISSIBLE DOGFOOD BASIS

A bounded adoption / revalidation relation would need to preserve campaign identity semantics and historical evidence while establishing current applicability. No such relation is present in the inspected v0 campaign / selection / preparation machinery.

Preserved distinctions:
- CAMPAIGN PACKET EXISTS != CAMPAIGN CURRENTLY APPLICABLE
- CAMPAIGN POSTED != CAMPAIGN ADOPTED
- TEST FIXTURE REBASED CAMPAIGN != LIVE DOGFOOD BASIS ESTABLISHED
- HISTORICAL BASIS RETAINED != CURRENT BASIS ADMITTED

The control-adapter qualification test deliberately reconstructs a campaign spec against an isolated fixture Git basis. That is valid qualification pressure, but it is not evidence of a live campaign-adoption relation.

Silently rebuilding COCKPIT_OPERATING_SPACE_001 with the current Cockpit head would cross the declared stop boundary.

## FAILED

NONE

The dogfood loop did not behaviorally fail. It was not entered.
No real Cockpit control object was emitted and no runtime consequence was attempted.

## REPAIRED

NONE

No implementation-local repair was needed or authorized to bridge the missing semantic relation.

Qualification closeout materialized separately at:
docs/candidates/cockpit_control_adapter_v0/QUALIFICATION_001.md

That documentation closeout does not alter runtime semantics.

## UNRESOLVED

Smallest proposed new distinction:
CAMPAIGN_BASIS_REVALIDATED != CAMPAIGN_BASIS_REWRITTEN

Equivalent bounded relation:
historical campaign object + explicit current-basis revalidation evidence → current applicability

It must not rewrite original campaign basis_refs, silently change campaign identity, create standing, create priority, create scheduler authority, or create execution authority.

This packet does not authorize that distinction or its implementation.

## Dogfood observations

- explicit human gestures: 0
- manual ID / hash copying required: NOT OBSERVED — loop not entered
- current handles discoverable from Cockpit: NOT OBSERVED — loop not entered
- blocked state legible: YES — source machinery exposes STALE / BLOCKED_PENDING_REVALIDATION
- assignment state legible: NOT OBSERVED — no assignment created
- preview useful before commit: NOT OBSERVED — no control preview created
- context recovered outside Cockpit: YES — campaign applicability required repository/API inspection before loop
- one-unit wake result: NOT OBSERVED — no wake opportunity created
- API naming / invocation friction: NONE IN DOGFOOD — loop not entered
- storage metadata contaminated identity: NOT OBSERVED
- screen/list ordering implied priority: NOT OBSERVED
- hidden convention required: NO — basis mismatch is explicit in code semantics
- stale/current basis semantics understandable: YES — campaign snapshot uses explicit CURRENT / STALE

## Real object chain

- campaign: INSPECTED ONLY
- request: NONE
- selection: NONE
- assignment: NONE
- bell: NONE
- wake opportunity: NONE
- preparation receipt: NONE
- satisfaction: NONE

## MAYA

- pre-state: NOT MATERIALIZED FOR DOGFOOD
- occupancy event: NONE
- unit count: 0
- post-state: NOT MATERIALIZED FOR DOGFOOD

## Control adapter effects

- control adapter invoked: NO
- direct controller mutation: NO
- authority effect: NONE
- priority effect: NONE
- scheduler effect: NONE

## Final classification

DOGFOOD_BLOCKED_BASIS
REAL LOOP: NOT EXECUTED
NEW SEMANTIC RELATION REQUIRED: YES
PROPOSED DISTINCTION: CAMPAIGN_BASIS_REVALIDATED != CAMPAIGN_BASIS_REWRITTEN
MERGE: NO
STOP
