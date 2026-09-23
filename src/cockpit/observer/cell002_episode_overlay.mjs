import {
  CELL002_SOURCE_ARTIFACTS,
  buildCell002Specimen,
} from './cell002_model.mjs';

export const CELL002_EPISODE_TRACE_PATH =
  '../../../traces/authority_membrane_security_cell_002_installed_qualification_result.json';

export const SCIENTIFIC_CLASSIFICATIONS = Object.freeze([
  'CHANGED',
  'HELD_FIXED',
  'WITNESSED',
  'UNRESOLVED',
  'OUT_OF_SCOPE',
  'UNCLASSIFIED',
]);

const AUTHORITY_MODULE_PATH = 'src/runtime/local_authority_consumption_v0.py';
const BRIDGE_PATH = 'docs/campaigns/authority_membrane_security_001/cell002_bound_installed_bridge_candidate/bridge.py';
const HARNESS_PATH = 'tests/security/run_installed_authority_membrane_cell002.py';
const TRACE_PATH = 'traces/authority_membrane_security_cell_002_installed_qualification_result.json';
const RESULT_PATH = 'docs/campaigns/authority_membrane_security_001/CELL_002_INSTALLED_QUALIFICATION_RESULT.md';
const FRAME_PATH = 'docs/campaigns/authority_membrane_security_001/COCKPIT_CELL002_PRESSURE_SPECIMEN_FRAME.md';
const ADJUDICATION_PATH = 'docs/campaigns/authority_membrane_security_001/CELL_002_THREE_WAY_ADJUDICATION_001.md';

export const CELL002_EPISODE_SOURCE_PATHS = Object.freeze([
  AUTHORITY_MODULE_PATH,
  BRIDGE_PATH,
  HARNESS_PATH,
  TRACE_PATH,
  RESULT_PATH,
  FRAME_PATH,
  ADJUDICATION_PATH,
]);

function pointerValue(source, pointer) {
  if (pointer === '') return source;
  let current = source;
  for (const encoded of pointer.split('/').slice(1)) {
    const key = encoded.replaceAll('~1', '/').replaceAll('~0', '~');
    if (current === null || typeof current !== 'object' || !(key in current)) {
      return undefined;
    }
    current = current[key];
  }
  return current;
}

function sourceObjectsForPath(repositoryModel, path) {
  const file = repositoryModel.objects.find(
    (object) => object.object_kind === 'file' && object.path === path,
  );
  const version = repositoryModel.objects.find(
    (object) => object.object_kind === 'file_version' && object.path === path,
  );
  return {file, version};
}

function exactSourceHandle(pair, role) {
  const version = pair.version;
  return {
    handleKind: 'REPOSITORY_FILE_VERSION',
    role,
    objectId: version?.object_id || null,
    path: version?.path || null,
    address: version?.address || null,
    contentIdentity: version?.content_identity || null,
    gitBlobIdentity: version?.git_blob_identity || null,
  };
}

function traceFieldHandle(tracePair, trace, jsonPointer) {
  const observedValue = pointerValue(trace, jsonPointer);
  return {
    ...exactSourceHandle(tracePair, 'PRIMARY_WITNESS'),
    handleKind: 'TRACE_FIELD',
    jsonPointer,
    observedValue: observedValue === undefined ? 'UNAVAILABLE' : observedValue,
    supportAvailable: observedValue !== undefined,
  };
}

