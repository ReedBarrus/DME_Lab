import { selectedInspectable } from './cell002_model.mjs';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function renderList(values, empty = 'NOT_DERIVED') {
  if (!Array.isArray(values) || values.length === 0) {
    return `<p class="empty-value">${escapeHtml(empty)}</p>`;
  }
  return `<ul>${values.map((value) => `<li>${escapeHtml(value)}</li>`).join('')}</ul>`;
}

function badge(label, tone = '') {
  return `<span class="standing-badge ${escapeHtml(tone)}">${escapeHtml(label)}</span>`;
}

function renderCurrentness(model) {
  const standing = model.standing;
  const items = [
    ['SOURCE CURRENTNESS', standing.sourceCurrentness],
    ['HISTORICAL STANDING', standing.historicalStanding],
    ['CURRENT STANDING', standing.currentStanding],
    ['CURRENT AUTHORITY', standing.currentAuthority],
    ['HISTORICAL AUTHORITY', standing.historicalAuthority],
  ];
  return `
    <section class="currentness-strip" aria-label="Specimen currentness and standing">
      ${items.map(([title, item]) => `
        <article class="currentness-card" data-primitive="STANDING">
          <p class="eyebrow">${escapeHtml(title)}</p>
          ${badge(item.label, item.label.toLowerCase().replaceAll('_', '-'))}
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `).join('')}
    </section>
  `;
}

function renderInspectableCard(model, id, style) {
  const item = model.inspectableById[id];
  const selected = model.selectedInspectableId === id;
  return `
    <button
      type="button"
      class="trajectory-card ${escapeHtml(style)} ${selected ? 'is-selected' : ''}"
      data-inspect-id="${escapeHtml(id)}"
      data-primitive="${escapeHtml(item.kind)}"
      aria-pressed="${selected ? 'true' : 'false'}"
    >
      <span class="primitive-label">${escapeHtml(item.kind)}</span>
      <strong>${escapeHtml(item.title)}</strong>
      <span class="state-lines">${item.afterState.map(escapeHtml).join('<br>')}</span>
      <span class="micro-standing">CURRENTNESS ${escapeHtml(item.sourceCurrentness.label)} · AUTHORITY ${escapeHtml(item.currentAuthority.label)}</span>
    </button>
  `;
}

function renderEdge(model, id) {
  const item = model.inspectableById[id];
  const selected = model.selectedInspectableId === id;
  return `
    <button
      type="button"
      class="trajectory-edge ${selected ? 'is-selected' : ''}"
      data-inspect-id="${escapeHtml(id)}"
      data-primitive="TRANSFORMATION"
      aria-pressed="${selected ? 'true' : 'false'}"
    >
      <span class="edge-line" aria-hidden="true"></span>
      <span class="edge-copy">
        <span class="primitive-label">TRANSFORMATION</span>
        <strong>${escapeHtml(item.operator)}</strong>
        <small>witness · ${escapeHtml(item.witness)}</small>
      </span>
      <span class="edge-arrow" aria-hidden="true">→</span>
    </button>
  `;
}

function renderControl(model) {
  const sequence = [
    renderInspectableCard(model, 'control-active', 'state-active'),
    renderEdge(model, 'control-reserve'),
    renderInspectableCard(model, 'control-consuming', 'state-consuming'),
    renderEdge(model, 'control-invoke'),
    renderInspectableCard(model, 'control-invoked', 'state-observed'),
    renderEdge(model, 'control-finalize'),
    renderInspectableCard(model, 'control-consumed', 'state-consumed'),
  ];
  return `
    <section class="specimen-panel control-panel" aria-labelledby="control-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow">CONTROL TRAJECTORY · OBSERVED</p>
          <h2 id="control-title">One use crosses the governed boundary</h2>
        </div>
        ${badge('QUALIFIED', 'qualified')}
      </div>
      <div class="trajectory-scroll">
        <div class="trajectory control-trajectory">${sequence.join('')}</div>
      </div>
      <div class="coordinate-register" data-primitive="RELATION" aria-label="Exact bound control coordinates">
        ${Object.entries(model.coordinates.control).map(([key, value]) => `
          <p><span>${escapeHtml(key)}</span><code>${escapeHtml(value)}</code></p>
        `).join('')}
      </div>
      <p class="reading-note">Select any object, state, witness, or transformation to challenge its basis.</p>
    </section>
  `;
}

