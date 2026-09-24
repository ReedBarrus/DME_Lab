import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  buildGeometricRepositoryField,
  dollyFieldCamera,
  orbitFieldCamera,
  panFieldCamera,
  repositoryFieldRelationCounts,
  setGeometricBasisWeights,
} from '../../src/cockpit/observer/repository_fabric_geometry.mjs';
import {
  buildRepositoryFabricModel,
  exactRepositoryQueryMatch,
  selectRepositoryObject,
  setRepositoryQuery,
  visibleRepositoryObjects,
} from '../../src/cockpit/observer/repository_fabric_model.mjs';
import {
  drawGeometricRepositoryField,
  renderRepositoryFabric,
  renderRepositoryFabricUnavailable,
} from '../../src/cockpit/observer/repository_fabric_render.mjs';

function fixture() {
  const base = {
    repository_identity: 'ReedBarrus/DME_Lab',
    source_commit: 'a'.repeat(40),
    source_ref: 'HEAD',
    source_branch: 'candidate',
    parent_path: '',
    content_identity: null,
    git_blob_identity: null,
    existence_standing: 'EXISTS_AT_SOURCE_COMMIT',
    semantic_standing: 'UNINTERPRETED',
    typed_projections: [],
  };
  const objects = [
    {
      ...base, object_id: 'repo-1', object_kind: 'repository', path: '', parent_path: null,
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: ''},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: '', object_kind: 'repository'},
    },
    {
      ...base, object_id: 'dir-1', object_kind: 'directory', path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque'},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: 'opaque', object_kind: 'directory'},
    },
    {
      ...base, object_id: 'file-1', object_kind: 'file', path: 'opaque/mystery.zqx', parent_path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque/mystery.zqx'},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: 'opaque/mystery.zqx', object_kind: 'file'},
    },
    {
      ...base, object_id: 'version-1', object_kind: 'file_version', path: 'opaque/mystery.zqx', parent_path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque/mystery.zqx'},
      git_blob_identity: 'b'.repeat(40), content_identity: `sha256:${'c'.repeat(64)}`,
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: 'opaque/mystery.zqx', object_kind: 'file_version', git_blob_sha: 'b'.repeat(40)},
    },
  ];
  return {
    object_type: 'REPOSITORY_ADDRESS_FABRIC_V0',
    repository_identity: 'ReedBarrus/DME_Lab',
    source_commit: 'a'.repeat(40),
    source_branch: 'candidate',
    authority_effect: 'NONE',
    execution_effect: 'NONE',
    claim_ceiling: 'mechanical repository identity only',
    objects,
    relations: [
      {relation_id: 'r1', source_id: 'repo-1', relation: 'CONTAINS', target_id: 'dir-1'},
      {relation_id: 'r2', source_id: 'dir-1', relation: 'CONTAINS', target_id: 'file-1'},
      {relation_id: 'r3', source_id: 'file-1', relation: 'HAS_VERSION', target_id: 'version-1'},
    ],
  };
}

const positions = (field, key = 'restPosition') => Object.fromEntries(
  field.nodes.map((node) => [node.objectId, node[key]]),
);

test('all source objects remain addressable and unknown objects remain visible', () => {
  const model = buildRepositoryFabricModel(fixture());
  const field = buildGeometricRepositoryField(model);
  assert.equal(field.nodes.length, model.objects.length);
  for (const object of model.objects) {
    assert.equal(field.nodeById[object.object_id].sourceObject, object);
    assert.deepEqual(field.nodeById[object.object_id].sourceObject.address, object.address);
  }
  const selected = selectRepositoryObject(model, 'file-1');
  assert.equal(selected.objectById[selected.selectedObjectId].semantic_standing, 'UNINTERPRETED');
  assert.equal(field.nodeById['file-1'].sourceObject.semantic_standing, 'UNINTERPRETED');
  assert.deepEqual(field.dynamicStanding, {authority: 'UNAVAILABLE', consequence: 'UNAVAILABLE'});
});

