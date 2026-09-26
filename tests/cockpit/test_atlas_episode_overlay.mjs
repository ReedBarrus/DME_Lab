import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  CELL002_EPISODE_SOURCE_PATHS,
  buildCell002EpisodeOverlay,
  classificationsForObject,
  createAtlasOperatorState,
  setEpisodeStep,
  toggleAtlasInspector,
  toggleScientificEpisode,
} from '../../src/cockpit/observer/cell002_episode_overlay.mjs';
import { buildGeometricRepositoryField } from '../../src/cockpit/observer/repository_fabric_geometry.mjs';
import { buildRepositoryFabricModel, selectRepositoryObject } from '../../src/cockpit/observer/repository_fabric_model.mjs';
import {
  drawGeometricRepositoryField,
  renderRepositoryFabric,
} from '../../src/cockpit/observer/repository_fabric_render.mjs';

const ROOT = new URL('../../', import.meta.url);
const COMMIT = 'e'.repeat(40);

async function sha256(path) {
  const bytes = await readFile(new URL(path, ROOT));
  return createHash('sha256').update(bytes).digest('hex');
}

async function traceSource() {
  return JSON.parse(await readFile(
    new URL('traces/authority_membrane_security_cell_002_installed_qualification_result.json', ROOT),
    'utf8',
  ));
}

async function repositoryFixture(extraPath = 'outside/unrelated.txt') {
  const repository = {
    object_id: 'repo-1', object_kind: 'repository', repository_identity: 'ReedBarrus/DME_Lab',
    source_commit: COMMIT, source_branch: 'candidate', path: '', parent_path: null,
    path_identity: {repository: 'ReedBarrus/DME_Lab', path: ''},
    content_identity: null, git_blob_identity: null,
    existence_standing: 'EXISTS_AT_SOURCE_COMMIT', semantic_standing: 'UNINTERPRETED',
    typed_projections: [],
    address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: COMMIT, path: '', object_kind: 'repository'},
  };
  const objects = [repository];
  const relations = [];
  const paths = [...CELL002_EPISODE_SOURCE_PATHS, extraPath];
  for (let index = 0; index < paths.length; index += 1) {
    const path = paths[index];
    const content = path === extraPath ? '0'.repeat(64) : await sha256(path);
    const fileId = `file-${index}`;
    const versionId = `version-${index}`;
    const common = {
      repository_identity: 'ReedBarrus/DME_Lab', source_commit: COMMIT,
      source_branch: 'candidate', path, parent_path: '',
      path_identity: {repository: 'ReedBarrus/DME_Lab', path},
      existence_standing: 'EXISTS_AT_SOURCE_COMMIT', semantic_standing: 'UNINTERPRETED',
      typed_projections: [],
    };
    objects.push({
      ...common, object_id: fileId, object_kind: 'file', content_identity: null,
      git_blob_identity: null,
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: COMMIT, path, object_kind: 'file'},
    });
    objects.push({
      ...common, object_id: versionId, object_kind: 'file_version',
      content_identity: `sha256:${content}`, git_blob_identity: content.slice(0, 40),
      address: {substrate: 'repo', repository: 'ReedBarrus/DME_Lab', commit: COMMIT, path, object_kind: 'file_version', git_blob_sha: content.slice(0, 40)},
    });
    relations.push(
      {relation_id: `contains-${index}`, source_id: 'repo-1', relation: 'CONTAINS', target_id: fileId},
      {relation_id: `version-${index}`, source_id: fileId, relation: 'HAS_VERSION', target_id: versionId},
    );
  }
  return buildRepositoryFabricModel({
    object_type: 'REPOSITORY_ADDRESS_FABRIC_V0', repository_identity: 'ReedBarrus/DME_Lab',
    source_commit: COMMIT, source_branch: 'candidate', authority_effect: 'NONE', execution_effect: 'NONE',
    claim_ceiling: 'mechanical source identity only', objects, relations,
  });
}