function renderPressureLane(model, config) {
  const nodeA = renderInspectableCard(model, config.nodes[0], config.startStyle);
  const edge = renderEdge(model, config.edges[0]);
  const nodeB = renderInspectableCard(model, config.nodes[1], config.endStyle);
  return `
    <section class="specimen-panel pressure-panel" aria-labelledby="${escapeHtml(config.id)}-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow">${escapeHtml(config.eyebrow)}</p>
          <h2 id="${escapeHtml(config.id)}-title">${escapeHtml(config.title)}</h2>
        </div>
        ${badge(config.badge, config.badge.toLowerCase().replaceAll('_', '-'))}
      </div>
      <div class="pressure-trajectory">${nodeA}${edge}${nodeB}</div>
      <div class="diff-grid" aria-label="Control pressure difference">
        <article class="diff-card changed">
          <p class="eyebrow">CHANGED</p>
          ${renderList(config.changed)}
        </article>
        <article class="diff-card held">
          <p class="eyebrow">HELD FIXED</p>
          ${renderList(config.heldFixed)}
        </article>
        <article class="diff-card effect">
          <p class="eyebrow">OBSERVED EFFECT</p>
          ${renderList(config.observedEffect)}
        </article>
      </div>
    </section>
  `;
}

function renderTraversal(model, item) {
  const ids = model.selectedTraversal === 'WHY' ? item.backward : item.forward;
  const title = model.selectedTraversal === 'WHY'
    ? 'WHY IS THIS STATE HERE?'
    : 'WHAT DID THIS TRANSFORMATION CAUSE?';
  return `
    <div class="traversal-block">
      <div class="traversal-tabs" role="group" aria-label="Provenance traversal direction">
        <button type="button" data-traversal="WHY" class="${model.selectedTraversal === 'WHY' ? 'is-selected' : ''}">WHY IS THIS STATE HERE?</button>
        <button type="button" data-traversal="CAUSE" class="${model.selectedTraversal === 'CAUSE' ? 'is-selected' : ''}">WHAT DID THIS TRANSFORMATION CAUSE?</button>
      </div>
      <p class="eyebrow">${title}</p>
      <div class="traversal-chain">
        ${ids.length === 0
          ? '<span class="empty-value">No further witnessed relation.</span>'
          : ids.map((id) => {
            const linked = model.inspectableById[id];
            return linked
              ? `<button type="button" data-inspect-id="${escapeHtml(id)}"><span>${escapeHtml(linked.kind)}</span>${escapeHtml(linked.title)}</button>`
              : `<span>${escapeHtml(id)}</span>`;
          }).join('<span class="chain-arrow" aria-hidden="true">←</span>')}
      </div>
    </div>
  `;
}

function inspectorField(label, content) {
  return `
    <div class="inspector-field">
      <dt>${escapeHtml(label)}</dt>
      <dd>${content}</dd>
    </div>
  `;
}

export function renderInspector(model) {
  const item = selectedInspectable(model);
  if (!item) {
    return '<aside class="edge-inspector"><p>UNRESOLVED: no inspectable selection.</p></aside>';
  }
  return `
    <aside class="edge-inspector" aria-labelledby="inspector-title">
      <div class="inspector-header">
        <div>
          <p class="eyebrow">EDGE INSPECTOR · ${escapeHtml(item.kind)}</p>
          <h2 id="inspector-title">${escapeHtml(item.title)}</h2>
        </div>
        ${badge(item.standingEarned, item.standingEarned.toLowerCase())}
      </div>
      <dl class="inspector-fields">
        ${inspectorField('BEFORE_OBJECT', `<code>${escapeHtml(item.beforeObject)}</code>`)}
        ${inspectorField('BEFORE_STATE', renderList(item.beforeState))}
        ${inspectorField('TRANSFORMATION / OPERATOR', `<p>${escapeHtml(item.operator)}</p>`)}
        ${inspectorField('BASIS', `<p>${escapeHtml(item.basis)}</p>`)}
        ${inspectorField('WITNESS', `<code>${escapeHtml(item.witness)}</code>`)}
        ${inspectorField('AFTER_OBJECT', `<code>${escapeHtml(item.afterObject)}</code>`)}
        ${inspectorField('AFTER_STATE', renderList(item.afterState))}
        ${inspectorField('WHAT_CHANGED', renderList(item.whatChanged))}
        ${inspectorField('WHAT_DID_NOT_CHANGE', renderList(item.whatDidNotChange))}
        ${inspectorField('STANDING_EARNED', badge(item.standingEarned, item.standingEarned.toLowerCase()))}
        ${inspectorField('CLAIM_CEILING', `<p>${escapeHtml(item.claimCeiling)}</p>`)}
        ${inspectorField('UNRESOLVED', renderList(item.unresolved, 'none declared'))}
        ${inspectorField('SOURCE_ARTIFACTS', renderList(item.sourceArtifacts))}
      </dl>
      ${renderTraversal(model, item)}
    </aside>
  `;
}