function addClassification(model, specification) {
  const targetPairs = specification.targetPaths.map(
    (path) => model.sourcePairsByPath[path],
  );
  const targetObjectIds = targetPairs.flatMap((pair) => [
    pair?.file?.object_id,
    pair?.version?.object_id,
  ]).filter(Boolean);
  const traceHandles = specification.tracePointers.map(
    (pointer) => traceFieldHandle(model.tracePair, model.sourceTrace, pointer),
  );
  const sourceHandles = [
    ...targetPairs.filter(Boolean).map((pair) => exactSourceHandle(pair, 'TARGET_SOURCE')),
    ...traceHandles,
  ];
  const sourceClosure = targetPairs.every((pair) => pair?.file && pair?.version);
  const traceClosure = traceHandles.every((handle) => handle.supportAvailable);
  const additionalSupport = specification.supportCheck
    ? specification.supportCheck(model, targetPairs)
    : true;
  const supported = sourceClosure && traceClosure && additionalSupport;
  const category = supported ? specification.category : 'UNRESOLVED';
  const classification = {
    classificationId: `${model.episodeId}:classification:${specification.id}`,
    category,
    intendedCategory: specification.category,
    title: specification.title,
    targetObjectIds,
    targetPaths: [...specification.targetPaths],
    sourceHandles,
    whatChanged: [...specification.whatChanged],
    whatDidNotChange: [...specification.whatDidNotChange],
    claimCeiling: specification.claimCeiling || model.claimCeiling,
    unresolved: supported
      ? [...specification.unresolved]
      : [`source support incomplete for intended ${specification.category}`, ...specification.unresolved],
    supportStatus: supported ? 'SOURCE_SUPPORTED' : 'SOURCE_SUPPORT_INCOMPLETE',
    sourceObjectChanged: false,
  };
  model.classifications.push(classification);
  for (const objectId of targetObjectIds) {
    if (!model.classificationByObjectId[objectId]) {
      model.classificationByObjectId[objectId] = [];
    }
    model.classificationByObjectId[objectId].push(classification);
  }
  return classification;
}

function identityMatch(pair, expected) {
  return pair?.version?.content_identity === `sha256:${expected}`;
}

