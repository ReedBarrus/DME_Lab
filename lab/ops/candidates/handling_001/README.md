# HANDLING_001 — bounded explicit handling-claim apparatus

Basis: ce205ca6e6052e5a08d227d7f663f4a7cbd88c94
Status: APPARATUS ONLY — mechanically qualified; held-out contract not frozen; held-out realization not executed
Execution authority: NONE
Scientific standing: unchanged

## Candidate event

HANDLING_CLAIM_EVENT_v0 has exactly:

- claim_event_id
- event_type
- work_record_id

No claimant, owner, seat, cursor, completion, acknowledgement, release,
expiration, transfer, arbitration, routing, or execution field is introduced.

## Correspondence

CORRESPONDS(claim, work) is true only when:

claim.event_type == CLAIM_FOR_HANDLING

and:

claim.work_record_id == work.record_id

WORK_CLAIMED_FOR_HANDLING(work) is true iff at least one valid corresponding
claim exists. Malformed claim mappings are rejected by the event parser and do
not count.

## Causal firewall

The predicate reads only claim.event_type, claim.work_record_id, and
work.record_id. It does not mutate the durable work record or its immutable
addressed-work payload. The existing ADDRESSING_001 projection remains
unchanged.

## Qualification

Command:

python -m unittest tests.lab.test_handling_001_apparatus -v

Qualified surface:

Q1 no claim -> false
Q2 exact corresponding claim -> true
Q3 claim for other work -> false
Q4 wrong event_type for this work -> false
Q5 malformed claim -> rejected / not counted

Additional checks preserve work mapping, record identity, global existence,
role-local availability, and the NO_CONSEQUENCE_AUTHORITY ceiling. The handling
predicate has no execution or consequence input.

Current mechanical qualification:

8 tests
PASS

## Claim ceiling

This apparatus qualification does not establish the held-out HANDLING_001
scientific result.

Not earned: claim-owner semantics, release, expiration, exclusive ownership,
multiple-claim arbitration, pending-work, completion, acknowledgement, seat
continuity, handling continuity across seats, cursor semantics, routing
continuity, or execution authority.
