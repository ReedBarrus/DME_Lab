import {buildRepositoryFabricModel, selectRepositoryObject} from './repository_fabric_model.mjs';

export const REPOSITORY_TEMPORAL_LINEAGE_PATH = '../../../generated/repository_temporal_lineage.json';

const TEMPORAL_CLASSIFICATIONS = new Set([
  'PERSISTED', 'APPEARED', 'DISAPPEARED', 'CONTENT_CHANGED', 'PATH_CHANGED',
  'IDENTITY_UNRESOLVED', 'RELATION_ADDED', 'RELATION_REMOVED',
]);

function required(value, key, scope) {
  if (!value || typeof value !== 'object' || !(key in value)) {
    throw new TypeError(`temporal lineage missing ${scope}.${key}`);
  }
  return value[key];
}

function clamp(value, minimum, maximum) {
  return Math.max(minimum, Math.min(maximum, Number(value)));
}

function safeId(value) {
  return encodeURIComponent(String(value)).replaceAll('%', '_');
}

function parentPath(path) {
  const index = path.lastIndexOf('/');
  return index < 0 ? '' : path.slice(0, index);
}

function relation(sourceId, kind, targetId = null, targetAddress = null, derivation = 'GIT_MECHANICAL') {
  return {
    relation_id: `temporal-relation:${safeId(sourceId)}:${kind}:${safeId(targetId || JSON.stringify(targetAddress))}`,
    source_id: sourceId,
    relation: kind,
    target_id: targetId,
    target_address: targetAddress,
    derivation,
  };
}

export function buildTemporalLineageModel(source) {
  if (!source || source.object_type !== 'REPOSITORY_TEMPORAL_LINEAGE_V0') {
    throw new TypeError('unsupported repository temporal lineage source');
  }
  const frames = required(source, 'frames', 'source');
  const transitions = required(source, 'transitions', 'source');
  const initialEntries = required(source, 'initial_entries', 'source');
  const actorSourceVersions = required(source, 'actor_source_versions', 'source');
  if (!Array.isArray(frames) || !Array.isArray(transitions) || !Array.isArray(initialEntries)
      || !Array.isArray(actorSourceVersions) || !frames.length) {
    throw new TypeError('temporal lineage arrays are unavailable or empty');
  }
  if (transitions.length !== frames.length - 1) {
    throw new TypeError('temporal lineage is not adjacent-frame closed');
  }
  const frameById = Object.create(null);
  frames.forEach((frame, index) => {
    if (frame.frame_index !== index || frameById[frame.frame_id]) {
      throw new TypeError('temporal frame order or identity is invalid');
    }
    frameById[frame.frame_id] = frame;
  });
  const transitionById = Object.create(null);
  transitions.forEach((transition, index) => {
    if (transition.transition_index !== index
        || transition.from_frame_id !== frames[index].frame_id
        || transition.to_frame_id !== frames[index + 1].frame_id) {
      throw new TypeError('temporal transition does not bind adjacent exact frames');
    }
    if (transitionById[transition.transition_id]) throw new TypeError('duplicate temporal transition');
    for (const event of transition.events) {
      if (!event.classifications.every((item) => TEMPORAL_CLASSIFICATIONS.has(item))) {
        throw new TypeError('unsupported temporal classification');
      }
      if (!event.source_handles?.length) throw new TypeError('transition event lacks source handles');
    }
    transitionById[transition.transition_id] = transition;
  });
  return {
    source,
    frames,
    frameById,
    transitions,
    transitionById,
    initialEntries,
    actorSourceVersions,
    woundReplay: required(source, 'wound_replay', 'source'),
  };
}

function entriesAtFrame(lineage, frameIndex) {
  const state = new Map(lineage.initialEntries.map((entry) => [entry.path, {...entry}]));
  for (let index = 0; index < frameIndex; index += 1) {
    const transition = lineage.transitions[index];
    for (const event of transition.events) {
      if (event.old_path) state.delete(event.old_path);
      if (event.new_path && event.after) state.set(event.new_path, {...event.after});
    }
  }
  return state;
}