export function buildCell002EpisodeOverlay(repositoryModel, sourceTrace) {
  const specimen = buildCell002Specimen(sourceTrace);
  const sourcePairsByPath = Object.fromEntries(
    CELL002_EPISODE_SOURCE_PATHS.map((path) => [
      path,
      sourceObjectsForPath(repositoryModel, path),
    ]),
  );
  const tracePair = sourcePairsByPath[TRACE_PATH];
  const expectedTraceHash = CELL002_SOURCE_ARTIFACTS.find(
    (artifact) => artifact.id === 'qualification-trace',
  )?.sha256;
  if (!tracePair?.version || tracePair.version.content_identity !== `sha256:${expectedTraceHash}`) {
    throw new TypeError('Cell 002 trace identity does not match its admitted source contract');
  }

  const episodeId = [
    'episode',
    'AUTHORITY_MEMBRANE_SECURITY_CELL_002',
    repositoryModel.source.source_commit,
    tracePair.version.content_identity,
  ].join(':');
  const episode = {
    objectType: 'EPISODE_SCIENTIFIC_OVERLAY_V0',
    episodeId,
    episodeAddress: {
      substrate: 'repository_episode',
      repository: repositoryModel.source.repository_identity,
      commit: repositoryModel.source.source_commit,
      operator: 'EPISODE_SCIENTIFIC_OVERLAY_V0',
      episode: 'AUTHORITY_MEMBRANE_SECURITY_CELL_002',
      primaryWitnessContentIdentity: tracePair.version.content_identity,
    },
    title: 'Cell 002 - principal-bound one-shot authority pressure',
    sourceTrace,
    specimen,
    sourcePairsByPath,
    tracePair,
    sourceArtifacts: CELL002_EPISODE_SOURCE_PATHS.map((path) => ({
      path,
      ...exactSourceHandle(sourcePairsByPath[path], 'ADMITTED_EPISODE_SOURCE'),
    })),
    admittedObjectIds: new Set(),
    classifications: [],
    classificationByObjectId: Object.create(null),
    claimCeiling: sourceTrace.standing_candidate.claim_ceiling,
    unresolvedExternalCoordinates: [
      {
        kind: 'INSTALLED_POLICY_COORDINATE',
        path: sourceTrace.installed_coordinates_before.installed_policy_path,
        sha256: sourceTrace.installed_coordinates_before.installed_policy_sha256,
        atlasStanding: 'NO_CORRESPONDING_REPOSITORY_OBJECT',
      },
    ],
  };
  for (const pair of Object.values(sourcePairsByPath)) {
    if (pair.file) episode.admittedObjectIds.add(pair.file.object_id);
    if (pair.version) episode.admittedObjectIds.add(pair.version.object_id);
  }

  addClassification(episode, {
    id: 'authority-state-transition', category: 'CHANGED',
    title: 'Recorded authority state changed through one-shot consumption',
    targetPaths: [AUTHORITY_MODULE_PATH],
    tracePointers: [
      '/control/status_before', '/control/status_after',
      '/control/remaining_uses_before', '/control/remaining_uses_after',
    ],
    whatChanged: ['episode authority state ACTIVE -> CONSUMING -> CONSUMED', 'remaining_uses 1 -> 0'],
    whatDidNotChange: ['the repository source file is not claimed to have changed during the episode'],
    unresolved: ['crash recovery from CONSUMING', 'crash-safe exactly-once'],
  });
  addClassification(episode, {
    id: 'authority-module-held-fixed', category: 'HELD_FIXED',
    title: 'Authority-module bytes held fixed at the tested installed coordinate',
    targetPaths: [AUTHORITY_MODULE_PATH],
    tracePointers: [
      '/installed_coordinates_before/installed_authority_module_sha256',
      '/installed_coordinates_after/installed_authority_module_sha256',
    ],
    supportCheck: (model, pairs) => (
      identityMatch(pairs[0], model.sourceTrace.installed_coordinates_before.installed_authority_module_sha256)
      && model.sourceTrace.installed_coordinates_before.installed_authority_module_sha256
        === model.sourceTrace.installed_coordinates_after.installed_authority_module_sha256
    ),
    whatChanged: [],
    whatDidNotChange: ['installed authority-module SHA-256', 'repository version bound to the same SHA-256'],
    unresolved: ['installed filesystem tamper resistance'],
  });
  addClassification(episode, {
    id: 'bridge-held-fixed', category: 'HELD_FIXED',
    title: 'Bridge bytes held fixed at the tested installed coordinate',
    targetPaths: [BRIDGE_PATH],
    tracePointers: [
      '/installed_coordinates_before/installed_bridge_sha256',
      '/installed_coordinates_after/installed_bridge_sha256',
    ],
    supportCheck: (model, pairs) => (
      identityMatch(pairs[0], model.sourceTrace.installed_coordinates_before.installed_bridge_sha256)
      && model.sourceTrace.installed_coordinates_before.installed_bridge_sha256
        === model.sourceTrace.installed_coordinates_after.installed_bridge_sha256
    ),
    whatChanged: [],
    whatDidNotChange: ['installed bridge SHA-256', 'repository candidate version bound to the same SHA-256'],
    unresolved: ['bridge-wide bypass resistance beyond the governed path'],
  });
  addClassification(episode, {
    id: 'reservation-and-invocation-witness', category: 'WITNESSED',
    title: 'Harness witnessed reservation before one governed boundary call',
    targetPaths: [HARNESS_PATH],
    tracePointers: ['/control/reservation_before_invocation', '/control/invocation_count', '/real_lmstudio_http_calls'],
    supportCheck: (model) => (
      model.sourceTrace.control.reservation_before_invocation === true
      && model.sourceTrace.control.invocation_count === 1
      && model.sourceTrace.real_lmstudio_http_calls === 0
    ),
    whatChanged: ['mocked governed boundary invocation count 0 -> 1'],
    whatDidNotChange: ['real LM Studio HTTP calls remained 0'],
    unresolved: ['real HTTP consequence', 'external effect'],
  });
  addClassification(episode, {
    id: 'replay-coordinates-held-fixed', category: 'HELD_FIXED',
    title: 'Exact replay retained the tested request, input, principal, model, endpoint, and policy coordinates',
    targetPaths: [TRACE_PATH],
    tracePointers: [
      '/control/request_sha256', '/exact_replay/request_sha256',
      '/control/input_sha256', '/exact_replay/input_sha256',
      '/control/principal_id', '/exact_replay/principal_id',
      '/control/model', '/exact_replay/model',
      '/control/endpoint_identity', '/exact_replay/endpoint_identity',
      '/control/installed_policy_sha256', '/exact_replay/installed_policy_sha256',
    ],
    supportCheck: (model) => [
      'request_sha256', 'input_sha256', 'principal_id', 'model',
      'endpoint_identity', 'installed_policy_sha256',
    ].every((key) => model.sourceTrace.control[key] === model.sourceTrace.exact_replay[key]),
    whatChanged: [],
    whatDidNotChange: ['request', 'input', 'declared principal', 'model', 'endpoint', 'policy SHA-256'],
    unresolved: ['principal authentication', 'hidden model configuration'],
  });
  addClassification(episode, {
    id: 'durable-pressure-witness', category: 'WITNESSED',
    title: 'Qualification trace records receipt, replay denial, principal denial, and Cell-001 rejection',
    targetPaths: [TRACE_PATH],
    tracePointers: [
      '/control/receipt_id', '/exact_replay/denial_id',
      '/wrong_declared_principal/denial_id', '/cell001_regression/reason',
    ],
    whatChanged: ['durable witness records were produced by the bounded pressure'],
    whatDidNotChange: ['current authority remained NONE after consumed replay pressure'],
    unresolved: ['independent currentness of the historical trace'],
  });
  addClassification(episode, {
    id: 'qualified-standing-witness', category: 'WITNESSED',
    title: 'Result and adjudication retain the bounded installed standing',
    targetPaths: [RESULT_PATH, ADJUDICATION_PATH],
    tracePointers: ['/all_four_pressures_passed', '/standing_candidate/cell002_installed_executor'],
    supportCheck: (model) => model.sourceTrace.all_four_pressures_passed === true,
    whatChanged: ['bounded standing was recorded after four pressures passed'],
    whatDidNotChange: ['claim ceiling remains bounded to the tested governed path'],
    unresolved: ['current installed-source revalidation'],
  });
  addClassification(episode, {
    id: 'view-contract-witness', category: 'WITNESSED',
    title: 'Specimen frame bounds the source-backed view contract',
    targetPaths: [FRAME_PATH],
    tracePointers: ['/object_type'],
    whatChanged: [],
    whatDidNotChange: ['the view cannot promote historical evidence into live authority'],
    unresolved: ['human comprehension under the new overlay'],
  });
  addClassification(episode, {
    id: 'claim-ceiling-unresolved', category: 'UNRESOLVED',
    title: 'Qualification evidence stops at explicit unestablished boundaries',
    targetPaths: [TRACE_PATH, RESULT_PATH],
    tracePointers: ['/not_established'],
    whatChanged: [],
    whatDidNotChange: ['unestablished relations remain unestablished'],
    unresolved: [...sourceTrace.not_established],
  });

  episode.sequence = [
    {id: 'active', label: 'ACTIVE / remaining_uses=1', objectIds: episode.sourcePairsByPath[AUTHORITY_MODULE_PATH].version ? [episode.sourcePairsByPath[AUTHORITY_MODULE_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/control/status_before')]},
    {id: 'reservation', label: 'RESERVATION', objectIds: episode.sourcePairsByPath[HARNESS_PATH].version ? [episode.sourcePairsByPath[HARNESS_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/control/reservation_id')]},
    {id: 'consuming', label: 'CONSUMING / remaining_uses=0', objectIds: episode.sourcePairsByPath[AUTHORITY_MODULE_PATH].version ? [episode.sourcePairsByPath[AUTHORITY_MODULE_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/control/remaining_uses_after')]},
    {id: 'invoke', label: 'INVOCATION BOUNDARY', objectIds: episode.sourcePairsByPath[BRIDGE_PATH].version ? [episode.sourcePairsByPath[BRIDGE_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/control/invocation_count')]},
    {id: 'consumed', label: 'CONSUMED', objectIds: episode.sourcePairsByPath[TRACE_PATH].version ? [episode.sourcePairsByPath[TRACE_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/control/status_after')]},
    {id: 'replay', label: 'REPLAY ATTEMPT', objectIds: episode.sourcePairsByPath[HARNESS_PATH].version ? [episode.sourcePairsByPath[HARNESS_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/exact_replay/same_capability_object_reference_reused')]},
    {id: 'denied', label: 'DENY / AUTHORITY_EXHAUSTED', objectIds: episode.sourcePairsByPath[TRACE_PATH].version ? [episode.sourcePairsByPath[TRACE_PATH].version.object_id] : [], sourceHandles: [traceFieldHandle(tracePair, sourceTrace, '/exact_replay/reason')]},
  ];
  episode.defaultClassificationId = episode.classifications[0].classificationId;
  return episode;
}

export function classificationsForObject(episode, object) {
  const explicit = episode.classificationByObjectId[object.object_id];
  if (explicit?.length) return explicit;
  if (episode.admittedObjectIds.has(object.object_id)) {
    return [{
      classificationId: `${episode.episodeId}:unclassified:${object.object_id}`,
      category: 'UNCLASSIFIED',
      intendedCategory: 'UNCLASSIFIED',
      title: 'Admitted episode source has no supported scientific classification',
      targetObjectIds: [object.object_id],
      targetPaths: [object.path],
      sourceHandles: [exactSourceHandle({version: object.object_kind === 'file_version' ? object : null}, 'ADMITTED_SOURCE')],
      whatChanged: [],
      whatDidNotChange: [],
      claimCeiling: episode.claimCeiling,
      unresolved: ['classification basis absent'],
      supportStatus: 'SOURCE_SUPPORT_INCOMPLETE',
      sourceObjectChanged: false,
    }];
  }
  return [{
    classificationId: `${episode.episodeId}:out-of-scope:${object.object_id}`,
    category: 'OUT_OF_SCOPE',
    intendedCategory: 'OUT_OF_SCOPE',
    title: 'Source object is outside the admitted Cell-002 episode basis',
    targetObjectIds: [object.object_id],
    targetPaths: [object.path || '/'],
    sourceHandles: [{
      handleKind: 'EPISODE_SCOPE_MEMBERSHIP',
      episodeId: episode.episodeId,
      episodeAddress: episode.episodeAddress,
      objectId: object.object_id,
      admitted: false,
    }],
    whatChanged: [],
    whatDidNotChange: ['OUT_OF_SCOPE does not mean held fixed or scientifically controlled'],
    claimCeiling: episode.claimCeiling,
    unresolved: [],
    supportStatus: 'SOURCE_SUPPORTED',
    sourceObjectChanged: false,
  }];
}

export function createAtlasOperatorState(episode) {
  return {
    base: 'STRUCTURAL',
    overlay: 'NONE',
    episodeId: episode?.episodeId || null,
    episodeStep: 0,
    inspectorCollapsed: false,
  };
}

export function toggleScientificEpisode(state, episode) {
  if (!episode || state.episodeId !== episode.episodeId) return state;
  return {
    ...state,
    overlay: state.overlay === 'SCIENTIFIC_EPISODE' ? 'NONE' : 'SCIENTIFIC_EPISODE',
  };
}

export function setEpisodeStep(state, episode, step) {
  if (!episode || state.episodeId !== episode.episodeId) return state;
  const next = Math.max(0, Math.min(episode.sequence.length - 1, Number(step)));
  return Number.isFinite(next) ? {...state, episodeStep: next} : state;
}

export function toggleAtlasInspector(state) {
  return {...state, inspectorCollapsed: !state.inspectorCollapsed};
}
