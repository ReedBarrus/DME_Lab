from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from lab.ops.candidates.execution_stop_latch_001.fixture_setup import (
    DECLARATION_SCHEMA_VERSION,
    materialize_declared_initial_authority,
)
from lab.ops.candidates.execution_stop_latch_001.stop_latch import (
    ACTIVE,
    ExecutionStopLatch,
)
from lab.ops.candidates.workshop_authority_gate_001.consequence_adapter import (
    ADAPTER_ID,
    TARGET_BYTES,
    ExclusiveFileConsequenceAdapter,
    observe_target,
)
from src.runtime.workshop_frozen_cell import (
    E015,
    E017,
    FAULT_SCHEMA,
    RECEIPT_SCHEMA,
    STATE_AUTHORITY_ADMITTED,
    MemoryOutputSink,
    run_frozen_cell,
    sha256_bytes,
)

BASIS_SHA = "d83429f8cc25cfb2a6105af7ae9d41bcb1b023a2"
DUMMY_E = "WAG001-DUMMY-E"
SPECIMEN = b"WORKSHOP_AUTHORITY_GATE_001 dummy qualification specimen\n"


class WorkshopAuthorityGate001Test(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def manifest_bytes(self, root: Path) -> bytes:
        root.mkdir(parents=True)
        (root / "specimen.txt").write_bytes(SPECIMEN)
        manifest = {
            "schema": "workshop_frozen_cell_manifest_v0",
            "manifest_id": "WAG001-DUMMY-MANIFEST",
            "experiment_id": "WORKSHOP_AUTHORITY_GATE_001_QUALIFICATION",
            "cell_id": "DUMMY-CELL",
            "basis": {
                "contract_commit": BASIS_SHA,
                "authorization_ref": "WORKSHOP_AUTHORITY_GATE_001:APPARATUS_QUALIFICATION",
            },
            "inputs": {
                "specimen": {
                    "path": "specimen.txt",
                    "sha256": sha256_bytes(SPECIMEN),
                }
            },
            "assembly": {
                "encoding": "utf-8",
                "newline": "lf",
                "separator": "",
                "order": ["specimen"],
                "expected_payload_sha256": sha256_bytes(SPECIMEN),
            },
            "invocation": {
                "adapter": ADAPTER_ID,
                "surface": {
                    "adapter_id": {
                        "expected": ADAPTER_ID,
                        "verification": "VERIFIABLE_REQUIRED",
                    },
                    "consequence_kind": {
                        "expected": "exclusive_file_creation",
                        "verification": "VERIFIABLE_REQUIRED",
                    },
                },
            },
            "execution": {
                "max_invocations": 1,
                "retry_allowed": False,
                "repair_allowed": False,
                "skip_allowed": False,
                "best_effort_allowed": False,
            },
            "output": {
                "retain_raw": True,
                "hash_raw": True,
                "anonymize": False,
            },
        }
        return json.dumps(
            manifest,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ).encode("utf-8")

    def materialize_active(self, store: Path) -> None:
        materialize_declared_initial_authority(
            store,
            {
                "schema_version": DECLARATION_SCHEMA_VERSION,
                "execution_envelope_id": DUMMY_E,
                "declared_state": ACTIVE,
            },
        )

    def run_case(self, name: str, *, active: bool):
        case = self.root / name
        workshop_root = case / "workshop"
        store = case / "authority"
        external = case / "external"
        external.mkdir(parents=True)
        target = external / "consequence.txt"
        manifest = self.manifest_bytes(workshop_root)
        self.assertFalse(target.exists())
        if active:
            self.materialize_active(store)
        self.assertFalse(target.exists())

        latch = ExecutionStopLatch(store, DUMMY_E)
        adapter = ExclusiveFileConsequenceAdapter(target)
        report = run_frozen_cell(
            manifest_bytes=manifest,
            authorized_manifest_sha256=sha256_bytes(manifest),
            root=workshop_root,
            adapter=adapter,
            output_sink=MemoryOutputSink(),
            execution_stop_latch=latch,
        )
        return manifest, latch, adapter, report, observe_target(target)

    def test_dummy_active_and_absent_use_same_runner_path(self) -> None:
        active_manifest, _, active_adapter, active_report, active_target = self.run_case(
            "active", active=True
        )
        absent_manifest, absent_latch, absent_adapter, absent_report, absent_target = self.run_case(
            "absent", active=False
        )

        self.assertEqual(active_manifest, absent_manifest)
        self.assertEqual(active_report["schema"], RECEIPT_SCHEMA)
        self.assertIn(STATE_AUTHORITY_ADMITTED, active_report["state_trace"])
        self.assertEqual(active_adapter.surface_observation_count, 1)
        self.assertEqual(active_adapter.invocation_count, 1)
        self.assertTrue(active_target["exists"])

        self.assertEqual(absent_report["schema"], FAULT_SCHEMA)
        self.assertEqual(absent_report["code"], E015)
        self.assertEqual(absent_adapter.surface_observation_count, 0)
        self.assertEqual(absent_adapter.invocation_count, 0)
        self.assertFalse(absent_target["exists"])
        self.assertFalse(absent_latch.state_path.exists())

    def test_external_target_creation_is_exclusive(self) -> None:
        case = self.root / "preexisting"
        workshop_root = case / "workshop"
        store = case / "authority"
        external = case / "external"
        external.mkdir(parents=True)
        target = external / "consequence.txt"
        manifest = self.manifest_bytes(workshop_root)
        self.materialize_active(store)
        target.write_bytes(b"PREEXISTING\n")
        before = target.read_bytes()

        adapter = ExclusiveFileConsequenceAdapter(target)
        report = run_frozen_cell(
            manifest_bytes=manifest,
            authorized_manifest_sha256=sha256_bytes(manifest),
            root=workshop_root,
            adapter=adapter,
            output_sink=MemoryOutputSink(),
            execution_stop_latch=ExecutionStopLatch(store, DUMMY_E),
        )

        self.assertEqual(report["schema"], FAULT_SCHEMA)
        self.assertEqual(report["code"], E017)
        self.assertEqual(target.read_bytes(), before)
        self.assertNotEqual(target.read_bytes(), TARGET_BYTES)


if __name__ == "__main__":
    unittest.main()
