const KNOWN_ARRAY_SURFACES = [
  'pressure_nodes',
  'pressure_relations',
  'constraints',
  'evidence_refs',
  'projection_documents',
  'projection_diagnostics',
];

export const READ_ONLY_INTERACTIONS = Object.freeze([
  'switch_view',
  'select',
  'inspect',
  'follow_relation',
  'inspect_declared_history',
  'open_evidence_reference',
  'copy_reference',
]);

export const VIEW_NAMES = Object.freeze([
  'MAP',
  'CONSTRAINTS',
  'LINEAGE',
  'HORIZON',
  'SOURCE',
]);

export const TRANSITION_TYPES = Object.freeze({
  VIEW: 'view_transition',
  SELECTION: 'object_selection',
  TRAVERSAL: 'object_traversal',
});

export const STANDING_FORMS = Object.freeze({
  OPEN: 'open',
  PARTIAL_RESOLUTION: 'partial-resolution',
  BOUNDED_RESOLUTION: 'bounded-resolution',
  BASIS_INSUFFICIENT: 'basis-insufficient',
  BLOCKER_REMOVED: 'blocker-removed',
  CANDIDATE_SURVIVED: 'candidate-survived',
  EQUIVALENT_UNDER_CURRENT_PRESSURE: 'equivalent-current-pressure',
  SHELVED: 'shelved',
});

function own(object, key) {
  return object !== null
    && typeof object === 'object'
    && Object.prototype.hasOwnProperty.call(object, key);
}

export function normalizedField(field, labels = {}) {
  if (field === undefined) {
    return { kind: 'missing', text: labels.missing || 'missing', raw: undefined };
  }
  if (field === null) {
    return { kind: 'explicit-none', text: labels.explicitNone || 'explicit none', raw: null };
  }
  if (typeof field !== 'object' || Array.isArray(field)) {
    return { kind: 'value', text: String(field), raw: field };
  }

  const status = own(field, 'semantic_status')
    ? field.semantic_status
    : field.status;
  if (
    field.value === null
    && (status === 'explicit_none' || status === 'agreement')
    && (field.semantic_status === 'explicit_none' || status === 'explicit_none')
  ) {
    return {
      kind: 'explicit-none',
      text: labels.explicitNone || 'explicit none',
      raw: own(field, 'raw_value') ? field.raw_value : null,
      status,
    };
  }
  if (field.value === null && status === 'explicit_absent') {
    return {
      kind: 'explicit-absent',
      text: labels.explicitAbsent || 'explicitly absent',
      raw: own(field, 'raw_value') ? field.raw_value : null,
      status,
    };
  }
  if (status === 'conflict') {
    return {
      kind: 'conflict',
      text: labels.conflict || 'conflict',
      raw: own(field, 'raw_value') ? field.raw_value : field.declarations,
      status,
    };
  }
  if (status === 'missing' || (!own(field, 'value') && !own(field, 'raw_value'))) {
    return {
      kind: 'missing',
      text: labels.missing || 'missing',
      raw: own(field, 'raw_value') ? field.raw_value : undefined,
      status,
    };
  }
  const value = field.value ?? field.raw_value;
  if (value === null || value === undefined) {
    return { kind: 'missing', text: labels.missing || 'missing', raw: value, status };
  }
  return { kind: 'value', text: String(value), raw: value, status };
}

function occurrenceKey(node, index) {
  const line = node?.provenance?.source_line;
  const id = String(node?.id ?? 'missing').replace(/[^A-Za-z0-9_-]/g, '-');
  return 'pressure-' + String(index).padStart(3, '0') + '-' + id + '-line-' + (line ?? 'missing');
}

function normalizedObjectKey(prefix, object, index) {
  const identity = object?.id ?? object?.title ?? object?.source_path ?? 'missing';
  const safeIdentity = String(identity).replace(/[^A-Za-z0-9_-]/g, '-');
  return prefix + '-' + String(index).padStart(3, '0') + '-' + safeIdentity;
}

function objectDiagnostics(diagnostics, object, identityKeys = []) {
  return diagnostics.filter((diagnostic) => {
    const affected = diagnostic?.affected ?? {};
    if (identityKeys.some((key) => affected[key] && affected[key] === object?.id)) {
      return true;
    }
    if (
      affected.source_path
      && object?.source_path
      && affected.source_path === object.source_path
    ) {
      return true;
    }
    return false;
  });
}

