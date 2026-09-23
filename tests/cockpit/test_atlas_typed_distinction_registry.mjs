import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {buildGeometricRepositoryField} from '../../src/cockpit/observer/repository_fabric_geometry.mjs';
import {
  buildRepositoryFabricModel,
  selectRepositoryObject,
} from '../../src/cockpit/observer/repository_fabric_model.mjs';
import {renderRepositoryFabric} from '../../src/cockpit/observer/repository_fabric_render.mjs';
import {
  buildTypedDistinctionRegistryModel,
  distinctionsForObject,
  reconstructionHandleFor,
} from '../../src/cockpit/observer/typed_distinction_registry.mjs';

const ROOT = new URL('../../', import.meta.url);
const PATH = 'src/cockpit/observer/repository_fabric_app.mjs';
const COMMIT = 'f'.repeat(40);

function record() {
  return {
    object_type: 'TYPED_DISTINCTION_RECORD_V0',
    distinction_id: 'DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001',
    subject_addresses: [{
      substrate: 'repo_path', repository: 'ReedBarrus/DME_Lab', path: PATH, object_kind: 'file',
    }],
    relation_type: 'NOT_EQUAL',
    value: {left: 'PATH_IDENTITY', right: 'CONTENT_IDENTITY'},
    scope: {scope_type: 'EXACT_ADJACENT_GIT_TRANSITIONS', repository: 'ReedBarrus/DME_Lab', path: PATH},
    source_handles: [{handle_kind: 'GIT_ADJACENT_PATH_CONTENT_CHANGE'}],
    resolved_source_handles: [{
      handle_kind: 'GIT_ADJACENT_PATH_CONTENT_CHANGE', path: PATH,
      from_frame_id: 'frame-before', to_frame_id: 'frame-after',
      old_blob_sha: 'a'.repeat(40), new_blob_sha: 'b'.repeat(40),
    }],
    constructed_by: {kind: 'BOUNDED_IMPLEMENTATION_WARRANT'},
    constructed_at: {kind: 'REPOSITORY_COORDINATE'},
    observed_at: {kind: 'TEMPORAL_LINEAGE_WOUND'},
    evaluated_at: {kind: 'CELL'},
    standing: 'ADMITTED_BOUNDED', currentness: 'HISTORICAL_SPECIMEN',
    claim_ceiling: 'exact registered historical specimen only',
    dependencies: [], unresolved: ['ACTOR_LINEAGE', 'SEMANTIC_CAUSE'],
    authority_effect: 'NONE', execution_effect: 'NONE', control_effect: 'NONE',
  };
}

function projection() {
  const item = record();
  return {
    object_type: 'TYPED_DISTINCTION_REGISTRY_PROJECTION_V0',
    projection_standing: 'DERIVED_READ_ONLY',
    source_registry: {path: 'docs/registry.jsonl', sha256: 'c'.repeat(64)},
    temporal_source_commit: COMMIT,
    authority_effect: 'NONE', execution_effect: 'NONE', control_effect: 'NONE',
    records: [item],
    reconstruction_packets: [{
      packet_type: 'DISTINCTION_RECONSTRUCTION_PACKET_V0',
      distinction_address: item.distinction_id,
      subject_address: item.subject_addresses[0],
      source_handles: item.resolved_source_handles,
      current_standing: item.standing,
      claim_ceiling: item.claim_ceiling,
      dependencies: item.dependencies,
      unresolved: item.unresolved,
    }],
  };
}

function fabricSource() {
  const repositoryId = 'repo';
  const fileId = 'file';
  const versionId = 'version';
  const base = {
    repository_identity: 'ReedBarrus/DME_Lab', source_commit: COMMIT,
    source_ref: 'HEAD', source_branch: 'candidate', existence_standing: 'EXISTS_AT_SOURCE_COMMIT',
    semantic_standing: 'UNINTERPRETED', typed_projections: [],
  };
  return {
    object_type: 'REPOSITORY_ADDRESS_FABRIC_V0', repository_identity: base.repository_identity,
    source_commit: COMMIT, source_branch: 'candidate', authority_effect: 'NONE',
    execution_effect: 'NONE', claim_ceiling: 'mechanical only',
    objects: [
      {...base, object_id: repositoryId, object_kind: 'repository', path: '', parent_path: null,
        content_identity: null, git_blob_identity: null, path_identity: {path: ''},
        address: {substrate: 'repo', repository: base.repository_identity, commit: COMMIT, path: '', object_kind: 'repository'}},
      {...base, object_id: fileId, object_kind: 'file', path: PATH, parent_path: 'src/cockpit/observer',
        content_identity: null, git_blob_identity: null, path_identity: {path: PATH},
        address: {substrate: 'repo', repository: base.repository_identity, commit: COMMIT, path: PATH, object_kind: 'file'}},
      {...base, object_id: versionId, object_kind: 'file_version', path: PATH, parent_path: 'src/cockpit/observer',
        content_identity: `sha256:${'d'.repeat(64)}`, git_blob_identity: 'e'.repeat(40), path_identity: {path: PATH},
        address: {substrate: 'repo', repository: base.repository_identity, commit: COMMIT, path: PATH, object_kind: 'file_version'}},
    ],
    relations: [
      {relation_id: 'contains', source_id: repositoryId, relation: 'CONTAINS', target_id: fileId},
      {relation_id: 'version', source_id: fileId, relation: 'HAS_VERSION', target_id: versionId},
    ],
  };
}

