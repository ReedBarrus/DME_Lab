from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from lab.ops.candidates.authorization_to_active_001.correspondence import corresponds
from lab.ops.candidates.authorization_to_active_001.materializer import (
    materialize_active_if_corresponding,
)
from lab.ops.candidates.execution_stop_latch_001.stop_latch import ExecutionStopLatch
from src.projection.draci_local_frame_v0 import (
    AUTHORIZATION_OBJECT_CENTERED,
    CLAIM_LANE_CENTERED,
    CONTROLLER_CENTERED,
    EXACT_AUTHORIZATION_BASIS_REFS,
    EXACT_BASIS_REFS,
    EXACT_GUARD_SEQUENCE,
    EXACT_SPARSE_OBSERVATION_BASIS_REFS,
    EXACT_SPARSE_OBSERVATION_SOURCE_REFS,
    EXACT_SOURCE_REFS,
    LATCH_STATE_CARRIER_CENTERED,
    OBSERVER_CENTERED,
    ProjectionInputError,
    REPOSITORY_CENTERED,
    exact_authorization_source_refs,
    project_authorization_to_active_001,
    project_lifecycle_complete_cell_a,
    project_sparse_observation_s1,
)
from tools.lane_lifecycle_disposition_v0 import LifecycleController


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "fixtures" / "lane_lifecycle_disposition_v0"
AUTHORIZATION_FIXTURE_ROOT = (
    ROOT / "lab" / "ops" / "candidates" / "authorization_to_active_001" / "fixtures"
)
SPARSE_TRACE_PATH = ROOT / "traces" / "absent_interval_round_trip_pressure_v0.json"


