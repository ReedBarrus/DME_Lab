import {
  navigationPresentation,
  normalizedField,
  selectedOccurrence,
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

function evidenceSection(occurrence, viewModel) {
  const ids = Array.isArray(occurrence.node?.evidence_ref_ids)
    ? occurrence.node.evidence_ref_ids
    : [];
  if (ids.length === 0) {
    return '<section class="inspector-section"><h3>EVIDENCE</h3><p class="missing">none supplied</p></section>';
  }
  const items = ids.map((id) => {
    const reference = viewModel.evidenceById.get(id);
    if (!reference) {
      return '<li class="reference missing"><code>' + escapeHtml(id)
        + '</code><span>reference object missing</span></li>';
    }
    const href = referenceUrl(reference, viewModel.repositoryState);
    const target = reference.label || reference.original_target || reference.id;
    const targetMarkup = href
      ? '<a href="' + escapeHtml(href) + '" target="_blank" rel="noreferrer">'
        + escapeHtml(target) + '</a>'
      : '<span>' + escapeHtml(target) + '</span>';
    return '<li class="reference reference-' + safeClass(reference.resolution_status) + '">'
      + targetMarkup
      + '<small>reference status: ' + escapeHtml(reference.resolution_status ?? 'missing')
      + '</small></li>';
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
        ? '<button type="button" data-follow-occurrence-key="'
          + escapeHtml(counterpart[0].key) + '">follow</button>'
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
    + escapeHtml(node?.id ?? '') + '">Copy ID</button></div>'
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