test('search highlights matches without deleting or filtering the geometric field', () => {
  const model = buildRepositoryFabricModel(fixture());
  const field = buildGeometricRepositoryField(model);
  const queried = setRepositoryQuery(model, 'mystery.zqx');
  assert.equal(visibleRepositoryObjects(queried).length, 2);
  assert.equal(exactRepositoryQueryMatch(setRepositoryQuery(model, 'opaque/mystery.zqx')).object_id, 'file-1');
  assert.equal(field.nodes.length, 4);
  assert.equal(queried.objects, model.objects);
  assert.equal(queried.source, model.source);
});

test('layout is deterministic and relation-driven rather than source list order', () => {
  const source = fixture();
  const shuffled = {...source, objects: [...source.objects].reverse(), relations: [...source.relations].reverse()};
  const first = buildGeometricRepositoryField(buildRepositoryFabricModel(source));
  const second = buildGeometricRepositoryField(buildRepositoryFabricModel(shuffled));
  assert.deepEqual(positions(first), positions(second));
  assert.equal(first.layoutAlgorithm, 'DETERMINISTIC_HIERARCHICAL_RADIAL_VOLUME_V0');
  assert.deepEqual(repositoryFieldRelationCounts(first), {containment: 2, version: 1, dependency: 0});
});

test('basis deformation preserves node identity, selected identity, source identity, and rest coordinates', () => {
  const model = selectRepositoryObject(buildRepositoryFabricModel(fixture()), 'version-1');
  const field = buildGeometricRepositoryField(model);
  const selectedBefore = model.selectedObjectId;
  const nodeBefore = field.nodeById['version-1'];
  const sourceBefore = nodeBefore.sourceObject;
  const restBefore = structuredClone(nodeBefore.restPosition);
  const currentBefore = structuredClone(nodeBefore.currentPosition);
  setGeometricBasisWeights(field, {structural: {containment: 0.55, version: 0.31}});
  assert.equal(field.nodeById['version-1'], nodeBefore);
  assert.equal(field.nodeById['version-1'].sourceObject, sourceBefore);
  assert.equal(model.selectedObjectId, selectedBefore);
  assert.deepEqual(nodeBefore.restPosition, restBefore);
  assert.notDeepEqual(nodeBefore.currentPosition, currentBefore);
  assert.equal(nodeBefore.objectId, 'version-1');
});

test('camera orbit, pan, and dolly preserve field and object identities', () => {
  const model = selectRepositoryObject(buildRepositoryFabricModel(fixture()), 'file-1');
  const field = buildGeometricRepositoryField(model);
  const nodesBefore = [...field.nodes];
  const restBefore = structuredClone(positions(field));
  const cameraBefore = structuredClone(field.camera);
  orbitFieldCamera(field, 0.3, -0.2);
  panFieldCamera(field, 14, -9);
  dollyFieldCamera(field, -0.18);
  assert.notDeepEqual(field.camera, cameraBefore);
  assert.deepEqual(field.nodes, nodesBefore);
  assert.deepEqual(positions(field), restBefore);
  assert.equal(model.selectedObjectId, 'file-1');
});

test('zoom changes relation level-of-detail without creating or replacing objects', () => {
  const model = buildRepositoryFabricModel(fixture());
  const field = buildGeometricRepositoryField(model);
  const context = {
    setTransform() {}, clearRect() {}, fillRect() {}, beginPath() {}, arc() {},
    fill() {}, stroke() {}, moveTo() {}, lineTo() {}, fillText() {},
  };
  const canvas = {
    width: 0, height: 0,
    getBoundingClientRect: () => ({width: 900, height: 650}),
    getContext: () => context,
  };
  const nodesBefore = [...field.nodes];
  field.camera.distance = 1500;
  const whole = drawGeometricRepositoryField(canvas, model, field);
  field.camera.distance = 1000;
  const local = drawGeometricRepositoryField(canvas, model, field);
  assert.equal(whole.renderedObjects, model.objects.length);
  assert.equal(local.renderedObjects, model.objects.length);
  assert.ok(local.renderedRelations > whole.renderedRelations);
  assert.deepEqual(field.nodes, nodesBefore);
});

