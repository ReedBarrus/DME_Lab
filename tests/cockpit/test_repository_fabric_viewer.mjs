import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  buildRepositoryFabricModel,
  selectRepositoryObject,
  setRepositoryQuery,
  visibleRepositoryObjects,
} from '../../src/cockpit/observer/repository_fabric_model.mjs';
import {
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
      ...base,
      object_id: 'repo-1',
      object_kind: 'repository',
      path: '',
      parent_path: null,
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: ''},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: '', object_kind: 'repository'},
    },
    {
      ...base,
      object_id: 'dir-1',
      object_kind: 'directory',
      path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque'},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: 'opaque', object_kind: 'directory'},
    },
    {
      ...base,
      object_id: 'file-1',
      object_kind: 'file',
      path: 'opaque/mystery.zqx',
      parent_path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque/mystery.zqx'},
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: 'a'.repeat(40), path: 'opaque/mystery.zqx', object_kind: 'file'},
    },
    {
      ...base,
      object_id: 'version-1',
      object_kind: 'file_version',
      path: 'opaque/mystery.zqx',
      parent_path: 'opaque',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path: 'opaque/mystery.zqx'},
      git_blob_identity: 'b'.repeat(40),
      content_identity: `sha256:${'c'.repeat(64)}`,
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

test('unknown repository objects are visible and selectable before interpretation', () => {
  const model = buildRepositoryFabricModel(fixture());
  assert.equal(model.objects.length, 4);
  const selected = selectRepositoryObject(model, 'file-1');
  assert.equal(selected.objectById[selected.selectedObjectId].path, 'opaque/mystery.zqx');
  assert.equal(selected.objectById[selected.selectedObjectId].semantic_standing, 'UNINTERPRETED');
  assert.equal(selectRepositoryObject(model, 'absent'), model);
});

test('filtering changes visibility only and preserves exact source objects', () => {
  const model = buildRepositoryFabricModel(fixture());
  const filtered = setRepositoryQuery(model, 'mystery.zqx');
  assert.equal(visibleRepositoryObjects(filtered).length, 2);
  assert.equal(filtered.objects, model.objects);
  assert.equal(filtered.source, model.source);
});

test('render answers exact identity questions without deriving semantics', () => {
  const model = selectRepositoryObject(buildRepositoryFabricModel(fixture()), 'version-1');
  const html = renderRepositoryFabric(model);
  for (const text of [
    'UNKNOWN SEMANTICS != INVISIBLE OBJECT',
    'PATH IDENTITY != CONTENT IDENTITY',
    'FILE OBJECT != FILE VERSION',
    'SAME ADDRESS != SAME AUTHORITY',
    'opaque/mystery.zqx',
    'GIT_BLOB_IDENTITY',
    'CONTENT_IDENTITY',
    'EXISTENCE_STANDING',
    'SEMANTIC_STANDING',
    'TYPED_PROJECTIONS',
    'UNINTERPRETED',
    'NONE — SEMANTIC ROLE NOT DERIVED',
    'COPY EXACT ADDRESS',
    'CLAIM CEILING',
  ]) assert.match(html, new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.doesNotMatch(html, /data-authorize|data-execute|data-control/);
});

test('source-unavailable rendering fails closed', () => {
  const html = renderRepositoryFabricUnavailable('404');
  assert.match(html, /SOURCE UNAVAILABLE · UNKNOWN_REGION/);
  assert.match(html, /No cached tree or inferred repository objects/);
  assert.doesNotMatch(html, /opaque\/mystery/);
});

test('browser loader remains fixed read-only and has no operative transport', async () => {
  const app = await readFile(
    new URL('../../src/cockpit/observer/repository_fabric_app.mjs', import.meta.url),
    'utf8',
  );
  assert.match(app, /method: 'GET'/);
  assert.match(app, /cache: 'no-store'/);
  assert.doesNotMatch(app, /EventSource|WebSocket|startControlAdapter/);
  assert.doesNotMatch(app, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
});
