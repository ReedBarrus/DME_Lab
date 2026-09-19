import hashlib
import importlib.util
import inspect
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "lab/ops/candidates/counterfeit_warrant_001"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lab_conductor = load_module("lab_conductor_cw001", ROOT / "tools/lab_conductor.py")
evaluator = load_module("counterfeit_warrant_001_evaluator", APP / "evaluator.py")
comparator = load_module(
    "counterfeit_warrant_001_static_comparator", APP / "static_comparator.py"
)


class CounterfeitWarrant001ApparatusTests(unittest.TestCase):
    def fixture(self, name):
        return APP / "fixtures" / name

    def test_canonicalization_is_deterministic_and_generic_sha_vector_matches(self):
        x = {"b": 2, "a": 1}
        self.assertEqual(
            evaluator.canonicalize(x), evaluator.canonicalize({"a": 1, "b": 2})
        )
        self.assertEqual(
            evaluator.sha256_bytes(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_published_hashes_reproduce_without_held_out_evaluation(self):
        packet_bytes = self.fixture("role_output_packet.json").read_bytes()
        self.assertEqual(
            hashlib.sha256(packet_bytes).hexdigest(),
            "04b24d8beb04803f6a6b208f4f953efaa005bd2bb94556499870e15e68fd2beb",
        )
        packet = json.loads(packet_bytes)
        self.assertEqual(
            evaluator.sha256_canonical(packet["payload"]),
            "9e5e367615e9df465dbf945272d011c1d2ec0646ff4baa9bfbc27202c438a203",
        )
        binding_bytes = self.fixture("binding_tuple.json").read_bytes()
        self.assertEqual(
            hashlib.sha256(binding_bytes).hexdigest(),
            "685925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2",
        )
        routed = dict(packet)
        routed["status"] = "ACCEPTED_FOR_TRANSPORT"
        self.assertEqual(
            evaluator.sha256_canonical(routed),
            "fe837a4a9885404846bf353d3edb3f573976fba56d7e9e929d4dc183fede8e1e",
        )

    def test_packet_transport_validation_is_frozen_prerequisite(self):
        packet = json.loads(self.fixture("role_output_packet.json").read_text())
        self.assertEqual(lab_conductor.validate_packet(packet), [])

    def test_frozen_warrants_parse_and_differ_only_at_binding_sha256(self):
        a = json.loads(self.fixture("routing_warrant_A.json").read_text())
        b = json.loads(self.fixture("routing_warrant_B.json").read_text())
        self.assertEqual(
            a,
            {
                "schema_version": "routing_warrant_fixture_v0",
                "binding_sha256": "685925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2",
            },
        )
        self.assertEqual(
            b,
            {
                "schema_version": "routing_warrant_fixture_v0",
                "binding_sha256": "085925fa653bc2cf82d8b2e70aa9d61650075fab64fdb5c10f25c0c2449316a2",
            },
        )
        receipt = comparator.compare_warrant_objects(a, b)
        self.assertTrue(receipt["same_schema"])
        self.assertTrue(receipt["only_permitted_difference"])
        self.assertEqual(receipt["differing_fields"], ["binding_sha256"])

    def test_experimental_interfaces_exist_without_held_out_invocation(self):
        expected = {
            "derive_warrant_validity",
            "derive_edge_admissibility",
            "prerequisite_checks",
            "evaluate_condition",
            "materialize_transition",
            "emit_routed_object",
            "realize_condition",
        }
        self.assertTrue(expected <= set(dir(evaluator)))
        self.assertEqual(evaluator.RESULT_DOMAIN, ("PASS", "FAIL", "REJECTED"))
        self.assertIn("supplied_routing_warrant", inspect.signature(
            evaluator.evaluate_condition
        ).parameters)
        self.assertNotIn("condition", inspect.signature(
            evaluator.evaluate_condition
        ).parameters)

    def test_generic_dummy_vectors_exercise_equality_helper_only(self):
        same = {
            "schema_version": "routing_warrant_fixture_v0",
            "binding_sha256": "1" * 64,
        }
        different = {
            "schema_version": "routing_warrant_fixture_v0",
            "binding_sha256": "2" * 64,
        }
        self.assertEqual(
            evaluator.derive_warrant_validity("1" * 64, same), "KNOWN_TRUE"
        )
        self.assertEqual(
            evaluator.derive_warrant_validity("1" * 64, different), "KNOWN_FALSE"
        )
        with self.assertRaises(ValueError):
            evaluator.derive_warrant_validity(
                "1" * 64,
                {
                    "schema_version": "routing_warrant_fixture_v0",
                    "binding_sha256": "1" * 64,
                    "valid": True,
                },
            )

    def test_two_fresh_roots_have_identical_start_surfaces_except_warrant_binding(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            aroot = base / "A"
            broot = base / "B"
            comparator.initialize_isolated_root(
                APP, aroot, self.fixture("routing_warrant_A.json"), lab_conductor
            )
            comparator.initialize_isolated_root(
                APP, broot, self.fixture("routing_warrant_B.json"), lab_conductor
            )
            receipt = comparator.compare_initialized_roots(aroot, broot)
            self.assertTrue(receipt["all_required_surfaces_identical"])
            self.assertTrue(
                receipt["warrant_difference"]["only_permitted_difference"]
            )
            self.assertEqual(
                (aroot / "lab/state/LAB_STATE_v0.json").read_bytes(),
                (broot / "lab/state/LAB_STATE_v0.json").read_bytes(),
            )
            self.assertEqual(
                (aroot / "lab/events/events.jsonl").read_bytes(),
                (broot / "lab/events/events.jsonl").read_bytes(),
            )
            # Isolation check: A-only mutation does not appear in B.
            (aroot / "sentinel.txt").write_text("A only", encoding="utf-8")
            self.assertFalse((broot / "sentinel.txt").exists())

    def test_static_comparator_does_not_import_or_call_experimental_evaluator(self):
        source = (APP / "static_comparator.py").read_text(encoding="utf-8")
        self.assertNotIn("derive_warrant_validity", source)
        self.assertNotIn("evaluate_condition", source)
        self.assertNotIn("realize_condition", source)


if __name__ == "__main__":
    unittest.main()
