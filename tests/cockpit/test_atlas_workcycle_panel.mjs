import assert from 'node:assert/strict';
import test from 'node:test';

import {
  atlasFrameUrlWithRuntime,
} from '../../src/cockpit/observer/atlas_landing.mjs';
import {
  renderWorkcycleOperator,
  renderWorkcycleRail,
} from '../../src/cockpit/observer/repository_fabric_render.mjs';

test('Atlas landing forwards runtime sidecar endpoint into repository fabric iframe', () => {
  const result = atlasFrameUrlWithRuntime(
    'http://127.0.0.1:9000/src/cockpit/observer/?runtime=http%3A%2F%2F127.0.0.1%3A8765%2Fruntime%2Fevents&control=http%3A%2F%2F127.0.0.1%3A8770',
    './repository_fabric.html',
  );
  const url = new URL(result);
  assert.equal(url.pathname, '/src/cockpit/observer/repository_fabric.html');
  assert.equal(
    url.searchParams.get('runtime'),
    'http://127.0.0.1:8765/runtime/events',
  );
  assert.equal(
    url.searchParams.get('control'),
    'http://127.0.0.1:8770',
  );
});

test('workcycle operator visibly exposes currentness consequence budget and read-only control posture', () => {
  const html = renderWorkcycleOperator({
    campaign_id: 'WORKCYCLE_STABILIZATION_001',
    active_horizon: 'COMPRESSION_HISTORY_CONSERVATION',
    next_pressure: 'T2_ADJUDICATION',
    active_work_item: null,
    latest_completed_work_item: 'W1',
    next_eligible_work_item: null,
    campaign_progress: {
      T0: {posture: 'BOUNDED_PASS'},
      T1: {posture: 'BOUNDED_PASS'},
      T2: {posture: 'EXERCISED_UNADJUDICATED'},
    },
    latest_consequence: {
      observations: {
        source_bytes: 4051,
        candidate_bytes: 3486,
        delta_bytes: -565,
        reduction_ratio: 0.139472,
      },
    },
    latest_consequence_evaluation: {
      disposition: 'CONSEQUENCE_MATCHED',
    },
    wake_budget: {
      work_items: {consumed: 0, reserved: 0, allowed_per_wake: 1},
      seat_invocations: {consumed: 0, reserved: 0, allowed_per_wake: 1},
      repair_attempts: {consumed: 0, reserved: 0, allowed: 0},
    },
    eligibility: {
      posture: 'PARTIAL_COORDINATES_ONLY',
      eligible: null,
      unresolved_coordinates: ['seat_available', 'authority_satisfied'],
    },
    current_unresolved: ['bounded claim ceiling remains'],
    temporal_horizon_closure: {
      disposition: 'HORIZON_MATCHED',
      history_posture: 'SUPPORTED',
      currentness_posture: 'SUPPORTED',
      upcoming_work_posture: 'SUPPORTED',
      primary_horizon: {
        family: 'H_reconstruct',
        subject: 'campaign-to-work decomposition lineage',
      },
      seven_surfaces: {
        identity_address: {posture: 'SUPPORTED'},
        mechanical: {posture: 'SUPPORTED'},
        symbolic_semantic: {posture: 'SUPPORTED'},
        relational_topological: {posture: 'SUPPORTED'},
        consequence_environmental: {posture: 'SUPPORTED'},
        provenance: {posture: 'SUPPORTED'},
        invariance_meta: {posture: 'SUPPORTED'},
      },
      six_load_dimensions: {
        functional: {direction: 'INCREASING'},
        semantic: {direction: 'REDISTRIBUTED'},
        authority: {direction: 'STABLE'},
        provenance: {direction: 'STABLE'},
        temporal: {direction: 'INCREASING'},
        coordination: {direction: 'INCREASING'},
      },
    },
    qualification_readiness: {
      bounded_workcycle: {
        qualification_readiness: 'HELD',
        blockers: ['T7:IMPLEMENTED_UNPRESSURED', 'TEMPORAL_HORIZON:UNFROZEN'],
      },
      self_moving_workcycle: {
        qualification_readiness: 'HELD',
        blockers: [
          'T7:IMPLEMENTED_UNPRESSURED',
          'TEMPORAL_HORIZON:UNFROZEN',
          'ONE_SUCCESSOR:UNFROZEN',
          'ATOMIC_ADMISSION:UNFROZEN',
        ],
      },
    },
    basis_record: {
      basis_posture: 'SUPPORTED',
      basis_id: 'basis:sha256:fixture',
    },
    pressure_justification: {
      pressure_posture: 'JUSTIFIED',
      proposed_pressure: 'T7_PRESSURE',
      next_work_posture: 'RESOLVE_LOAD_BEARING_GAP',
      load_bearing_relation: 'operator currentness and control truth',
      if_resolved: {
        expected_operating_change: 'replace operator-projection uncertainty',
      },
      if_nothing_changes: 'DO_NOT_RUN',
    },
    operator_summary: {
      workflow: 'OFF',
      campaign: 'ACTIVE',
      seat_work: 'DISABLED',
      reed_action: 'REVIEW_NEXT_PRESSURE',
      auto_continuation_limit: 0,
    },
  });

  for (const phrase of [
    'WORKCYCLE / METABOLISM',
    'WORKCYCLE_STABILIZATION_001',
    'COMPRESSION_HISTORY_CONSERVATION',
    'T2_ADJUDICATION',
    'CONSEQUENCE_MATCHED',
    '4051',
    '3486',
    'REVIEW_NEXT_PRESSURE',
    'CONTROL WRITE NOT YET ADMITTED',
    'DISPLAYED CONTROL STATE ≠ EXECUTION AUTHORITY',
    'RELATIONAL HORIZON',
    'H_reconstruct',
    'HORIZON_MATCHED',
    'SEVEN CONSERVATION SURFACES',
    'SIX LOAD DIMENSIONS',
    'identity_address',
    'functional',
    'QUALIFICATION READINESS',
    'T7:IMPLEMENTED_UNPRESSURED',
    'TEMPORAL_HORIZON:UNFROZEN',
    'BASIS / PRESSURE JUSTIFICATION',
    'operator currentness and control truth',
    'DO_NOT_RUN',
  ]) {
    assert.ok(html.includes(phrase), phrase);
  }
  assert.ok(html.includes('WAKE'));
  assert.ok(html.includes('PAUSE'));
  assert.ok(html.includes('STOP'));
  assert.doesNotMatch(html, /data-authorize|data-execute|data-control-write/);
});