test('Atlas is the default Cockpit surface and legacy observer remains reachable', async () => {
  const [html, landing] = await Promise.all([
    readFile(new URL('src/cockpit/observer/index.html', ROOT), 'utf8'),
    import('../../src/cockpit/observer/atlas_landing.mjs'),
  ]);
  assert.equal(landing.DEFAULT_COCKPIT_SURFACE, 'ATLAS');
  assert.match(html, /data-default-cockpit-surface="ATLAS"/);
  assert.match(html, /id="atlas-primary-frame"[\s\S]*src="\.\/repository_fabric\.html"/);
  assert.match(html, /id="legacy-observer-shell" hidden/);
  assert.match(html, /id="instrument-root"/);
  assert.equal(landing.selectCockpitSurface({surface: 'ATLAS'}, 'LEGACY_OBSERVER').surface, 'LEGACY_OBSERVER');
});

test('episode identity is deterministic and bound to exact commit plus primary witness identity', async () => {
  const repository = await repositoryFixture();
  const trace = await traceSource();
  const first = buildCell002EpisodeOverlay(repository, trace);
  const second = buildCell002EpisodeOverlay(repository, structuredClone(trace));
  assert.equal(first.episodeId, second.episodeId);
  assert.equal(first.episodeAddress.commit, COMMIT);
  assert.equal(first.episodeAddress.primaryWitnessContentIdentity, `sha256:${await sha256(CELL002_EPISODE_SOURCE_PATHS[3])}`);
  assert.equal(first.sourceArtifacts.length, 7);
  assert.ok(first.sourceArtifacts.every((artifact) => artifact.objectId && artifact.contentIdentity));
});

test('every empirical scientific classification retains explicit source handles', async () => {
  const episode = buildCell002EpisodeOverlay(await repositoryFixture(), await traceSource());
  const categories = new Set(episode.classifications.map((item) => item.category));
  assert.ok(categories.has('CHANGED'));
  assert.ok(categories.has('HELD_FIXED'));
  assert.ok(categories.has('WITNESSED'));
  assert.ok(categories.has('UNRESOLVED'));
  for (const classification of episode.classifications) {
    assert.ok(classification.sourceHandles.length > 0);
    assert.ok(classification.sourceHandles.every((handle) => handle.objectId));
    assert.equal(classification.supportStatus, 'SOURCE_SUPPORTED');
    assert.equal(classification.sourceObjectChanged, false);
  }
});

test('missing witness support degrades the intended classification to UNRESOLVED', async () => {
  const repository = await repositoryFixture();
  const trace = await traceSource();
  delete trace.control.status_after;
  const episode = buildCell002EpisodeOverlay(repository, trace);
  const changed = episode.classifications.find((item) => item.intendedCategory === 'CHANGED');
  assert.equal(changed.category, 'UNRESOLVED');
  assert.equal(changed.supportStatus, 'SOURCE_SUPPORT_INCOMPLETE');
  assert.ok(changed.sourceHandles.some((handle) => handle.observedValue === 'UNAVAILABLE'));
});

test('overlay OFF ON OFF preserves field nodes, selected source identity, address, camera, and source objects', async () => {
  let repository = await repositoryFixture();
  const episode = buildCell002EpisodeOverlay(repository, await traceSource());
  const authorityPath = CELL002_EPISODE_SOURCE_PATHS[0];
  const authorityObject = repository.objects.find((object) => object.object_kind === 'file' && object.path === authorityPath);
  repository = selectRepositoryObject(repository, authorityObject.object_id);
  const field = buildGeometricRepositoryField(repository);
  const nodeRefs = [...field.nodes];
  const sourceRefs = field.nodes.map((node) => node.sourceObject);
  const address = structuredClone(repository.objectById[repository.selectedObjectId].address);
  const camera = structuredClone(field.camera);
  let state = createAtlasOperatorState(episode);
  state = toggleScientificEpisode(state, episode);
  assert.equal(state.overlay, 'SCIENTIFIC_EPISODE');
  state = setEpisodeStep(state, episode, 5);
  state = toggleScientificEpisode(state, episode);
  assert.equal(state.overlay, 'NONE');
  assert.deepEqual(field.nodes, nodeRefs);
  assert.ok(field.nodes.every((node, index) => node.sourceObject === sourceRefs[index]));
  assert.equal(repository.selectedObjectId, authorityObject.object_id);
  assert.deepEqual(repository.objectById[repository.selectedObjectId].address, address);
  assert.deepEqual(field.camera, camera);
});