function renderUnknownRegion(model) {
  const unknown = model.unknownRegion;
  return `
    <section class="unknown-region" data-primitive="UNKNOWN_REGION" aria-labelledby="unknown-title">
      <div class="unknown-glyph" aria-hidden="true">?</div>
      <div>
        <p class="eyebrow">UNKNOWN_REGION · ${escapeHtml(unknown.standing)}</p>
        <h2 id="unknown-title">Evidence stops here</h2>
        <p>${escapeHtml(unknown.rule)}</p>
        <div class="future-shape" aria-label="Future sparse specimen compatibility">
          ${unknown.futureShape.map((part) => `<span>${escapeHtml(part)}</span>`).join('<i aria-hidden="true">→</i>')}
        </div>
      </div>
      <div class="unknown-list">${renderList(unknown.items)}</div>
    </section>
  `;
}

function renderSources(model) {
  return `
    <section class="source-register" aria-labelledby="sources-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow">PROVENANCE REGISTER</p>
          <h2 id="sources-title">Exact admitted source artifacts</h2>
        </div>
        ${badge('PROJECTED', 'projected')}
      </div>
      <div class="source-grid">
        ${model.sourceArtifacts.map((source) => `
          <article class="source-card" data-primitive="WITNESS">
            <p class="eyebrow">${escapeHtml(source.role)}</p>
            <a href="../../../${escapeHtml(source.path)}"><code>${escapeHtml(source.path)}</code></a>
            ${source.sha256 ? `<p><span>SHA-256</span><code>${escapeHtml(source.sha256)}</code></p>` : '<p class="empty-value">CONTENT HASH NOT_DERIVED IN THIS VIEW</p>'}
          </article>
        `).join('')}
      </div>
    </section>
  `;
}

export function renderCell002Specimen(model) {
  return `
    <header class="hero">
      <div class="hero-brand" aria-label="DME Cockpit">
        <span class="brand-mark">DME</span>
        <span>COCKPIT / SPECIMEN 001</span>
      </div>
      <div class="hero-copy">
        <p class="eyebrow">AUTHORITY MEMBRANE · CELL 002</p>
        <h1>${escapeHtml(model.title)}</h1>
        <p>${escapeHtml(model.subtitle)}</p>
      </div>
      <div class="primitive-key" aria-label="Visual grammar">
        ${model.semanticPrimitives.map((primitive) => `<span>${escapeHtml(primitive)}</span>`).join('')}
      </div>
    </header>
    ${renderCurrentness(model)}
    <div class="workbench">
      <main class="specimen-main">
        ${renderControl(model)}
        ${renderPressureLane(model, {
          ...model.replay,
          id: 'replay',
          eyebrow: 'PRESSURE A · EXACT REPLAY',
          title: 'Consumed means unavailable',
          badge: 'QUALIFIED',
          startStyle: 'state-consumed',
          endStyle: 'state-denied',
        })}
        ${renderPressureLane(model, {
          ...model.wrongPrincipal,
          id: 'wrong-principal',
          eyebrow: 'PRESSURE B · DECLARED PRINCIPAL',
          title: 'A mismatch cannot reserve authority',
          badge: 'QUALIFIED',
          startStyle: 'state-active',
          endStyle: 'state-preserved',
        })}
        ${renderUnknownRegion(model)}
        ${renderSources(model)}
      </main>
      ${renderInspector(model)}
    </div>
    <footer class="specimen-footer">
      <p>Derived read-only projection. Source artifacts remain authoritative.</p>
      <p>Test metadata · ${escapeHtml(model.testMetadata.pressureResult)} · real HTTP calls ${escapeHtml(model.testMetadata.realHttpCalls)} · observed ${escapeHtml(model.testMetadata.observedAt)}</p>
    </footer>
  `;
}

export function renderUnavailable(message) {
  return `
    <main class="specimen-unavailable" data-primitive="UNKNOWN_REGION">
      <p class="eyebrow">UNKNOWN_REGION · SOURCE UNAVAILABLE</p>
      <h1>Cell 002 specimen cannot be projected</h1>
      <p>${escapeHtml(message)}</p>
      <p>No cached or inferred trajectory is displayed.</p>
    </main>
  `;
}
