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
    'OPERATOR CONTROL IS LOCAL + PREVIEWED + CONFIRMED',
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
    seat_ecology: {
      durable_seats: [{seat_id: 'LABBOIB', occupant_binding: 'UNBOUND'}],
      registered_runtime_seats: [],
      occupied_runtime_seats: [],
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
  ]) assert.ok(html.includes(phrase), phrase);
  assert.ok(html.includes('data-workcycle-control="ADMIT_ONE"'));
  assert.match(html, /data-workcycle-control="ADMIT_ONE"\s+disabled/);
});

test('workcycle operator fails visibly when runtime projection is unavailable', () => {
  const html = renderWorkcycleOperator(null, 'runtime missing');
  assert.match(html, /RUNTIME PROJECTION UNAVAILABLE/);
  assert.match(html, /runtime missing/);
});