test('inspector collapse is independent view state and cannot alter camera', async () => {
  const repository = await repositoryFixture();
  const field = buildGeometricRepositoryField(repository);
  const episode = buildCell002EpisodeOverlay(repository, await traceSource());
  const camera = structuredClone(field.camera);
  const state = toggleAtlasInspector(createAtlasOperatorState(episode));
  assert.equal(state.inspectorCollapsed, true);
  assert.deepEqual(field.camera, camera);
  const [css, app] = await Promise.all([
    readFile(new URL('src/cockpit/observer/repository_fabric.css', ROOT), 'utf8'),
    readFile(new URL('src/cockpit/observer/repository_fabric_app.mjs', ROOT), 'utf8'),
  ]);
  assert.match(css, /\.fabric-inspector[^}]*overflow:\s*auto/s);
  assert.match(css, /\.fabric-canvas[^}]*overscroll-behavior:\s*contain/s);
  assert.match(app, /canvas\.addEventListener\('wheel',[\s\S]*event\.preventDefault\(\)[\s\S]*dollyFieldCamera/);
  assert.doesNotMatch(app, /fabric-inspector[^\n]*addEventListener\(['"]wheel/);
});

test('objects outside episode basis remain source objects and are not called held fixed', async () => {
  const repository = await repositoryFixture();
  const episode = buildCell002EpisodeOverlay(repository, await traceSource());
  const outside = repository.objects.find((object) => object.path === 'outside/unrelated.txt' && object.object_kind === 'file');
  const classification = classificationsForObject(episode, outside)[0];
  assert.equal(classification.category, 'OUT_OF_SCOPE');
  assert.match(classification.whatDidNotChange.join(' '), /does not mean held fixed/);
  assert.equal(classification.sourceHandles[0].admitted, false);
  assert.equal(episode.admittedObjectIds.has(outside.object_id), false);
});

test('active episode annotates the same field and exposes click-through challenge handles', async () => {
  let repository = await repositoryFixture();
  const episode = buildCell002EpisodeOverlay(repository, await traceSource());
  const authority = repository.objects.find(
    (object) => object.object_kind === 'file' && object.path === CELL002_EPISODE_SOURCE_PATHS[0],
  );
  repository = selectRepositoryObject(repository, authority.object_id);
  const field = buildGeometricRepositoryField(repository);
  const state = toggleScientificEpisode(createAtlasOperatorState(episode), episode);
  const html = renderRepositoryFabric(repository, field, state, episode);
  for (const text of [
    'SCIENTIFIC CHALLENGE', 'CHANGED', 'HELD FIXED', 'WITNESSED', 'UNRESOLVED',
    'OUT OF SCOPE - STILL VISIBLE', 'SOURCE_ARTIFACTS / WITNESS HANDLES',
    episode.episodeId, '/control/status_before', 'NO NEW AUTHORITY',
  ]) assert.match(html, new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));

  const context = {
    setTransform() {}, clearRect() {}, fillRect() {}, beginPath() {}, arc() {},
    fill() {}, stroke() {}, moveTo() {}, lineTo() {}, fillText() {}, setLineDash() {},
  };
  const canvas = {
    width: 0, height: 0,
    getBoundingClientRect: () => ({width: 1000, height: 720}),
    getContext: () => context,
  };
  const nodeRefs = [...field.nodes];
  const frame = drawGeometricRepositoryField(canvas, repository, field, episode, state);
  assert.equal(frame.renderedObjects, repository.objects.length);
  assert.ok(frame.overlayClassifiedObjects > 0);
  assert.ok(frame.outOfScopeObjects > 0);
  assert.deepEqual(field.nodes, nodeRefs);
});

test('episode overlay introduces no authority, execution, control, or synthetic live transport', async () => {
  const [episodeSource, appSource] = await Promise.all([
    readFile(new URL('src/cockpit/observer/cell002_episode_overlay.mjs', ROOT), 'utf8'),
    readFile(new URL('src/cockpit/observer/repository_fabric_app.mjs', ROOT), 'utf8'),
  ]);
  assert.doesNotMatch(`${episodeSource}\n${appSource}`, /EventSource|WebSocket|startControlAdapter|invoke_lmstudio|evaluate_branch/);
  assert.doesNotMatch(appSource, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  const trace = await traceSource();
  assert.equal(trace.real_lmstudio_http_calls, 0);
  assert.equal(trace.authority_state_surface, 'TEMPORARY_ONLY');
});
