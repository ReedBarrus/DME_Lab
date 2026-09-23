import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';

import {buildGeometricRepositoryField} from '../../src/cockpit/observer/repository_fabric_geometry.mjs';
import {selectRepositoryObject} from '../../src/cockpit/observer/repository_fabric_model.mjs';
import {renderRepositoryFabric} from '../../src/cockpit/observer/repository_fabric_render.mjs';
import {
  aggregateTransitionEmissions,
  buildTemporalLineageModel,
  buildTransitionEmissionLedger,
  createTemporalOperatorState,
  findObjectByTemporalIdentity,
  moveTemporalFrame,
  reconstructTemporalFrame,
  recordTemporalSelection,
  toggleActorLayer,
} from '../../src/cockpit/observer/repository_temporal_lineage.mjs';

const ROOT = new URL('../../', import.meta.url);

function sourceFixture() {
  const frames = [0, 1, 2].map((index) => ({
    frame_index: index,
    frame_id: `frame-${index}`,
    commit_sha: String(index).repeat(40),
    tree_sha: `tree-${index}`,
    parent_commit_shas: index ? [String(index - 1).repeat(40)] : [],
    first_parent_commit_sha: index ? String(index - 1).repeat(40) : null,
    git_author: {name: 'Git Author', email: 'git@example.invalid', standing: 'GIT_METADATA_ONLY'},
    git_committer: {name: 'Git Committer', email: 'git@example.invalid', standing: 'GIT_METADATA_ONLY'},
    subject: `frame ${index}`,
  }));
  const event1 = {
    event_id: 'event-content', ordinal: 0, status: 'M', old_path: 'a.txt', new_path: 'a.txt',
    old_mode: '100644', new_mode: '100644', old_object_sha: 'blob-one', new_object_sha: 'blob-two',
    lineage_id_before: 'lineage-a', lineage_id_after: 'lineage-a',
    identity_basis: 'SAME_PATH_ADJACENT_FIRST_PARENT_FRAMES',
    classifications: ['PERSISTED', 'CONTENT_CHANGED', 'RELATION_REMOVED', 'RELATION_ADDED'],
    before: {path: 'a.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-one', content_identity: 'sha256:one', lineage_id: 'lineage-a'},
    after: {path: 'a.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-two', content_identity: 'sha256:two', lineage_id: 'lineage-a'},
    relation_changes: {added: ['HAS_VERSION'], removed: ['HAS_VERSION']},
    actor_lineage: 'UNRESOLVED', semantic_lineage: 'UNRESOLVED',
    source_handles: [{handle_kind: 'GIT_ADJACENT_DIFF', from_commit_sha: frames[0].commit_sha, to_commit_sha: frames[1].commit_sha}],
  };
  const event2 = {
    event_id: 'event-rename-ambiguous', ordinal: 0, status: 'R80', old_path: 'a.txt', new_path: 'b.txt',
    old_mode: '100644', new_mode: '100644', old_object_sha: 'blob-two', new_object_sha: 'blob-three',
    lineage_id_before: 'lineage-a', lineage_id_after: 'lineage-b',
    identity_basis: 'GIT_RENAME_SIMILARITY_80_INSUFFICIENT_FOR_IDENTITY',
    classifications: ['IDENTITY_UNRESOLVED'],
    before: {path: 'a.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-two', content_identity: 'sha256:two', lineage_id: 'lineage-a'},
    after: {path: 'b.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-three', content_identity: 'sha256:three', lineage_id: 'lineage-b'},
    relation_changes: {added: [], removed: []},
    actor_lineage: 'UNRESOLVED', semantic_lineage: 'UNRESOLVED',
    source_handles: [{handle_kind: 'GIT_ADJACENT_DIFF', from_commit_sha: frames[1].commit_sha, to_commit_sha: frames[2].commit_sha}],
  };
  const transitions = [
    {transition_id: 'transition-01', transition_index: 0, from_frame_id: 'frame-0', to_frame_id: 'frame-1', from_commit_sha: frames[0].commit_sha, to_commit_sha: frames[1].commit_sha, events: [event1], event_count: 1, git_authorship: frames[1].git_author, seat_actor: 'UNRESOLVED', semantic_cause: 'UNRESOLVED', source_handles: [{handle_kind: 'GIT_COMMIT'}]},
    {transition_id: 'transition-12', transition_index: 1, from_frame_id: 'frame-1', to_frame_id: 'frame-2', from_commit_sha: frames[1].commit_sha, to_commit_sha: frames[2].commit_sha, events: [event2], event_count: 1, git_authorship: frames[2].git_author, seat_actor: 'UNRESOLVED', semantic_cause: 'UNRESOLVED', source_handles: [{handle_kind: 'GIT_COMMIT'}]},
  ];
  const cursorPayload = {consumer: 'labboib', cursor_state: 'POSITIONED', last_seen_event_id: 'CE-1', bootstrap_mode: 'FROM_HEAD'};
  const seatPayload = {schema_version: 'temporal_seat_manifest_v0', seat_id: 'LABBOIB', consumer_id: 'labboib', cursor_ref: 'continuity/cursors/labboib.json', trigger: {state: 'UNBOUND'}, occupant: {binding: 'UNBOUND'}, authority_effect: 'NONE_BY_MANIFEST', execution_effect: 'NONE_BY_MANIFEST'};
  return {
    object_type: 'REPOSITORY_TEMPORAL_LINEAGE_V0', repository_identity: 'Example/Temporal',
    requested_ref: 'HEAD', source_branch: 'candidate', source_commit: frames[2].commit_sha,
    authority_effect: 'NONE', execution_effect: 'NONE', control_effect: 'NONE',
    claim_ceiling: 'mechanical history only', frames, transitions,
    initial_entries: [{path: 'a.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-one', content_identity: 'sha256:one', lineage_id: 'lineage-a'}],
    actor_source_versions: [
      {source_version_id: 'cursor-v1', source_kind: 'CURSOR_SOURCE', path: 'continuity/cursors/labboib.json', start_frame_index: 1, end_frame_index_exclusive: null, git_object_sha: 'cursor-blob', content_identity: 'sha256:cursor', admission_standing: 'SOURCE_BOUND', payload: cursorPayload},
      {source_version_id: 'seat-v1', source_kind: 'SEAT_SOURCE', path: 'continuity/seats/labboib.json', start_frame_index: 1, end_frame_index_exclusive: null, git_object_sha: 'seat-blob', content_identity: 'sha256:seat', admission_standing: 'SOURCE_BOUND', payload: seatPayload},
    ],
    wound_replay: {
      wound_id: 'wound-1', family: 'PATH_IDENTITY != CONTENT_IDENTITY', target_path: 'a.txt',
      claim_ceiling: 'mechanical only',
      steps: [{step_id: 'step-1', transition_id: 'transition-01', event_id: 'event-content', from_frame_id: 'frame-0', to_frame_id: 'frame-1', mechanical_diff: event1, distinctions: [{classification: 'CONTENT_CHANGED', source_handles: event1.source_handles}, {classification: 'SEAT_ACTOR_UNRESOLVED', source_handles: [{handle_kind: 'ABSENCE_IN_ADMITTED_TRANSITION_EVIDENCE'}]}], actor_lineage: 'UNRESOLVED', semantic_lineage: 'UNRESOLVED'}],
    },
  };
}

