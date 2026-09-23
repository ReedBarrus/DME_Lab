export const CELL002_TRACE_PATH = '../../../traces/authority_membrane_security_cell_002_installed_qualification_result.json';

export const CELL002_SOURCE_ARTIFACTS = Object.freeze([
  {
    id: 'qualification-trace',
    path: 'traces/authority_membrane_security_cell_002_installed_qualification_result.json',
    role: 'PRIMARY WITNESS',
    sha256: 'bb6f042b854fa619f393c9d125e6bcd87a6693d74b79d7e08b212b6d35476dd1',
  },
  {
    id: 'installed-harness',
    path: 'tests/security/run_installed_authority_membrane_cell002.py',
    role: 'PRESSURE APPARATUS',
  },
  {
    id: 'qualification-result',
    path: 'docs/campaigns/authority_membrane_security_001/CELL_002_INSTALLED_QUALIFICATION_RESULT.md',
    role: 'STANDING BASIS',
  },
  {
    id: 'specimen-frame',
    path: 'docs/campaigns/authority_membrane_security_001/COCKPIT_CELL002_PRESSURE_SPECIMEN_FRAME.md',
    role: 'VIEW CONTRACT',
  },
  {
    id: 'projection-audit',
    path: 'docs/campaigns/authority_membrane_security_001/COCKPIT_EXISTING_STATE_PROJECTION_AUDIT_V0.md',
    role: 'SOURCE-BOUNDARY BASIS',
  },
]);

export const CELL002_PRIMITIVES = Object.freeze([
  'OBJECT',
  'STATE',
  'RELATION',
  'TRANSFORMATION',
  'WITNESS',
  'STANDING',
  'UNKNOWN_REGION',
]);

function required(object, key, scope) {
  if (object === null || typeof object !== 'object' || !(key in object)) {
    throw new TypeError(`Cell 002 source missing ${scope}.${key}`);
  }
  return object[key];
}

function asList(...values) {
  return values.filter((value) => value !== null && value !== undefined);
}

function sharedStanding(trace) {
  const standing = required(
    required(trace, 'standing_candidate', 'trace'),
    'cell002_installed_executor',
    'trace.standing_candidate',
  );
  const claimCeiling = required(
    trace.standing_candidate,
    'claim_ceiling',
    'trace.standing_candidate',
  );
  return {
    sourceCurrentness: {
      label: 'UNRESOLVED',
      detail: 'The admitted trace is a recorded specimen and contains no live freshness check.',
    },
    historicalStanding: {
      label: 'QUALIFIED',
      detail: standing,
    },
    currentStanding: {
      label: 'UNRESOLVED',
      detail: `${standing} is historical at the recorded basis; no live source currentness check establishes present standing.`,
    },
    currentAuthority: {
      label: 'NOT_DERIVED',
      detail: 'Temporary authority state was destroyed after pressure; no live authority state is admitted.',
    },
    historicalAuthority: {
      label: 'OBSERVED',
      detail: 'Control ended with current_authority=NONE; wrong-principal pressure preserved ACTIVE / remaining=1 in its temporary fixture.',
    },
    claimCeiling,
  };
}

function inspectorRecord(shared, record) {
  return {
    ...record,
    sourceCurrentness: shared.sourceCurrentness,
    historicalStanding: shared.historicalStanding,
    currentStanding: shared.currentStanding,
    currentAuthority: shared.currentAuthority,
    historicalAuthority: shared.historicalAuthority,
    claimCeiling: shared.claimCeiling,
    sourceArtifacts: CELL002_SOURCE_ARTIFACTS.map((source) => source.path),
  };
}

function sourceCoordinates(record) {
  return {
    capabilityId: record.capability_id,
    approvalId: record.approval_id,
    principalId: record.principal_id,
    attemptingPrincipalId: record.attempting_principal_id,
    requestSha256: record.request_sha256,
    inputSha256: record.input_sha256,
    model: record.model,
    endpoint: record.endpoint_identity,
    executorSha256: record.installed_bridge_sha256,
    authorityModuleSha256: record.installed_authority_module_sha256,
    policySha256: record.installed_policy_sha256,
  };
}