def load_json(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def load_authorization_json(name: str) -> dict:
    return json.loads((AUTHORIZATION_FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def load_sparse_trace() -> dict:
    return json.loads(SPARSE_TRACE_PATH.read_text(encoding="utf-8"))


class DraciLocalFrameProjectionTest(unittest.TestCase):
    def setUp(self) -> None:
        pressure = load_json("pressure_cells_v0.json")
        registry = load_json("producer_registry_v0.json")
        catalog = load_json("basis_catalog_v0.json")
        self.lifecycle_input = pressure["bases"]["complete_valid"]
        self.adjudication = LifecycleController(registry, catalog).evaluate_branch(
            self.lifecycle_input
        )
        self.source_refs = deepcopy(EXACT_SOURCE_REFS)
        self.basis_refs = deepcopy(EXACT_BASIS_REFS)

    def project(self, question: str = CONTROLLER_CENTERED) -> dict:
        return project_lifecycle_complete_cell_a(
            projection_question=question,
            lifecycle_input=self.lifecycle_input,
            adjudication=self.adjudication,
            source_refs=self.source_refs,
            basis_refs=self.basis_refs,
        )

    def test_exact_cell_a_produces_bounded_trajectory(self) -> None:
        projection = self.project()

        self.assertEqual(projection["trajectory"], ["FRAME_0", "EVENT_1", "FRAME_1"])
        temporal = projection["temporal_relations"]
        self.assertEqual(temporal["PRE"]["claim_status"], "ACTIVE")
        self.assertEqual(temporal["PRE"]["lane_status"], "ACTIVE")
        self.assertEqual(temporal["PRE"]["occupant_presence"], "PRESENT")
        self.assertEqual(temporal["OPERATIVE"]["requested_transition"], "COMPLETE")
        self.assertEqual(temporal["OPERATIVE"]["joint_guard"], list(EXACT_GUARD_SEQUENCE))
        self.assertEqual(
            temporal["POST"]["projected"],
            {
                "claim_status": "COMPLETED",
                "lane_status": "READY_UNCLAIMED",
                "occupant_binding": None,
            },
        )
        self.assertEqual(projection["post_mode"], "ADJUDICATED")

    def test_adjudication_cannot_report_realized_live_state(self) -> None:
        projection = self.project()

        self.assertEqual(
            projection["temporal_relations"]["POST"]["realized"], "UNRESOLVED"
        )
        self.assertEqual(
            projection["observation_depth"]["live_post_state"],
            {
                "realized": "UNRESOLVED",
                "observed": "UNRESOLVED",
                "evidenced": "UNRESOLVED",
                "qualified": "UNRESOLVED",
            },
        )

    def test_execution_effect_none_remains_visible(self) -> None:
        projection = self.project()

        self.assertEqual(projection["execution_effect"], "NONE")
        self.assertEqual(
            projection["event"]["full_consequence_footprint"][
                "controller_execution_effect"
            ],
            "NONE",
        )
        self.assertEqual(
            projection["event"]["full_consequence_footprint"]["live_execution"],
            "EXPLICITLY_ABSENT",
        )

    def test_dual_projections_preserve_sources_and_change_roles(self) -> None:
        controller = self.project(CONTROLLER_CENTERED)
        claim_lane = self.project(CLAIM_LANE_CENTERED)

        self.assertEqual(controller["source_refs"], claim_lane["source_refs"])
        self.assertEqual(controller["basis_refs"], claim_lane["basis_refs"])
        self.assertEqual(
            controller["source_content_identities"],
            claim_lane["source_content_identities"],
        )
        self.assertNotEqual(controller["roles"], claim_lane["roles"])
        self.assertNotEqual(
            controller["projection_identity"], claim_lane["projection_identity"]
        )
        self.assertEqual(
            controller["roles"]["S"]["configuration"], "LIFECYCLE_CONTROLLER"
        )
        self.assertEqual(
            claim_lane["roles"]["S"]["configuration"],
            "CLAIM_LANE_REQUEST_TUPLE",
        )

    def test_pairwise_views_cannot_substitute_for_joint_guard(self) -> None:
        altered = deepcopy(self.adjudication)
        altered["predicates_consulted"]["admissibility"] = ["P01", "P02", "P03"]

        with self.assertRaisesRegex(ProjectionInputError, "exact P01-P08 joint guard"):
            project_lifecycle_complete_cell_a(
                projection_question=CONTROLLER_CENTERED,
                lifecycle_input=self.lifecycle_input,
                adjudication=altered,
                source_refs=self.source_refs,
                basis_refs=self.basis_refs,
            )

        projection = self.project()
        self.assertFalse(
            projection["pairwise_relations"]["joint_admissibility_established"]
        )
        self.assertEqual(
            projection["higher_order_couplings"][0]["pairwise_substitution"],
            "FORBIDDEN",
        )

    def test_event_origin_footprint_and_full_consequence_are_distinct(self) -> None:
        event = self.project()["event"]

        self.assertNotEqual(event["origin"], event["footprint"])
        self.assertNotEqual(event["footprint"], event["full_consequence_footprint"])
        self.assertEqual(event["origin"]["location"], "controller evaluation")
        self.assertEqual(
            event["footprint"],
            [
                "request",
                "selection",
                "P01-P08 joint guard",
                "returned adjudication",
            ],
        )

    def test_event_occurrence_and_consequence_closure_are_separate(self) -> None:
        event = self.project()["event"]

        self.assertEqual(event["occurrence"]["status"], "OCCURRED")
        self.assertEqual(event["consequence_closure"]["adjudication_return"], "CLOSED")
        self.assertEqual(
            event["consequence_closure"]["downstream_consequences"], "UNRESOLVED"
        )
        self.assertNotEqual(event["occurrence"], event["consequence_closure"])

    def test_missing_observations_and_currentness_remain_unresolved(self) -> None:
        projection = self.project()

        self.assertEqual(projection["currentness"], "UNRESOLVED")
        self.assertIn("live post-execution state", projection["unresolved_coordinates"])
        self.assertIn("currentness", projection["unresolved_coordinates"])
        self.assertEqual(
            projection["authority"]["view"], "DERIVED_SOURCE_BOUND_VIEW_ONLY"
        )
        self.assertEqual(
            projection["authority"]["general_authority_standing"], "NONE"
        )

    def test_recomputation_is_deterministic(self) -> None:
        self.assertEqual(self.project(), self.project())

    def test_projection_is_io_free_and_does_not_mutate_sources(self) -> None:
        lifecycle_before = deepcopy(self.lifecycle_input)
        adjudication_before = deepcopy(self.adjudication)
        source_refs_before = deepcopy(self.source_refs)
        basis_refs_before = deepcopy(self.basis_refs)

        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected I/O")),
            mock.patch.object(
                Path, "write_text", side_effect=AssertionError("unexpected append")
            ),
            mock.patch.object(
                subprocess, "run", side_effect=AssertionError("unexpected process")
            ),
        ):
            self.project()

        self.assertEqual(self.lifecycle_input, lifecycle_before)
        self.assertEqual(self.adjudication, adjudication_before)
        self.assertEqual(self.source_refs, source_refs_before)
        self.assertEqual(self.basis_refs, basis_refs_before)

    def test_source_and_basis_drift_fail_closed(self) -> None:
        source_refs = deepcopy(self.source_refs)
        source_refs["controller"] = "git-blob:wrong:controller"
        with self.assertRaisesRegex(ProjectionInputError, "source_refs"):
            project_lifecycle_complete_cell_a(
                projection_question=CONTROLLER_CENTERED,
                lifecycle_input=self.lifecycle_input,
                adjudication=self.adjudication,
                source_refs=source_refs,
                basis_refs=self.basis_refs,
            )

        altered_input = deepcopy(self.lifecycle_input)
        altered_input["lane"]["status"] = "HELD"
        with self.assertRaisesRegex(ProjectionInputError, "lifecycle_input"):
            project_lifecycle_complete_cell_a(
                projection_question=CONTROLLER_CENTERED,
                lifecycle_input=altered_input,
                adjudication=self.adjudication,
                source_refs=self.source_refs,
                basis_refs=self.basis_refs,
            )


class AuthorizationToActiveProjectionPressureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.envelope = load_authorization_json("execution_envelope.json")
        self.authorizations = {
            "A": load_authorization_json("authorization_A.json"),
            "B0": None,
            "B1": load_authorization_json("authorization_B1.json"),
            "B2": load_authorization_json("authorization_B2.json"),
            "B3": load_authorization_json("authorization_B3.json"),
            "B4": load_authorization_json("authorization_B4.json"),
        }
        self.basis_refs = deepcopy(EXACT_AUTHORIZATION_BASIS_REFS)

    def observe(self, cell_id: str) -> dict:
        authorization = self.authorizations[cell_id]
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            latch = ExecutionStopLatch(
                root, self.envelope["execution_envelope_id"]
            )
            prior_state_exists = latch.state_path.exists()
            correspondence_result = corresponds(authorization, self.envelope)
            result = materialize_active_if_corresponding(
                root, self.envelope, authorization
            )
            carrier_exists = latch.state_path.exists()
            carrier_state = latch.state() if carrier_exists else None
            return {
                "prior_state_exists": prior_state_exists,
                "corresponds": correspondence_result,
                "materializer_returned_path": result is not None,
                "carrier_exists": carrier_exists,
                "carrier_state": carrier_state,
            }

    def project(
        self,
        cell_id: str = "A",
        question: str = AUTHORIZATION_OBJECT_CENTERED,
        observation: dict | None = None,
    ) -> dict:
        return project_authorization_to_active_001(
            projection_question=question,
            cell_id=cell_id,
            authorization=self.authorizations[cell_id],
            execution_envelope=self.envelope,
            materialization_observation=(
                self.observe(cell_id) if observation is None else observation
            ),
            source_refs=exact_authorization_source_refs(cell_id),
            basis_refs=self.basis_refs,
        )

    def test_positive_exact_conjunction_projects_active_carrier(self) -> None:
        projection = self.project("A")

        self.assertEqual(projection["specimen"], "AUTHORIZATION_TO_ACTIVE_001")
        self.assertEqual(projection["trajectory"], ["FRAME_0", "EVENT_1", "FRAME_1"])
        self.assertEqual(projection["post_mode"], "REALIZED")
        self.assertEqual(
            projection["temporal_relations"]["POST"]["active_carrier"], "ACTIVE"
        )
        coupling = projection["higher_order_couplings"][0]
        self.assertEqual(coupling["conjunction_result"], "CORRESPONDS")
        self.assertTrue(
            all(
                coupling["term_results"][term]
                for term in coupling["required_terms"]
            )
        )

    def test_b0_through_b4_fail_closed(self) -> None:
        for cell_id in ("B0", "B1", "B2", "B3", "B4"):
            with self.subTest(cell_id=cell_id):
                projection = self.project(cell_id)
                self.assertEqual(
                    projection["higher_order_couplings"][0]["conjunction_result"],
                    "NONCORRESPONDING",
                )
                self.assertEqual(
                    projection["temporal_relations"]["POST"]["active_carrier"],
                    "ABSENT",
                )
                self.assertEqual(projection["post_mode"], "OBSERVED")
                self.assertEqual(
                    projection["authority"]["general_authority"],
                    "NOT_ESTABLISHED",
                )

    def test_no_pairwise_subset_establishes_active(self) -> None:
        positive = self.project("A")
        coupling = positive["higher_order_couplings"][0]

        self.assertFalse(
            positive["pairwise_relations"]["active_materialization_established"]
        )
        self.assertEqual(coupling["pairwise_substitution"], "FORBIDDEN")
        self.assertEqual(
            coupling["required_terms"],
            [
                "execution_envelope_id_equal",
                "implementation_basis_equal",
                "requested_consequence_allowed",
                "authorization_status_live",
                "prior_state_absent",
            ],
        )
        for cell_id in ("B1", "B2", "B3", "B4"):
            with self.subTest(cell_id=cell_id):
                negative = self.project(cell_id)
                term_results = negative["higher_order_couplings"][0]["term_results"]
                self.assertIn(False, [term_results[name] for name in coupling["required_terms"]])
                self.assertEqual(
                    negative["temporal_relations"]["POST"]["active_carrier"],
                    "ABSENT",
                )

    def test_positive_carrier_is_realized_only_in_bounded_scope(self) -> None:
        depth = self.project("A")["observation_depth"]["active_carrier"]

        self.assertEqual(depth["realized"], "ACTIVE")
        self.assertEqual(depth["observed"], "ACTIVE")
        self.assertEqual(
            depth["qualified"],
            "AUTHORIZATION_TO_ACTIVE_001_BOUNDED_POSITIVE_PROPERTY",
        )

    def test_workshop_execution_and_currentness_remain_unresolved(self) -> None:
        projection = self.project("A")

        self.assertEqual(
            projection["temporal_relations"]["POST"]["workshop_execution"],
            "UNRESOLVED",
        )
        self.assertEqual(
            projection["observation_depth"]["workshop_execution"]["realized"],
            "UNRESOLVED",
        )
        self.assertEqual(projection["currentness"], "UNRESOLVED")

    def test_correspondence_never_emits_generalized_authority(self) -> None:
        for cell_id in self.authorizations:
            with self.subTest(cell_id=cell_id):
                authority = self.project(cell_id)["authority"]
                self.assertIn(
                    authority["authorization_correspondence"],
                    ("CORRESPONDS", "NONCORRESPONDING"),
                )
                self.assertEqual(authority["general_authority"], "NOT_ESTABLISHED")
                self.assertEqual(authority["delegation"], "NOT_ESTABLISHED")
                self.assertEqual(authority["retry_authority"], "NOT_ESTABLISHED")

    def test_authorization_object_presence_does_not_establish_issuer_authority(self) -> None:
        projection = self.project("A")

        self.assertEqual(
            projection["temporal_relations"]["PRE"]["authorization_object"],
            "PRESENT",
        )
        self.assertEqual(projection["authority"]["issuer_authority"], "UNRESOLVED")

    def test_alternate_projection_preserves_identical_source_identities(self) -> None:
        authorization_centered = self.project("A", AUTHORIZATION_OBJECT_CENTERED)
        latch_centered = self.project("A", LATCH_STATE_CARRIER_CENTERED)

        self.assertEqual(
            authorization_centered["source_refs"], latch_centered["source_refs"]
        )
        self.assertEqual(
            authorization_centered["basis_refs"], latch_centered["basis_refs"]
        )
        self.assertEqual(
            authorization_centered["source_content_identities"],
            latch_centered["source_content_identities"],
        )
        self.assertNotEqual(
            authorization_centered["projection_identity"],
            latch_centered["projection_identity"],
        )
        self.assertNotEqual(
            authorization_centered["roles"], latch_centered["roles"]
        )

    def test_event_geometry_and_closure_remain_distinct(self) -> None:
        event = self.project("A")["event"]

        self.assertNotEqual(event["origin"], event["footprint"])
        self.assertNotEqual(event["footprint"], event["full_consequence_footprint"])
        self.assertEqual(
            event["consequence_closure"]["active_materialization"],
            "CLOSED_ACTIVE",
        )
        self.assertEqual(
            event["consequence_closure"]["workshop_consequence"], "UNRESOLVED"
        )
        self.assertNotEqual(event["occurrence"], event["consequence_closure"])

    def test_projection_is_deterministic_io_free_and_source_preserving(self) -> None:
        observation = self.observe("A")
        authorization_before = deepcopy(self.authorizations["A"])
        envelope_before = deepcopy(self.envelope)
        observation_before = deepcopy(observation)
        sources = exact_authorization_source_refs("A")
        sources_before = deepcopy(sources)
        basis_before = deepcopy(self.basis_refs)

        def invoke() -> dict:
            return project_authorization_to_active_001(
                projection_question=AUTHORIZATION_OBJECT_CENTERED,
                cell_id="A",
                authorization=self.authorizations["A"],
                execution_envelope=self.envelope,
                materialization_observation=observation,
                source_refs=sources,
                basis_refs=self.basis_refs,
            )

        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected I/O")),
            mock.patch.object(
                Path, "write_text", side_effect=AssertionError("unexpected append")
            ),
            mock.patch.object(
                subprocess, "run", side_effect=AssertionError("unexpected process")
            ),
        ):
            first = invoke()
            second = invoke()

        self.assertEqual(first, second)
        self.assertEqual(self.authorizations["A"], authorization_before)
        self.assertEqual(self.envelope, envelope_before)
        self.assertEqual(observation, observation_before)
        self.assertEqual(sources, sources_before)
        self.assertEqual(self.basis_refs, basis_before)


class SparseObservationProjectionPressureTest(unittest.TestCase):
    def setUp(self) -> None:
        trace = load_sparse_trace()
        self.control = trace["specimens"]["S1"]["control"]
        specimen = trace["specimens"]["S1"]
        self.sparse_evidence = {
            key: specimen[key]
            for key in (
                "first_capture",
                "second_capture",
                "endpoint_relation",
                "occurrence_relation",
                "health",
                "recovery",
            )
        }
        self.source_refs = deepcopy(EXACT_SPARSE_OBSERVATION_SOURCE_REFS)
        self.basis_refs = deepcopy(EXACT_SPARSE_OBSERVATION_BASIS_REFS)

    def project(self, question: str = REPOSITORY_CENTERED) -> dict:
        return project_sparse_observation_s1(
            projection_question=question,
            sparse_evidence=self.sparse_evidence,
            source_refs=self.source_refs,
            basis_refs=self.basis_refs,
        )

    def test_endpoint_observation_occurrences_remain_distinct(self) -> None:
        occurrences = self.project()["endpoint_occurrences"]

        frame_0_ids = {
            occurrences["FRAME_0"][source]["record_id"]
            for source in ("filesystem", "git")
        }
        frame_1_ids = {
            occurrences["FRAME_1"][source]["record_id"]
            for source in ("filesystem", "git")
        }
        self.assertEqual(frame_0_ids, {"rec-000001", "rec-000002"})
        self.assertEqual(frame_1_ids, {"rec-000005", "rec-000006"})
        self.assertTrue(frame_0_ids.isdisjoint(frame_1_ids))

    def test_equivalent_endpoint_content_does_not_collapse_identity(self) -> None:
        projection = self.project()

        self.assertEqual(
            projection["endpoint_configurations"]["FRAME_0"],
            projection["endpoint_configurations"]["FRAME_1"],
        )
        self.assertEqual(
            projection["endpoint_relation"]["configuration"], "EQUIVALENT"
        )
        self.assertEqual(
            projection["endpoint_relation"]["observation_occurrences"], "DISTINCT"
        )
        self.assertFalse(
            projection["endpoint_relation"][
                "configuration_equality_collapses_occurrence_identity"
            ]
        )

    def test_operative_slice_is_transition_gap(self) -> None:
        projection = self.project()

        self.assertEqual(
            projection["temporal_relations"]["OPERATIVE"],
            projection["transition_gap"],
        )
        self.assertEqual(projection["transition_gap"]["kind"], "TRANSITION_GAP")
        self.assertEqual(
            projection["trajectory"], ["FRAME_0", "TRANSITION_GAP", "FRAME_1"]
        )

    def test_equal_endpoints_do_not_derive_event(self) -> None:
        projection = self.project()

        self.assertIsNone(projection["event"])
        self.assertEqual(projection["transition_gap"]["event"], "NOT_DERIVED")

    def test_absence_of_observed_difference_does_not_derive_event(self) -> None:
        projection = self.project()

        self.assertEqual(
            projection["endpoint_relation"]["configuration"], "EQUIVALENT"
        )
        self.assertIsNone(projection["event"])
        self.assertIn(
            "whether any transformation occurred",
            projection["unresolved_coordinates"],
        )

    def test_exact_intermediate_trajectory_remains_unresolved(self) -> None:
        projection = self.project()

        self.assertEqual(
            projection["transition_gap"]["intermediate_trajectory"], "UNRESOLVED"
        )
        self.assertEqual(projection["event_hypothesis"], "UNRESOLVED")
        self.assertIn(
            "intermediate configurations", projection["unresolved_coordinates"]
        )

    def test_external_driver_knowledge_is_excluded(self) -> None:
        projection = self.project()
        rendered = json.dumps(projection, sort_keys=True)
        beta_hash = self.control["mutation"]["beta_control"]["state_txt_sha256"]

        self.assertNotIn("control", self.sparse_evidence)
        self.assertNotIn(beta_hash, rendered)
        self.assertNotIn("alpha -> beta -> alpha", rendered)
        self.assertFalse(
            projection["external_driver_ceiling"]["driver_knowledge_imported"]
        )
        self.assertEqual(
            projection["external_driver_ceiling"]["reconstructed_interval_claim"],
            "UNRESOLVED",
        )

    def test_endpoint_invariants_survive_without_trajectory_claim(self) -> None:
        projection = self.project()
        invariants = projection["known_invariants"]

        self.assertIn("observation occurrence identities are distinct", invariants)
        self.assertIn("source provenance is retained", invariants)
        self.assertIn(
            "endpoint filesystem configurations are equivalent", invariants
        )
        self.assertIn("endpoint Git configurations are equivalent", invariants)
        self.assertEqual(
            projection["transition_gap"]["intermediate_trajectory"], "UNRESOLVED"
        )

    def test_observer_centered_projection_preserves_source_identities(self) -> None:
        repository_centered = self.project(REPOSITORY_CENTERED)
        observer_centered = self.project(OBSERVER_CENTERED)

        self.assertEqual(
            repository_centered["source_refs"], observer_centered["source_refs"]
        )
        self.assertEqual(
            repository_centered["basis_refs"], observer_centered["basis_refs"]
        )
        self.assertEqual(
            repository_centered["endpoint_occurrences"],
            observer_centered["endpoint_occurrences"],
        )
        self.assertNotEqual(
            repository_centered["projection_identity"],
            observer_centered["projection_identity"],
        )
        self.assertNotEqual(
            repository_centered["roles"], observer_centered["roles"]
        )

    def test_later_observation_does_not_emit_generic_currentness(self) -> None:
        projection = self.project()

        self.assertEqual(projection["post_mode"], "OBSERVED")
        self.assertEqual(projection["currentness"], "UNRESOLVED")
        self.assertIn("generic currentness", projection["unresolved_coordinates"])

    def test_no_consequence_closure_without_admitted_event(self) -> None:
        projection = self.project()

        self.assertIsNone(projection["event"])
        self.assertEqual(
            projection["consequence_closure"],
            "UNAVAILABLE_NO_ADMITTED_EVENT",
        )

    def test_projection_is_deterministic_io_free_and_source_preserving(self) -> None:
        evidence_before = deepcopy(self.sparse_evidence)
        source_refs_before = deepcopy(self.source_refs)
        basis_refs_before = deepcopy(self.basis_refs)

        with (
            mock.patch("builtins.open", side_effect=AssertionError("unexpected I/O")),
            mock.patch.object(
                Path, "write_text", side_effect=AssertionError("unexpected append")
            ),
            mock.patch.object(
                subprocess, "run", side_effect=AssertionError("unexpected process")
            ),
        ):
            first = self.project()
            second = self.project()

        self.assertEqual(first, second)
        self.assertEqual(self.sparse_evidence, evidence_before)
        self.assertEqual(self.source_refs, source_refs_before)
        self.assertEqual(self.basis_refs, basis_refs_before)

    def test_sparse_evidence_drift_fails_closed(self) -> None:
        altered = deepcopy(self.sparse_evidence)
        altered["endpoint_relation"]["both_sources_equivalent"] = False

        with self.assertRaisesRegex(ProjectionInputError, "exact admitted S1"):
            project_sparse_observation_s1(
                projection_question=REPOSITORY_CENTERED,
                sparse_evidence=altered,
                source_refs=self.source_refs,
                basis_refs=self.basis_refs,
            )


if __name__ == "__main__":
    unittest.main()