function diagnosticsForNode(diagnostics, node) {
  return diagnostics.filter((diagnostic) => {
    const affected = diagnostic?.affected ?? {};
    if (affected.object_id && affected.object_id === node.id) {
      return true;
    }
    if (
      affected.source_path
      && affected.source_path === node?.provenance?.source_path
      && diagnostic?.provenance?.source_line
      && diagnostic.provenance.source_line === node?.provenance?.source_line
    ) {
      return true;
    }
    return false;
  });
}

function activePressureId(repositoryState) {
  const active = repositoryState?.current_navigation?.active_pressure;
  const presented = normalizedField(active, { explicitNone: 'none selected' });
  return presented.kind === 'value' ? presented.text : null;
}

function standingClass(standing) {
  return STANDING_FORMS[standing] || 'unknown-standing';
}

function relationPresentation(relation, index, occurrences) {
  const sourceCandidates = occurrences.filter(
    (occurrence) => occurrence.node.id === relation?.source_pressure_id,
  );
  const targetCandidates = relation?.target_kind === 'pressure'
    ? occurrences.filter(
      (occurrence) => occurrence.node.id === relation?.target_pressure_id,
    )
    : [];
  const emittedResolution = relation?.target_resolution;
  const ambiguous = emittedResolution?.status === 'ambiguous'
    || sourceCandidates.length !== 1
    || (relation?.target_kind === 'pressure' && targetCandidates.length !== 1);

  return {
    key: 'relation-' + String(index).padStart(3, '0'),
    relation,
    sourceCandidates,
    targetCandidates,
    ambiguous,
    drawable: !ambiguous
      && relation?.target_kind === 'pressure'
      && sourceCandidates.length === 1
      && targetCandidates.length === 1,
  };
}

export function buildObserverModel(rawModel) {
  if (rawModel === null || typeof rawModel !== 'object' || Array.isArray(rawModel)) {
    throw new TypeError('normalized Cockpit model must be a JSON object');
  }

  const surfaceAvailability = {};
  for (const surface of KNOWN_ARRAY_SURFACES) {
    surfaceAvailability[surface] = Array.isArray(rawModel[surface]);
  }

  const diagnostics = surfaceAvailability.projection_diagnostics
    ? rawModel.projection_diagnostics
    : [];
  const nodes = surfaceAvailability.pressure_nodes ? rawModel.pressure_nodes : [];
  const idCounts = new Map();
  for (const node of nodes) {
    idCounts.set(node?.id, (idCounts.get(node?.id) || 0) + 1);
  }

  const explicitActiveId = activePressureId(rawModel.repository_state);
  const occurrences = nodes.map((node, index) => {
    const localDiagnostics = diagnosticsForNode(diagnostics, node);
    const standingField = normalizedField(node?.standing);
    const currentStanding = standingField.text;
    const currentStandingClass = standingField.kind === 'value'
      ? standingClass(currentStanding)
      : 'missing-standing';
    return {
      key: occurrenceKey(node, index),
      index,
      node,
      currentStanding,
      standingClass: currentStandingClass,
      isActive: explicitActiveId !== null
        && node?.id === explicitActiveId
        && idCounts.get(explicitActiveId) === 1,
      hasAmbiguousActivity: explicitActiveId !== null
        && node?.id === explicitActiveId
        && idCounts.get(explicitActiveId) !== 1,
      isDuplicate: (idCounts.get(node?.id) || 0) > 1,
      missingDiscriminator: normalizedField(node?.missing_discriminator),
      residue: normalizedField(node?.residue),
      hasUnknownStanding: currentStandingClass === 'unknown-standing',
      hasMissingStanding: currentStandingClass === 'missing-standing',
      historyCount: Array.isArray(node?.resolution_history)
        ? node.resolution_history.length
        : 0,
      diagnostics: localDiagnostics,
      hasProjectionDiagnostic: localDiagnostics.length > 0,
    };
  });

  const inputRelations = surfaceAvailability.pressure_relations
    ? rawModel.pressure_relations
    : [];
  const semanticEdges = inputRelations.map(
    (relation, index) => relationPresentation(relation, index, occurrences),
  );
  const evidenceRefs = surfaceAvailability.evidence_refs
    ? rawModel.evidence_refs
    : [];
  const constraints = surfaceAvailability.constraints ? rawModel.constraints : [];
  const constraintOccurrences = constraints.map((constraint, index) => ({
    key: normalizedObjectKey('constraint', constraint, index),
    index,
    constraint,
    diagnostics: objectDiagnostics(diagnostics, constraint, ['object_id', 'constraint_id']),
  }));
  const evidenceOccurrences = evidenceRefs.map((reference, index) => ({
    key: normalizedObjectKey('evidence', reference, index),
    index,
    reference,
    diagnostics: objectDiagnostics(diagnostics, reference, ['object_id', 'reference_id']),
  }));
  const projectionDocuments = surfaceAvailability.projection_documents
    ? rawModel.projection_documents
    : [];
  const projectionDocumentOccurrences = projectionDocuments.map((document, index) => ({
    key: normalizedObjectKey('projection', document, index),
    index,
    document,
    diagnostics: objectDiagnostics(diagnostics, document, ['object_id', 'document_id']),
  }));

  return {
    rawModel,
    repositoryState: rawModel.repository_state,
    surfaceAvailability,
    occurrences,
    semanticEdges,
    constraintOccurrences,
    evidenceRefs,
    evidenceOccurrences,
    projectionDocumentOccurrences,
    diagnostics: {
      available: surfaceAvailability.projection_diagnostics,
      items: diagnostics,
    },
    activeView: 'MAP',
    selectedOccurrenceKey: occurrences[0]?.key ?? null,
    selectedConstraintKey: constraintOccurrences[0]?.key ?? null,
    selectedEvidenceKey: evidenceOccurrences[0]?.key ?? null,
    selectedProjectionDocumentKey: projectionDocumentOccurrences[0]?.key ?? null,
    lastTransition: {
      type: TRANSITION_TYPES.VIEW,
      from: null,
      to: 'MAP',
      coordinate: 'initial_view',
      assertsRelation: false,
    },
  };
}

