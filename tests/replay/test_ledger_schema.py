from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.ledger import (
    HASH_BOUNDARY,
    JsonlLedger,
    canonical_json,
    missingness_envelopes,
    preservation_envelope,
    record_digest,
    validate_ledger_record,
)


def schema_ready_record(envelope: dict[str, object]) -> dict[str, object]:
    boundary = {
        "record_id": "schema-000001",
        "commit_index": 1,
        "envelope": envelope,
    }
    return {
        **boundary,
        "integrity": {
            "algorithm": "sha256",
            "boundary": HASH_BOUNDARY,
            "digest": record_digest(boundary),
        },
    }


class LedgerSchemaTest(unittest.TestCase):
    def test_current_runtime_record_conforms_to_schema(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            record = ledger.append(preservation_envelope())

        self.assertTrue(validate_ledger_record(record).valid)

    def test_schema_rejects_runtime_possible_non_object_envelope(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            record = ledger.append(["runtime can persist this list"])  # type: ignore[arg-type]
            self.assertTrue(ledger.verify().ok)

        result = validate_ledger_record(record)

        self.assertFalse(result.valid)
        self.assertIn("$.envelope", [error.path for error in result.errors])

    def test_schema_rejects_runtime_possible_nan_inside_envelope(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            record = ledger.append({"value": math.nan})
            self.assertTrue(ledger.verify().ok)

        result = validate_ledger_record(record)

        self.assertFalse(result.valid)
        self.assertEqual(result.errors[0].validator, "json_domain")

    def test_schema_validity_does_not_establish_integrity_validity(self) -> None:
        record = schema_ready_record({"value": "before"})
        mutated = deepcopy(record)
        mutated["envelope"]["value"] = "after"  # type: ignore[index]

        self.assertTrue(validate_ledger_record(mutated).valid)
        with TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "ledger.jsonl"
            ledger_path.write_text(canonical_json(mutated) + "\n", encoding="utf-8")
            verification = JsonlLedger(ledger_path).verify()

        self.assertFalse(verification.ok)

    def test_missingness_cases_are_schema_valid_but_convention_dependent(self) -> None:
        with TemporaryDirectory() as tmpdir:
            ledger = JsonlLedger(Path(tmpdir) / "ledger.jsonl")
            records = [ledger.append(envelope) for envelope in missingness_envelopes()]

        self.assertTrue(all(validate_ledger_record(record).valid for record in records))
        states = [next(iter(record["envelope"]["missingness"].values())) for record in records]
        self.assertEqual(states, ["absent", "explicit_null", "unavailable", "malformed"])

    def test_per_record_schema_does_not_enforce_cross_record_invariants(self) -> None:
        first = schema_ready_record({"value": 1})
        second = schema_ready_record({"value": 2})

        self.assertTrue(validate_ledger_record(first).valid)
        self.assertTrue(validate_ledger_record(second).valid)
        self.assertEqual(first["record_id"], second["record_id"])
        self.assertEqual(first["commit_index"], second["commit_index"])


if __name__ == "__main__":
    unittest.main()

