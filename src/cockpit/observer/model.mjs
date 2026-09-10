const KNOWN_ARRAY_SURFACES = [
  'pressure_nodes',
  'pressure_relations',
  'constraints',
  'evidence_refs',
  'projection_documents',
  'projection_diagnostics',
];

export const READ_ONLY_INTERACTIONS = Object.freeze([
  'select',
  'inspect',
  'follow_relation',
  'open_evidence_reference',
  'copy_reference',
]);

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

function standingText(node) {
  return normalizedField(node?.standing).text;
}

function standingClass(standing) {
  const mappings = {
    OPEN: 'open',
    BASIS_INSUFFICIENT: 'basis-insufficient',
    CANDIDATE_SURVIVED: 'candidate-survived',
    BOUNDED_RESOLUTION: 'bounded',
  };
  return mappings[standing] || 'neutral';
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
    const currentStanding = standingText(node);
    return {
      key: occurrenceKey(node, index),
      index,
      node,
      currentStanding,
      standingClass: standingClass(currentStanding),
      isActive: explicitActiveId !== null && node?.id === explicitActiveId,
      isDuplicate: (idCounts.get(node?.id) || 0) > 1,
      historyCount: Array.isArray(node?.resolution_history)
        ? node.resolution_history.length
        : 0,
      diagnostics: localDiagnostics,
      isWounded: localDiagnostics.length > 0,
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
  const evidenceById = new Map(evidenceRefs.map((reference) => [reference.id, reference]));

  return {
    rawModel,
    repositoryState: rawModel.repository_state,
    surfaceAvailability,
    occurrences,
    semanticEdges,
    evidenceRefs,
    evidenceById,
    diagnostics: {
      available: surfaceAvailability.projection_diagnostics,
      items: diagnostics,
    },
    selectedOccurrenceKey: occurrences[0]?.key ?? null,
  };
}

export function selectOccurrence(viewModel, key) {
  if (!viewModel.occurrences.some((occurrence) => occurrence.key === key)) {
    return viewModel;
  }
  return { ...viewModel, selectedOccurrenceKey: key };
}

export function selectedOccurrence(viewModel) {
  return viewModel.occurrences.find(
    (occurrence) => occurrence.key === viewModel.selectedOccurrenceKey,
  ) ?? null;
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
