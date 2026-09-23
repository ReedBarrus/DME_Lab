import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  CELL002_PRIMITIVES,
  buildCell002Specimen,
  selectInspectable,
  selectTraversal,
} from '../../src/cockpit/observer/cell002_model.mjs';
import {
  renderCell002Specimen,
  renderInspector,
  renderUnavailable,
} from '../../src/cockpit/observer/cell002_render.mjs';

const tracePath = new URL(
  '../../traces/authority_membrane_security_cell_002_installed_qualification_result.json',
  import.meta.url,
);
const traceBytes = await readFile(tracePath);
const trace = JSON.parse(traceBytes.toString('utf8'));

test('source-bound model preserves the exact admitted specimen and its ceilings', () => {
  const model = buildCell002Specimen(trace);

  assert.deepEqual(model.semanticPrimitives, [...CELL002_PRIMITIVES]);
  assert.equal(model.standing.sourceCurrentness.label, 'UNRESOLVED');
  assert.equal(model.standing.currentStanding.label, 'UNRESOLVED');
  assert.equal(model.standing.currentAuthority.label, 'NOT_DERIVED');
  assert.equal(model.standing.historicalStanding.detail, 'BOUNDEDLY_QUALIFIED');
  assert.equal(model.testMetadata.realHttpCalls, 0);
  assert.equal(
    model.sourceArtifacts.find((source) => source.id === 'qualification-trace').sha256,
    createHash('sha256').update(traceBytes).digest('hex'),
  );
  assert.deepEqual(model.control.nodes, [
    'control-active', 'control-consuming', 'control-invoked', 'control-consumed',
  ]);
  assert.deepEqual(model.control.edges, [
    'control-reserve', 'control-invoke', 'control-finalize',
  ]);
  assert.equal(model.inspectableById['control-reserve'].witness, trace.control.reservation_id);
  assert.equal(model.inspectableById['control-finalize'].witness, trace.control.receipt_id);
  assert.equal(model.inspectableById['replay-attempt'].beforeObject, trace.control.capability_id);
  assert.ok(model.replay.heldFixed.includes('capability instance'));
  assert.deepEqual(model.wrongPrincipal.changed, ['attempting_principal_id P → Q']);
  assert.ok(model.wrongPrincipal.heldFixed.includes('remaining_uses=1'));
  assert.ok(model.unknownRegion.items.includes('principal authentication'));
  assert.deepEqual(model.unknownRegion.futureShape, ['FRAME 0', 'UNKNOWN_REGION', 'FRAME 1']);
});

test('every inspectable exposes the full challengeable inspector contract', () => {
  const model = buildCell002Specimen(trace);
  const required = [
    'beforeObject', 'beforeState', 'operator', 'basis', 'witness', 'afterObject',
    'afterState', 'whatChanged', 'whatDidNotChange', 'standingEarned',
    'claimCeiling', 'unresolved', 'sourceArtifacts', 'backward', 'forward',
  ];

  for (const inspectable of model.inspectables) {
    for (const field of required) {
      assert.ok(field in inspectable, `${inspectable.id} missing ${field}`);
    }
    assert.ok(inspectable.sourceArtifacts.includes(
      'traces/authority_membrane_security_cell_002_installed_qualification_result.json',
    ));
  }
});

test('selection and provenance traversal modify only derived view state', () => {
  const model = buildCell002Specimen(trace);
  const selected = selectInspectable(model, 'wrong-principal-attempt');
  const traversed = selectTraversal(selected, 'CAUSE');

  assert.notEqual(selected, model);
  assert.equal(selected.sourceTrace, model.sourceTrace);
  assert.equal(selected.selectedInspectableId, 'wrong-principal-attempt');
  assert.equal(traversed.selectedTraversal, 'CAUSE');
  assert.equal(selectInspectable(model, 'not-present'), model);
  assert.equal(selectTraversal(model, 'SIDEWAYS'), model);
  assert.match(renderInspector(traversed), /WHAT DID THIS TRANSFORMATION CAUSE\?/);
  assert.match(renderInspector(traversed), /Principal mismatch denied/);
});

test('render contains exact trajectories, matched differences, provenance, and unknowns', () => {
  const html = renderCell002Specimen(buildCell002Specimen(trace));

  for (const value of [
    'status=ACTIVE', 'status=CONSUMING', 'status=CONSUMED',
    'AUTHORITY_EXHAUSTED', 'PRINCIPAL_MISMATCH',
    'CHANGED', 'HELD FIXED', 'OBSERVED EFFECT',
    'BEFORE_OBJECT', 'BEFORE_STATE', 'TRANSFORMATION / OPERATOR', 'BASIS',
    'WITNESS', 'AFTER_OBJECT', 'AFTER_STATE', 'WHAT_CHANGED',
    'WHAT_DID_NOT_CHANGE', 'STANDING_EARNED', 'CLAIM_CEILING',
    'UNRESOLVED', 'SOURCE_ARTIFACTS',
    'WHY IS THIS STATE HERE?', 'WHAT DID THIS TRANSFORMATION CAUSE?', 'UNKNOWN_REGION',
    'FRAME 0', 'FRAME 1', 'SOURCE CURRENTNESS', 'CURRENT AUTHORITY',
    'HISTORICAL AUTHORITY', 'CURRENT STANDING', 'HISTORICAL STANDING',
    'tests/security/run_installed_authority_membrane_cell002.py',
    trace.control.capability_id,
    trace.control.installed_bridge_sha256,
    trace.control.installed_authority_module_sha256,
    trace.control.installed_policy_sha256,
  ]) {
    assert.match(html, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  }
  assert.doesNotMatch(html, /<form\b|contenteditable|data-execute/i);
  assert.match(html, /Test metadata · PASS/);
  assert.doesNotMatch(html, />PASS<\/span>/);
});

test('unavailable source fails visibly closed without an inferred specimen', () => {
  const html = renderUnavailable('fixture missing');
  assert.match(html, /UNKNOWN_REGION · SOURCE UNAVAILABLE/);
  assert.match(html, /No cached or inferred trajectory is displayed/);
  assert.doesNotMatch(html, /status=ACTIVE|AUTHORITY_EXHAUSTED/);
});

test('browser loader is fixed to GET and contains no mutation transport', async () => {
  const app = await readFile(
    new URL('../../src/cockpit/observer/cell002_app.mjs', import.meta.url),
    'utf8',
  );
  assert.match(app, /method: 'GET'/);
  assert.match(app, /cache: 'no-store'/);
  assert.doesNotMatch(app, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  assert.doesNotMatch(app, /localStorage|sessionStorage|WebSocket|EventSource/);
});
