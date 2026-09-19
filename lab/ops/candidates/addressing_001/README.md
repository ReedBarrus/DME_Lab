# ADDRESSING_001 — bounded role-local availability apparatus

**Basis:** `e0b17587f29a2f66711544f839283ea1ec43cd64`  
**Status:** APPARATUS ONLY — identity geometry repaired; held-out A/B not realized  
**Execution authority:** NONE  
**Scientific standing:** unchanged

## Question

```text
Does exact TARGET_ROLE identity
mechanically determine role-local work availability
while preserving global durable existence
and without conferring consequence authority?
```

## Frozen distinctions

```text
WORK EXISTS
!=
WORK AVAILABLE TO ROLE

WORK AVAILABLE TO ROLE
!=
WORK VISIBLE TO AUDIT / REGISTRY

TARGET_ROLE
!=
CURRENT SEAT INSTANCE

AVAILABLE_TO_ROLE
!=
AUTHORIZED_TO_EXECUTE

DURABLE RECORD IDENTITY
!=
MANIPULATED WORK PAYLOAD
```

## Identity geometry

The repaired candidate separates durable coexistence identity from the scientific
work payload:

```text
DURABLE_WORK_RECORD_v0
  record_id
  work_payload

ADDRESSED_WORK_v0
  source_role
  target_role
  created_against_basis
  task_type
  payload_refs
  authority_ceiling
  required_output_type
  depends_on
  supersedes
```

`record_id` is required for distinct durable records and global audit identity.
It is outside the compared work payload.

The later matched pair may therefore use:

```text
record_A.record_id != record_B.record_id

record_A.work_payload
==
record_B.work_payload

except:

record_A.work_payload.target_role = WORKSHOP
record_B.work_payload.target_role = COMMANDER
```

No held-out A/B record is materialized by this apparatus.

## Role registry

`role_registry_v0.json` names exactly:

```text
COMMANDER
WORKSHOP
```

No hierarchy, aliasing, permissions, personality inference, or seat-instance
identity is part of role resolution.

## Causal firewall

The global registry loader reads every durable record without target-role
filtering.

The role-local projection is exactly:

```text
AVAILABLE_WORK(role_id)
=
{
  record |
  record.work_payload.target_role == role_id
}
```

The projection may read:

```text
work_payload.target_role
```

It must not read:

```text
record_id
filename
registry key
insertion order
path
timestamp
serialization position
seat-instance identity
```

The projection is read-only. It does not mutate work, interpret
`authority_ceiling`, acknowledge work, claim work, execute work, or hide
non-target records from the global registry.

## Qualification pressures

```text
Q1 — RECORD IDENTITY FIREWALL

same work payload
different record_id only
→ same role-local availability
```

```text
Q2 — TARGET ROLE DISCRIMINATION

same administrative record geometry
same work payload except target_role
→ different role-local availability
```

Qualification command:

```bash
python -m unittest tests.lab.test_addressing_001_apparatus -v
```

Current local qualification:

```text
9 tests
PASS
```

Qualification uses dummy values only and does not instantiate the held-out A/B
pair.

It additionally checks:

- the role registry is explicit and exact;
- `record_id` is outside `work_payload`;
- global existence is preserved before and after role-local projection;
- non-target work remains present globally;
- projection accepts `role_id`, not seat-instance identity;
- the projection implementation contains no read of `record_id` or the frozen
  forbidden administrative coordinates;
- projection does not strengthen `authority_ceiling`;
- records and work payloads are immutable after validation;
- unknown roles and injected authority flags are rejected;
- duplicate global `record_id` values are rejected.

## Claim ceiling

Successful apparatus qualification establishes only that this candidate
implementation supplies a bounded surface in which:

```text
RECORD_IDENTITY
→ durable coexistence / audit distinction

RECORD_IDENTITY
↛ role-local availability

TARGET_ROLE
→ role-local availability
```

for the dummy qualification surface.

It does not establish the held-out scientific `ADDRESSING_001` result.

It also does **not** establish:

```text
seat-replacement continuity
acknowledgement semantics
claim semantics
pending-work semantics
stale-basis policy
role hierarchy
permissions / secrecy
scheduler behavior
cursor semantics
autonomous execution
```