function activeActorSources(lineage, frameIndex) {
  return lineage.actorSourceVersions.filter((version) => (
    version.admission_standing === 'SOURCE_BOUND'
    && version.start_frame_index <= frameIndex
    && (version.end_frame_index_exclusive === null || frameIndex < version.end_frame_index_exclusive)
  ));
}

function commonObject(frame, source, objectId, objectKind, path, parent, temporalIdentity) {
  return {
    object_id: objectId,
    object_kind: objectKind,
    repository_identity: source.repository_identity,
    source_commit: frame.commit_sha,
    source_ref: source.requested_ref,
    source_branch: source.source_branch,
    path,
    parent_path: parent,
    path_identity: {
      substrate: 'repo_path', repository: source.repository_identity,
      path, object_kind: objectKind,
    },
    temporal_identity: temporalIdentity,
    existence_standing: 'EXISTS_AT_SOURCE_COMMIT',
    semantic_standing: 'UNINTERPRETED',
    typed_projections: [],
  };
}

function actorObjects(lineage, frame, frameIndex, repositoryId) {
  const objects = [];
  const relations = [];
  const sourceVersions = activeActorSources(lineage, frameIndex);
  const cursorByPath = Object.create(null);
  for (const sourceVersion of sourceVersions) {
    if (sourceVersion.source_kind !== 'CURSOR_SOURCE') continue;
    const payload = sourceVersion.payload;
    const objectId = `temporal-cursor:${safeId(payload.consumer)}`;
    const path = `@cursor/${payload.consumer}`;
    const object = {
      ...commonObject(frame, lineage.source, objectId, 'cursor', path, '', `cursor:${payload.consumer}`),
      actor_standing: 'DECLARED_OPERATIONAL_LINEAGE',
      consumer_id: payload.consumer,
      cursor_state: payload.cursor_state,
      last_seen_event_id: payload.last_seen_event_id,
      bootstrap_mode: payload.bootstrap_mode,
      source_artifact: {
        path: sourceVersion.path,
        git_object_sha: sourceVersion.git_object_sha,
        content_identity: sourceVersion.content_identity,
      },
      content_identity: sourceVersion.content_identity,
      git_blob_identity: sourceVersion.git_object_sha,
      git_tree_identity: null,
      address: {
        substrate: 'continuity_cursor_projection', repository: lineage.source.repository_identity,
        commit: frame.commit_sha, consumer: payload.consumer, source_path: sourceVersion.path,
      },
    };
    objects.push(object);
    cursorByPath[sourceVersion.path] = object;
    relations.push(relation(repositoryId, 'PROJECTS_ACTOR', objectId, null, 'SOURCE_BOUND_PROJECTION'));
    if (payload.last_seen_event_id) {
      relations.push(relation(
        objectId,
        'CURSOR_REFERENCES_STATE',
        null,
        {
          substrate: 'continuity_event', repository: lineage.source.repository_identity,
          event_id: payload.last_seen_event_id,
          source_path: 'continuity/events.jsonl',
        },
        'DECLARED_CURSOR_COORDINATE',
      ));
    }
  }
  for (const sourceVersion of sourceVersions) {
    if (sourceVersion.source_kind !== 'SEAT_SOURCE') continue;
    const payload = sourceVersion.payload;
    const objectId = `temporal-seat:${safeId(payload.seat_id)}`;
    const path = `@seat/${payload.seat_id}`;
    const object = {
      ...commonObject(frame, lineage.source, objectId, 'seat', path, '', `seat:${payload.seat_id}`),
      actor_standing: 'DECLARED_OPERATIONAL_LINEAGE',
      seat_id: payload.seat_id,
      consumer_id: payload.consumer_id,
      seat_class: payload.seat_class,
      trigger_state: payload.trigger?.state ?? 'UNRESOLVED',
      occupant_binding: payload.occupant?.binding ?? 'UNRESOLVED',
      authority_effect: payload.authority_effect,
      execution_effect: payload.execution_effect,
      source_artifact: {
        path: sourceVersion.path,
        git_object_sha: sourceVersion.git_object_sha,
        content_identity: sourceVersion.content_identity,
      },
      content_identity: sourceVersion.content_identity,
      git_blob_identity: sourceVersion.git_object_sha,
      git_tree_identity: null,
      address: {
        substrate: 'continuity_seat_projection', repository: lineage.source.repository_identity,
        commit: frame.commit_sha, seat_id: payload.seat_id, source_path: sourceVersion.path,
      },
    };
    objects.push(object);
    relations.push(relation(repositoryId, 'PROJECTS_ACTOR', objectId, null, 'SOURCE_BOUND_PROJECTION'));
    const cursor = cursorByPath[payload.cursor_ref];
    if (cursor) {
      relations.push(relation(objectId, 'SEAT_HAS_CURSOR', cursor.object_id, null, 'DECLARED_SEAT_MANIFEST'));
    }
  }
  return {objects, relations, sourceVersions};
}

