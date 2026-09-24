# LOAD_TRANSFER_001 — FIRST TWO-SEAT HANDOFF PRESSURE

OBJECT_TYPE: READY_TO_SEND_PRESSURE_PACKET

STANDING: CANDIDATE_ONLY

## Target

Test whether two fresh seats can continue one bounded repository-local
development handoff without Reed serving as current-state cache, packet router,
or handoff narrator.

## Seat A

ROLE: IMPLEMENTER

Use only:

- `docs/campaigns/load_transfer_001/CURRENT_OPERATIVE_FRAME_V0.json`
- W1 `LOAD_TRANSFER_001_W1_IMPLEMENTER` from `WORK_QUEUE_V0.jsonl`
- `docs/campaigns/load_transfer_001/LOAD_TRANSFER_001_FRAME.md`
- `src/coordination/load_transfer_v0.py`

Do not use live-chat context to fill missing state.

Required transformation is exactly the transformation declared by W1.

Required output path:

`docs/campaigns/load_transfer_001/pressure_runs/LOAD_TRANSFER_001_OUTPUT_O1.md`

After output creation:

1. bind the exact output bytes with `artifact_descriptor`;
2. complete W1 with result posture `COMPLETED`, `HELD`, or `REJECTED`;
3. emit handoff id `LOAD_TRANSFER_001_H1`;
4. append the terminal W1 record to the queue history / retained pressure record;
5. append H1 to `HANDOFFS_V0.jsonl`;
6. stop.

Seat A must not start reviewer work.

## Seat B

ROLE: REVIEWER

Seat B may act only after H1 exists and validates.

Use only:

- operative frame;
- W2 `LOAD_TRANSFER_001_W2_REVIEWER`;
- terminal W1;
- H1;
- exact O1 bytes bound by H1;
- `src/coordination/load_transfer_v0.py`.

Claim W2 using H1 as `available_handoffs`. If H1 is absent, malformed, or does
not bind O1, stop unresolved. Do not ask Reed to explain.

Required output path:

`docs/campaigns/load_transfer_001/pressure_runs/LOAD_TRANSFER_001_REVIEW_O2.md`

Seat B reviews only. It must not repair O1.

Complete W2 and emit `LOAD_TRANSFER_001_H2`, then stop.

## Reed constraint

During the pressure Reed may start the seat/thread and inspect final records.

Reed does not:

- explain current state;
- explain W1 to Seat A;
- narrate Seat A output to Seat B;
- route Seat B manually;
- repair stale state;
- inject live-chat context.

## Pass criteria

PASS requires:

```
REED_CURRENT_STATE_EXPLANATION_REQUIRED: NO
REED_WORK_ROUTING_REQUIRED: NO
REED_PACKET_ASSEMBLY_REQUIRED: NO
REED_HANDOFF_NARRATION_REQUIRED: NO
REED_STALE_FRAME_REPAIR_REQUIRED: NO
SEAT_A_RECONSTRUCTION: SUFFICIENT_FOR_ASSIGNED_WORK
SEAT_B_RECONSTRUCTION: SUFFICIENT_FOR_REVIEW
INPUT_FRAME_IDENTITY: PRESERVED
WORK_ITEM_IDENTITY: PRESERVED
OUTPUT_IDENTITY: PRESERVED
UNRESOLVED_LOAD: EXPLICIT
AUTHORITY_EFFECT: NONE
SCIENTIFIC_PROMOTION: NONE
AUTO_NEXT_SEAT_INVOCATION: NO
AUTO_RETRY: NO
```

## Stop membrane

Stop after H2.

Do not build a scheduler, swarm, clock, automatic worker spawn, automatic
authority, automatic qualification, or generic orchestration framework.
