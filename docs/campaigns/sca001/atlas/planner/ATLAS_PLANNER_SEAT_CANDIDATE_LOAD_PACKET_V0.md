# ATLAS PLANNER SEAT CANDIDATE LOAD PACKET V0

OBJECT_TYPE:
ATLAS_CANDIDATE_LOAD_PACKET

OBJECT_ID:
ATLAS_PLANNER_SEAT_CANDIDATE_LOAD_PACKET_V0

TARGET_OBJECT:
ATLAS_RELATIONAL_HORIZON_PLANNER_SEAT_CANDIDATE_V0

TARGET_STANDING:
CANDIDATE_ONLY

LOAD_DESTINATION:
ATLAS_CANDIDATE_OPERATIVE_SURFACE

FORMAL_REGISTRATION:
PROHIBITED

SCIENTIFIC_ADMISSION:
PROHIBITED

AUTHORITY_EFFECT:
NONE

# PURPOSE

Make the planner-seat candidate recoverable as an addressed Atlas candidate
without granting formal seat standing, topology standing, execution authority,
or occupant identity.

# CANDIDATE ADDRESS

atlas://operative-candidates/relational-horizon-planner/v0

# LOADABLE RELATIONS

CANDIDATE_HAS_PURPOSE:
relational-horizon planning

CANDIDATE_CONSUMES:
qualified frames
primary axes
projected consequential frames
unresolved load
provenance handles

CANDIDATE_PRODUCES:
horizon candidates
pressure families
redundancy findings
candidate next pressures
replan proposals

CANDIDATE_AUTHORITY:
NONE

CANDIDATE_EXECUTION:
NONE

CANDIDATE_OCCUPANT:
UNBOUND

# CHALLENGE PATH

The candidate must remain traceable to:
- its seat contract;
- planning-pressure results;
- planning adjudications;
- horizon-review artifacts;
- future seat-specific pressure results.

# LOAD CONDITION

LOAD_AS_CANDIDATE:
YES

PROMOTE_TO_FORMAL_SEAT:
NO

PROMOTION_REQUIRES:
- explicit seat pressure campaign;
- role/seat/occupant separation test;
- substitution/occupant-change pressure;
- missing-input failure-legibility pressure;
- cross-instance planning reconstruction pressure;
- formal adjudication.

# CLAIM CEILING

Candidate load makes the object environmentally addressable only.

Addressability
!=
formal seat standing

Candidate presence
!=
authority

Planner output
!=
admitted topology mutation