export function buildCell002Specimen(trace) {
  if (trace === null || typeof trace !== 'object' || Array.isArray(trace)) {
    throw new TypeError('Cell 002 qualification source must be a JSON object');
  }
  if (
    trace.object_type
    !== 'AUTHORITY_MEMBRANE_SECURITY_CELL_002_INSTALLED_QUALIFICATION_RESULT'
  ) {
    throw new TypeError('unsupported Cell 002 qualification source object_type');
  }

  const control = required(trace, 'control', 'trace');
  const replay = required(trace, 'exact_replay', 'trace');
  const wrong = required(trace, 'wrong_declared_principal', 'trace');
  const shared = sharedStanding(trace);
  const controlCoordinates = sourceCoordinates(control);
  const replayCoordinates = sourceCoordinates(replay);
  const wrongCoordinates = sourceCoordinates(wrong);
  const notEstablished = Array.isArray(trace.not_established)
    ? [...trace.not_established]
    : ['not_established source field missing'];

  const inspectables = [
    inspectorRecord(shared, {
      id: 'control-active',
      kind: 'OBJECT',
      title: 'Issued authority capability',
      beforeObject: control.capability_id,
      beforeState: ['status=ACTIVE', 'remaining_uses=1'],
      operator: 'STATE OBSERVATION',
      basis: 'control.status_before + control.remaining_uses_before',
      witness: control.approval_id,
      afterObject: control.capability_id,
      afterState: ['status=ACTIVE', 'remaining_uses=1'],
      whatChanged: ['authority envelope was issued after approval and revalidation'],
      whatDidNotChange: ['request, input, model, endpoint, executor, policy'],
      standingEarned: 'OBSERVED',
      unresolved: ['live current authority after the temporary fixture'],
      backward: ['request-input', 'approval'],
      forward: ['control-reserve'],
    }),
    inspectorRecord(shared, {
      id: 'control-reserve',
      kind: 'TRANSFORMATION',
      title: 'Reserve the one available use',
      beforeObject: control.capability_id,
      beforeState: ['status=ACTIVE', 'remaining_uses=1'],
      operator: 'PRE-CALL ONE-USE RESERVATION',
      basis: 'control.reservation_before_invocation=true',
      witness: control.reservation_id,
      afterObject: control.capability_id,
      afterState: ['status=CONSUMING', 'remaining_uses=0'],
      whatChanged: ['status ACTIVE → CONSUMING', 'remaining_uses 1 → 0'],
      whatDidNotChange: ['capability, approval, principal, request, input, model, endpoint'],
      standingEarned: 'OBSERVED',
      unresolved: ['crash recovery from CONSUMING'],
      backward: ['control-active', 'approval'],
      forward: ['control-consuming', 'control-invoke'],
    }),
    inspectorRecord(shared, {
      id: 'control-consuming',
      kind: 'STATE',
      title: 'Reserved authority',
      beforeObject: control.capability_id,
      beforeState: ['status=CONSUMING', 'remaining_uses=0'],
      operator: 'STATE OBSERVATION',
      basis: 'installed harness inspected durable state inside the invocation mock',
      witness: control.reservation_id,
      afterObject: control.capability_id,
      afterState: ['status=CONSUMING', 'remaining_uses=0'],
      whatChanged: ['current authority became unavailable to a second admission'],
      whatDidNotChange: ['consequence completion was not yet established'],
      standingEarned: 'OBSERVED',
      unresolved: ['whether a crash occurred after reservation'],
      backward: ['control-reserve'],
      forward: ['control-invoke'],
    }),
    inspectorRecord(shared, {
      id: 'control-invoke',
      kind: 'TRANSFORMATION',
      title: 'Cross governed invocation boundary',
      beforeObject: control.capability_id,
      beforeState: ['status=CONSUMING', 'remaining_uses=0'],
      operator: 'GOVERNED invoke_lmstudio BOUNDARY',
      basis: 'control.invocation_count=1',
      witness: 'installed harness boundary witness; real_lmstudio_http_calls=0',
      afterObject: 'model invocation occurrence',
      afterState: ['invocation_count_delta=1'],
      whatChanged: ['mocked invocation boundary call count 0 → 1'],
      whatDidNotChange: ['no real LM Studio HTTP call was made'],
      standingEarned: 'OBSERVED',
      unresolved: ['real HTTP consequence', 'external effect'],
      backward: ['control-consuming', 'control-reserve'],
      forward: ['control-invoked', 'control-finalize'],
    }),
    inspectorRecord(shared, {
      id: 'control-invoked',
      kind: 'WITNESS',
      title: 'Invocation boundary occurrence',
      beforeObject: 'governed invocation boundary',
      beforeState: ['invocation_count_delta=0'],
      operator: 'BOUNDARY OBSERVATION',
      basis: 'control.invocation_count',
      witness: 'invocation_count=1',
      afterObject: 'model invocation occurrence',
      afterState: ['invocation_count_delta=1'],
      whatChanged: ['one boundary invocation was observed'],
      whatDidNotChange: ['real network consequence remained untested'],
      standingEarned: 'OBSERVED',
      unresolved: ['real model response', 'external effect'],
      backward: ['control-invoke'],
      forward: ['control-finalize'],
    }),
    inspectorRecord(shared, {
      id: 'control-finalize',
      kind: 'TRANSFORMATION',
      title: 'Finalize authority consumption',
      beforeObject: control.capability_id,
      beforeState: ['status=CONSUMING', 'remaining_uses=0'],
      operator: 'PERSIST CONSUMPTION RECEIPT',
      basis: 'control.receipt_id + control.status_after',
      witness: control.receipt_id,
      afterObject: control.capability_id,
      afterState: ['status=CONSUMED', 'remaining_uses=0', 'current_authority=NONE'],
      whatChanged: ['status CONSUMING → CONSUMED', 'receipt persisted'],
      whatDidNotChange: ['remaining_uses stayed 0'],
      standingEarned: 'OBSERVED',
      unresolved: ['crash between invocation and receipt persistence'],
      backward: ['control-invoked', 'control-reserve'],
      forward: ['control-consumed', 'replay-attempt'],
    }),
    inspectorRecord(shared, {
      id: 'control-consumed',
      kind: 'STATE',
      title: 'Consumed authority',
      beforeObject: control.capability_id,
      beforeState: ['status=CONSUMED', 'remaining_uses=0'],
      operator: 'STATE OBSERVATION',
      basis: 'control.status_after + control.current_authority',
      witness: control.receipt_id,
      afterObject: control.capability_id,
      afterState: ['status=CONSUMED', 'remaining_uses=0', 'current_authority=NONE'],
      whatChanged: ['historical receipt became readable'],
      whatDidNotChange: ['no use was restored'],
      standingEarned: 'OBSERVED',
      unresolved: ['live authority after temporary fixture deletion'],
      backward: ['control-finalize'],
      forward: ['replay-attempt'],
    }),
    inspectorRecord(shared, {
      id: 'replay-attempt',
      kind: 'TRANSFORMATION',
      title: 'Reuse the exact consumed capability',
      beforeObject: replay.capability_id,
      beforeState: ['status=CONSUMED', 'remaining_uses=0'],
      operator: 'EXACT SEQUENTIAL REPLAY ATTEMPT',
      basis: 'exact_replay.same_capability_object_reference_reused=true',
      witness: replay.denial_id,
      afterObject: replay.capability_id,
      afterState: ['decision=DENY', 'reason=AUTHORITY_EXHAUSTED', 'invocation_count_delta=0'],
      whatChanged: ['a replay attempt occurred'],
      whatDidNotChange: [
        'capability instance', 'approval', 'principal', 'request', 'input',
        'model', 'endpoint', 'executor', 'policy', 'status=CONSUMED',
      ],
      standingEarned: 'QUALIFIED',
      unresolved: ['distributed replay resistance', 'multi-process replay'],
      backward: ['control-consumed', 'control-finalize'],
      forward: ['replay-denied'],
    }),
    inspectorRecord(shared, {
      id: 'replay-denied',
      kind: 'STANDING',
      title: 'Replay denied',
      beforeObject: replay.capability_id,
      beforeState: ['status=CONSUMED', 'remaining_uses=0'],
      operator: 'DENIAL OBSERVATION',
      basis: 'exact_replay.decision + exact_replay.reason',
      witness: replay.denial_id,
      afterObject: replay.capability_id,
      afterState: ['DENY', 'AUTHORITY_EXHAUSTED', 'current_authority=NONE'],
      whatChanged: ['denial witness appended'],
      whatDidNotChange: ['invocation_count_delta=0', 'historical receipt remained readable'],
      standingEarned: 'QUALIFIED',
      unresolved: ['concurrent replay', 'distributed replay'],
      backward: ['replay-attempt', 'control-consumed'],
      forward: [],
    }),
    inspectorRecord(shared, {
      id: 'wrong-active',
      kind: 'OBJECT',
      title: 'Fresh P-bound capability',
      beforeObject: wrong.capability_id,
      beforeState: ['principal=P', 'status=ACTIVE', 'remaining_uses=1'],
      operator: 'STATE OBSERVATION',
      basis: 'wrong_declared_principal source state',
      witness: wrong.approval_id,
      afterObject: wrong.capability_id,
      afterState: ['principal=P', 'status=ACTIVE', 'remaining_uses=1'],
      whatChanged: ['fresh authority instance was issued'],
      whatDidNotChange: ['request, input, model, endpoint, executor, policy'],
      standingEarned: 'OBSERVED',
      unresolved: ['principal authentication'],
      backward: ['request-input', 'approval'],
      forward: ['wrong-principal-attempt'],
    }),
    inspectorRecord(shared, {
      id: 'wrong-principal-attempt',
      kind: 'TRANSFORMATION',
      title: 'Substitute attempting principal P → Q',
      beforeObject: wrong.capability_id,
      beforeState: ['issued principal=P', 'attempting principal=P'],
      operator: 'DECLARED PRINCIPAL CORRESPONDENCE CHECK',
      basis: 'wrong_declared_principal.attempting_principal_id',
      witness: wrong.denial_id,
      afterObject: wrong.capability_id,
      afterState: ['attempting principal=Q', 'decision=DENY', 'reason=PRINCIPAL_MISMATCH'],
      whatChanged: ['attempting_principal_id P → Q'],
      whatDidNotChange: [
        'capability', 'approval', 'request', 'input', 'model', 'endpoint',
        'executor', 'policy', 'remaining_uses=1', 'status=ACTIVE',
      ],
      standingEarned: 'QUALIFIED',
      unresolved: ['authentication of either declared identity'],
      backward: ['wrong-active', 'approval'],
      forward: ['wrong-denied'],
    }),
    inspectorRecord(shared, {
      id: 'wrong-denied',
      kind: 'STANDING',
      title: 'Principal mismatch denied',
      beforeObject: wrong.capability_id,
      beforeState: ['status=ACTIVE', 'remaining_uses=1'],
      operator: 'DENIAL OBSERVATION',
      basis: 'wrong_declared_principal decision/reason/state fields',
      witness: wrong.denial_id,
      afterObject: wrong.capability_id,
      afterState: ['status=ACTIVE', 'remaining_uses=1', 'reservation_count_delta=0', 'invocation_count_delta=0'],
      whatChanged: ['principal-mismatch denial witness appended'],
      whatDidNotChange: ['authority remained available to the issued declared principal'],
      standingEarned: 'QUALIFIED',
      unresolved: ['principal authentication', 'identity forgery resistance'],
      backward: ['wrong-principal-attempt', 'wrong-active'],
      forward: [],
    }),
    inspectorRecord(shared, {
      id: 'request-input',
      kind: 'OBJECT',
      title: 'Request and input coordinates',
      beforeObject: control.request_sha256,
      beforeState: [`input_sha256=${control.input_sha256}`],
      operator: 'SOURCE COORDINATE RETENTION',
      basis: 'qualification trace request/input/model/endpoint fields',
      witness: control.request_sha256,
      afterObject: control.request_sha256,
      afterState: [`model=${control.model}`, `endpoint=${control.endpoint_identity}`],
      whatChanged: [],
      whatDidNotChange: ['source coordinates retained through the tested path'],
      standingEarned: 'OBSERVED',
      unresolved: ['hidden internal model prompt'],
      backward: [],
      forward: ['approval', 'control-active', 'wrong-active'],
    }),
    inspectorRecord(shared, {
      id: 'approval',
      kind: 'WITNESS',
      title: 'Approval occurrence',
      beforeObject: control.request_sha256,
      beforeState: ['approval not yet observed'],
      operator: 'INSTALLED APPROVE PATH',
      basis: 'control.approval_calls=1 + approval_input_fixture=LOCAL_YES',
      witness: control.approval_id,
      afterObject: control.approval_id,
      afterState: ['approval occurrence observed'],
      whatChanged: ['approval call count 0 → 1'],
      whatDidNotChange: ['human identity was not attested'],
      standingEarned: 'OBSERVED',
      unresolved: ['human identity', 'principal authentication'],
      backward: ['request-input'],
      forward: ['control-active', 'wrong-active'],
    }),
  ];

  const inspectableById = Object.fromEntries(
    inspectables.map((inspectable) => [inspectable.id, inspectable]),
  );

  return {
    objectType: 'COCKPIT_CELL002_SOURCE_BOUND_SPECIMEN_VIEW_V0',
    specimenId: 'AUTHORITY_MEMBRANE_SECURITY_CELL_002',
    title: 'One-shot authority under pressure',
    subtitle: 'Installed bridge specimen · declared principal binding · sequential replay',
    semanticPrimitives: [...CELL002_PRIMITIVES],
    sourceArtifacts: CELL002_SOURCE_ARTIFACTS.map((source) => ({ ...source })),
    sourceTrace: trace,
    standing: shared,
    coordinates: {
      control: controlCoordinates,
      replay: replayCoordinates,
      wrongPrincipal: wrongCoordinates,
    },
    control: {
      nodes: ['control-active', 'control-consuming', 'control-invoked', 'control-consumed'],
      edges: ['control-reserve', 'control-invoke', 'control-finalize'],
    },
    replay: {
      nodes: ['control-consumed', 'replay-denied'],
      edges: ['replay-attempt'],
      changed: [
        'authority standing ACTIVE / remaining=1 -> CONSUMED / remaining=0 / current_authority=NONE',
        'recorded replay attempt occurrence',
      ],
      heldFixed: [
        'capability instance', 'approval', 'principal', 'request', 'input',
        'model', 'endpoint', 'executor', 'policy',
      ],
      observedEffect: ['DENY', 'AUTHORITY_EXHAUSTED', 'second invocation delta=0'],
    },
    wrongPrincipal: {
      nodes: ['wrong-active', 'wrong-denied'],
      edges: ['wrong-principal-attempt'],
      changed: ['attempting_principal_id P → Q'],
      heldFixed: [
        'capability', 'approval', 'request', 'input', 'model', 'endpoint',
        'executor', 'policy', 'remaining_uses=1', 'status=ACTIVE',
      ],
      observedEffect: [
        'DENY', 'PRINCIPAL_MISMATCH', 'no reservation', 'no invocation', 'authority preserved',
      ],
    },
    unknownRegion: {
      label: 'UNKNOWN_REGION',
      standing: 'NOT_ESTABLISHED',
      items: notEstablished,
      futureShape: ['FRAME 0', 'UNKNOWN_REGION', 'FRAME 1'],
      rule: 'No intermediate trajectory may be invented.',
    },
    inspectables,
    inspectableById,
    selectedInspectableId: 'control-reserve',
    selectedTraversal: 'WHY',
    testMetadata: {
      pressureResult: trace.all_four_pressures_passed === true ? 'PASS' : 'UNRESOLVED',
      realHttpCalls: trace.real_lmstudio_http_calls,
      observedAt: trace.observed_at,
    },
  };
}

export function selectInspectable(model, id) {
  if (!model.inspectableById[id]) {
    return model;
  }
  return {
    ...model,
    selectedInspectableId: id,
  };
}

export function selectTraversal(model, traversal) {
  if (traversal !== 'WHY' && traversal !== 'CAUSE') {
    return model;
  }
  return {
    ...model,
    selectedTraversal: traversal,
  };
}

export function selectedInspectable(model) {
  return model.inspectableById[model.selectedInspectableId] || null;
}