export function reconstructTemporalFrame(lineage, requestedFrameIndex) {
  const frameIndex = clamp(requestedFrameIndex, 0, lineage.frames.length - 1);
  const frame = lineage.frames[frameIndex];
  const entries = entriesAtFrame(lineage, frameIndex);
  const repositoryId = `temporal-repository:${safeId(lineage.source.repository_identity)}`;
  const repository = {
    ...commonObject(frame, lineage.source, repositoryId, 'repository', '', null, `repository:${lineage.source.repository_identity}`),
    content_identity: null,
    git_blob_identity: null,
    git_tree_identity: frame.tree_sha,
    semantic_standing: 'UNINTERPRETED',
    address: {
      substrate: 'repo', repository: lineage.source.repository_identity,
      commit: frame.commit_sha, tree: frame.tree_sha, path: '', object_kind: 'repository',
    },
  };
  const objects = [repository];
  const relations = [];
  const directoryPaths = new Set();
  for (const path of entries.keys()) {
    let parent = parentPath(path);
    while (parent) {
      directoryPaths.add(parent);
      parent = parentPath(parent);
    }
  }
  const directoryId = (path) => `temporal-directory:${safeId(lineage.source.repository_identity)}:${safeId(path)}`;
  for (const path of [...directoryPaths].sort((a, b) => a.split('/').length - b.split('/').length || a.localeCompare(b))) {
    const parent = parentPath(path);
    const objectId = directoryId(path);
    objects.push({
      ...commonObject(frame, lineage.source, objectId, 'directory', path, parent, `directory:${path}`),
      content_identity: null, git_blob_identity: null, git_tree_identity: null,
      address: {
        substrate: 'repo', repository: lineage.source.repository_identity,
        commit: frame.commit_sha, path, object_kind: 'directory',
      },
    });
    relations.push(relation(parent ? directoryId(parent) : repositoryId, 'CONTAINS', objectId));
  }
  for (const entry of [...entries.values()].sort((a, b) => a.path.localeCompare(b.path))) {
    const fileId = `temporal-file:${safeId(entry.lineage_id)}`;
    const versionId = `temporal-version:${safeId(frame.commit_sha)}:${safeId(entry.lineage_id)}:${safeId(entry.git_object_sha)}`;
    const parent = parentPath(entry.path);
    objects.push({
      ...commonObject(frame, lineage.source, fileId, 'file', entry.path, parent, entry.lineage_id),
      content_identity: null, git_blob_identity: null, git_tree_identity: null,
      git_mode: entry.git_mode, git_object_type: entry.git_object_type,
      address: {
        substrate: 'repo', repository: lineage.source.repository_identity,
        commit: frame.commit_sha, path: entry.path, object_kind: 'file',
      },
    });
    objects.push({
      ...commonObject(frame, lineage.source, versionId, 'file_version', entry.path, parent, `version:${entry.lineage_id}:${entry.git_object_sha}`),
      content_identity: entry.content_identity,
      git_blob_identity: entry.git_object_type === 'blob' ? entry.git_object_sha : null,
      git_tree_identity: null,
      git_mode: entry.git_mode, git_object_type: entry.git_object_type,
      address: {
        substrate: 'repo', repository: lineage.source.repository_identity,
        commit: frame.commit_sha, path: entry.path, object_kind: 'file_version',
        git_object_sha: entry.git_object_sha,
      },
    });
    relations.push(
      relation(parent ? directoryId(parent) : repositoryId, 'CONTAINS', fileId),
      relation(fileId, 'HAS_VERSION', versionId),
      relation(versionId, 'MATERIALIZED_AT', null, {substrate: 'git', commit: frame.commit_sha}),
    );
  }
  const actors = actorObjects(lineage, frame, frameIndex, repositoryId);
  objects.push(...actors.objects);
  relations.push(...actors.relations);
  const source = {
    object_type: 'REPOSITORY_ADDRESS_FABRIC_V0',
    projection_standing: 'DERIVED_READ_ONLY_TEMPORAL_FRAME',
    repository_identity: lineage.source.repository_identity,
    requested_ref: lineage.source.requested_ref,
    source_branch: lineage.source.source_branch,
    source_commit: frame.commit_sha,
    source_tree: frame.tree_sha,
    layout_identity: lineage.source.repository_identity,
    temporal_frame_id: frame.frame_id,
    temporal_frame_index: frameIndex,
    temporal_frame_count: lineage.frames.length,
    git_author: frame.git_author,
    git_committer: frame.git_committer,
    authority_effect: 'NONE', execution_effect: 'NONE', control_effect: 'NONE',
    objects,
    relations,
    claim_ceiling: lineage.source.claim_ceiling,
  };
  const model = buildRepositoryFabricModel(source);
  model.temporalContext = {
    frameIndex,
    frame,
    incomingTransition: frameIndex ? lineage.transitions[frameIndex - 1] : null,
    activeActorSources: actors.sourceVersions,
  };
  return model;
}

