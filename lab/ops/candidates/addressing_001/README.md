# ADDRESSING_001 — bounded role-local availability apparatus

**Basis:** `e0b17587f29a2f66711544f839283ea1ec43cd64`  
**Status:** APPARATUS ONLY — scientific matched pair not realized; A/B identity treatment not yet frozen  
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
```

## Candidate surface

`role_registry_v0.json` names exactly two role identities:

```text
COMMANDER
WORKSHOP
```

An `AddressedWork` is an immutable value with exactly:

```text
work_id
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

The global registry loader reads all durable work objects without target-role filtering.
The role-local projection is exactly:

```text
AVAILABLE_WORK(role_id)
=
{
  work |
  work.target_role == role_id
}
```

No seat-instance identity is an input to the projection.

The projection is read-only. It does not mutate work, interpret `authority_ceiling`,
claim work, acknowledge work, execute work, or hide non-target work from the global registry.

## Intended later matched pressure

The scientific A/B objects are **not materialized or realized by this implementation**.
A later frozen pressure must first close one identity seam: two coexisting durable records
need distinct record identity somewhere, while the scientific discriminator is intended to
be only `TARGET_ROLE`. This apparatus does not silently decide whether that identity is
inside `work_id` or carried by an external experimental/registry coordinate.

The intended semantic cut remains:

```text
A.target_role = WORKSHOP
B.target_role = COMMANDER

all non-administrative matched content:
identical
```

For one `ROLE_ID = WORKSHOP` projection, the bounded discriminator is:

```text
GLOBAL REGISTRY:
A = EXISTS
B = EXISTS

WORKSHOP ROLE-LOCAL PROJECTION:
A = AVAILABLE_TO_ROLE
B = NOT_AVAILABLE_TO_ROLE
```

## Qualification

```bash
python -m unittest tests.lab.test_addressing_001_apparatus -v
```

Qualification uses dummy work identities and does not instantiate the later held-out A/B pair.
It checks:

- the role registry is explicit and exact;
- global existence is preserved before and after role-local projection;
- exact target-role identity controls the dummy role-local projection while dummy durable identities remain distinct;
- non-target work remains present globally;
- projection accepts `role_id`, not seat-instance identity;
- projection does not strengthen `authority_ceiling`;
- unknown roles and injected authority flags are rejected;
- work objects are immutable after validation;
- duplicate global work identities are rejected.

## Claim ceiling

Successful apparatus qualification can establish only that this candidate implementation
provides a bounded surface on which a later, separately frozen pressure can test whether exact
`TARGET_ROLE` identity is behaviorally material to role-local work availability while global
work existence remains visible. Qualification does not close the later A/B identity geometry.

It does **not** establish:

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
scientific ADDRESSING_001 result
```
