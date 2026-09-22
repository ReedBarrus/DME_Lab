#!/usr/bin/env python3
"""Deterministic synthetic controller for LANE_LIFECYCLE_DISPOSITION_001.

No repository, network, lane, authority, or external-effect mutation exists here.
The controller consumes only frozen P01-P18 raw/qualified inputs.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ALLOWED_TRANSITIONS = ("COMPLETE", "RELEASE", "MARK_BLOCKED")
TERMINAL_REUSABLE = ("COMPLETED", "RELEASED")

ALLOWED_TOP_LEVEL = {
    "claim",
    "lane",
    "request",
    "binding",
    "envelope",
    "criterion",
    "receipt",
    "standings",
}

ALLOWED_CLAIM_FIELDS = {
    "claim_id", "status", "envelope_id", "bounded_unit_id", "unresolved_refs"
}
ALLOWED_LANE_FIELDS = {"status", "occupant_binding"}
ALLOWED_REQUEST_FIELDS = {"requested_transition"}
ALLOWED_BINDING_FIELDS = {"envelope_id", "bounded_unit_id"}
ALLOWED_ENVELOPE_FIELDS = {"envelope_id", "bounded_unit_id"}
ALLOWED_CRITERION_FIELDS = {
    "required_receipt_id", "required_bounded_unit_id", "required_outcome",
    "required_upstream_relations"
}
ALLOWED_RECEIPT_FIELDS = {"receipt_id", "bounded_unit_id", "outcome"}
REQUIRED_STANDING_FIELDS = {"relation_type", "standing", "basis_ref", "producer", "version"}


class AdministrationInvalid(Exception):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _assert_only_keys(obj: Mapping[str, Any], allowed: set[str], label: str) -> None:
    extra = sorted(set(obj) - allowed)
    if extra:
        raise AdministrationInvalid(f"{label}: undeclared fields: {extra}")


def _standing_map(standings: Sequence[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    result: Dict[str, Mapping[str, Any]] = {}
    for row in standings:
        missing = REQUIRED_STANDING_FIELDS - set(row)
        if missing:
            raise AdministrationInvalid(
                f"qualified standing missing fields {sorted(missing)}: {row}"
            )
        extra = set(row) - REQUIRED_STANDING_FIELDS
        if extra:
            raise AdministrationInvalid(
                f"qualified standing has undeclared fields {sorted(extra)}: {row}"
            )
        relation_type = str(row["relation_type"])
        if relation_type in result:
            raise AdministrationInvalid(f"duplicate relation_type: {relation_type}")
        result[relation_type] = row
    return result


class LifecycleController:
    def __init__(
        self,
        producer_registry: Mapping[str, Any],
        basis_catalog: Mapping[str, Any],
    ) -> None:
        self.producer_registry = producer_registry
        self.basis_catalog = basis_catalog

    def _validate_input_membrane(self, data: Mapping[str, Any]) -> None:
        _assert_only_keys(data, ALLOWED_TOP_LEVEL, "controller input")
        for required in ("claim", "lane", "request", "standings"):
            if required not in data:
                raise AdministrationInvalid(f"missing raw input object: {required}")
        _assert_only_keys(data["claim"], ALLOWED_CLAIM_FIELDS, "claim")
        _assert_only_keys(data["lane"], ALLOWED_LANE_FIELDS, "lane")
        _assert_only_keys(data["request"], ALLOWED_REQUEST_FIELDS, "request")
        if "binding" in data:
            _assert_only_keys(data["binding"], ALLOWED_BINDING_FIELDS, "binding")
        if "envelope" in data:
            _assert_only_keys(data["envelope"], ALLOWED_ENVELOPE_FIELDS, "envelope")
        if "criterion" in data:
            _assert_only_keys(data["criterion"], ALLOWED_CRITERION_FIELDS, "criterion")
        if "receipt" in data:
            _assert_only_keys(data["receipt"], ALLOWED_RECEIPT_FIELDS, "receipt")
        _standing_map(data["standings"])

    def _qualified(
        self,
        row: Mapping[str, Any],
        relation_type: str,
        allowed_standings: Iterable[str],
    ) -> bool:
        if row.get("relation_type") != relation_type:
            return False
        if row.get("standing") not in set(allowed_standings):
            return False

        producer = str(row.get("producer"))
        version = str(row.get("version"))
        registry_key = f"{producer}@{version}"
        reg = self.producer_registry.get("qualified_producers", {}).get(registry_key)
        if not reg:
            raise AdministrationInvalid(f"unqualified producer/version: {registry_key}")
        if relation_type not in reg.get("relation_types", []):
            raise AdministrationInvalid(
                f"producer/version not qualified for {relation_type}: {registry_key}"
            )

        basis_ref = str(row.get("basis_ref"))
        if basis_ref not in self.basis_catalog.get("basis_objects", {}):
            raise AdministrationInvalid(f"unrecoverable basis_ref: {basis_ref}")
        return True

    def _get_standing(
        self,
        standings: Mapping[str, Mapping[str, Any]],
        relation_type: str,
        allowed_standings: Iterable[str],
    ) -> Mapping[str, Any]:
        if relation_type not in standings:
            raise AdministrationInvalid(f"missing qualified standing: {relation_type}")
        row = standings[relation_type]
        self._qualified(row, relation_type, allowed_standings)
        return row

    def _derive_common(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        claim = data["claim"]
        lane = data["lane"]
        request = data["request"]
        requested = request.get("requested_transition")
        if requested not in ALLOWED_TRANSITIONS:
            raise AdministrationInvalid(f"P04 invalid transition token: {requested!r}")

        return {
            "P01": claim.get("status") == "ACTIVE",
            "P02": lane.get("status") == "ACTIVE",
            "P03": lane.get("occupant_binding"),
            "P04": requested,
        }

    def _derive_p05(self, data: Mapping[str, Any]) -> bool:
        for name in ("binding", "envelope"):
            if name not in data:
                raise AdministrationInvalid(f"P05 missing raw object: {name}")
        claim = data["claim"]
        binding = data["binding"]
        envelope = data["envelope"]
        return (
            binding.get("envelope_id") == claim.get("envelope_id") == envelope.get("envelope_id")
            and binding.get("bounded_unit_id") == claim.get("bounded_unit_id") == envelope.get("bounded_unit_id")
        )

    def _derive_p06(self, data: Mapping[str, Any]) -> bool:
        for name in ("criterion", "receipt"):
            if name not in data:
                raise AdministrationInvalid(f"P06 missing raw object: {name}")
        criterion = data["criterion"]
        receipt = data["receipt"]
        return (
            receipt.get("receipt_id") == criterion.get("required_receipt_id")
            and receipt.get("bounded_unit_id") == criterion.get("required_bounded_unit_id")
            and receipt.get("outcome") == criterion.get("required_outcome")
        )

    def _derive_p07(
        self,
        criterion: Mapping[str, Any],
        standings: Mapping[str, Mapping[str, Any]],
    ) -> bool:
        required = criterion.get("required_upstream_relations", [])
        if not isinstance(required, list):
            raise AdministrationInvalid("P07 criterion requirements must be a list")
        for req in required:
            if set(req) != {"relation_type", "standing"}:
                raise AdministrationInvalid(f"P07 malformed criterion relation requirement: {req}")
            relation_type = str(req["relation_type"])
            standing = str(req["standing"])
            row = self._get_standing(standings, relation_type, [standing])
            if row.get("standing") != standing:
                return False
        return True

    def _derive_p10(self, claim: Mapping[str, Any]) -> List[str]:
        refs = claim.get("unresolved_refs", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            raise AdministrationInvalid("P10 unresolved_refs must be a string list")
        return list(refs)

    def _p11_retainable(
        self,
        standings: Mapping[str, Mapping[str, Any]],
        required_refs: Sequence[str],
    ) -> bool:
        row = self._get_standing(
            standings,
            "REFERENCE_RETENTION_STATUS",
            ["RETAINABLE", "NOT_RETAINABLE"],
        )
        basis = self.basis_catalog["basis_objects"][row["basis_ref"]]
        basis_refs = basis.get("refs", [])
        return row.get("standing") == "RETAINABLE" and sorted(basis_refs) == sorted(required_refs)

    def evaluate_branch(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        self._validate_input_membrane(data)
        common = self._derive_common(data)
        selected = common["P04"]
        excluded = [x for x in ALLOWED_TRANSITIONS if x != selected]
        standings = _standing_map(data["standings"])

        consulted: List[str] = []
        conserved: List[str] = []

        def guard(pid: str, ok: bool) -> Optional[Dict[str, Any]]:
            consulted.append(pid)
            if not ok:
                return self._inadmissible(data, selected, excluded, consulted, conserved, pid)
            return None

        out = guard("P01", bool(common["P01"]))
        if out:
            return out
        out = guard("P02", bool(common["P02"]))
        if out:
            return out
        out = guard("P03", common["P03"] is not None)
        if out:
            return out
        out = guard("P04", common["P04"] == selected)
        if out:
            return out

        if selected == "COMPLETE":
            p05 = self._derive_p05(data)
            out = guard("P05", p05)
            if out:
                return out
            p06 = self._derive_p06(data)
            out = guard("P06", p06)
            if out:
                return out
            if "criterion" not in data:
                raise AdministrationInvalid("COMPLETE missing criterion")
            p07 = self._derive_p07(data["criterion"], standings)
            out = guard("P07", p07)
            if out:
                return out
            p08 = self._get_standing(
                standings,
                "COMPLETION_BLOCKER_STATUS",
                ["NONE_ESTABLISHED", "FORBIDS_COMPLETION"],
            )
            out = guard("P08", p08.get("standing") == "NONE_ESTABLISHED")
            if out:
                return out
            resulting = {
                "claim_status": "COMPLETED",
                "lane_status": "READY_UNCLAIMED",
                "occupant_binding": None,
            }

        elif selected == "RELEASE":
            p09 = self._get_standing(
                standings,
                "ACTIVE_OWNERSHIP_EFFECT_STATUS",
                [
                    "NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP",
                    "UNFINISHED_EFFECT_REQUIRES_ACTIVE_OWNERSHIP",
                ],
            )
            out = guard(
                "P09",
                p09.get("standing")
                == "NO_UNFINISHED_EFFECT_REQUIRING_ACTIVE_OWNERSHIP",
            )
            if out:
                return out
            required_refs = self._derive_p10(data["claim"])
            consulted.append("P10")
            retainable = self._p11_retainable(standings, required_refs)
            out = guard("P11", retainable)
            if out:
                return out
            if "INVOCATION_EFFECT_ATTRIBUTION" in standings:
                self._get_standing(
                    standings,
                    "INVOCATION_EFFECT_ATTRIBUTION",
                    ["UNRESOLVED", "ESTABLISHED"],
                )
                conserved.append("P18")
            resulting = {
                "claim_status": "RELEASED",
                "lane_status": "READY_UNCLAIMED",
                "occupant_binding": None,
            }

        elif selected == "MARK_BLOCKED":
            p12 = self._get_standing(
                standings,
                "MARK_BLOCKED_BLOCKING_STATUS",
                ["ESTABLISHED", "NONE_ESTABLISHED"],
            )
            out = guard("P12", p12.get("standing") == "ESTABLISHED")
            if out:
                return out
            resulting = {
                "claim_status": "BLOCKED",
                "lane_status": "HELD",
                "occupant_binding": common["P03"],
            }
        else:  # pragma: no cover
            raise AdministrationInvalid(f"unreachable dispatch: {selected}")

        return {
            "requested_transition": selected,
            "selected_branch": selected,
            "excluded_branches": excluded,
            "predicates_consulted": {
                "admissibility": consulted,
                "conserved_debt": conserved,
            },
            "admissible": True,
            "blocking_predicate": None,
            "resulting_state": resulting,
            "historical_claim": copy.deepcopy(data["claim"]),
            "unresolved_refs": list(data["claim"].get("unresolved_refs", [])),
            "disposition_evidence_reachable": True,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "integration_effect": "NONE",
        }

    def _inadmissible(
        self,
        data: Mapping[str, Any],
        selected: str,
        excluded: Sequence[str],
        consulted: Sequence[str],
        conserved: Sequence[str],
        blocking: str,
    ) -> Dict[str, Any]:
        return {
            "requested_transition": selected,
            "selected_branch": selected,
            "excluded_branches": list(excluded),
            "predicates_consulted": {
                "admissibility": list(consulted),
                "conserved_debt": list(conserved),
            },
            "admissible": False,
            "blocking_predicate": blocking,
            "resulting_state": None,
            "historical_claim": copy.deepcopy(data["claim"]),
            "unresolved_refs": list(data["claim"].get("unresolved_refs", [])),
            "disposition_evidence_reachable": False,
            "authority_effect": "NONE",
            "execution_effect": "NONE",
            "integration_effect": "NONE",
        }

    def validate_resulting_state(self, state_input: Mapping[str, Any]) -> Dict[str, Any]:
        allowed = {"claim", "lane", "disposition_evidence_ref", "disposition_objects"}
        _assert_only_keys(state_input, allowed, "state invariant input")
        claim = state_input["claim"]
        lane = state_input["lane"]
        _assert_only_keys(claim, {"claim_id", "status"}, "state claim")
        _assert_only_keys(lane, {"status", "occupant_binding"}, "state lane")

        evidence_ref = state_input.get("disposition_evidence_ref")
        objects = state_input.get("disposition_objects", {})
        p13 = evidence_ref is not None and evidence_ref in objects
        p14 = claim.get("status") in TERMINAL_REUSABLE
        p15 = lane.get("occupant_binding") is None

        violations = []
        if claim.get("status") == "ACTIVE" and lane.get("status") == "READY_UNCLAIMED" and p15:
            violations.append("D1")
        if claim.get("status") == "BLOCKED" and lane.get("status") == "READY_UNCLAIMED":
            violations.append("D2")
        if claim.get("status") == "BLOCKED" and lane.get("status") == "HELD" and p15:
            violations.append("D3")

        reusable = (
            lane.get("status") == "READY_UNCLAIMED"
            and p14
            and p15
            and p13
            and not violations
        )
        return {
            "predicates_consulted": ["P13", "P14", "P15"],
            "P13": p13,
            "P14": p14,
            "P15": p15,
            "violations": violations,
            "valid": not violations,
            "reusable": reusable,
        }

    def evaluate_reactivation(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        allowed = {
            "historical_claim",
            "lane",
            "disposition_evidence_ref",
            "disposition_objects",
            "current_attempt_object_set",
        }
        _assert_only_keys(data, allowed, "reactivation input")

        historical = data["historical_claim"]
        lane = data["lane"]
        evidence_ref = data["disposition_evidence_ref"]
        objects = data["disposition_objects"]
        attempt = data["current_attempt_object_set"]

        p13 = evidence_ref in objects
        p14 = historical.get("status") in TERMINAL_REUSABLE
        p15 = lane.get("occupant_binding") is None

        attempted_claim = attempt["attempted_current_claim"]
        p16 = attempted_claim.get("claim_id") == historical.get("claim_id")

        refs = attempt.get("binding_refs")
        bindings = attempt.get("bindings")
        if not isinstance(refs, list) or not isinstance(bindings, dict):
            raise AdministrationInvalid("P17 requires explicit binding_refs[] and bindings{}")
        p17 = False
        for ref in refs:
            binding = bindings.get(ref)
            if not binding:
                raise AdministrationInvalid(f"P17 missing referenced binding: {ref}")
            if (
                binding.get("claim_id") == attempted_claim.get("claim_id")
                and binding.get("bounded_unit_id") == attempted_claim.get("bounded_unit_id")
                and binding.get("fresh") is True
            ):
                p17 = True
                break

        invalid_resurrection = p13 and p14 and p15 and p16 and not p17
        return {
            "requested_transition": None,
            "selected_branch": None,
            "predicates_consulted": ["P13", "P14", "P15", "P16", "P17"],
            "admissible": not invalid_resurrection,
            "blocking_predicate": "P17" if invalid_resurrection else None,
            "resulting_state": None,
            "reason_code": (
                "OLD_CLAIM_RESURRECTION_WITHOUT_FRESH_BINDING"
                if invalid_resurrection
                else "REACTIVATION_NOT_PROHIBITED_BY_I"
            ),
        }
