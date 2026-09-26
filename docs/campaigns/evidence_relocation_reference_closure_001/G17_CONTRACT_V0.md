# G17 Relocation Reference Closure Contract V0

STATUS:
CANDIDATE

TARGET:
MECHANICALLY INVENTORY TRACKED-TREE REFERENCES TO THE 37 RELOCATED ROOT ARTIFACTS

SOURCE_INVENTORY:
docs/evidence/for_planner/ROOT_EVIDENCE_INVENTORY.md

MOVED_ARTIFACT_COUNT:
37

INPUT_SCOPE:
git-tracked files at the exact run source

FOR EACH MOVED ARTIFACT:
record:
- original_root_path
- relocated_path
- expected_blob
- relocated_path_current_blob
- relocated_blob_matches_inventory
- qualified_route_occurrences
- bare_or_root_style_occurrences
- occurrence locations

OCCURRENCE_CLASSIFICATION:

RELOCATED_QUALIFIED_ROUTE:
the exact text
docs/evidence/for_planner/<original_root_path>
appears in the line.

BARE_OR_ROOT_STYLE_MENTION:
the artifact basename appears, but the exact relocated path does not appear in
that line.

IMPORTANT:

BARE_OR_ROOT_STYLE_MENTION
!=
BROKEN_DEPENDENCY

The mechanical observer must not infer whether a bare occurrence is:
- an operative route;
- historical prose;
- a migration record;
- specimen content;
- a non-routing mention;
- unresolved.

REQUIRED_ASSEMBLY:
INVENTORY_ROWS_PARSED = 37
ALL_RELOCATED_PATHS_PRESENT = true
ALL_RELOCATED_BLOBS_MATCH_INVENTORY = true

MECHANICAL_OUTPUT:
docs/evidence/for_planner/evidence_relocation_reference_closure_v0_observation.json

NONCLAIMS:
No dependency classification.
No automatic repair.
No reference-rewrite authority.
No generic relocation resolver.
No archive policy.
No cold-storage admission.
No deletion permission.
No planning, authority, execution, or scientific standing.

STOP:
after mechanical occurrence inventory.
