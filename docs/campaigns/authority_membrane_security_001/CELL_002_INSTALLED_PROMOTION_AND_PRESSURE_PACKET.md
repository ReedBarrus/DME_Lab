# CELL 002 INSTALLED PROMOTION AND PRESSURE PACKET

TARGET:
AUTHORITY_MEMBRANE_SECURITY_CELL_002

ROLE:
TRUST-ROOT PROMOTION / INSTALLED PRESSURE

OBJECTIVE:

Promote the reviewed principal-bound one-shot authority
consumption primitive into the local trust root and pressure
the operative path without broadening capability.

DO NOT:
- add multi-use authority;
- add self-authorization;
- add seat spawning;
- add repo-write / CLI / arbitrary network authority;
- add revocation semantics yet;
- add Cockpit write authority directly;
- begin external membrane work.

## Promotion target

Installed trust-root remains rooted under:

%USERPROFILE%\.dme_lab_bridge

Current authority state:

%USERPROFILE%\.dme_lab_bridge\authority_state_v0\

The repo is not the source of current authority.

## Required installed pressures

CONTROL:

principal P
fresh P-bound CAP
use_limit=1
remaining=1

-> reserve authority before invocation
-> invocation boundary crosses once
-> remaining=0
-> status=CONSUMED
-> receipt persists

REPLAY:

principal P
same exact consumed CAP

-> decision DENY / AUTHORITY_EXHAUSTED
-> no new reservation
-> invocation delta=0
-> historical receipt remains readable

WRONG PRINCIPAL:

principal Q != P
fresh active P-bound CAP

-> decision DENY / PRINCIPAL_MISMATCH
-> reservation count=0
-> invocation count=0
-> remaining remains 1
-> status remains ACTIVE

## Required receipts

Installed receipt / denial evidence must include:

capability_id
approval_id
principal_id
attempting_principal_id where applicable
request / input identity
model / endpoint
executor hash
policy hash
pre/post remaining uses
pre/post status
reservation identity
invocation count
decision / reason
current authority standing
historical receipt linkage

## Claim ceiling after survival

At the tested installed executor / policy / authority-state
coordinates, one declared-principal-bound one-shot authority
envelope admitted at most one sequential invocation-boundary
crossing, denied exact replay after consumption, and denied a
mismatched declared principal before reservation or invocation.

No authentication / concurrency / crash / revocation /
containment claim is earned.