function transition(viewModel, updates, details) {
  return {
    ...viewModel,
    ...updates,
    lastTransition: {
      ...details,
      assertsRelation: false,
    },
  };
}

export function selectView(viewModel, view) {
  if (!VIEW_NAMES.includes(view)) {
    return viewModel;
  }
  return transition(viewModel, { activeView: view }, {
    type: TRANSITION_TYPES.VIEW,
    from: viewModel.activeView,
    to: view,
    coordinate: 'projection_lens',
  });
}

export function selectOccurrence(viewModel, key) {
  if (!viewModel.occurrences.some((occurrence) => occurrence.key === key)) {
    return viewModel;
  }
  return transition(viewModel, { selectedOccurrenceKey: key }, {
    type: TRANSITION_TYPES.SELECTION,
    from: viewModel.selectedOccurrenceKey,
    to: key,
    coordinate: 'pressure_occurrence',
  });
}

export function selectedOccurrence(viewModel) {
  return viewModel.occurrences.find(
    (occurrence) => occurrence.key === viewModel.selectedOccurrenceKey,
  ) ?? null;
}

export function openLineage(viewModel, occurrenceKeyValue) {
  if (!viewModel.occurrences.some((occurrence) => occurrence.key === occurrenceKeyValue)) {
    return viewModel;
  }
  return transition(viewModel, {
    activeView: 'LINEAGE',
    selectedOccurrenceKey: occurrenceKeyValue,
  }, {
    type: TRANSITION_TYPES.TRAVERSAL,
    from: occurrenceKeyValue,
    to: occurrenceKeyValue,
    coordinate: 'pressure_occurrence_to_declared_lineage',
  });
}

export function followPressureRelation(viewModel, relationKey, fromOccurrenceKey) {
  const edge = viewModel.semanticEdges.find((candidate) => candidate.key === relationKey);
  if (!edge?.drawable) {
    return viewModel;
  }
  const fromSource = edge.sourceCandidates[0]?.key === fromOccurrenceKey;
  const fromTarget = edge.targetCandidates[0]?.key === fromOccurrenceKey;
  if (!fromSource && !fromTarget) {
    return viewModel;
  }
  const target = fromSource ? edge.targetCandidates[0] : edge.sourceCandidates[0];
  return transition(viewModel, { selectedOccurrenceKey: target.key }, {
    type: TRANSITION_TYPES.TRAVERSAL,
    from: fromOccurrenceKey,
    to: target.key,
    coordinate: 'explicit_pressure_relation',
    relationKey,
  });
}