test('T01 same exact commit reconstructs the same source frame', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  assert.deepEqual(reconstructTemporalFrame(lineage, 1).source, reconstructTemporalFrame(lineage, 1).source);
});

test('T02 adjacent transition ledger is deterministic and exact-frame bound', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const first = buildTransitionEmissionLedger(reconstructTemporalFrame(lineage, 1));
  const second = buildTransitionEmissionLedger(reconstructTemporalFrame(lineage, 1));
  assert.deepEqual(first, second);
  assert.equal(first.events[0].from_frame_id, 'frame-0');
  assert.equal(first.events[0].to_frame_id, 'frame-1');
});

test('T03 initial source order does not change frame identity or addressed object identity', () => {
  const source = sourceFixture();
  source.initial_entries.push({path: 'z.txt', git_mode: '100644', git_object_type: 'blob', git_object_sha: 'blob-z', content_identity: 'sha256:z', lineage_id: 'lineage-z'});
  const shuffled = structuredClone(source);
  shuffled.initial_entries.reverse();
  const left = reconstructTemporalFrame(buildTemporalLineageModel(source), 0);
  const right = reconstructTemporalFrame(buildTemporalLineageModel(shuffled), 0);
  assert.equal(left.source.temporal_frame_id, right.source.temporal_frame_id);
  assert.deepEqual(left.objects.map((item) => item.object_id).sort(), right.objects.map((item) => item.object_id).sort());
});

test('T04 unsupported rename identity is not persisted', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const before = reconstructTemporalFrame(lineage, 1);
  const after = reconstructTemporalFrame(lineage, 2);
  assert.ok(findObjectByTemporalIdentity(before, 'lineage-a'));
  assert.equal(findObjectByTemporalIdentity(after, 'lineage-a'), null);
  assert.ok(findObjectByTemporalIdentity(after, 'lineage-b'));
  assert.equal(lineage.transitions[1].events[0].classifications.includes('PATH_CHANGED'), false);
});

test('T05 missing historical selection becomes IDENTITY_UNRESOLVED rather than synthetic persistence', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  let model = reconstructTemporalFrame(lineage, 1);
  const file = findObjectByTemporalIdentity(model, 'lineage-a');
  model = selectRepositoryObject(model, file.object_id);
  let state = recordTemporalSelection(createTemporalOperatorState(lineage, model), file);
  const moved = moveTemporalFrame(state, lineage, 2, model);
  assert.equal(moved.state.selectionStanding, 'IDENTITY_UNRESOLVED');
  assert.equal(moved.state.missingSelection.temporalIdentity, 'lineage-a');
});

