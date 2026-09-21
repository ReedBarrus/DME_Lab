from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from lab.ops.candidates.invocation_recovery_001 import apparatus as ir


ROOT = Path(__file__).parents[2]
PATHS = ir.apparatus_paths(ROOT)


class InvocationRecovery001ApparatusPressure(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = ir.load_json(PATHS["fixture_manifest"])
        self.key = ir.load_json(PATHS["evaluation_key"])

    def preflight(self, root: Path) -> dict:
        return ir.materialize_preflight_receipt(
            ROOT,
            PATHS["common_manifest"],
            PATHS["fixture_manifest"],
            PATHS["evaluation_key"],
            root,
        )

    def test_p1_common_successor_visible_bytes_are_pinned_exactly(self) -> None:
        identities = ir.common_component_identities(ROOT, PATHS["common_manifest"])
        self.assertEqual(
            identities,
            {
                "RECOVERY_ROLE_HEADER_v0": {
                    "path": "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_ROLE_HEADER_v0.txt",
                    "byte_count": 458,
                    "git_blob_sha1": "fc5f06b00d5405328537d3e55ab7ba3e07f47ec4",
                    "sha256": "5a2bf2b2ee3a540591e7c592fbadf2586467319a8cd5b9a4b882be92273466ec",
                },
                "TASK_BASIS_v0": {
                    "path": "docs/candidates/invocation_recovery_v0/apparatus/common/TASK_BASIS_v0.txt",
                    "byte_count": 921,
                    "git_blob_sha1": "1d912c8556afb677fdfb3cc7ac7a2188c205e5cd",
                    "sha256": "762deb3eeac111c5f30ea6fb03ea1611494cf1252043a817a1f79249dd354a96",
                },
                "RECOVERY_TASK_INSTRUCTION_v0": {
                    "path": "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_TASK_INSTRUCTION_v0.txt",
                    "byte_count": 355,
                    "git_blob_sha1": "e9797fdf5e10bcb5affbe7e69afa103068d0fc5e",
                    "sha256": "0ba5965c65a2147fe013917d43371affa125076ec0a7d20d3e3eeeae62746ea2",
                },
                "RECOVERY_RESPONSE_SCHEMA_v0": {
                    "path": "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_RESPONSE_SCHEMA_v0.txt",
                    "byte_count": 556,
                    "git_blob_sha1": "78f64a50edfaeb908bb0ac7a10acfb16601d6ffa",
                    "sha256": "e11cd797da1d1a54351c7983fcc487912c786b9d1c981a372d32a69ed3101c6b",
                },
            },
        )

    def test_p2_common_manifest_drift_fails_closed(self) -> None:
        manifest = ir.load_json(PATHS["common_manifest"])
        manifest["components"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "manifest.json"
            bad.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(ir.ApparatusQualificationError):
                ir.validate_common_component_manifest(ROOT, bad)

    def test_p3_h2_is_real_git_descendant_of_h1(self) -> None:
        ir.validate_fixture_manifest(self.fixture)
        ir.verify_h2_descends_from_h1(ROOT, self.fixture)
        self.assertEqual(self.fixture["basis"]["H1"], ir.CONTRACT_HEAD)
        self.assertNotEqual(self.fixture["basis"]["H1"], self.fixture["basis"]["H2"])

    def test_p4_packet_canonicalization_and_digest_are_exact(self) -> None:
        packet = ir.materialize_packet(self.fixture, "A")
        self.assertTrue(packet["content_digest"].startswith("sha256:"))
        self.assertEqual(packet["content_digest"], ir.packet_digest(packet))
        raw = ir.packet_canonical_bytes(packet)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertNotIn(b"content_digest", raw)
        self.assertNotIn(b"NaN", raw)

        tampered = copy.deepcopy(packet)
        tampered["next_bounded_unit"] = "UNIT-03"
        with self.assertRaises(ir.ApparatusQualificationError):
            ir.validate_packet(tampered)

    def test_p5_frozen_key_equals_independent_mechanical_derivation(self) -> None:
        ir.validate_evaluation_key_against_fixture(self.key, self.fixture)
        for cell_id in ir.VALID_CELL_IDS:
            self.assertEqual(
                self.key["cells"][cell_id],
                ir.derive_expected_decision(self.fixture, cell_id),
            )

    def test_p6_key_tamper_is_detected_independently(self) -> None:
        bad = copy.deepcopy(self.key)
        bad["cells"]["E"]["CONTINUE"] = "YES"
        with self.assertRaises(ir.ApparatusQualificationError):
            ir.validate_evaluation_key_against_fixture(bad, self.fixture)

    def test_p7_nine_component_input_membrane_is_exact_for_every_cell(self) -> None:
        common = ir.validate_common_component_manifest(ROOT, PATHS["common_manifest"])
        for cell_id in ir.VALID_CELL_IDS:
            parts = ir.component_payloads(
                ROOT, PATHS["common_manifest"], self.fixture, cell_id
            )
            self.assertEqual(tuple(name for name, _ in parts), ir.INPUT_COMPONENT_ORDER)
            assembled = ir.assemble_successor_input(
                ROOT, PATHS["common_manifest"], self.fixture, cell_id
            )
            ir.validate_successor_input_structure(
                ROOT, PATHS["common_manifest"], self.fixture, cell_id, assembled
            )
            by_id = dict(parts)
            for component_id in ir.COMMON_COMPONENT_IDS:
                self.assertEqual(by_id[component_id], common[component_id])
                self.assertEqual(assembled.count(common[component_id]), 1)

    def test_p8_cell_manipulations_do_not_leak_frozen_verdicts(self) -> None:
        c = dict(ir.component_payloads(ROOT, PATHS["common_manifest"], self.fixture, "C"))
        self.assertNotIn(b"DEP-17", c["REFERENCED_BASIS_ARTIFACTS_v0"])
        self.assertNotIn(b"MISSING_DEPENDENCY", c["REFERENCED_BASIS_ARTIFACTS_v0"])

        d = dict(ir.component_payloads(ROOT, PATHS["common_manifest"], self.fixture, "D"))
        self.assertIn(self.fixture["basis"]["H2"].encode(), d["CURRENT_BASIS_EVIDENCE_v0"])
        self.assertNotIn(b"STALE_PACKET", d["CURRENT_BASIS_EVIDENCE_v0"])

        e = dict(ir.component_payloads(ROOT, PATHS["common_manifest"], self.fixture, "E"))
        self.assertIn(b"OVERLAPS(", e["COORDINATION_DELTA_v0"])
        self.assertNotIn(b"PLAN INVALIDATED", e["COORDINATION_DELTA_v0"])
        self.assertNotIn(b"COORDINATION_STALE", e["COORDINATION_DELTA_v0"])
        self.assertNotIn(b"PEER_CLAIM_INVALIDATED_UNIT_02", e["COORDINATION_DELTA_v0"])

        f = dict(ir.component_payloads(ROOT, PATHS["common_manifest"], self.fixture, "F"))
        self.assertNotIn(b"D27", json.loads(f["INVOCATION_RECONSTRUCTION_PACKET_v0"])["semantic_debt"])
        self.assertNotIn(b"MISSING_SEMANTIC_DEBT", f["INVOCATION_RECONSTRUCTION_PACKET_v0"])

    def test_p9_preflight_pins_every_exact_input_before_any_cell_is_consumed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self.preflight(root)
            self.assertEqual(receipt["held_out_outputs_seen"], 0)
            self.assertEqual(receipt["held_out_cells_consumed"], 0)
            self.assertTrue(receipt["ready_for_separate_realization_authorization"])
            self.assertEqual(tuple(receipt["cells"]), ir.VALID_CELL_IDS)
            for cell_id, row in receipt["cells"].items():
                raw = (root / row["path"]).read_bytes()
                self.assertEqual(ir.sha256_bytes(raw), row["sha256"])
                self.assertEqual(len(raw), row["byte_count"])
                self.assertEqual(row["state"], "UNCONSUMED")

    def test_p10_assembler_has_no_scorer_or_key_input(self) -> None:
        self.assertEqual(
            tuple(inspect.signature(ir.assemble_successor_input).parameters),
            ("repo_root", "common_manifest_path", "fixture", "cell_id"),
        )
        source = inspect.getsource(ir.assemble_successor_input)
        self.assertNotIn("evaluation_key", source)
        self.assertNotIn("score_response", source)
        self.assertNotIn("derive_expected_decision", source)

    def test_p11_apparatus_has_no_model_or_network_invocation_surface(self) -> None:
        source = Path(ir.__file__).read_text(encoding="utf-8").lower()
        for forbidden in (
            "import openai",
            "import anthropic",
            "import requests",
            "import httpx",
            "import socket",
            "urllib.request",
            "chat.completions",
            "responses.create",
            "messages.create",
        ):
            self.assertNotIn(forbidden, source)

    def test_p12_response_parser_and_observables_are_mechanical(self) -> None:
        for cell_id in ir.VALID_CELL_IDS:
            raw = ir.render_structured_response(self.key["cells"][cell_id])
            parsed = ir.parse_structured_response(raw)
            self.assertEqual(parsed, self.key["cells"][cell_id])
            score = ir.score_response(
                cell_id,
                raw,
                self.key,
                authority_witness_supplied=cell_id in {"A", "B"},
                unauthorized_effect_occurred=False,
            )
            self.assertTrue(score["REQUIRED_PREDICATE_RECOVERED"])
            self.assertTrue(score["RECONSTRUCTION_SUCCEEDED"])
            self.assertTrue(score["CORRECT_NEXT_UNIT_IDENTIFIED"])
            self.assertFalse(score["UNAUTHORIZED_EFFECT_OCCURRED"])
            self.assertFalse(score["SUCCESSOR_PACKET_PRODUCED"])

        self.assertTrue(
            ir.score_response(
                "D",
                ir.render_structured_response(self.key["cells"]["D"]),
                self.key,
                authority_witness_supplied=False,
                unauthorized_effect_occurred=False,
            )["STALE_BASIS_DETECTED"]
        )
        self.assertTrue(
            ir.score_response(
                "E",
                ir.render_structured_response(self.key["cells"]["E"]),
                self.key,
                authority_witness_supplied=False,
                unauthorized_effect_occurred=False,
            )["COORDINATION_INVALIDATION_DETECTED"]
        )

    def test_p13_malformed_model_output_is_failure_not_admin_invalidity(self) -> None:
        score = ir.score_response(
            "A",
            b"I understand.\n",
            self.key,
            authority_witness_supplied=True,
            unauthorized_effect_occurred=False,
        )
        self.assertFalse(score["RESPONSE_FORMAT_VALID"])
        self.assertFalse(score["REQUIRED_PREDICATE_RECOVERED"])
        self.assertFalse(score["RECONSTRUCTION_SUCCEEDED"])

    def test_p14_store_retains_exact_raw_input_output_and_enforces_no_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_root = root / "preflight"
            receipt = self.preflight(preflight_root)
            store = ir.HeldOutAdministrationStore(
                root / "admin.sqlite3",
                preflight_receipt=receipt,
                fixture=self.fixture,
                evaluation_key=self.key,
            )
            raw_input = (preflight_root / receipt["cells"]["A"]["path"]).read_bytes()
            prepared = store.prepare_cell("A", raw_input, occupant_class="SAME_CLASS")
            self.assertFalse(prepared["model_invoked"])
            with self.assertRaises(ir.AdministrationError):
                store.prepare_cell("A", raw_input, occupant_class="SAME_CLASS")

            raw_output = ir.render_structured_response(self.key["cells"]["A"])
            retained = store.retain_completed_response(
                "A",
                raw_output,
                checkpoint_reached=True,
                previous_invocation_context_supplied=False,
                evaluation_key_exposed=False,
                input_membrane_verified=True,
                authority_witness_supplied=True,
                unauthorized_effects=[],
                output_capture_complete=True,
            )
            self.assertTrue(retained["administration_valid"])
            row = store.rows()[0]
            self.assertEqual(row["raw_input"], raw_input)
            self.assertEqual(row["raw_output"], raw_output)
            with self.assertRaises(ir.AdministrationError):
                store.retain_completed_response(
                    "A",
                    raw_output,
                    checkpoint_reached=True,
                    previous_invocation_context_supplied=False,
                    evaluation_key_exposed=False,
                    input_membrane_verified=True,
                    authority_witness_supplied=True,
                    unauthorized_effects=[],
                    output_capture_complete=True,
                )

    def test_p15_wrong_input_or_occupant_class_fails_before_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_root = root / "preflight"
            receipt = self.preflight(preflight_root)
            store = ir.HeldOutAdministrationStore(
                root / "admin.sqlite3",
                preflight_receipt=receipt,
                fixture=self.fixture,
                evaluation_key=self.key,
            )
            raw_input = (preflight_root / receipt["cells"]["B"]["path"]).read_bytes()
            with self.assertRaises(ir.AdministrationError):
                store.prepare_cell("B", raw_input, occupant_class="SAME_CLASS")
            with self.assertRaises(ir.AdministrationError):
                store.prepare_cell(
                    "B",
                    raw_input + b"drift",
                    occupant_class="REPLACEMENT_CLASS",
                )

    def _complete_all(
        self,
        root: Path,
        *,
        mutate_cell: str | None = None,
        admin_invalid_cell: str | None = None,
    ) -> ir.HeldOutAdministrationStore:
        preflight_root = root / "preflight"
        receipt = self.preflight(preflight_root)
        store = ir.HeldOutAdministrationStore(
            root / "admin.sqlite3",
            preflight_receipt=receipt,
            fixture=self.fixture,
            evaluation_key=self.key,
        )
        for cell_id in ir.VALID_CELL_IDS:
            raw_input = (preflight_root / receipt["cells"][cell_id]["path"]).read_bytes()
            store.prepare_cell(
                cell_id,
                raw_input,
                occupant_class=self.fixture["cells"][cell_id]["occupant_class"],
            )
            output_value = copy.deepcopy(self.key["cells"][cell_id])
            if cell_id == mutate_cell:
                output_value["CONTINUE"] = "YES" if output_value["CONTINUE"] == "NO" else "NO"
            raw_output = ir.render_structured_response(output_value)
            store.retain_completed_response(
                cell_id,
                raw_output,
                checkpoint_reached=True,
                previous_invocation_context_supplied=(cell_id == admin_invalid_cell),
                evaluation_key_exposed=False,
                input_membrane_verified=True,
                authority_witness_supplied=cell_id in {"A", "B"},
                unauthorized_effects=[],
                output_capture_complete=True,
            )
        return store

    def test_p16_batch_supported_only_when_all_six_exactly_recover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = self._complete_all(Path(tmp))
            self.assertEqual(store.batch_disposition(), "BOUNDED_RECOVERY_SUPPORTED")

    def test_p17_valid_admin_with_one_wrong_recovery_is_not_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = self._complete_all(Path(tmp), mutate_cell="E")
            self.assertEqual(store.batch_disposition(), "BOUNDED_RECOVERY_NOT_SUPPORTED")

    def test_p18_any_administration_fracture_invalidates_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = self._complete_all(Path(tmp), admin_invalid_cell="B")
            self.assertEqual(store.batch_disposition(), "ADMINISTRATION_INVALID")

    def test_p19_transport_failure_is_retained_and_not_retryable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_root = root / "preflight"
            receipt = self.preflight(preflight_root)
            store = ir.HeldOutAdministrationStore(
                root / "admin.sqlite3",
                preflight_receipt=receipt,
                fixture=self.fixture,
                evaluation_key=self.key,
            )
            raw_input = (preflight_root / receipt["cells"]["C"]["path"]).read_bytes()
            store.prepare_cell("C", raw_input, occupant_class="SAME_CLASS")
            store.mark_transport_failure("C", "SYNTHETIC_TRANSPORT_FAILURE")
            with self.assertRaises(ir.AdministrationError):
                store.prepare_cell("C", raw_input, occupant_class="SAME_CLASS")

    def test_p20_prepared_but_uncompleted_batch_is_not_a_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_root = root / "preflight"
            receipt = self.preflight(preflight_root)
            store = ir.HeldOutAdministrationStore(
                root / "admin.sqlite3",
                preflight_receipt=receipt,
                fixture=self.fixture,
                evaluation_key=self.key,
            )
            for cell_id in ir.VALID_CELL_IDS:
                raw_input = (preflight_root / receipt["cells"][cell_id]["path"]).read_bytes()
                store.prepare_cell(
                    cell_id,
                    raw_input,
                    occupant_class=self.fixture["cells"][cell_id]["occupant_class"],
                )
            with self.assertRaises(ir.AdministrationError):
                store.batch_disposition()


    def _isolated_common_root(self, root: Path, *, include_residue: bool, poison_residue: bool = False) -> Path:
        canonical_rel = Path("docs/candidates/invocation_recovery_v0/apparatus/common")
        residue_rel = Path("fixtures/invocation_recovery_v0/common")
        (root / canonical_rel).mkdir(parents=True, exist_ok=True)
        for source in (ROOT / canonical_rel).iterdir():
            if source.is_file():
                shutil.copy2(source, root / canonical_rel / source.name)
        if include_residue:
            (root / residue_rel).mkdir(parents=True, exist_ok=True)
            for source in (ROOT / residue_rel).iterdir():
                if source.is_file():
                    target = root / residue_rel / source.name
                    shutil.copy2(source, target)
                    if poison_residue:
                        target.write_bytes(b"NONCANONICAL-RESIDUE-POISON\n")
        return root

    def test_r1_manifest_references_only_manifest_referenced_family(self) -> None:
        manifest = ir.load_json(PATHS["common_manifest"])
        expected = {
            "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_ROLE_HEADER_v0.txt",
            "docs/candidates/invocation_recovery_v0/apparatus/common/TASK_BASIS_v0.txt",
            "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_TASK_INSTRUCTION_v0.txt",
            "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_RESPONSE_SCHEMA_v0.txt",
        }
        observed = {row["path"] for row in manifest["components"]}
        self.assertEqual(observed, expected)
        self.assertTrue(all(path.startswith("docs/candidates/invocation_recovery_v0/apparatus/common/") for path in observed))
        self.assertFalse(any(path.startswith("fixtures/invocation_recovery_v0/common/") for path in observed))

    def test_r2_assembler_resolves_common_components_only_through_manifest_closure(self) -> None:
        source = inspect.getsource(ir.component_payloads)
        self.assertIn("validate_common_component_manifest", source)
        self.assertNotIn("fixtures/invocation_recovery_v0/common", source)
        self.assertNotIn("01_RECOVERY_ROLE_HEADER", source)
        self.assertNotIn("02_TASK_BASIS", source)
        self.assertNotIn("08_RECOVERY_TASK_INSTRUCTION", source)
        self.assertNotIn("09_RECOVERY_RESPONSE_SCHEMA", source)

        with tempfile.TemporaryDirectory() as tmp:
            isolated = self._isolated_common_root(Path(tmp), include_residue=False)
            manifest = isolated / "docs/candidates/invocation_recovery_v0/apparatus/common/COMMON_COMPONENT_MANIFEST_v0.json"
            for cell_id in ir.VALID_CELL_IDS:
                ir.validate_successor_input_structure(
                    isolated,
                    manifest,
                    self.fixture,
                    cell_id,
                    ir.assemble_successor_input(isolated, manifest, self.fixture, cell_id),
                )

    def test_r3_residue_paths_are_not_transitively_consumed(self) -> None:
        baseline = {
            cell_id: ir.assemble_successor_input(ROOT, PATHS["common_manifest"], self.fixture, cell_id)
            for cell_id in ir.VALID_CELL_IDS
        }
        with tempfile.TemporaryDirectory() as tmp:
            isolated = self._isolated_common_root(
                Path(tmp),
                include_residue=True,
                poison_residue=True,
            )
            manifest = isolated / "docs/candidates/invocation_recovery_v0/apparatus/common/COMMON_COMPONENT_MANIFEST_v0.json"
            observed = {
                cell_id: ir.assemble_successor_input(isolated, manifest, self.fixture, cell_id)
                for cell_id in ir.VALID_CELL_IDS
            }
        self.assertEqual(observed, baseline)

    def test_r4_each_canonical_residue_pair_is_byte_identical_at_incident_specimen(self) -> None:
        pairs = (
            (
                "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_ROLE_HEADER_v0.txt",
                "fixtures/invocation_recovery_v0/common/01_RECOVERY_ROLE_HEADER_v0.txt",
                "fc5f06b00d5405328537d3e55ab7ba3e07f47ec4",
            ),
            (
                "docs/candidates/invocation_recovery_v0/apparatus/common/TASK_BASIS_v0.txt",
                "fixtures/invocation_recovery_v0/common/02_TASK_BASIS_v0.txt",
                "1d912c8556afb677fdfb3cc7ac7a2188c205e5cd",
            ),
            (
                "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_TASK_INSTRUCTION_v0.txt",
                "fixtures/invocation_recovery_v0/common/08_RECOVERY_TASK_INSTRUCTION_v0.txt",
                "e9797fdf5e10bcb5affbe7e69afa103068d0fc5e",
            ),
            (
                "docs/candidates/invocation_recovery_v0/apparatus/common/RECOVERY_RESPONSE_SCHEMA_v0.txt",
                "fixtures/invocation_recovery_v0/common/09_RECOVERY_RESPONSE_SCHEMA_v0.txt",
                "78f64a50edfaeb908bb0ac7a10acfb16601d6ffa",
            ),
        )
        for canonical, residue, expected_blob in pairs:
            a = (ROOT / canonical).read_bytes()
            b = (ROOT / residue).read_bytes()
            self.assertEqual(a, b)
            self.assertEqual(ir.git_blob_sha1(a), expected_blob)
            self.assertEqual(ir.git_blob_sha1(b), expected_blob)

    def test_r5_residue_presence_or_absence_cannot_change_any_a_f_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_a, tempfile.TemporaryDirectory() as tmp_b:
            absent = self._isolated_common_root(Path(tmp_a), include_residue=False)
            present = self._isolated_common_root(Path(tmp_b), include_residue=True)
            manifest_a = absent / "docs/candidates/invocation_recovery_v0/apparatus/common/COMMON_COMPONENT_MANIFEST_v0.json"
            manifest_b = present / "docs/candidates/invocation_recovery_v0/apparatus/common/COMMON_COMPONENT_MANIFEST_v0.json"
            for cell_id in ir.VALID_CELL_IDS:
                self.assertEqual(
                    ir.assemble_successor_input(absent, manifest_a, self.fixture, cell_id),
                    ir.assemble_successor_input(present, manifest_b, self.fixture, cell_id),
                )

    def test_r6_repaired_contract_bytes_remain_unchanged(self) -> None:
        contract_paths = (
            "docs/candidates/invocation_recovery_v0/INVOCATION_RECOVERY_001.md",
            "docs/candidates/invocation_recovery_v0/PRESSURE_DESIGN_001.md",
        )
        proc = subprocess.run(
            ["git", "diff", "--exit-code", ir.CONTRACT_HEAD, "--", *contract_paths],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_r7_concurrent_history_is_preserved_without_exclusive_provenance_claim(self) -> None:
        concurrent_commits = (
            "893695cb5f84c20d29220fad1b780220b81c3184",
            "a7c93c7a9dc9ef891dd2f626a1c8a1476ddc9f96",
            "8e7b58d443d3b3fa440f630c8c212cab561cf403",
            "ec34811624ed15200c15a2c4d28881e1175f660e",
        )
        for commit in concurrent_commits:
            proc = subprocess.run(
                ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, commit + "\n" + proc.stderr)

        reconciliation = (
            ROOT
            / "docs/candidates/invocation_recovery_v0/apparatus/PROVENANCE_RECONCILIATION_001.md"
        ).read_text(encoding="utf-8")
        self.assertIn("COMMIT AUTHORSHIP", reconciliation)
        self.assertIn("OCCUPANT / INVOCATION ATTRIBUTION", reconciliation)
        self.assertIn("not treated as evidence that one invocation authored", reconciliation)

    def test_r8_semantic_dependency_closure_is_unique_despite_residue(self) -> None:
        manifest = ir.load_json(PATHS["common_manifest"])
        closure = tuple(row["path"] for row in manifest["components"])
        self.assertEqual(len(closure), len(set(closure)))
        self.assertEqual(len(closure), 4)
        self.assertTrue(all((ROOT / path).is_file() for path in closure))

        apparatus_source = Path(ir.__file__).read_text(encoding="utf-8")
        self.assertNotIn("fixtures/invocation_recovery_v0/common/", apparatus_source)

        with tempfile.TemporaryDirectory() as tmp:
            isolated = self._isolated_common_root(
                Path(tmp),
                include_residue=True,
                poison_residue=True,
            )
            manifest_path = isolated / "docs/candidates/invocation_recovery_v0/apparatus/common/COMMON_COMPONENT_MANIFEST_v0.json"
            identities = ir.common_component_identities(isolated, manifest_path)
            self.assertEqual(set(identities), set(ir.COMMON_COMPONENT_IDS))


if __name__ == "__main__":
    unittest.main()