export function temporalIdentityForObject(object) {
  return object?.temporal_identity || null;
}

export function findObjectByTemporalIdentity(model, temporalIdentity) {
  return model.objects.find((object) => object.temporal_identity === temporalIdentity) || null;
}

export function createTemporalOperatorState(lineage, initialModel) {
  const selected = initialModel.objectById[initialModel.selectedObjectId];
  return {
    frameIndex: lineage.frames.length - 1,
    actorLayer: false,
    selectedTemporalIdentity: temporalIdentityForObject(selected),
    selectionStanding: 'PRESENT_IN_FRAME',
    missingSelection: null,
    selectedEmissionId: null,
    woundActive: false,
    woundStep: 0,
  };
}

export function moveTemporalFrame(state, lineage, nextIndex, currentModel) {
  const selected = currentModel.objectById[currentModel.selectedObjectId];
  const temporalIdentity = state.selectedTemporalIdentity || temporalIdentityForObject(selected);
  let nextModel = reconstructTemporalFrame(lineage, nextIndex);
  const survivor = findObjectByTemporalIdentity(nextModel, temporalIdentity);
  let selectionStanding = 'PRESENT_IN_FRAME';
  let missingSelection = null;
  if (survivor) {
    nextModel = selectRepositoryObject(nextModel, survivor.object_id);
  } else if (temporalIdentity) {
    selectionStanding = 'OBJECT_NOT_PRESENT_IN_FRAME';
    const transition = nextModel.temporalContext.incomingTransition;
    const unresolved = transition?.events.find((event) => (
      event.classifications.includes('IDENTITY_UNRESOLVED')
      && event.lineage_id_before === temporalIdentity
    ));
    if (unresolved) selectionStanding = 'IDENTITY_UNRESOLVED';
    missingSelection = {temporalIdentity, transitionEventId: unresolved?.event_id || null};
  }
  return {
    model: nextModel,
    state: {
      ...state,
      frameIndex: nextModel.temporalContext.frameIndex,
      selectedTemporalIdentity: temporalIdentity,
      selectionStanding,
      missingSelection,
      selectedEmissionId: null,
    },
  };
}

export function recordTemporalSelection(state, object) {
  return {
    ...state,
    selectedTemporalIdentity: temporalIdentityForObject(object),
    selectionStanding: 'PRESENT_IN_FRAME',
    missingSelection: null,
  };
}