test('T06-T07 no emission lacks a source-supported adjacent transition', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  assert.equal(buildTransitionEmissionLedger(reconstructTemporalFrame(lineage, 0)).events.length, 0);
  const ledger = buildTransitionEmissionLedger(reconstructTemporalFrame(lineage, 1));
  assert.ok(ledger.events.every((item) => item.from_frame_id && item.to_frame_id && item.source_handles.length));
});

test('T08 aggregation preserves every underlying event identity', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const ledger = buildTransitionEmissionLedger(reconstructTemporalFrame(lineage, 1));
  for (const regime of ['LOCAL', 'MID', 'GLOBAL']) {
    const ids = aggregateTransitionEmissions(ledger, regime).flatMap((item) => item.event_ids).sort();
    assert.deepEqual(ids, ledger.events.map((item) => item.event_id).sort());
  }
});

test('A01-A02 seat and cursor exist only when their exact sources are active', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const early = reconstructTemporalFrame(lineage, 0);
  const later = reconstructTemporalFrame(lineage, 1);
  assert.equal(early.objects.some((item) => item.object_kind === 'seat' || item.object_kind === 'cursor'), false);
  assert.equal(later.objects.filter((item) => item.object_kind === 'seat').length, 1);
  assert.equal(later.objects.filter((item) => item.object_kind === 'cursor').length, 1);
  assert.ok(later.source.relations.some((item) => item.relation === 'SEAT_HAS_CURSOR'));
});

test('A03-A04 Git author remains metadata and missing actor provenance remains unresolved', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const model = reconstructTemporalFrame(lineage, 1);
  const ledger = buildTransitionEmissionLedger(model);
  assert.equal(model.temporalContext.frame.git_author.standing, 'GIT_METADATA_ONLY');
  assert.equal(ledger.events[0].actor_lineage, 'UNRESOLVED');
  assert.notEqual(model.temporalContext.frame.git_author.name, model.objects.find((item) => item.object_kind === 'seat').seat_id);
});

test('A05 actor toggle preserves every repository object identity', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const model = reconstructTemporalFrame(lineage, 1);
  const before = model.objects.filter((item) => !['seat', 'cursor'].includes(item.object_kind)).map((item) => item.object_id);
  let state = createTemporalOperatorState(lineage, model);
  state = toggleActorLayer(state);
  state = toggleActorLayer(state);
  const after = model.objects.filter((item) => !['seat', 'cursor'].includes(item.object_kind)).map((item) => item.object_id);
  assert.deepEqual(after, before);
  assert.equal(state.actorLayer, false);
});

test('W01-W04 wound replay retains exact frames, challenge handles, and honest gaps', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const step = lineage.woundReplay.steps[0];
  assert.ok(lineage.frameById[step.from_frame_id]);
  assert.ok(lineage.frameById[step.to_frame_id]);
  assert.ok(step.distinctions.every((item) => item.source_handles.length));
  assert.equal(step.semantic_lineage, 'UNRESOLVED');
  assert.equal(step.actor_lineage, 'UNRESOLVED');
});

test('render exposes temporal, actor, wound, authorship, and no-causation controls', () => {
  const lineage = buildTemporalLineageModel(sourceFixture());
  const model = reconstructTemporalFrame(lineage, 1);
  const field = buildGeometricRepositoryField(model);
  const state = createTemporalOperatorState(lineage, model);
  const ledger = buildTransitionEmissionLedger(model);
  const html = renderRepositoryFabric(model, field, {}, null, null, {lineage, state, emissionLedger: ledger});
  for (const phrase of ['TEMPORAL LINEAGE OPERATOR V0', 'GIT_AUTHOR - METADATA ONLY', 'SHOW SEATS / CURSORS', 'REPLAY PATH IDENTITY WOUND', 'SEAT_ACTOR']) {
    assert.match(html, new RegExp(phrase));
  }
});

test('implementation introduces no authority, execution, control transport, or causal inference', async () => {
  const [modelSource, appSource] = await Promise.all([
    readFile(new URL('src/cockpit/observer/repository_temporal_lineage.mjs', ROOT), 'utf8'),
    readFile(new URL('src/cockpit/observer/repository_fabric_app.mjs', ROOT), 'utf8'),
  ]);
  assert.doesNotMatch(`${modelSource}\n${appSource}`, /EventSource|WebSocket|startControlAdapter|invoke_lmstudio|evaluate_branch/);
  assert.doesNotMatch(appSource, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  const source = sourceFixture();
  assert.equal(source.authority_effect, 'NONE');
  assert.equal(source.execution_effect, 'NONE');
  assert.equal(source.control_effect, 'NONE');
});
