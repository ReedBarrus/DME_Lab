import assert from 'node:assert/strict';
import test from 'node:test';

import {
  atlasFrameUrlWithRuntime,
} from '../../src/cockpit/observer/atlas_landing.mjs';
import {
  renderWorkcycleOperator,
} from '../../src/cockpit/observer/repository_fabric_render.mjs';

test('Atlas landing forwards runtime sidecar endpoint into repository fabric iframe', () => {
  const result = atlasFrameUrlWithRuntime(
    'http://127.0.0.1:9000/src/cockpit/observer/?runtime=http%3A%2F%2F127.0.0.1%3A8765%2Fruntime%2Fevents',
    './repository_fabric.html',
  );
  const url = new URL(result);
  assert.equal(url.pathname, '/src/cockpit/observer/repository_fabric.html');
  assert.equal(
    url.searchParams.get('runtime'),
    'http://127.0.0.1:8765/runtime/events',
  );
});

test('workcycle operator visibly exposes currentness consequence budget and read-only control posture', () => {
  const html = renderWorkcycleOperator({
    campaign_id: 'WORKCYCLE_STABILIZATION_001',
    active_horizon: 'COMPRESSION_HISTORY_CONSERVATION',
    next_pressure: 'T2_ADJUDICATION',
    current_work_item: 'W1',
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
    budget: {
      work_items: {consumed: 0, reserved: 0, allowed_per_wake: 1},
      seat_invocations: {consumed: 0, reserved: 0, allowed_per_wake: 1},
      repair_attempts: {consumed: 0, reserved: 0, allowed: 0},
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
  ]) {
    assert.ok(html.includes(phrase), phrase);
  }
  assert.ok(html.includes('<button type="button" disabled>WAKE</button>'));
  assert.ok(html.includes('<button type="button" disabled>PAUSE</button>'));
  assert.ok(html.includes('<button type="button" disabled>STOP</button>'));
  assert.doesNotMatch(html, /data-authorize|data-execute|data-control-write/);
});

test('workcycle operator fails visibly when runtime projection is unavailable', () => {
  const html = renderWorkcycleOperator(null, 'runtime missing');
  assert.match(html, /RUNTIME PROJECTION UNAVAILABLE/);
  assert.match(html, /runtime missing/);
});