function temporalView(registry) {
  return {
    lineage: {
      frames: [{
        frame_index: 0, frame_id: 'frame-head', commit_sha: COMMIT, tree_sha: '1'.repeat(40),
        subject: 'fixture', git_author: {name: 'Git Fixture', standing: 'GIT_METADATA_ONLY'},
      }],
      woundReplay: {family: 'PATH_IDENTITY != CONTENT_IDENTITY', steps: []},
    },
    state: {frameIndex: 0, actorLayer: false, woundActive: false, woundStep: 0,
      selectionStanding: 'PRESENT_IN_FRAME', missingSelection: null, selectedEmissionId: null},
    emissionLedger: {events: [], transition: null, eventById: {}},
    typedDistinctionRegistry: registry,
  };
}

test('Cell 001 projection admits the exact typed distinction and reconstruction handle', () => {
  const registry = buildTypedDistinctionRegistryModel(projection());
  const model = buildRepositoryFabricModel(fabricSource());
  const subject = model.objectById.file;
  assert.equal(distinctionsForObject(registry, subject).length, 1);
  assert.equal(distinctionsForObject(registry, model.objectById.version).length, 0);
  const handle = reconstructionHandleFor(registry, registry.admitted[0].distinction_id);
  assert.equal(handle.registry_sha256, 'c'.repeat(64));
  assert.equal(handle.packet.current_standing, 'ADMITTED_BOUNDED');
});

test('P07 visual relation without admitted registry support does not count', () => {
  const source = fabricSource();
  source.objects.find((item) => item.object_id === 'file').typed_projections = [
    {relation: 'PATH_IDENTITY != CONTENT_IDENTITY', visual_only: true},
  ];
  const model = buildRepositoryFabricModel(source);
  assert.deepEqual(distinctionsForObject(null, model.objectById.file), []);
  const empty = buildTypedDistinctionRegistryModel({...projection(), records: [], reconstruction_packets: []});
  assert.deepEqual(distinctionsForObject(empty, model.objectById.file), []);
});

test('wrong subject cannot inherit the exact registered distinction', () => {
  const source = projection();
  source.records[0].subject_addresses[0].path = 'src/cockpit/observer/wrong.mjs';
  const registry = buildTypedDistinctionRegistryModel(source);
  const model = buildRepositoryFabricModel(fabricSource());
  assert.deepEqual(distinctionsForObject(registry, model.objectById.file), []);
});

test('historical standing or forbidden effect cannot be collapsed in projection', () => {
  const current = projection();
  current.records[0].currentness = 'CURRENT';
  assert.throws(() => buildTypedDistinctionRegistryModel(current), /violates Cell 001/);
  const authority = projection();
  authority.authority_effect = 'ACTIVE';
  assert.throws(() => buildTypedDistinctionRegistryModel(authority), /forbidden effects/);
});

test('Atlas inspector shows exact bounded distinction without changing object identities', () => {
  const registry = buildTypedDistinctionRegistryModel(projection());
  let model = buildRepositoryFabricModel(fabricSource());
  const idsBefore = model.objects.map((item) => item.object_id);
  model = selectRepositoryObject(model, 'file');
  const field = buildGeometricRepositoryField(model);
  const html = renderRepositoryFabric(
    model, field, undefined, null, null, temporalView(registry),
  );
  for (const phrase of [
    'DISTINCTIONS', 'PATH_IDENTITY != CONTENT_IDENTITY', 'ADMITTED_BOUNDED',
    'HISTORICAL_SPECIMEN', 'SOURCE_HANDLES', 'CLAIM_CEILING', 'DEPENDENCIES',
    'UNRESOLVED', 'CHALLENGE / RECONSTRUCTION HANDLE',
  ]) assert.match(html, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.deepEqual(model.objects.map((item) => item.object_id), idsBefore);
  assert.doesNotMatch(html, /data-authorize|data-execute|data-control/);
});

test('browser surfaces remain read-only and do not mint authority', async () => {
  const [registrySource, appSource, renderSource] = await Promise.all([
    readFile(new URL('src/cockpit/observer/typed_distinction_registry.mjs', ROOT), 'utf8'),
    readFile(new URL('src/cockpit/observer/repository_fabric_app.mjs', ROOT), 'utf8'),
    readFile(new URL('src/cockpit/observer/repository_fabric_render.mjs', ROOT), 'utf8'),
  ]);
  assert.doesNotMatch(appSource, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  assert.doesNotMatch(`${registrySource}\n${appSource}\n${renderSource}`,
    /invoke_lmstudio|evaluate_branch|startControlAdapter|EventSource|WebSocket/);
});
