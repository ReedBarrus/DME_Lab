import {
  repositoryObjectRelations,
  selectedRepositoryObject,
  visibleRepositoryObjects,
} from './repository_fabric_model.mjs';

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function value(value, fallback = 'NOT_APPLICABLE') {
  if (value === null || value === undefined || value === '') {
    return `<span class="fabric-missing">${escapeHtml(fallback)}</span>`;
  }
  return `<code>${escapeHtml(value)}</code>`;
}

function field(label, content) {
  return `<div class="fabric-field"><dt>${escapeHtml(label)}</dt><dd>${content}</dd></div>`;
}

function depth(object) {
  if (object.object_kind === 'repository') return 0;
  const pathDepth = (object.path.match(/\//g) || []).length + 1;
  return object.object_kind === 'file_version' ? pathDepth + 1 : pathDepth;
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
      direction: 'IN',
      relation: relation.relation,
      coordinate: model.objectById[relation.source_id]?.path || '/',
    })),
    ...relations.outgoing.map((relation) => ({
      direction: 'OUT',
      relation: relation.relation,
      coordinate: relationTarget(relation, model),
    })),
  ];
  if (!rows.length) return '<p class="fabric-missing">NO MECHANICAL RELATIONS</p>';
  return `<ul class="fabric-relations">${rows.map((row) => `
    <li><span>${escapeHtml(row.direction)}</span><strong>${escapeHtml(row.relation)}</strong><code>${escapeHtml(row.coordinate)}</code></li>
  `).join('')}</ul>`;
}

function renderObjectList(model) {
  const objects = visibleRepositoryObjects(model);
  return `
    <div class="fabric-list-summary">${objects.length} / ${model.objects.length} objects visible</div>
    <div class="fabric-object-list" role="tree">
      ${objects.map((object) => {
        const selected = object.object_id === model.selectedObjectId;
        const label = object.path || object.repository_identity;
        return `
          <button
            type="button"
            role="treeitem"
            aria-selected="${selected ? 'true' : 'false'}"
            class="fabric-object ${selected ? 'is-selected' : ''}"
            style="--depth:${depth(object)}"
            data-repository-object-id="${escapeHtml(object.object_id)}"
          >
            <span>${escapeHtml(object.object_kind)}</span>
            <strong>${escapeHtml(label)}</strong>
            <em>${escapeHtml(object.semantic_standing)}</em>
          </button>
        `;
      }).join('')}
    </div>
  `;
}

function renderInspector(model) {
  const object = selectedRepositoryObject(model);
  if (!object) return '<aside class="fabric-inspector">NO OBJECT SELECTED</aside>';
  const typed = object.typed_projections?.length
    ? `<ul>${object.typed_projections.map((item) => `<li>${escapeHtml(JSON.stringify(item))}</li>`).join('')}</ul>`
    : '<span class="fabric-missing">NONE — SEMANTIC ROLE NOT DERIVED</span>';
  const address = JSON.stringify(object.address, null, 2);
  return `
    <aside class="fabric-inspector" aria-labelledby="fabric-inspector-title">
      <header>
        <p class="fabric-kicker">SOURCE OBJECT INSPECTOR</p>
        <h2 id="fabric-inspector-title">${escapeHtml(object.path || object.repository_identity)}</h2>
        <span class="fabric-standing">${escapeHtml(object.semantic_standing)}</span>
      </header>
      <dl>
        ${field('OBJECT_KIND', value(object.object_kind))}
        ${field('REPOSITORY_IDENTITY', value(object.repository_identity))}
        ${field('SOURCE_COMMIT', value(object.source_commit))}
        ${field('SOURCE_BRANCH', value(object.source_branch, 'DETACHED_OR_NOT_DERIVED'))}
        ${field('PATH', value(object.path || '/'))}
        ${field('PARENT_PATH', value(object.parent_path, 'ROOT_HAS_NO_PARENT'))}
        ${field('PATH_IDENTITY', `<pre>${escapeHtml(JSON.stringify(object.path_identity, null, 2))}</pre>`)}
        ${field('GIT_BLOB_IDENTITY', value(object.git_blob_identity))}
        ${field('CONTENT_IDENTITY', value(object.content_identity))}
        ${field('EXISTENCE_STANDING', value(object.existence_standing))}
        ${field('SEMANTIC_STANDING', value(object.semantic_standing))}
        ${field('TYPED_PROJECTIONS', typed)}
        ${field('MECHANICAL_RELATIONS', renderRelations(model, object))}
        ${field('CANONICAL_ADDRESS', `
          <pre class="fabric-address">${escapeHtml(address)}</pre>
          <button type="button" class="fabric-copy" data-copy-repository-address="${escapeHtml(object.object_id)}">COPY EXACT ADDRESS</button>
        `)}
      </dl>
    </aside>
  `;
}

export function renderRepositoryFabric(model) {
  const source = model.source;
  return `
    <header class="fabric-hero">
      <div>
        <p class="fabric-kicker">REPOSITORY ADDRESS FABRIC V0 · DERIVED READ-ONLY</p>
        <h1>${escapeHtml(source.repository_identity)}</h1>
        <p>Every committed object is addressable before semantic interpretation.</p>
      </div>
      <dl class="fabric-coordinate">
        <div><dt>BRANCH</dt><dd>${escapeHtml(source.source_branch || 'NOT_DERIVED')}</dd></div>
        <div><dt>COMMIT</dt><dd><code>${escapeHtml(source.source_commit)}</code></dd></div>
        <div><dt>AUTHORITY EFFECT</dt><dd>${escapeHtml(source.authority_effect)}</dd></div>
        <div><dt>EXECUTION EFFECT</dt><dd>${escapeHtml(source.execution_effect)}</dd></div>
      </dl>
    </header>
    <section class="fabric-laws">
      <span>UNKNOWN SEMANTICS != INVISIBLE OBJECT</span>
      <span>PATH IDENTITY != CONTENT IDENTITY</span>
      <span>FILE OBJECT != FILE VERSION</span>
      <span>SAME ADDRESS != SAME AUTHORITY</span>
    </section>
    <div class="fabric-workbench">
      <main class="fabric-browser">
        <label class="fabric-search">
          <span>FILTER ADDRESSED OBJECTS</span>
          <input type="search" data-repository-query value="${escapeHtml(model.query)}" placeholder="path, kind, hash, standing">
        </label>
        ${renderObjectList(model)}
      </main>
      ${renderInspector(model)}
    </div>
    <section class="fabric-ceiling">
      <p class="fabric-kicker">CLAIM CEILING</p>
      <p>${escapeHtml(source.claim_ceiling)}</p>
    </section>
  `;
}

export function renderRepositoryFabricUnavailable(message) {
  return `
    <main class="fabric-unavailable">
      <p class="fabric-kicker">SOURCE UNAVAILABLE · UNKNOWN_REGION</p>
      <h1>Repository address fabric cannot be projected</h1>
      <p>${escapeHtml(message)}</p>
      <p>No cached tree or inferred repository objects are displayed.</p>
    </main>
  `;
}
