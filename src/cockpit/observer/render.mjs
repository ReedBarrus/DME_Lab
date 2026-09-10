import {
  navigationPresentation,
  normalizedField,
  selectedConstraint,
  selectedEvidence,
  selectedOccurrence,
  selectedProjectionDocument,
  VIEW_NAMES,
} from './model.mjs';

export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function safeClass(value) {
  return String(value || 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
}

function repositoryLabel(identity) {
  if (!identity || typeof identity !== 'object') {
    return 'missing';
  }
  if (identity.owner && identity.repository) {
    return String(identity.owner) + '/' + String(identity.repository);
  }
  return identity.raw_origin ? String(identity.raw_origin) : 'missing';
}

function metric(label, value, className = '') {
  return '<div class="metric ' + safeClass(className) + '">'
    + '<dt>' + escapeHtml(label) + '</dt>'
    + '<dd>' + escapeHtml(value) + '</dd>'
    + '</div>';
}

function exactValue(field, labels = {}) {
  return normalizedField(field, labels).text;
}

export function renderHeader(viewModel) {
  const state = viewModel.repositoryState ?? {};
  const freshness = state.freshness;
  const freshnessStatus = freshness?.status ?? 'missing';
  const projectionStatus = state.projection_status ?? 'missing';
  const hasProjectionCondition = projectionStatus !== 'complete'
    || freshnessStatus === 'stale'
    || freshnessStatus === 'unknown'
    || freshnessStatus === 'missing'
    || !viewModel.diagnostics.available
    || viewModel.diagnostics.items.length > 0;
  const classes = 'repository-header status-' + safeClass(projectionStatus)
    + ' freshness-' + safeClass(freshnessStatus)
    + (hasProjectionCondition ? ' has-projection-condition' : '');

  return '<section class="' + classes + '" aria-labelledby="instrument-title">'
    + '<div class="title-block">'
    + '<p class="eyebrow">READ-ONLY DERIVED PROJECTION</p>'
    + '<h1 id="instrument-title">DME_LAB</h1>'
    + '<p>' + escapeHtml(repositoryLabel(state.repository_identity)) + '</p>'
    + '</div>'
    + '<dl class="metrics">'
    + metric('Branch', exactValue(state.branch))
    + metric('Source commit', state.source_commit ?? 'missing', 'monospace')
    + metric('Source ref', state.source_ref ?? 'missing', 'monospace')
    + metric('Projection class', state.projection_classification ?? 'missing')
    + metric('Projection status', projectionStatus, projectionStatus)
    + metric('Freshness', freshnessStatus, freshnessStatus)
    + metric('Projection time', state.projection_time ?? 'missing', 'monospace')
    + metric('Adapter', state.adapter_version ?? 'missing', 'monospace')
    + '</dl>'
    + '<p class="time-boundary">Projection time is not evidence time.</p>'
    + '</section>';
}

function listValue(values, status, missingLabel = 'missing') {
  if (values === null || status === 'missing') {
    return '<span class="missing">' + escapeHtml(missingLabel) + '</span>';
  }
  if (values.length === 0) {
    return '<span class="explicit-none">none declared</span>';
  }
  return '<span class="token-list">'
    + values.map((value) => '<code>' + escapeHtml(value) + '</code>').join('')
    + '</span>';
}

export function renderNavigation(viewModel) {
  const navigation = navigationPresentation(viewModel.repositoryState);
  let diagnosticText = 'diagnostics unavailable';
  let diagnosticClass = 'missing';
  if (viewModel.diagnostics.available) {
    diagnosticText = String(viewModel.diagnostics.items.length) + ' reported';
    diagnosticClass = viewModel.diagnostics.items.length === 0 ? 'current' : 'diagnostic-present';
  }

  return '<section class="navigation-strip" aria-label="Current navigation">'
    + '<div><span>ACTIVE PRESSURE</span><strong class="' + safeClass(navigation.active.kind)
    + '">' + escapeHtml(navigation.active.text) + '</strong></div>'
    + '<div><span>OPEN / REACHABLE</span>'
    + listValue(navigation.open, navigation.openStatus) + '</div>'
    + '<div><span>SHELVED</span>'
    + listValue(navigation.shelved, navigation.shelvedStatus) + '</div>'
    + '<div><span>NEXT PRESSURE</span><strong class="' + safeClass(navigation.next.kind)
    + '">' + escapeHtml(navigation.next.text) + '</strong></div>'
    + '<div><span>PROJECTION DIAGNOSTICS</span><a href="#diagnostics" class="'
    + diagnosticClass + '">' + escapeHtml(diagnosticText) + '</a></div>'
    + '</section>';
}

function selectedContext(viewModel) {
  if (viewModel.activeView === 'MAP' || viewModel.activeView === 'LINEAGE') {
    const occurrence = selectedOccurrence(viewModel);
    return occurrence
      ? '<code>' + escapeHtml(occurrence.node?.id ?? 'missing ID') + '</code> occurrence '
        + String(occurrence.index + 1)
      : '<span class="missing">none available</span>';
  }
  if (viewModel.activeView === 'CONSTRAINTS') {
    const occurrence = selectedConstraint(viewModel);
    return occurrence
      ? '<code>' + escapeHtml(occurrence.constraint?.id ?? 'missing ID') + '</code>'
      : '<span class="missing">none available</span>';
  }
  if (viewModel.activeView === 'HORIZON') {
    const occurrence = selectedProjectionDocument(viewModel);
    return occurrence
      ? escapeHtml(occurrence.document?.title ?? 'missing title')
      : '<span class="missing">none available</span>';
  }
  const occurrence = selectedEvidence(viewModel);
  return occurrence
    ? '<code>' + escapeHtml(occurrence.reference?.id ?? 'missing ID') + '</code>'
    : '<span class="missing">none available</span>';
}

export function renderViewNavigation(viewModel) {
  const diagnosticText = viewModel.diagnostics.available
    ? String(viewModel.diagnostics.items.length) + ' diagnostics'
    : 'diagnostics unavailable';
  const buttons = VIEW_NAMES.map((view) => '<button type="button" data-view="'
    + view + '" aria-pressed="' + String(viewModel.activeView === view) + '">'
    + view + '</button>').join('');
  return '<section class="view-shell" aria-label="Projection views">'
    + '<nav class="view-tabs">' + buttons + '</nav>'
    + '<div class="selected-context"><span>SELECTED IN THIS LENS</span><strong>'
    + selectedContext(viewModel) + '</strong></div>'
    + '<div class="transition-context"><span>LAST LOCAL TRANSITION</span><strong><code>'
    + escapeHtml(viewModel.lastTransition?.type ?? 'missing') + '</code> / '
    + escapeHtml(viewModel.lastTransition?.coordinate ?? 'missing') + '</strong>'
    + '<small>foreground only; asserts no new relation</small></div>'
    + '<a class="view-diagnostic-link" href="#diagnostics">'
    + escapeHtml(diagnosticText) + '</a></section>';
}

function mapGeometry(occurrences) {
  const columns = 4;
  const cellWidth = 270;
  const cellHeight = 154;
  const insetX = 28;
  const insetY = 30;
  const nodeWidth = 224;
  const nodeHeight = 112;
  const points = new Map();
  occurrences.forEach((occurrence, index) => {
    const column = index % columns;
    const row = Math.floor(index / columns);
    points.set(occurrence.key, {
      x: insetX + column * cellWidth,
      y: insetY + row * cellHeight,
      width: nodeWidth,
      height: nodeHeight,
    });
  });
  return {
    points,
    width: columns * cellWidth,
    height: Math.max(1, Math.ceil(occurrences.length / columns)) * cellHeight + 38,
  };
}

function renderEdge(edge, geometry, selectedKey) {
  if (!edge.drawable) {
    return '';
  }
  const source = geometry.points.get(edge.sourceCandidates[0].key);
  const target = geometry.points.get(edge.targetCandidates[0].key);
  if (!source || !target) {
    return '';
  }
  const x1 = source.x + source.width / 2;
  const y1 = source.y + source.height / 2;
  const x2 = target.x + target.width / 2;
  const y2 = target.y + target.height / 2;
  const relation = edge.relation;
  const midpoint = (x1 + x2) / 2;
  const selected = edge.sourceCandidates[0].key === selectedKey
    || edge.targetCandidates[0].key === selectedKey;
  const label = String(relation.source_pressure_id) + ' '
    + String(relation.relation_kind) + ' ' + String(relation.target_pressure_id);
  return '<path class="semantic-edge edge-' + safeClass(relation.relation_kind)
    + (selected ? ' is-foreground' : '')
    + '" data-relation-key="' + escapeHtml(edge.key)
    + '" d="M ' + x1 + ' ' + y1 + ' H ' + midpoint + ' V ' + y2 + ' H ' + x2
    + '" marker-end="url(#arrow)">'
    + '<title>' + escapeHtml(label) + '</title></path>';
}

function nodeBadges(occurrence) {
  const badges = [];
  if (occurrence.historyCount > 0) {
    badges.push('<span class="badge history">history ' + occurrence.historyCount + '</span>');
  }
  if (occurrence.isDuplicate) {
    badges.push('<span class="badge ambiguous">duplicate identity</span>');
  }
  if (occurrence.hasAmbiguousActivity) {
    badges.push('<span class="badge ambiguous">active occurrence ambiguous</span>');
  }
  if (occurrence.hasProjectionDiagnostic) {
    badges.push('<span class="badge diagnostic">projection diagnostic '
      + occurrence.diagnostics.length + '</span>');
  }
  if (occurrence.hasUnknownStanding) {
    badges.push('<span class="badge diagnostic">unknown standing</span>');
  }
  if (occurrence.hasMissingStanding) {
    badges.push('<span class="badge missing-field">standing missing</span>');
  }
  if (occurrence.missingDiscriminator.kind === 'value') {
    badges.push('<span class="badge discriminator">missing discriminator</span>');
  } else if (occurrence.missingDiscriminator.kind === 'missing') {
    badges.push('<span class="badge missing-field">discriminator unprojected</span>');
  }
  if (occurrence.residue.kind === 'value') {
    badges.push('<span class="badge residue">residue</span>');
  }
  if (occurrence.isActive) {
    badges.push('<span class="badge active">active</span>');
  }
  return badges.join('');
}

function renderNode(occurrence, point, selectedKey) {
  const node = occurrence.node;
  const selected = occurrence.key === selectedKey;
  const classes = [
    'pressure-node',
    'standing-' + occurrence.standingClass,
    occurrence.isActive ? 'is-active' : '',
    occurrence.isDuplicate ? 'is-duplicate' : '',
    occurrence.hasProjectionDiagnostic ? 'has-diagnostic' : '',
    selected ? 'is-selected' : '',
  ].filter(Boolean).join(' ');
  return '<foreignObject x="' + point.x + '" y="' + point.y
    + '" width="' + point.width + '" height="' + point.height + '">'
    + '<button type="button" class="' + classes
    + '" data-occurrence-key="' + escapeHtml(occurrence.key)
    + '" aria-pressed="' + String(selected) + '">'
    + '<span class="node-heading"><code>' + escapeHtml(node?.id ?? 'missing ID')
    + '</code><span class="occurrence-index">occurrence ' + (occurrence.index + 1)
    + '</span></span>'
    + '<strong>' + escapeHtml(node?.title ?? 'missing title') + '</strong>'
    + '<span class="standing-text">' + escapeHtml(occurrence.currentStanding) + '</span>'
    + '<span class="badges">' + nodeBadges(occurrence) + '</span>'
    + '</button></foreignObject>';
}

function renderUnresolvedRelations(edges) {
  const unresolved = edges.filter((edge) => !edge.drawable);
  if (unresolved.length === 0) {
    return '';
  }
  const items = unresolved.map((edge) => {
    const relation = edge.relation;
    const target = relation.target_kind === 'pressure'
      ? relation.target_pressure_id
      : relation.condition_text;
    const status = edge.ambiguous ? 'endpoint unresolved / ambiguous' : 'not drawn';
    return '<li><code>' + escapeHtml(relation.source_pressure_id) + '</code> '
      + escapeHtml(relation.relation_kind) + ' '
      + '<code>' + escapeHtml(target ?? 'missing target') + '</code>'
      + '<span>' + escapeHtml(status) + '</span></li>';
  }).join('');
  return '<details class="relation-residue"><summary>Relations without unique drawable pressure endpoints ('
    + unresolved.length + ')</summary><ul>' + items + '</ul></details>';
}

export function renderMap(viewModel) {
  const geometry = mapGeometry(viewModel.occurrences);
  const edges = viewModel.semanticEdges.map(
    (edge) => renderEdge(edge, geometry, viewModel.selectedOccurrenceKey),
  ).join('');
  const nodes = viewModel.occurrences.map(
    (occurrence) => renderNode(
      occurrence,
      geometry.points.get(occurrence.key),
      viewModel.selectedOccurrenceKey,
    ),
  ).join('');

  return '<section class="map-panel" aria-labelledby="map-title">'
    + '<div class="section-heading"><div><p class="eyebrow">PRIMARY VISUAL OBJECT</p>'
    + '<h2 id="map-title">Pressure / Resolution Map</h2></div>'
    + '<p>' + viewModel.occurrences.length + ' node occurrences · '
    + viewModel.semanticEdges.length + ' explicit relations</p></div>'
    + '<div class="map-legend" aria-label="Map legend">'
    + '<span><i class="legend-form solid"></i>BOUNDED_RESOLUTION</span>'
    + '<span><i class="legend-form open"></i>OPEN</span>'
    + '<span><i class="legend-form interrupted"></i>BASIS_INSUFFICIENT &ne; projection diagnostic</span>'
    + '<span><i class="legend-form candidate"></i>CANDIDATE_SURVIVED</span>'
    + '<span><i class="legend-edge unlocks"></i>unlocks</span>'
    + '<span><i class="legend-edge blocked"></i>blocked_by</span>'
    + '<strong>Position and proximity aid composition only. Relations exist only where the normalized model supplies them.</strong>'
    + '</div>'
    + '<div class="map-scroll">'
    + '<svg class="pressure-map" viewBox="0 0 ' + geometry.width + ' ' + geometry.height
    + '" role="group" aria-label="Normalized pressure nodes and explicit relations">'
    + '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
    + '<path d="M 0 0 L 10 5 L 0 10 z"></path></marker></defs>'
    + '<g class="edge-layer">' + edges + '</g>'
    + '<g class="node-layer">' + nodes + '</g>'
    + '</svg></div>'
    + renderUnresolvedRelations(viewModel.semanticEdges)
    + '</section>';
}

function fieldSection(label, field) {
  const value = normalizedField(field);
  return '<section class="inspector-section field-' + safeClass(value.kind) + '">'
    + '<h3>' + escapeHtml(label) + '</h3>'
    + '<p>' + escapeHtml(value.text) + '</p>'
    + (value.status ? '<small>field status: ' + escapeHtml(value.status) + '</small>' : '')
    + '</section>';
}

function fieldBlock(label, field) {
  const value = normalizedField(field);
  return '<div class="inspector-field field-' + safeClass(value.kind) + '">'
    + '<h4>' + escapeHtml(label) + '</h4><p>' + escapeHtml(value.text) + '</p>'
    + (value.status ? '<small>field status: ' + escapeHtml(value.status) + '</small>' : '')
    + '</div>';
}

function safeHttpUrl(value) {
  try {
    const url = new URL(String(value));
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : null;
  } catch {
    return null;
  }
}

function referenceUrl(reference, repositoryState) {
  const external = safeHttpUrl(reference?.original_target);
  if (external) {
    return external;
  }
  const identity = repositoryState?.repository_identity;
  const sourceCommit = repositoryState?.source_commit;
  const path = reference?.committed_path_checked;
  if (
    identity?.host !== 'github.com'
    || !identity.owner
    || !identity.repository
    || !sourceCommit
    || !path
  ) {
    return null;
  }
  const encodedPath = String(path).split('/').map(encodeURIComponent).join('/');
  return 'https://github.com/' + encodeURIComponent(identity.owner)
    + '/' + encodeURIComponent(identity.repository)
    + '/blob/' + encodeURIComponent(sourceCommit)
    + '/' + encodedPath;
}

function committedPathUrl(path, repositoryState) {
  const identity = repositoryState?.repository_identity;
  const sourceCommit = repositoryState?.source_commit;
  if (
    identity?.host !== 'github.com'
    || !identity.owner
    || !identity.repository
    || !sourceCommit
    || !path
  ) {
    return null;
  }
  const encodedPath = String(path).split('/').map(encodeURIComponent).join('/');
  return 'https://github.com/' + encodeURIComponent(identity.owner)
    + '/' + encodeURIComponent(identity.repository)
    + '/blob/' + encodeURIComponent(sourceCommit)
    + '/' + encodedPath;
}

function evidenceIdentity(viewModel, id) {
  const occurrences = viewModel.evidenceOccurrences.filter(
    (occurrence) => occurrence.reference?.id === id,
  );
  return {
    occurrences,
    occurrence: occurrences.length === 1 ? occurrences[0] : null,
  };
}

function evidenceTransitionButton(ownerKind, ownerKey, evidenceOccurrence) {
  if (!evidenceOccurrence) {
    return '';
  }
  return '<button type="button" class="text-action" data-follow-evidence-key="'
    + escapeHtml(evidenceOccurrence.key) + '" data-evidence-owner-kind="'
    + escapeHtml(ownerKind) + '" data-evidence-owner-key="'
    + escapeHtml(ownerKey) + '">inspect in SOURCE</button>';
}

function evidenceSection(occurrence, viewModel) {
  const ids = Array.isArray(occurrence.node?.evidence_ref_ids)
    ? occurrence.node.evidence_ref_ids
    : [];
  if (ids.length === 0) {
    return '<section class="inspector-section"><h3>EVIDENCE</h3><p class="missing">none supplied</p></section>';
  }
  const items = ids.map((id) => {
    const identity = evidenceIdentity(viewModel, id);
    if (identity.occurrences.length === 0) {
      return '<li class="reference missing"><code>' + escapeHtml(id)
        + '</code><span>reference object missing</span></li>';
    }
    if (identity.occurrences.length > 1) {
      return '<li class="reference missing"><code>' + escapeHtml(id)
        + '</code><span>reference identity ambiguous: '
        + String(identity.occurrences.length) + ' normalized occurrences; no target selected</span></li>';
    }
    const evidenceOccurrence = identity.occurrence;
    const reference = evidenceOccurrence.reference;
    const href = referenceUrl(reference, viewModel.repositoryState);
    const target = reference.label || reference.original_target || reference.id;
    const targetMarkup = href
      ? '<a href="' + escapeHtml(href) + '" target="_blank" rel="noreferrer">'
        + escapeHtml(target) + '</a>'
      : '<span>' + escapeHtml(target) + '</span>';
    return '<li class="reference reference-' + safeClass(reference.resolution_status) + '">'
      + targetMarkup
      + '<small>reference status: ' + escapeHtml(reference.resolution_status ?? 'missing')
      + '</small>' + evidenceTransitionButton('pressure', occurrence.key, evidenceOccurrence)
      + '</li>';
  }).join('');
  return '<section class="inspector-section"><h3>EVIDENCE</h3><ul class="evidence-list">'
    + items + '</ul><p class="reference-boundary">References support navigation. Resolution is not a proof badge.</p></section>';
}

function historySection(occurrence) {
  const history = Array.isArray(occurrence.node?.resolution_history)
    ? occurrence.node.resolution_history
    : [];
  if (history.length === 0) {
    return '<section class="inspector-section history-section"><h3>RESOLUTION HISTORY</h3>'
      + '<p class="explicit-none">no normalized history entries</p></section>';
  }
  const items = history.map((entry) => {
    const standing = normalizedField(entry?.standing);
    return '<li><div><code>' + escapeHtml(entry?.id ?? 'missing label') + '</code>'
      + '<strong>' + escapeHtml(standing.text) + '</strong></div>'
      + '<p>' + escapeHtml(entry?.summary ?? 'missing summary') + '</p>'
      + '<details><summary>provenance</summary><pre>'
      + escapeHtml(JSON.stringify(entry?.provenance ?? {}, null, 2))
      + '</pre></details></li>';
  }).join('');
  return '<section class="inspector-section history-section"><h3>RESOLUTION HISTORY</h3>'
    + '<ol>' + items + '</ol></section>';
}

function localDiagnosticsSection(occurrence) {
  if (occurrence.diagnostics.length === 0) {
    return '<section class="inspector-section"><h3>DIAGNOSTICS</h3><p>0 associated</p></section>';
  }
  return '<section class="inspector-section has-diagnostic"><h3>DIAGNOSTICS</h3><ul>'
    + occurrence.diagnostics.map((diagnostic) => '<li><code>'
      + escapeHtml(diagnostic.kind ?? 'missing kind') + '</code><p>'
      + escapeHtml(diagnostic.message ?? 'missing message') + '</p></li>').join('')
    + '</ul></section>';
}

function relationSection(occurrence, viewModel) {
  const relations = viewModel.semanticEdges.filter((edge) =>
    edge.sourceCandidates.some((candidate) => candidate.key === occurrence.key)
      || edge.targetCandidates.some((candidate) => candidate.key === occurrence.key));
  const normalized = relations.length === 0
    ? '<p class="explicit-none">no explicit normalized relations for this occurrence</p>'
    : '<ul class="relation-list">' + relations.map((edge) => {
      const relation = edge.relation;
      const outgoing = edge.sourceCandidates.some(
        (candidate) => candidate.key === occurrence.key,
      );
      const counterpart = outgoing ? edge.targetCandidates : edge.sourceCandidates;
      const target = outgoing
        ? relation.target_pressure_id ?? relation.condition_text ?? 'missing target'
        : relation.source_pressure_id ?? 'missing source';
      const follow = edge.drawable && counterpart.length === 1
        ? '<button type="button" data-follow-relation-key="'
          + escapeHtml(edge.key) + '" data-from-occurrence-key="'
          + escapeHtml(occurrence.key) + '">follow</button>'
        : '';
      return '<li><div><code>' + escapeHtml(outgoing ? 'OUT' : 'IN') + '</code> '
        + '<strong>' + escapeHtml(relation.relation_kind ?? 'missing relation kind')
        + '</strong> <code>' + escapeHtml(target) + '</code></div>'
        + '<small>' + escapeHtml(edge.ambiguous ? 'endpoint ambiguous' : 'explicit normalized relation')
        + '</small>' + follow + '</li>';
    }).join('') + '</ul>';
  return '<section class="inspector-section relation-section"><h3>RELATIONS</h3>'
    + fieldBlock('BLOCKED BY', occurrence.node?.blocked_by)
    + fieldBlock('UNLOCKS', occurrence.node?.unlocks)
    + normalized + '</section>';
}

export function renderInspector(viewModel) {
  const occurrence = selectedOccurrence(viewModel);
  if (!occurrence) {
    return '<aside class="inspector empty" aria-labelledby="inspector-title">'
      + '<h2 id="inspector-title">Pressure Inspector</h2>'
      + '<p>No pressure occurrence is available.</p></aside>';
  }
  const node = occurrence.node;
  return '<aside class="inspector" aria-labelledby="inspector-title">'
    + '<div class="inspector-heading"><div><p class="eyebrow">SELECTED OCCURRENCE '
    + (occurrence.index + 1) + '</p><h2 id="inspector-title"><code>'
    + escapeHtml(node?.id ?? 'missing ID') + '</code> '
    + escapeHtml(node?.title ?? 'missing title') + '</h2></div>'
    + '<button type="button" id="copy-pressure-id" data-copy-value="'
    + escapeHtml(node?.id ?? '') + '">Copy ID</button>'
    + '<button type="button" class="text-action" data-open-lineage-key="'
    + escapeHtml(occurrence.key) + '">open LINEAGE</button></div>'
    + '<section class="inspector-section current-standing"><h3>CURRENT</h3>'
    + '<h4>STANDING</h4>'
    + '<strong>' + escapeHtml(occurrence.currentStanding) + '</strong>'
    + (occurrence.isActive ? '<span class="badge active">active</span>' : '<span class="badge">not active</span>')
    + '<p class="projection-limit">basis not explicitly projected</p>'
    + '</section>'
    + '<section class="inspector-section context-section"><h3>CONTEXT / MISSING DISCRIMINATOR</h3>'
    + fieldBlock('PRESSURE', node?.pressure)
    + fieldBlock('MISSING DISCRIMINATOR', node?.missing_discriminator)
    + '</section>'
    + fieldSection('RESOLUTION SO FAR', node?.resolution_so_far)
    + fieldSection('RESIDUE', node?.residue)
    + relationSection(occurrence, viewModel)
    + historySection(occurrence)
    + evidenceSection(occurrence, viewModel)
    + '<section class="inspector-section"><h3>PROVENANCE</h3><pre>'
    + escapeHtml(JSON.stringify(node?.provenance ?? {}, null, 2))
    + '</pre></section>'
    + localDiagnosticsSection(occurrence)
    + '</aside>';
}

function unavailableSurface(title, surfaceName) {
  return '<section class="bounded-view unavailable-surface"><p class="eyebrow">'
    + escapeHtml(title) + '</p><h2>' + escapeHtml(surfaceName) + ' unavailable</h2>'
    + '<p>The normalized <code>' + escapeHtml(surfaceName)
    + '</code> array is missing. This lens does not reconstruct it from repository files.</p></section>';
}

function ownedEvidenceSection(ownerKind, ownerKey, ids, viewModel) {
  if (!Array.isArray(ids) || ids.length === 0) {
    return '<section class="inspector-section"><h3>EVIDENCE</h3>'
      + '<p class="explicit-none">none supplied</p></section>';
  }
  const items = ids.map((id) => {
    const identity = evidenceIdentity(viewModel, id);
    if (identity.occurrences.length > 1) {
      return '<li><code>' + escapeHtml(id) + '</code><span>reference identity ambiguous: '
        + String(identity.occurrences.length) + ' normalized occurrences; no target selected</span></li>';
    }
    const occurrence = identity.occurrence;
    const reference = occurrence?.reference;
    return '<li><code>' + escapeHtml(id) + '</code><span>'
      + escapeHtml(reference?.resolution_status ?? 'reference object missing') + '</span>'
      + evidenceTransitionButton(ownerKind, ownerKey, occurrence) + '</li>';
  }).join('');
  return '<section class="inspector-section"><h3>EVIDENCE</h3>'
    + '<ul class="owned-evidence-list">' + items + '</ul>'
    + '<p class="reference-boundary">Evidence references are navigation, not proof.</p></section>';
}

function renderConstraintCard(occurrence, selectedKey) {
  const constraint = occurrence.constraint;
  const searchable = [
    constraint?.id,
    constraint?.left,
    constraint?.relation,
    constraint?.right,
    constraint?.scope,
    constraint?.basis,
    constraint?.standing,
    constraint?.note,
  ].filter((value) => value !== null && value !== undefined).join(' ').toLowerCase();
  return '<button type="button" class="constraint-card'
    + (occurrence.key === selectedKey ? ' is-selected' : '')
    + '" data-constraint-key="' + escapeHtml(occurrence.key)
    + '" data-filter-text="' + escapeHtml(searchable) + '">'
    + '<span class="object-heading"><code>' + escapeHtml(constraint?.id ?? 'missing ID')
    + '</code><small>' + escapeHtml(constraint?.standing ?? 'missing standing') + '</small></span>'
    + '<span class="constraint-expression"><strong>' + escapeHtml(constraint?.left ?? 'missing left')
    + '</strong><em>' + escapeHtml(constraint?.relation ?? 'missing relation')
    + '</em><strong>' + escapeHtml(constraint?.right ?? 'missing right') + '</strong></span>'
    + '<span class="constraint-coordinates"><code>scope '
    + escapeHtml(constraint?.scope ?? 'missing') + '</code><code>basis '
    + escapeHtml(constraint?.basis ?? 'missing') + '</code></span></button>';
}

function renderConstraintInspector(viewModel) {
  const occurrence = selectedConstraint(viewModel);
  if (!occurrence) {
    return '<aside class="inspector empty"><h2>Constraint Inspector</h2><p>No constraint is available.</p></aside>';
  }
  const constraint = occurrence.constraint;
  return '<aside class="inspector"><div class="inspector-heading"><div>'
    + '<p class="eyebrow">SELECTED CONSTRAINT OCCURRENCE ' + String(occurrence.index + 1) + '</p>'
    + '<h2><code>' + escapeHtml(constraint?.id ?? 'missing ID') + '</code></h2></div></div>'
    + '<section class="inspector-section constraint-inspection"><h3>CONSTRAINT</h3>'
    + fieldBlock('LEFT', constraint?.left)
    + fieldBlock('RELATION', constraint?.relation)
    + fieldBlock('RIGHT', constraint?.right) + '</section>'
    + '<section class="inspector-section"><h3>BOUNDED COORDINATES</h3>'
    + fieldBlock('SCOPE', constraint?.scope)
    + fieldBlock('BASIS', constraint?.basis)
    + fieldBlock('STANDING', constraint?.standing) + '</section>'
    + fieldSection('NOTE', constraint?.note)
    + ownedEvidenceSection('constraint', occurrence.key, constraint?.evidence_ref_ids, viewModel)
    + '<section class="inspector-section"><h3>RECORD PROVENANCE</h3><pre>'
    + escapeHtml(JSON.stringify(constraint?.provenance ?? [], null, 2)) + '</pre></section>'
    + '<section class="inspector-section"><h3>ADAPTER PROVENANCE</h3><pre>'
    + escapeHtml(JSON.stringify(constraint?.adapter_provenance ?? {}, null, 2)) + '</pre></section>'
    + localObjectDiagnostics(occurrence.diagnostics) + '</aside>';
}

function localObjectDiagnostics(diagnostics) {
  if (!Array.isArray(diagnostics) || diagnostics.length === 0) {
    return '<section class="inspector-section"><h3>DIAGNOSTICS</h3><p>0 associated</p></section>';
  }
  return '<section class="inspector-section has-diagnostic"><h3>DIAGNOSTICS</h3><ul>'
    + diagnostics.map((diagnostic) => '<li><code>'
      + escapeHtml(diagnostic?.kind ?? 'missing kind') + '</code> '
      + escapeHtml(diagnostic?.message ?? 'missing message') + '</li>').join('')
    + '</ul></section>';
}

export function renderConstraintsView(viewModel) {
  if (!viewModel.surfaceAvailability.constraints) {
    return unavailableSurface('BOUNDED VIEW', 'constraints');
  }
  const cards = viewModel.constraintOccurrences.map(
    (occurrence) => renderConstraintCard(occurrence, viewModel.selectedConstraintKey),
  ).join('');
  return '<section class="bounded-view" data-view-name="CONSTRAINTS">'
    + '<div class="section-heading"><div><p class="eyebrow">BOUNDED VIEW</p>'
    + '<h2>Constraints</h2></div><p>' + String(viewModel.constraintOccurrences.length)
    + ' normalized records</p></div>'
    + '<p class="semantic-boundary"><code>constraint != local distinction event</code>. '
    + 'Existence establishes no pressure relevance, priority, confidence, or universal truth.</p>'
    + '<label class="view-filter">SEARCH EMITTED CONSTRAINT FIELDS'
    + '<input type="search" data-filter-target="constraint-card" placeholder="ID, term, scope, basis, standing"></label>'
    + '<div class="bounded-grid"><div class="object-list">' + cards + '</div>'
    + renderConstraintInspector(viewModel) + '</div></section>';
}

function lineageRelationList(occurrence, viewModel) {
  const relations = viewModel.semanticEdges.filter((edge) =>
    edge.sourceCandidates.some((candidate) => candidate.key === occurrence.key)
      || edge.targetCandidates.some((candidate) => candidate.key === occurrence.key));
  if (relations.length === 0) {
    return '<p class="explicit-none">no explicit normalized pressure relations</p>';
  }
  return '<ul class="lineage-relations">' + relations.map((edge) => {
    const outgoing = edge.sourceCandidates.some((candidate) => candidate.key === occurrence.key);
    const counterpart = outgoing ? edge.targetCandidates : edge.sourceCandidates;
    const targetText = outgoing
      ? edge.relation?.target_pressure_id ?? edge.relation?.condition_text ?? 'missing target'
      : edge.relation?.source_pressure_id ?? 'missing source';
    const follow = edge.drawable && counterpart.length === 1
      ? '<button type="button" data-follow-relation-key="' + escapeHtml(edge.key)
        + '" data-from-occurrence-key="' + escapeHtml(occurrence.key) + '">follow</button>'
      : '';
    return '<li><code>' + escapeHtml(outgoing ? 'OUT' : 'IN') + '</code><strong>'
      + escapeHtml(edge.relation?.relation_kind ?? 'missing kind') + '</strong><span>'
      + escapeHtml(targetText) + '</span><small>'
      + escapeHtml(edge.ambiguous ? 'endpoint ambiguous' : 'explicit normalized relation')
      + '</small>' + follow + '</li>';
  }).join('') + '</ul>';
}

export function renderLineageView(viewModel) {
  if (!viewModel.surfaceAvailability.pressure_nodes) {
    return unavailableSurface('BOUNDED VIEW', 'pressure_nodes');
  }
  const occurrence = selectedOccurrence(viewModel);
  if (!occurrence) {
    return '<section class="bounded-view"><h2>Lineage</h2><p>No pressure occurrence is available.</p></section>';
  }
  const pressureChoices = viewModel.occurrences.map((candidate) => '<button type="button" class="lineage-choice'
    + (candidate.key === occurrence.key ? ' is-selected' : '') + '" data-occurrence-key="'
    + escapeHtml(candidate.key) + '"><code>' + escapeHtml(candidate.node?.id ?? 'missing ID')
    + '</code><span>occurrence ' + String(candidate.index + 1) + '</span></button>').join('');
  const history = Array.isArray(occurrence.node?.resolution_history)
    ? occurrence.node.resolution_history
    : [];
  const historyMarkup = history.length === 0
    ? '<p class="explicit-none">no normalized history entries</p>'
    : '<ol class="declared-history">' + history.map((entry, index) => '<li>'
      + '<span>DECLARED ORDER ' + String(index + 1) + '</span><code>'
      + escapeHtml(entry?.id ?? 'missing label') + '</code><strong>'
      + escapeHtml(normalizedField(entry?.standing).text) + '</strong><p>'
      + escapeHtml(entry?.summary ?? 'missing summary') + '</p><details><summary>provenance</summary><pre>'
      + escapeHtml(JSON.stringify(entry?.provenance ?? {}, null, 2)) + '</pre></details></li>').join('')
      + '</ol>';
  return '<section class="bounded-view" data-view-name="LINEAGE">'
    + '<div class="section-heading"><div><p class="eyebrow">SELECTED-PRESSURE LINEAGE</p>'
    + '<h2>Declared lineage</h2></div><p><code>'
    + escapeHtml(occurrence.node?.id ?? 'missing ID') + '</code> occurrence '
    + String(occurrence.index + 1) + '</p></div>'
    + '<p class="semantic-boundary">Declared history order is shown. '
    + '<strong>Visual continuity does not establish causal lineage.</strong></p>'
    + '<div class="lineage-layout"><nav class="lineage-pressure-list">' + pressureChoices + '</nav>'
    + '<div class="lineage-detail"><section class="lineage-current"><span>CURRENT STANDING</span><strong>'
    + escapeHtml(occurrence.currentStanding) + '</strong><small>basis not explicitly projected</small></section>'
    + '<section><h3>DECLARED RESOLUTION HISTORY</h3>' + historyMarkup + '</section>'
    + '<section><h3>EXPLICIT PRESSURE RELATIONS</h3>'
    + lineageRelationList(occurrence, viewModel) + '</section>'
    + evidenceSection(occurrence, viewModel)
    + '<section class="inspector-section"><h3>PROVENANCE</h3><pre>'
    + escapeHtml(JSON.stringify(occurrence.node?.provenance ?? {}, null, 2)) + '</pre></section>'
    + localObjectDiagnostics(occurrence.diagnostics) + '</div></div></section>';
}

function renderProjectionDocument(occurrence, selectedKey) {
  const document = occurrence.document;
  const standing = normalizedField(document?.standing);
  return '<button type="button" class="projection-card'
    + (occurrence.key === selectedKey ? ' is-selected' : '')
    + '" data-projection-document-key="' + escapeHtml(occurrence.key) + '">'
    + '<span class="object-heading"><strong>' + escapeHtml(document?.title ?? 'missing title')
    + '</strong><code>' + escapeHtml(standing.text) + '</code></span>'
    + '<span>' + escapeHtml(document?.classification ?? 'missing classification') + '</span>'
    + '<small>' + escapeHtml(document?.source_path ?? 'missing source path') + '</small>'
    + '<em>' + escapeHtml(document?.explicit_non_authority?.declared === true
      ? 'NON-AUTHORITATIVE' : 'non-authority declaration unavailable') + '</em></button>';
}

export function renderHorizonView(viewModel) {
  if (!viewModel.surfaceAvailability.projection_documents) {
    return unavailableSurface('BOUNDED VIEW', 'projection_documents');
  }
  const selected = selectedProjectionDocument(viewModel);
  const cards = viewModel.projectionDocumentOccurrences.map(
    (occurrence) => renderProjectionDocument(occurrence, viewModel.selectedProjectionDocumentKey),
  ).join('');
  let inspector = '<aside class="inspector empty"><h2>Projection Document</h2><p>No document is available.</p></aside>';
  if (selected) {
    const document = selected.document;
    const href = committedPathUrl(document?.source_path, viewModel.repositoryState);
    inspector = '<aside class="inspector"><div class="inspector-heading"><div>'
      + '<p class="eyebrow">PROJECTED TERRITORY</p><h2>'
      + escapeHtml(document?.title ?? 'missing title') + '</h2></div></div>'
      + fieldSection('STANDING', document?.standing)
      + fieldSection('CLASSIFICATION', document?.classification)
      + '<section class="inspector-section"><h3>EXPLICIT NON-AUTHORITY</h3><strong>'
      + escapeHtml(document?.explicit_non_authority?.declared === true ? 'DECLARED' : 'UNAVAILABLE')
      + '</strong><p>' + escapeHtml(document?.explicit_non_authority?.text ?? 'missing') + '</p></section>'
      + '<section class="inspector-section"><h3>SOURCE</h3><code>'
      + escapeHtml(document?.source_path ?? 'missing path') + '</code>'
      + (href ? '<a class="source-open" href="' + escapeHtml(href)
        + '" target="_blank" rel="noreferrer">open normalized committed source</a>' : '')
      + '<p class="reference-boundary">Opening is navigation only. Document contents do not feed back into this model.</p></section>'
      + '<section class="inspector-section"><h3>PROVENANCE</h3><pre>'
      + escapeHtml(JSON.stringify(document?.provenance ?? {}, null, 2)) + '</pre></section>'
      + localObjectDiagnostics(selected.diagnostics) + '</aside>';
  }
  return '<section class="bounded-view horizon-view" data-view-name="HORIZON">'
    + '<div class="section-heading"><div><p class="eyebrow">BOUNDED VIEW</p><h2>Projection Horizon</h2></div>'
    + '<p>' + String(viewModel.projectionDocumentOccurrences.length) + ' normalized documents</p></div>'
    + '<div class="earned-boundary"><strong>EARNED / OBSERVED COCKPIT TERRITORY</strong>'
    + '<span>projection horizon</span><strong>PROJECTED TERRITORY</strong></div>'
    + '<p class="semantic-boundary">Projection documents remain non-authoritative. '
    + 'Display does not make them implemented, available, authorized, active, or ready.</p>'
    + '<div class="bounded-grid"><div class="object-list projection-list">' + cards + '</div>'
    + inspector + '</div></section>';
}

function evidenceFilterText(reference) {
  return [
    reference?.id,
    reference?.origin?.kind,
    reference?.origin?.id,
    reference?.original_target,
    reference?.label,
    reference?.target_kind,
    reference?.resolution_status,
    reference?.committed_path_checked,
  ].filter((value) => value !== null && value !== undefined).join(' ').toLowerCase();
}

function renderEvidenceCard(occurrence, selectedKey) {
  const reference = occurrence.reference;
  return '<button type="button" class="source-card reference-'
    + safeClass(reference?.resolution_status) + (occurrence.key === selectedKey ? ' is-selected' : '')
    + '" data-evidence-key="' + escapeHtml(occurrence.key)
    + '" data-filter-text="' + escapeHtml(evidenceFilterText(reference)) + '">'
    + '<span class="object-heading"><code>' + escapeHtml(reference?.id ?? 'missing ID')
    + '</code><strong>' + escapeHtml(reference?.resolution_status ?? 'missing status') + '</strong></span>'
    + '<span>' + escapeHtml(reference?.label ?? reference?.original_target ?? 'missing target') + '</span>'
    + '<small>origin ' + escapeHtml(reference?.origin?.kind ?? 'missing') + ' / '
    + escapeHtml(reference?.origin?.id ?? 'missing') + '</small></button>';
}

export function renderSourceView(viewModel) {
  if (!viewModel.surfaceAvailability.evidence_refs) {
    return unavailableSurface('BOUNDED VIEW', 'evidence_refs');
  }
  const selected = selectedEvidence(viewModel);
  const cards = viewModel.evidenceOccurrences.map(
    (occurrence) => renderEvidenceCard(occurrence, viewModel.selectedEvidenceKey),
  ).join('');
  let inspector = '<aside class="inspector empty"><h2>Source Inspector</h2><p>No reference is available.</p></aside>';
  if (selected) {
    const reference = selected.reference;
    const href = referenceUrl(reference, viewModel.repositoryState);
    inspector = '<aside class="inspector"><div class="inspector-heading"><div>'
      + '<p class="eyebrow">SELECTED EVIDENCE REFERENCE ' + String(selected.index + 1) + '</p><h2><code>'
      + escapeHtml(reference?.id ?? 'missing ID') + '</code></h2></div></div>'
      + fieldSection('RESOLUTION STATUS', reference?.resolution_status)
      + fieldSection('TARGET KIND', reference?.target_kind)
      + fieldSection('ORIGINAL TARGET', reference?.original_target)
      + '<section class="inspector-section"><h3>ORIGIN IDENTITY</h3><pre>'
      + escapeHtml(JSON.stringify(reference?.origin ?? {}, null, 2)) + '</pre></section>'
      + fieldSection('COMMITTED PATH CHECKED', reference?.committed_path_checked)
      + '<section class="inspector-section"><h3>SOURCE NAVIGATION</h3>'
      + (href ? '<a class="source-open" href="' + escapeHtml(href)
        + '" target="_blank" rel="noreferrer">open normalized source reference</a>'
        : '<p class="missing">no safe navigable URL emitted or derivable from normalized repository identity</p>')
      + '<p class="reference-boundary"><code>resolved</code> means resolvable under the adapter rule, not proved, verified, true, or causal. Source contents are not fetched back into the model.</p></section>'
      + '<section class="inspector-section"><h3>PROVENANCE</h3><pre>'
      + escapeHtml(JSON.stringify(reference?.provenance ?? {}, null, 2)) + '</pre></section>'
      + localObjectDiagnostics(selected.diagnostics) + '</aside>';
  }
  return '<section class="bounded-view" data-view-name="SOURCE">'
    + '<div class="section-heading"><div><p class="eyebrow">BOUNDED VIEW</p><h2>Source / Reference Browser</h2></div>'
    + '<p>' + String(viewModel.evidenceOccurrences.length) + ' normalized references</p></div>'
    + '<p class="semantic-boundary">Exact resolution status is retained. Reference resolution is not epistemic warrant.</p>'
    + '<label class="view-filter">SEARCH EMITTED REFERENCE FIELDS'
    + '<input type="search" data-filter-target="source-card" placeholder="ID, origin, target, status"></label>'
    + '<div class="bounded-grid"><div class="object-list source-list">' + cards + '</div>'
    + inspector + '</div></section>';
}

export function renderActiveView(viewModel) {
  if (viewModel.activeView === 'CONSTRAINTS') {
    return renderConstraintsView(viewModel);
  }
  if (viewModel.activeView === 'LINEAGE') {
    return renderLineageView(viewModel);
  }
  if (viewModel.activeView === 'HORIZON') {
    return renderHorizonView(viewModel);
  }
  if (viewModel.activeView === 'SOURCE') {
    return renderSourceView(viewModel);
  }
  return '<div class="observer-grid" data-view-name="MAP"><div>'
    + renderMap(viewModel) + '</div><div>' + renderInspector(viewModel) + '</div></div>';
}

function diagnosticItem(diagnostic) {
  const raw = Object.prototype.hasOwnProperty.call(diagnostic, 'raw_value')
    ? '<details><summary>retained raw value</summary><pre>'
      + escapeHtml(JSON.stringify(diagnostic.raw_value, null, 2)) + '</pre></details>'
    : '';
  return '<li class="diagnostic diagnostic-' + safeClass(diagnostic?.severity) + '">'
    + '<div><code>' + escapeHtml(diagnostic?.kind ?? 'missing kind') + '</code>'
    + '<strong>' + escapeHtml(diagnostic?.severity ?? 'missing severity') + '</strong></div>'
    + '<p>' + escapeHtml(diagnostic?.message ?? 'missing message') + '</p>'
    + '<dl><dt>Affected</dt><dd><pre>'
    + escapeHtml(JSON.stringify(diagnostic?.affected ?? {}, null, 2))
    + '</pre></dd><dt>Provenance</dt><dd><pre>'
    + escapeHtml(JSON.stringify(diagnostic?.provenance ?? {}, null, 2))
    + '</pre></dd></dl>' + raw + '</li>';
}

export function renderDiagnostics(viewModel) {
  if (!viewModel.diagnostics.available) {
    return '<section id="diagnostics" class="diagnostics-panel has-diagnostic" aria-labelledby="diagnostics-title">'
      + '<div class="section-heading"><div><p class="eyebrow">PROJECTION DIAGNOSTICS MISSING</p>'
      + '<h2 id="diagnostics-title">Diagnostics unavailable</h2></div></div>'
      + '<p>The normalized diagnostics array is missing. This is not zero diagnostics.</p></section>';
  }
  if (viewModel.diagnostics.items.length === 0) {
    return '<section id="diagnostics" class="diagnostics-panel" aria-labelledby="diagnostics-title">'
      + '<div class="section-heading"><div><p class="eyebrow">PROJECTION DIAGNOSTICS</p>'
      + '<h2 id="diagnostics-title">0 reported</h2></div></div>'
      + '<p>The normalized diagnostics array is present and empty.</p></section>';
  }
  return '<section id="diagnostics" class="diagnostics-panel has-diagnostic" aria-labelledby="diagnostics-title">'
    + '<div class="section-heading"><div><p class="eyebrow">PROJECTION DIAGNOSTICS PRESENT</p>'
    + '<h2 id="diagnostics-title">' + viewModel.diagnostics.items.length
    + ' diagnostics reported</h2></div></div>'
    + '<ol>' + viewModel.diagnostics.items.map(diagnosticItem).join('') + '</ol></section>';
}

export function unavailableMarkup(message) {
  return '<section class="load-failure has-diagnostic" role="alert">'
    + '<p class="eyebrow">PROJECTION FAILED</p>'
    + '<h1>PROJECTION UNAVAILABLE</h1>'
    + '<p>' + escapeHtml(message) + '</p>'
    + '<p>No repository state is inferred and no cached clean model is shown.</p>'
    + '</section>';
}