test('only explicit mechanical dependency relations create dependency geometry', () => {
  const source = fixture();
  source.relations.push({relation_id: 'r4', source_id: 'file-1', relation: 'REFERENCES', target_id: 'repo-1'});
  const field = buildGeometricRepositoryField(buildRepositoryFabricModel(source));
  assert.equal(field.dependencyEdges.length, 1);
  assert.notDeepEqual(field.nodeById['file-1'].components.dependency, {x: 0, y: 0, z: 0});
  const withoutDependency = structuredClone(field.nodeById['file-1'].currentPosition);
  setGeometricBasisWeights(field, {structural: {dependency: 0}});
  assert.notDeepEqual(field.nodeById['file-1'].currentPosition, withoutDependency);
});

test('filenames do not infer semantic roles or affect coordinates independently of identity', () => {
  const source = fixture();
  const renamedLabels = structuredClone(source);
  renamedLabels.objects.find((object) => object.object_id === 'file-1').path = 'authority/runtime/controller.py';
  renamedLabels.objects.find((object) => object.object_id === 'version-1').path = 'authority/runtime/controller.py';
  const first = buildGeometricRepositoryField(buildRepositoryFabricModel(source));
  const second = buildGeometricRepositoryField(buildRepositoryFabricModel(renamedLabels));
  assert.deepEqual(positions(first), positions(second));
  assert.equal(second.nodeById['file-1'].sourceObject.semantic_standing, 'UNINTERPRETED');
  assert.equal('semanticRole' in second.nodeById['file-1'], false);
});

test('render is a geometric primary surface with subordinate exact inspector', () => {
  const model = selectRepositoryObject(buildRepositoryFabricModel(fixture()), 'version-1');
  const field = buildGeometricRepositoryField(model);
  const html = renderRepositoryFabric(model, field);
  for (const text of [
    'GEOMETRIC REPOSITORY PROJECTION V0',
    'UNKNOWN SEMANTICS != INVISIBLE OBJECT',
    'ZOOM != NEW DATA MODEL',
    'BASIS CHANGE != NEW OBJECT IDENTITY',
    'STRUCTURAL BASE SPACE != DYNAMIC FIELD STATE',
    'data-geometric-field',
    'opaque/mystery.zqx',
    'STRUCTURAL_REST_S(X)',
    'CURRENT_PROJECTED_P(X,T)',
    'CONTENT_IDENTITY',
    'UNINTERPRETED',
    'NONE - SEMANTIC ROLE NOT DERIVED',
    'COPY EXACT ADDRESS',
    'AUTHORITY - UNAVAILABLE',
    'CONSEQUENCE - UNAVAILABLE',
    'SCIENTIFIC OPERATOR != SOURCE TRUTH',
  ]) assert.match(html, new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.doesNotMatch(html, /role="tree"|fabric-object-list|data-authorize|data-execute|data-control/);
});

test('source-unavailable rendering fails closed without fabricated field data', () => {
  const html = renderRepositoryFabricUnavailable('404');
  assert.match(html, /SOURCE UNAVAILABLE - UNKNOWN_REGION/);
  assert.match(html, /No cached tree, inferred repository objects, or fabricated telemetry/);
  assert.doesNotMatch(html, /opaque\/mystery/);
});

test('browser loader permits observation plus only the bounded local workcycle control transport', async () => {
  const [app, geometry, renderer] = await Promise.all([
    readFile(new URL('../../src/cockpit/observer/repository_fabric_app.mjs', import.meta.url), 'utf8'),
    readFile(new URL('../../src/cockpit/observer/repository_fabric_geometry.mjs', import.meta.url), 'utf8'),
    readFile(new URL('../../src/cockpit/observer/repository_fabric_render.mjs', import.meta.url), 'utf8'),
  ]);
  assert.match(app, /method: 'GET'/);
  assert.match(app, /cache: 'no-store'/);
  assert.match(app, /EventSource/);
  assert.match(app, /\/workcycle\/control\/preview/);
  assert.match(app, /\/workcycle\/control\/commit/);
  assert.doesNotMatch(app, /WebSocket|startControlAdapter/);
  assert.doesNotMatch(app, /method:\s*['"](?:PUT|PATCH|DELETE)['"]/i);
  assert.doesNotMatch(`${geometry}\n${renderer}`, /data-authorize|data-execute|invoke_lmstudio|evaluate_branch/);
});
