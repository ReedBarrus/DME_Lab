"""Minimal synthetic ledger harness."""

from .continuity import ContinuityVerificationResult, verify_continuity
from .correspondence import (
    HistoryExtentComparisonResult,
    HistoryRelationResult,
    compare_extent_lower_bound,
    compare_history_extent,
    compare_prefix_preservation,
    history_extent,
    prefix_identity,
)
from .jsonl import (
    HASH_BOUNDARY,
    INTEGRITY_ALGORITHM,
    JsonlLedger,
    VerificationResult,
    canonical_json,
    record_digest,
)
from .live_ingest import (
    CANONICAL_LIVE_INGEST_LEDGER_PATH,
    canonical_live_ingest_ledger,
    replay_canonical_live_ingest,
    verify_canonical_live_ingest,
    verify_canonical_live_ingest_continuity,
)
from .schema import SCHEMA_PATH, SchemaError, SchemaValidationResult, load_schema, validate_ledger_record
from .synthetic import (
    amendment_pair,
    identity_collision_envelopes,
    missingness_envelopes,
    ordering_conflict_envelopes,
    preservation_envelope,
)

__all__ = [
    "HASH_BOUNDARY",
    "INTEGRITY_ALGORITHM",
    "JsonlLedger",
    "CANONICAL_LIVE_INGEST_LEDGER_PATH",
    "ContinuityVerificationResult",
    "HistoryExtentComparisonResult",
    "HistoryRelationResult",
    "SCHEMA_PATH",
    "SchemaError",
    "SchemaValidationResult",
    "VerificationResult",
    "amendment_pair",
    "canonical_json",
    "canonical_live_ingest_ledger",
    "compare_extent_lower_bound",
    "compare_history_extent",
    "compare_prefix_preservation",
    "history_extent",
    "identity_collision_envelopes",
    "missingness_envelopes",
    "ordering_conflict_envelopes",
    "preservation_envelope",
    "prefix_identity",
    "record_digest",
    "replay_canonical_live_ingest",
    "load_schema",
    "validate_ledger_record",
    "verify_canonical_live_ingest",
    "verify_canonical_live_ingest_continuity",
    "verify_continuity",
]