export function selectConstraint(viewModel, key) {
  if (!viewModel.constraintOccurrences.some((occurrence) => occurrence.key === key)) {
    return viewModel;
  }
  return transition(viewModel, { selectedConstraintKey: key }, {
    type: TRANSITION_TYPES.SELECTION,
    from: viewModel.selectedConstraintKey,
    to: key,
    coordinate: 'constraint_occurrence',
  });
}

export function selectedConstraint(viewModel) {
  return viewModel.constraintOccurrences.find(
    (occurrence) => occurrence.key === viewModel.selectedConstraintKey,
  ) ?? null;
}

export function selectEvidence(viewModel, key) {
  if (!viewModel.evidenceOccurrences.some((occurrence) => occurrence.key === key)) {
    return viewModel;
  }
  return transition(viewModel, { selectedEvidenceKey: key }, {
    type: TRANSITION_TYPES.SELECTION,
    from: viewModel.selectedEvidenceKey,
    to: key,
    coordinate: 'evidence_reference',
  });
}

export function selectedEvidence(viewModel) {
  return viewModel.evidenceOccurrences.find(
    (occurrence) => occurrence.key === viewModel.selectedEvidenceKey,
  ) ?? null;
}

export function selectProjectionDocument(viewModel, key) {
  if (!viewModel.projectionDocumentOccurrences.some((occurrence) => occurrence.key === key)) {
    return viewModel;
  }
  return transition(viewModel, { selectedProjectionDocumentKey: key }, {
    type: TRANSITION_TYPES.SELECTION,
    from: viewModel.selectedProjectionDocumentKey,
    to: key,
    coordinate: 'projection_document',
  });
}

export function selectedProjectionDocument(viewModel) {
  return viewModel.projectionDocumentOccurrences.find(
    (occurrence) => occurrence.key === viewModel.selectedProjectionDocumentKey,
  ) ?? null;
}

function ownerEvidenceIds(viewModel, ownerKind, ownerKey) {
  if (ownerKind === 'pressure') {
    const owner = viewModel.occurrences.find((occurrence) => occurrence.key === ownerKey);
    return owner?.node?.evidence_ref_ids;
  }
  if (ownerKind === 'constraint') {
    const owner = viewModel.constraintOccurrences.find((occurrence) => occurrence.key === ownerKey);
    return owner?.constraint?.evidence_ref_ids;
  }
  return null;
}

export function followEvidence(viewModel, ownerKind, ownerKey, evidenceKey) {
  const selectedEvidenceOccurrence = viewModel.evidenceOccurrences.find(
    (occurrence) => occurrence.key === evidenceKey,
  );
  const ids = ownerEvidenceIds(viewModel, ownerKind, ownerKey);
  const identityMatches = selectedEvidenceOccurrence
    ? viewModel.evidenceOccurrences.filter(
      (occurrence) => occurrence.reference?.id === selectedEvidenceOccurrence.reference?.id,
    )
    : [];
  if (
    !selectedEvidenceOccurrence
    || identityMatches.length !== 1
    || !Array.isArray(ids)
    || !ids.includes(selectedEvidenceOccurrence.reference?.id)
  ) {
    return viewModel;
  }
  return transition(viewModel, {
    activeView: 'SOURCE',
    selectedEvidenceKey: evidenceKey,
  }, {
    type: TRANSITION_TYPES.TRAVERSAL,
    from: ownerKey,
    to: evidenceKey,
    coordinate: 'explicit_evidence_ref_id',
  });
}

export async function loadProjection(fetchImplementation, url) {
  const response = await fetchImplementation(url, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error('projection JSON unavailable: HTTP ' + response.status);
  }
  const model = await response.json();
  return buildObserverModel(model);
}

export function navigationPresentation(repositoryState) {
  const navigation = repositoryState?.current_navigation ?? {};
  const active = normalizedField(navigation.active_pressure, {
    explicitNone: 'none selected',
  });
  const next = normalizedField(navigation.next_experimental_pressure, {
    explicitNone: 'none selected',
  });
  const openField = navigation.newly_reachable_open_pressures;
  const shelvedField = navigation.shelved_pressures;
  return {
    active,
    open: Array.isArray(openField?.values) ? openField.values.map(String) : null,
    openStatus: openField?.status ?? 'missing',
    shelved: Array.isArray(shelvedField?.values) ? shelvedField.values.map(String) : null,
    shelvedStatus: shelvedField?.status ?? 'missing',
    next,
  };
}
