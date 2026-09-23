import {
  projectFieldPoint,
  repositoryFieldRelationCounts,
} from './repository_fabric_geometry.mjs';
import {
  repositoryObjectRelations,
  repositoryQueryMatches,
  selectedRepositoryObject,
} from './repository_fabric_model.mjs';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function value(valueToRender, fallback = 'NOT_APPLICABLE') {
  if (valueToRender === null || valueToRender === undefined || valueToRender === '') {
    return `<span class="fabric-missing">${escapeHtml(fallback)}</span>`;
  }
  return `<code>${escapeHtml(valueToRender)}</code>`;
}

function field(label, content) {
  return `<div class="fabric-field"><dt>${escapeHtml(label)}</dt><dd>${content}</dd></div>`;
}

function relationTarget(relation, model) {
  if (relation.target_id && model.objectById[relation.target_id]) {
    const target = model.objectById[relation.target_id];
    return `${target.object_kind}:${target.path || '/'}`;
  }
  return JSON.stringify(relation.target_address);
}

function renderRelations(model, object) {
  const relations = repositoryObjectRelations(model, object.object_id);
  const rows = [
    ...relations.incoming.map((relation) => ({
      direction: 'IN', relation: relation.relation,
      coordinate: model.objectById[relation.source_id]?.path || '/',
    })),
    ...relations.outgoing.map((relation) => ({
      direction: 'OUT', relation: relation.relation,
      coordinate: relationTarget(relation, model),
    })),
  ];
  if (!rows.length) return '<p class="fabric-missing">NO MECHANICAL RELATIONS</p>';
  return `<ul class="fabric-relations">${rows.map((row) => `
    <li><span>${escapeHtml(row.direction)}</span><strong>${escapeHtml(row.relation)}</strong><code>${escapeHtml(row.coordinate)}</code></li>
  `).join('')}</ul>`;
}

function coordinate(point) {
  return `${point.x.toFixed(3)}, ${point.y.toFixed(3)}, ${point.z.toFixed(3)}`;
}

function renderInspector(model, geometricField) {
  const object = selectedRepositoryObject(model);
  if (!object) return '<aside class="fabric-inspector">NO OBJECT SELECTED</aside>';
  const node = geometricField.nodeById[object.object_id];
  const typed = object.typed_projections?.length
    ? `<ul>${object.typed_projections.map((item) => `<li>${escapeHtml(JSON.stringify(item))}</li>`).join('')}</ul>`
    : '<span class="fabric-missing">NONE - SEMANTIC ROLE NOT DERIVED</span>';
  const address = JSON.stringify(object.address, null, 2);
  return `
    <aside class="fabric-inspector" aria-labelledby="fabric-inspector-title">
      <header>
        <p class="fabric-kicker">LOCAL SYMBOLIC INSPECTOR</p>
        <h2 id="fabric-inspector-title">${escapeHtml(object.path || object.repository_identity)}</h2>
        <span class="fabric-standing">${escapeHtml(object.semantic_standing)}</span>
        <div class="fabric-inspector-actions">
          <button type="button" data-focus-selected>FOCUS SELECTED</button>
          <button type="button" data-copy-repository-address="${escapeHtml(object.object_id)}">COPY EXACT ADDRESS</button>
        </div>
      </header>
      <dl>
        ${field('OBJECT_ID', value(object.object_id))}
        ${field('OBJECT_KIND', value(object.object_kind))}
        ${field('PATH', value(object.path || '/'))}
        ${field('STRUCTURAL_REST_S(X)', value(coordinate(node.restPosition)))}
        ${field('CURRENT_PROJECTED_P(X,T)', value(coordinate(node.currentPosition)))}
        ${field('REPOSITORY_IDENTITY', value(object.repository_identity))}
        ${field('SOURCE_COMMIT', value(object.source_commit))}
        ${field('SOURCE_BRANCH', value(object.source_branch, 'DETACHED_OR_NOT_DERIVED'))}
        ${field('PARENT_PATH', value(object.parent_path, 'ROOT_HAS_NO_PARENT'))}
        ${field('PATH_IDENTITY', `<pre>${escapeHtml(JSON.stringify(object.path_identity, null, 2))}</pre>`)}
        ${field('GIT_BLOB_IDENTITY', value(object.git_blob_identity))}
        ${field('CONTENT_IDENTITY', value(object.content_identity))}
        ${field('EXISTENCE_STANDING', value(object.existence_standing))}
        ${field('SEMANTIC_STANDING', value(object.semantic_standing))}
        ${field('TYPED_PROJECTIONS', typed)}
        ${field('MECHANICAL_RELATIONS', renderRelations(model, object))}
        ${field('CANONICAL_ADDRESS', `<pre class="fabric-address">${escapeHtml(address)}</pre>`)}
      </dl>
    </aside>
  `;
}

