import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  buildControlIntent,
  controlPath,
} from '../../src/cockpit/observer/control_live.mjs';

const ROOT = new URL('../../', import.meta.url);

test('FOCUS intent contains only exact typed focus fields', () => {
  const intent = buildControlIntent({
    verb: 'FOCUS',
    gesture_id: 'G1',
    campaign_id: 'COCKPIT_OPERATING_SPACE_001',
    request_id: 'COS-E1',
    reason: 'focus it',
    assignment_id: 'ignored',
    seat_id: 'ignored',
    preparation_kind: 'ignored',
  });
  assert.deepEqual(intent, {
    verb: 'FOCUS',
    gesture_id: 'G1',
    reason: 'focus it',
    campaign_id: 'COCKPIT_OPERATING_SPACE_001',
    request_id: 'COS-E1',
  });
});

test('ASSIGN intent names exact seat and preparation kind', () => {
  const intent = buildControlIntent({
    verb: 'ASSIGN',
    gesture_id: 'G2',
    campaign_id: 'COCKPIT_OPERATING_SPACE_001',
    request_id: 'COS-E1',
    seat_id: 'MAYA',
    preparation_kind: 'RESOLVE_REFS',
    reason: '',
  });
  assert.deepEqual(intent, {
    verb: 'ASSIGN',
    gesture_id: 'G2',
    reason: null,
    campaign_id: 'COCKPIT_OPERATING_SPACE_001',
    request_id: 'COS-E1',
    seat_id: 'MAYA',
    preparation_kind: 'RESOLVE_REFS',
  });
});

test('RELEASE and RING name one exact assignment and do not infer work', () => {
  for (const verb of ['RELEASE', 'RING']) {
    const intent = buildControlIntent({
      verb,
      gesture_id: 'G-' + verb,
      campaign_id: 'COCKPIT_OPERATING_SPACE_001',
      assignment_id: 'A17',
      reason: null,
    });
    assert.deepEqual(intent, {
      verb,
      gesture_id: 'G-' + verb,
      reason: null,
      campaign_id: 'COCKPIT_OPERATING_SPACE_001',
      assignment_id: 'A17',
    });
    assert.equal('request_id' in intent, false);
    assert.equal('priority' in intent, false);
    assert.equal('authority' in intent, false);
  }
});

test('unsupported control verbs are rejected client-side', () => {
  assert.throws(
    () => buildControlIntent({verb: 'AUTHORIZE'}),
    /unsupported Cockpit control verb/,
  );
  assert.throws(
    () => buildControlIntent({verb: 'STOP'}),
    /unsupported Cockpit control verb/,
  );
});

test('control endpoint remains a separate base from runtime projection', () => {
  assert.equal(
    controlPath('http://127.0.0.1:8770/', '/control/preview'),
    'http://127.0.0.1:8770/control/preview',
  );
});

test('observer HTML exposes separate read and control roots', async () => {
  const html = await readFile(
    new URL('src/cockpit/observer/index.html', ROOT),
    'utf8',
  );
  assert.match(html, /id="runtime-root"/);
  assert.match(html, /id="control-root"/);
  assert.notEqual(
    html.indexOf('id="runtime-root"'),
    html.indexOf('id="control-root"'),
  );
});

test('app starts read projection and control adapter as separate modules', async () => {
  const app = await readFile(
    new URL('src/cockpit/observer/app.mjs', ROOT),
    'utf8',
  );
  assert.match(app, /startRuntimeProjection/);
  assert.match(app, /startControlAdapter/);
  assert.match(app, /#runtime-root/);
  assert.match(app, /#control-root/);
});

test('read-side runtime module does not acquire control endpoints', async () => {
  const runtime = await readFile(
    new URL('src/cockpit/observer/runtime_live.mjs', ROOT),
    'utf8',
  );
  assert.doesNotMatch(runtime, /\/control\/(?:preview|commit|state)/);
  assert.doesNotMatch(runtime, /startControlAdapter/);
});