function eventRegion(event) {
  const path = event.new_path || event.old_path || 'ROOT';
  return path.includes('/') ? path.split('/')[0] : path || 'ROOT';
}

export function buildTransitionEmissionLedger(model) {
  const transition = model.temporalContext?.incomingTransition;
  if (!transition) return {transition: null, events: [], eventById: Object.create(null)};
  const events = transition.events.map((event) => {
    const destination = event.lineage_id_after
      ? findObjectByTemporalIdentity(model, event.lineage_id_after)
      : null;
    const fallbackPath = parentPath(event.new_path || event.old_path || '');
    const fallback = findObjectByTemporalIdentity(model, `directory:${fallbackPath}`)
      || model.objects.find((object) => object.object_kind === 'repository');
    return {
      emission_id: `emission:${event.event_id}`,
      event_id: event.event_id,
      transition_id: transition.transition_id,
      from_frame_id: transition.from_frame_id,
      to_frame_id: transition.to_frame_id,
      object_id: destination?.object_id || fallback?.object_id || null,
      region: eventRegion(event),
      classifications: [...event.classifications],
      mechanical_diff: event,
      actor_lineage: event.actor_lineage || 'UNRESOLVED',
      semantic_lineage: event.semantic_lineage || 'UNRESOLVED',
      source_handles: event.source_handles,
    };
  });
  return {transition, events, eventById: Object.fromEntries(events.map((event) => [event.event_id, event]))};
}

export function emissionScaleRegime(cameraDistance) {
  if (cameraDistance < 520) return 'LOCAL';
  if (cameraDistance < 1600) return 'MID';
  return 'GLOBAL';
}

export function aggregateTransitionEmissions(ledger, regime) {
  if (regime === 'LOCAL') {
    return ledger.events.map((event) => ({
      aggregate_id: `local:${event.event_id}`,
      region: event.region,
      event_ids: [event.event_id],
      object_ids: event.object_id ? [event.object_id] : [],
      classifications: [...event.classifications],
    }));
  }
  const groups = new Map();
  for (const event of ledger.events) {
    const key = regime === 'GLOBAL'
      ? (event.classifications.includes('APPEARED') ? 'GROWTH'
        : event.classifications.includes('DISAPPEARED') ? 'CONTRACTION' : 'MUTATION')
      : event.region;
    if (!groups.has(key)) groups.set(key, {region: key, event_ids: [], object_ids: [], classifications: new Set()});
    const group = groups.get(key);
    group.event_ids.push(event.event_id);
    if (event.object_id) group.object_ids.push(event.object_id);
    event.classifications.forEach((item) => group.classifications.add(item));
  }
  return [...groups.entries()].map(([key, group]) => ({
    aggregate_id: `${regime.toLowerCase()}:${safeId(key)}:${group.event_ids.join(':')}`,
    region: group.region,
    event_ids: [...group.event_ids],
    object_ids: [...new Set(group.object_ids)],
    classifications: [...group.classifications].sort(),
  }));
}

export function toggleActorLayer(state) {
  return {...state, actorLayer: !state.actorLayer};
}

export function selectTransitionEmission(state, eventId) {
  return {...state, selectedEmissionId: eventId || null};
}

export function activateWoundReplay(state, lineage) {
  const steps = lineage.woundReplay.steps;
  if (!steps.length) return state;
  const firstFrameId = steps[0].from_frame_id;
  const frameIndex = lineage.frames.findIndex((frame) => frame.frame_id === firstFrameId);
  return {...state, woundActive: true, woundStep: 0, frameIndex: Math.max(0, frameIndex)};
}

export function setWoundStep(state, lineage, stepIndex) {
  const steps = lineage.woundReplay.steps;
  if (!steps.length) return state;
  const woundStep = clamp(stepIndex, 0, steps.length - 1);
  const frameId = steps[woundStep].to_frame_id;
  const frameIndex = lineage.frames.findIndex((frame) => frame.frame_id === frameId);
  return {...state, woundActive: true, woundStep, frameIndex};
}