function slider({channel, label, value: sliderValue, minimum, maximum, step, disabled = false}) {
  return `
    <label class="fabric-basis-control ${disabled ? 'is-unavailable' : ''}">
      <span>${escapeHtml(label)}</span>
      <input type="range" min="${minimum}" max="${maximum}" step="${step}"
        value="${sliderValue}" data-basis-channel="${channel}" ${disabled ? 'disabled' : ''}>
      <output data-basis-value="${channel}">${Number(sliderValue).toFixed(2)}</output>
    </label>
  `;
}

export function renderRepositoryFabric(model, geometricField) {
  const source = model.source;
  const counts = repositoryFieldRelationCounts(geometricField);
  const matches = model.query ? repositoryQueryMatches(model).length : model.objects.length;
  const dependencyUnavailable = counts.dependency === 0;
  return `
    <main class="geometric-fabric">
      <header class="fabric-hero">
        <div>
          <p class="fabric-kicker">GEOMETRIC REPOSITORY PROJECTION V0 - DERIVED READ-ONLY</p>
          <h1>${escapeHtml(source.repository_identity)}</h1>
          <p>One continuous source-bound 3D field. Geometry compresses mechanical relational difference.</p>
        </div>
        <dl class="fabric-coordinate">
          <div><dt>BRANCH</dt><dd>${escapeHtml(source.source_branch || 'NOT_DERIVED')}</dd></div>
          <div><dt>COMMIT</dt><dd><code>${escapeHtml(source.source_commit)}</code></dd></div>
          <div><dt>OBJECTS</dt><dd>${model.objects.length}</dd></div>
          <div><dt>INTERNAL RELATIONS</dt><dd>${geometricField.structuralEdges.length + geometricField.dependencyEdges.length}</dd></div>
        </dl>
      </header>
      <section class="fabric-laws" aria-label="projection laws">
        <span>UNKNOWN SEMANTICS != INVISIBLE OBJECT</span>
        <span>ZOOM != NEW DATA MODEL</span>
        <span>BASIS CHANGE != NEW OBJECT IDENTITY</span>
        <span>STRUCTURAL BASE SPACE != DYNAMIC FIELD STATE</span>
      </section>
      <section class="fabric-toolbar">
        <label class="fabric-search">
          <span>SEARCH-TO-FOCUS (ACCELERATOR ONLY)</span>
          <input type="search" data-repository-query value="${escapeHtml(model.query)}" placeholder="exact path, address, object id" autocomplete="off">
          <output data-query-count>${matches} MATCHES - FIELD UNFILTERED</output>
        </label>
        <div class="fabric-camera-controls" aria-label="camera controls">
          <button type="button" data-focus-selected>FOCUS SELECTED</button>
          <button type="button" data-reset-field>RESET WHOLE FIELD</button>
        </div>
      </section>
      <div class="fabric-workbench">
        <section class="fabric-spatial-stage" aria-label="continuous repository field">
          <canvas class="fabric-canvas" data-geometric-field tabindex="0"
            aria-label="Navigable 3D repository field. Drag to orbit, shift-drag to pan, wheel to dolly, click to select."></canvas>
          <div class="fabric-field-hud">
            <span>DRAG ORBIT</span><span>SHIFT/RIGHT DRAG PAN</span><span>WHEEL DOLLY</span><span>CLICK SELECT</span>
            <output data-camera-coordinate></output>
          </div>
          <div class="fabric-legend" aria-label="visual legend">
            <span class="repository">REPOSITORY</span>
            <span class="directory">DIRECTORY VOLUME</span>
            <span class="file">FILE</span>
            <span class="file-version">FILE VERSION</span>
            <span>ALL SEMANTIC STANDING VISIBLE</span>
          </div>
        </section>
        <aside class="fabric-operators">
          <section>
            <p class="fabric-kicker">STRUCTURAL_BASIS_V0</p>
            ${slider({channel: 'containment', label: 'CONTAINMENT', value: geometricField.weights.structural.containment, minimum: 0.35, maximum: 1.65, step: 0.05})}
            ${slider({channel: 'dependency', label: `DEPENDENCY (${dependencyUnavailable ? 'UNAVAILABLE' : counts.dependency})`, value: geometricField.weights.structural.dependency, minimum: 0, maximum: 0.8, step: 0.05, disabled: dependencyUnavailable})}
            ${slider({channel: 'version', label: 'VERSION', value: geometricField.weights.structural.version, minimum: 0, maximum: 0.35, step: 0.01})}
            <button type="button" data-reset-basis>RESET STRUCTURAL REST BASIS</button>
          </section>
          <section>
            <p class="fabric-kicker">DYNAMIC FIELD PAIR</p>
            ${slider({channel: 'authority', label: `AUTHORITY - ${geometricField.dynamicStanding.authority}`, value: geometricField.weights.dynamic.authority, minimum: 0, maximum: 1, step: 0.05, disabled: true})}
            ${slider({channel: 'consequence', label: `CONSEQUENCE - ${geometricField.dynamicStanding.consequence}`, value: geometricField.weights.dynamic.consequence, minimum: 0, maximum: 1, step: 0.05, disabled: true})}
            <p class="fabric-unavailable-note">No source-backed dynamic telemetry exists in this fabric. No displacement is fabricated.</p>
          </section>
          <section class="fabric-relation-ledger">
            <p class="fabric-kicker">MECHANICAL RELATION LEDGER</p>
            <dl>
              <div><dt>CONTAINS</dt><dd>${counts.containment}</dd></div>
              <div><dt>HAS_VERSION</dt><dd>${counts.version}</dd></div>
              <div><dt>DEPENDENCY / REFERENCE</dt><dd>${counts.dependency || 'UNAVAILABLE'}</dd></div>
            </dl>
          </section>
        </aside>
        ${renderInspector(model, geometricField)}
      </div>
      <section class="fabric-ceiling">
        <p class="fabric-kicker">CLAIM CEILING</p>
        <p>${escapeHtml(source.claim_ceiling)}</p>
        <p>SCIENTIFIC OPERATOR != SOURCE TRUTH. NO NEW AUTHORITY. NO NEW EXECUTION. NO NEW CONTROL PATH.</p>
      </section>
    </main>
  `;
}