test('workcycle witness rail is persistent-left content with truthful partial eligibility', () => {
  const html = renderWorkcycleRail({
    next_pressure: 'T2_ADJUDICATION',
    active_work_item: null,
    latest_completed_work_item: 'W1',
    next_eligible_work_item: null,
    latest_consequence: {observations: {delta_bytes: -565}},
    latest_consequence_evaluation: {disposition: 'CONSEQUENCE_MATCHED'},
    wake_budget: {work_items: {consumed: 0, reserved: 0, allowed_per_wake: 1}},
    eligibility: {posture: 'PARTIAL_COORDINATES_ONLY', eligible: null},
    current_unresolved: ['bounded claim ceiling remains'],
    temporal_horizon_closure: {
      disposition: 'HORIZON_MATCHED',
      history_posture: 'SUPPORTED',
      currentness_posture: 'SUPPORTED',
      upcoming_work_posture: 'SUPPORTED',
      primary_horizon: {
        family: 'H_reconstruct',
        subject: 'campaign-to-work decomposition lineage',
      },
      seven_surfaces: {
        identity_address: {posture: 'SUPPORTED'},
        mechanical: {posture: 'SUPPORTED'},
        symbolic_semantic: {posture: 'SUPPORTED'},
        relational_topological: {posture: 'SUPPORTED'},
        consequence_environmental: {posture: 'SUPPORTED'},
        provenance: {posture: 'SUPPORTED'},
        invariance_meta: {posture: 'SUPPORTED'},
      },
      six_load_dimensions: {
        functional: {direction: 'INCREASING'},
        semantic: {direction: 'REDISTRIBUTED'},
        authority: {direction: 'STABLE'},
        provenance: {direction: 'STABLE'},
        temporal: {direction: 'INCREASING'},
        coordination: {direction: 'INCREASING'},
      },
    },
    seat_ecology: {
      durable_seats: [{seat_id: 'LABBOIB', occupant_binding: 'UNBOUND'}],
      registered_runtime_seats: [],
      occupied_runtime_seats: [],
    },
    qualification_readiness: {
      bounded_workcycle: {
        qualification_readiness: 'HELD',
        blockers: ['T7:IMPLEMENTED_UNPRESSURED', 'TEMPORAL_HORIZON:UNFROZEN'],
      },
      self_moving_workcycle: {
        qualification_readiness: 'HELD',
        blockers: [
          'T7:IMPLEMENTED_UNPRESSURED',
          'TEMPORAL_HORIZON:UNFROZEN',
          'ONE_SUCCESSOR:UNFROZEN',
          'ATOMIC_ADMISSION:UNFROZEN',
        ],
      },
    },
    basis_record: {
      basis_posture: 'SUPPORTED',
      basis_id: 'basis:sha256:fixture',
    },
    pressure_justification: {
      pressure_posture: 'JUSTIFIED',
      proposed_pressure: 'T7_PRESSURE',
      next_work_posture: 'RESOLVE_LOAD_BEARING_GAP',
      load_bearing_relation: 'operator currentness and control truth',
      if_resolved: {
        expected_operating_change: 'replace operator-projection uncertainty',
      },
      if_nothing_changes: 'DO_NOT_RUN',
    },
    operator_summary: {
      workflow: 'OFF',
      campaign: 'ACTIVE',
      seat_work: 'DISABLED',
      wake_requested: false,
      reed_action: 'REVIEW_NEXT_PRESSURE',
    },
  }, null, true);
  for (const phrase of [
    'WORKCYCLE / METABOLISM',
    'T2_ADJUDICATION',
    'PARTIAL_COORDINATES_ONLY',
    'W1',
    'OPEN SCIENTIFIC DETAIL',
    '1 CURRENT UNRESOLVED',
    'LABBOIB',
    'LOCAL OPERATOR CONTROL CONNECTED',
    'data-workcycle-control="ENABLE"',
    'data-workcycle-control="STOP"',
    'H_reconstruct',
    'HORIZON_MATCHED',
    'SUPPORTED / SUPPORTED / SUPPORTED',
    'BOUNDED QUALIFICATION',
    'SELF-MOVING QUALIFICATION',
    'PRESSURE JUSTIFICATION',
    'JUSTIFIED',
    'T7_PRESSURE',
    'RESOLVE_LOAD_BEARING_GAP',
  ]) assert.ok(html.includes(phrase), phrase);
  assert.ok(html.includes('data-workcycle-control="ADMIT_ONE"'));
  assert.match(html, /data-workcycle-control="ADMIT_ONE"\s+disabled/);
});

test('workcycle operator fails visibly when runtime projection is unavailable', () => {
  const html = renderWorkcycleOperator(null, 'runtime missing');
  assert.match(html, /RUNTIME PROJECTION UNAVAILABLE/);
  assert.match(html, /runtime missing/);
});
