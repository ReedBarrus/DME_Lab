# ATLAS BRIDGE EVIDENCE DELIVERY FAILURE 001

OBJECT_TYPE:
APPARATUS_FAILURE_WITNESS

OBJECT_ID:
ATLAS_BRIDGE_EVIDENCE_DELIVERY_FAILURE_001

REQUEST_ID:
ROUND014_COMPRESSION_CELL002_ADJUDICATION

TRANSPORT_STATUS:
SUCCESS

MODEL_INVOCATION_STATUS:
SUCCESS

RESULT_WITNESS_STATUS:
SUCCESS

REQUIRED_EVIDENCE_DELIVERY:
FAILED

SCIENTIFIC_ADJUDICATION_PRODUCED:
NO

# FAILURE

The adjudication prompt referenced required repository evidence by path, but the
local LM Studio bridge supplied only the adjudication packet text.

The local model had:
- no repository access;
- no tools;
- no connectors;
- no external retrieval.

The model explicitly stated that it could not access the referenced files and
returned a generic adjudication procedure plus hypothetical example output.

# NON-COLLAPSES

REQUEST_DELIVERED
!=
REQUIRED_EVIDENCE_DELIVERED

MODEL_RESPONSE_PRODUCED
!=
SCIENTIFIC_ADJUDICATION_PRODUCED

TRANSPORT_SUCCESS
!=
EVIDENCE-COMPLETE TASK SUCCESS

# DISPOSITION

APPARATUS_DELIVERY_FAILURE

The response is not admissible as Cell 002 adjudication evidence.

# REPAIR DIRECTION

Assemble the exact required evidence into a bounded model-visible evidence
bundle before invocation while preserving:
- immutable source identity;
- evidence boundaries;
- bundle identity;
- no model repository access;
- no model tools/network authority.