function canvasSize(canvas) {
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(320, Math.floor(rect.width));
  const height = Math.max(320, Math.floor(rect.height));
  const ratio = Math.min(2, globalThis.devicePixelRatio || 1);
  const pixelWidth = Math.floor(width * ratio);
  const pixelHeight = Math.floor(height * ratio);
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }
  return {width, height, ratio};
}

function nodeColor(kind) {
  return {repository: '#f0f5f3', directory: '#b8a1ff', file: '#5ad7df', file_version: '#78d99a'}[kind] || '#e5eef2';
}

function nodeRadius(kind) {
  return {repository: 7, directory: 4.5, file: 2.5, file_version: 1.8}[kind] || 2;
}

export function drawGeometricRepositoryField(canvas, model, geometricField) {
  const {width, height, ratio} = canvasSize(canvas);
  const context = canvas.getContext('2d');
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  context.fillStyle = '#070c11';
  context.fillRect(0, 0, width, height);
  const projectedById = Object.create(null);
  for (const node of geometricField.nodes) {
    projectedById[node.objectId] = projectFieldPoint(node.currentPosition, geometricField.camera, width, height);
  }

  const directoryNodes = geometricField.nodes
    .filter((node) => node.objectKind === 'repository' || node.objectKind === 'directory')
    .sort((left, right) => right.depth - left.depth);
  for (const node of directoryNodes) {
    const projected = projectedById[node.objectId];
    if (!projected.visible) continue;
    const radius = Math.max(7, geometricField.volumeRadiusById[node.objectId] * projected.scale);
    context.beginPath(); context.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
    context.fillStyle = node.objectKind === 'repository' ? 'rgba(240,245,243,.018)' : 'rgba(184,161,255,.018)';
    context.strokeStyle = node.objectKind === 'repository' ? 'rgba(240,245,243,.18)' : 'rgba(184,161,255,.14)';
    context.lineWidth = node.objectKind === 'repository' ? 1.2 : 0.7;
    context.fill(); context.stroke();
  }

  let renderedRelations = 0;
  for (const edge of [...geometricField.structuralEdges, ...geometricField.dependencyEdges]) {
    const source = projectedById[edge.source_id];
    const target = projectedById[edge.target_id];
    if (!source?.visible || !target?.visible) continue;
    const fineVersionEdge = edge.relation === 'HAS_VERSION';
    const selectedEdge = edge.source_id === model.selectedObjectId || edge.target_id === model.selectedObjectId;
    if (fineVersionEdge && geometricField.camera.distance > 1050 && !selectedEdge) continue;
    context.beginPath(); context.moveTo(source.x, source.y); context.lineTo(target.x, target.y);
    context.strokeStyle = edge.relation === 'CONTAINS'
      ? 'rgba(90,215,223,.10)'
      : edge.relation === 'HAS_VERSION' ? 'rgba(120,217,154,.18)' : 'rgba(255,190,92,.38)';
    context.lineWidth = selectedEdge ? 1.3 : 0.55;
    context.stroke();
    renderedRelations += 1;
  }

  const matches = new Set(model.query ? repositoryQueryMatches(model).map((object) => object.object_id) : []);
  const painterOrder = [...geometricField.nodes]
    .filter((node) => projectedById[node.objectId].visible)
    .sort((left, right) => projectedById[right.objectId].depth - projectedById[left.objectId].depth);
  let renderedObjects = 0;
  for (const node of painterOrder) {
    const projected = projectedById[node.objectId];
    const selected = node.objectId === model.selectedObjectId;
    const matched = matches.has(node.objectId);
    const radius = nodeRadius(node.objectKind) + (selected ? 2.5 : 0);
    context.beginPath(); context.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
    context.fillStyle = nodeColor(node.objectKind);
    context.globalAlpha = Math.max(0.38, Math.min(1, 1150 / projected.depth));
    context.fill(); context.globalAlpha = 1;
    if (selected || matched) {
      context.beginPath(); context.arc(projected.x, projected.y, radius + 5, 0, Math.PI * 2);
      context.strokeStyle = selected ? '#ffffff' : '#ffbe5c';
      context.lineWidth = selected ? 2 : 1.2; context.stroke();
    }
    const topDirectory = node.objectKind === 'directory' && node.depth === 1;
    const showLabel = selected || matched || node.objectKind === 'repository' || topDirectory
      || (geometricField.camera.distance < 520 && node.objectKind !== 'file_version');
    if (showLabel) {
      context.fillStyle = selected ? '#ffffff' : nodeColor(node.objectKind);
      context.font = selected ? '600 12px ui-monospace, monospace' : '10px ui-monospace, monospace';
      context.fillText(node.sourceObject.path || node.sourceObject.repository_identity, projected.x + radius + 5, projected.y - 3);
    }
    renderedObjects += 1;
  }
  return {width, height, projectedById, renderedObjects, renderedRelations};
}

export function pickGeometricRepositoryObject(frame, geometricField, x, y) {
  let best = null;
  let bestDistance = Infinity;
  for (const node of geometricField.nodes) {
    const projected = frame.projectedById[node.objectId];
    if (!projected?.visible) continue;
    const distance = Math.hypot(projected.x - x, projected.y - y);
    const threshold = Math.max(7, nodeRadius(node.objectKind) + 4);
    if (distance <= threshold && distance < bestDistance) {
      best = node.objectId;
      bestDistance = distance;
    }
  }
  return best;
}

export function renderRepositoryFabricUnavailable(message) {
  return `
    <main class="fabric-unavailable">
      <p class="fabric-kicker">SOURCE UNAVAILABLE - UNKNOWN_REGION</p>
      <h1>Geometric repository field cannot be projected</h1>
      <p>${escapeHtml(message)}</p>
      <p>No cached tree, inferred repository objects, or fabricated telemetry are displayed.</p>
    </main>
  `;
}
