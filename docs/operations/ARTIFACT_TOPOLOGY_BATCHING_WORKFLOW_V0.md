# Artifact Topology & Batching Workflow V0

OBJECT_TYPE:
GENERAL_WORKFLOW_SURFACE

OBJECT_ID:
ARTIFACT_TOPOLOGY_BATCHING_WORKFLOW_V0

STANDING:
OPERATIVE_WORKFLOW_RULE

# PURPOSE

Keep high-volume scientific and operational artifacts navigable without losing
history, provenance, standing, or relational context.

The repository should not accumulate hundreds of same-family files in one
directory merely because they were produced sequentially.

Organization is part of memory management.

# CORE LAW

CATEGORIZE_TOPOLOGICALLY
→ THEN BATCH_BY_RELATION

not:

BATCH_BY_FILE_COUNT
→ THEN GUESS_RELATION

# NON-COLLAPSES

FILE_LOCATION
!=
SCIENTIFIC_STANDING

MOVE
!=
SEMANTIC_MUTATION

FOLDER
!=
AUTHORITY_DOMAIN

HISTORY
!=
CURRENT_NAVIGATION_SURFACE

SAME_PREFIX
!=
SAME_TOPOLOGICAL_ROLE

# SOFT / HARD DENSITY RULE

SOFT_REVIEW_THRESHOLD:
15 files of one coherent relation-family in one directory

DEFAULT_BATCH_THRESHOLD:
20 files of one coherent relation-family in one directory

At or above the threshold, an agent should ask:

1. Do these files share one stable topological relation?
2. Is there an existing canonical folder for that relation?
3. If not, does a new folder reduce navigation burden without hiding cross-cutting
   dependencies?
4. Are there live path references that must be updated?
5. Can the move be expressed as pure renames with zero content mutation?

# BATCHING ORDER

1. RELATION / FUNCTION
   Examples:
   - conversation candidate extraction
   - relational horizon planning
   - Atlas core / metabolism / continuity artifacts
   - representation-transformation pressure
   - bridge lifecycle
   - single-seat lifecycle

2. LINEAGE / CAMPAIGN
   Keep artifacts that share a pressure family, cell lineage, or operator surface
   together.

3. STAGE / DISPOSITION
   Only when a relation-family itself becomes too dense, subdivide by stage such
   as:
   - packets
   - frozen outputs
   - adjudications
   - results
   - receipts

4. CHRONOLOGY
   Use chronology only inside an already coherent relation-family. Do not use
   arbitrary "batch_001" folders merely to reduce file count.

# AGENT WORKFLOW

Before creating a new artifact:

A. Identify its topological family.
B. Resolve the current canonical folder from the topology rule registry.
C. Count same-family siblings.
D. If the family is already batched, write directly into its canonical folder.
E. If a new family crosses the review threshold, create or extend a declared rule
   before adding more root-level files.
F. Preserve immutable historical references; update only current/live references.
G. Run structural/path checks after moves.
H. Record pure-reorganization commits separately from semantic changes whenever
   practical.

# CURRENT OPERATIVE RULE REGISTRY

Machine-readable rules live at:

config/artifact_topology_rules_v0.json

Automation / audit helper:

tools/artifact_topology_audit_v0.py

The helper is deliberately conservative:
- dry-run by default;
- moves only explicitly declared families;
- refuses collisions;
- refuses mutation on a dirty working tree;
- uses git mv;
- never edits artifact contents while organizing them.

# REFERENCE HYGIENE

Immutable packet references bound to historical commit + path remain valid.

Current/live references should point to the current canonical path.

After a reorganization:

- run repository path-reference checks;
- update tests and operational docs that intentionally follow current paths;
- do not rewrite frozen historical packets solely to modernize paths.

# INDEXING RULE

When a folder exceeds approximately 20 artifacts, prefer a short README or index
that states:

- family purpose;
- key entry points;
- current/active artifacts;
- frozen/historical artifacts;
- next pressure or unresolved seam.

The index is navigation metadata, not scientific standing.

# MEMORY MANAGEMENT INTERPRETATION

Repository organization is a bounded form of environmental memory metabolism:

ACCUMULATED ARTIFACTS
→ RELATIONAL CLASSIFICATION
→ CANONICAL LOCATION
→ NAVIGABLE INDEX
→ RECONSTRUCTABLE HISTORY

The process should reduce active search burden without compressing away
provenance or standing distinctions.

# TRIGGER FOR AGENT ACTION

An agent maintaining the repository should perform a topology audit when any of
the following become true:

- a directory gains 15+ same-family siblings;
- a campaign root exceeds 40 direct child artifacts;
- repeated search/navigation failures occur;
- a new pressure family begins producing multiple cells;
- an existing family gains a second distinct lifecycle stage that would benefit
  from subdivision.

# CLAIM CEILING

This workflow governs repository navigation and environmental memory
organization only.

It does not establish scientific validity, authority, execution permission, or
automatic semantic classification.
