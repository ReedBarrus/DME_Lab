# G17 Relocation Reference Closure Horizon V0

STATUS:
JUSTIFIED_CANDIDATE

PREDECESSOR:
G16 / EVIDENCE_PATH_RELOCATION_REACHABILITY_V0_MATCHED

EARNED_INVARIANT:
EMI-015 / CONTENT_IDENTITY_PRESERVATION != WITNESS_PATH_REACHABILITY

REPAIR_RECEIPT:
docs/campaigns/evidence_path_relocation_reachability_001/repairs/EVIDENCE_PATH_ROUTE_REPAIR_001.md

RELOCATION_INVENTORY:
docs/evidence/for_planner/ROOT_EVIDENCE_INVENTORY.md

MOVED_ARTIFACT_COUNT:
37

TARGET_RELATION:
KNOWN_ROUTE_REPAIR != RELOCATION_REFERENCE_CLOSURE

QUESTION:
After repairing the six exact invariant-ledger witness routes exposed by G16,
what other tracked-tree references still mention the old root-level artifact
identities, and which of those occurrences may require classification before
relocation dependency closure can be claimed?

FIRST_PRESSURE:
mechanical occurrence inventory only

SCAN_CLASSES:
- RELOCATED_QUALIFIED_ROUTE
- BARE_OR_ROOT_STYLE_MENTION

IMPORTANT:
BARE_OR_ROOT_STYLE_MENTION != BROKEN_DEPENDENCY

A later bounded classifier may distinguish:
- live route dependency;
- historical statement;
- specimen text;
- migration record;
- non-routing mention;
- unresolved.

REQUIRED_NONCOLLAPSES:
TEXT_OCCURRENCE != LIVE_DEPENDENCY
KNOWN_ROUTE_REPAIR != ALL_REFERENCE_CLOSURE
RELOCATED_ROUTE_PRESENT != ALL_DEPENDENCIES_REPAIRED
HISTORICAL_MENTION != CURRENT_ROUTE
REFERENCE_DISCOVERY != REFERENCE_REWRITE_AUTHORITY

DEFERRED:
automatic rewrite
generic relocation resolver
archive policy
cold-storage admission
deletion permission
global evidence lifecycle
planning
authority
execution

CLAIM_CEILING:
One tracked-tree occurrence inventory over the 37 exact artifacts listed in
ROOT_EVIDENCE_INVENTORY.md. No reference is classified as a live dependency by
the mechanical scan alone.
