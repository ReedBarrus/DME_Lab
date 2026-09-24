import {
  projectFieldPoint,
  repositoryFieldRelationCounts,
} from './repository_fabric_geometry.mjs';
import {
  repositoryObjectRelations,
  repositoryQueryMatches,
  selectedRepositoryObject,
} from './repository_fabric_model.mjs';
import { classificationsForObject } from './cell002_episode_overlay.mjs';
import {
  aggregateTransitionEmissions,
  emissionScaleRegime,
} from './repository_temporal_lineage.mjs';
import {
  distinctionsForObject,
  reconstructionHandleFor,
} from './typed_distinction_registry.mjs';

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

function renderSourceHandles(handles) {
  return `<ol class="scientific-source-handles">${handles.map((handle) => `
    <li>
      <strong>${escapeHtml(handle.handleKind)}</strong>
      ${handle.path ? `<code>${escapeHtml(handle.path)}</code>` : ''}
      ${handle.jsonPointer ? `<code>${escapeHtml(handle.jsonPointer)}</code>` : ''}
      ${'observedValue' in handle ? `<pre>${escapeHtml(JSON.stringify(handle.observedValue, null, 2))}</pre>` : ''}
      ${handle.contentIdentity ? `<code>${escapeHtml(handle.contentIdentity)}</code>` : ''}
    </li>
  `).join('')}</ol>`;
}

function renderScientificChallenge(episode, object) {
  const classifications = classificationsForObject(episode, object);
  return `
    <section class="scientific-challenge">
      <p class="fabric-kicker">SCIENTIFIC CHALLENGE - CLICKED SOURCE OBJECT</p>
      ${classifications.map((classification) => `
        <article class="scientific-classification is-${classification.category.toLowerCase()}">
          <header>
            <span>${escapeHtml(classification.category)}</span>
            <strong>${escapeHtml(classification.title)}</strong>
          </header>
          <dl>
            ${field('SOURCE_SUPPORT', value(classification.supportStatus))}
            ${field('WHAT_CHANGED', value(classification.whatChanged.join('; '), 'NONE CLAIMED'))}
            ${field('WHAT_DID_NOT_CHANGE', value(classification.whatDidNotChange.join('; '), 'NONE CLAIMED'))}
            ${field('CLAIM_CEILING', value(classification.claimCeiling))}
            ${field('UNRESOLVED', value(classification.unresolved.join('; '), 'NONE RECORDED'))}
            ${field('SOURCE_ARTIFACTS / WITNESS HANDLES', renderSourceHandles(classification.sourceHandles))}
          </dl>
        </article>
      `).join('')}
    </section>
  `;
}

function renderTransitionChallenge(temporalView) {
  const eventId = temporalView?.state?.selectedEmissionId;
  const emission = eventId ? temporalView.emissionLedger?.eventById[eventId] : null;
  if (!emission) return '';
  const event = emission.mechanical_diff;
  return `
    <section class="temporal-challenge">
      <p class="fabric-kicker">TRANSITION CHALLENGE - SOURCE-SUPPORTED EMISSION</p>
      <h3>${escapeHtml(event.classifications.join(' + '))}</h3>
      <dl>
        ${field('FROM_FRAME', value(emission.from_frame_id))}
        ${field('TO_FRAME', value(emission.to_frame_id))}
        ${field('SOURCE_OBJECT', value(event.old_path, 'NOT_PRESENT'))}
        ${field('DESTINATION_OBJECT', value(event.new_path, 'NOT_PRESENT'))}
        ${field('MECHANICAL_DIFF', `<pre>${escapeHtml(JSON.stringify({status: event.status, old_mode: event.old_mode, new_mode: event.new_mode}, null, 2))}</pre>`)}
        ${field('BLOB IDENTITIES', `<pre>${escapeHtml(JSON.stringify({before: event.old_object_sha, after: event.new_object_sha}, null, 2))}</pre>`)}
        ${field('RELATIONS ADDED / REMOVED', `<pre>${escapeHtml(JSON.stringify(event.relation_changes, null, 2))}</pre>`)}
        ${field('DECLARED OPERATIONAL RELATIONS', `<pre>${escapeHtml(JSON.stringify(event.declared_operational_relations || [], null, 2))}</pre>`)}
        ${field('IDENTITY BASIS', value(event.identity_basis))}
        ${field('ACTOR LINEAGE', value(emission.actor_lineage))}
        ${field('SEMANTIC LINEAGE', value(emission.semantic_lineage))}
        ${field('SOURCE HANDLES', renderSourceHandles(emission.source_handles.map((handle) => ({
          handleKind: handle.handle_kind,
          observedValue: handle,
        }))))}
      </dl>
    </section>
  `;
}

function renderMissingTemporalSelection(temporalView) {
  const state = temporalView?.state;
  if (!state || state.selectionStanding === 'PRESENT_IN_FRAME') return '';
  return `
    <section class="temporal-missing-selection">
      <strong>${escapeHtml(state.selectionStanding)}</strong>
      <code>${escapeHtml(state.missingSelection?.temporalIdentity)}</code>
      ${state.missingSelection?.transitionEventId
        ? `<code>${escapeHtml(state.missingSelection.transitionEventId)}</code>` : ''}
      <p>No synthetic persistence or rename continuity was created.</p>
    </section>
  `;
}

function renderDistinctions(object, temporalView) {
  const registry = temporalView?.typedDistinctionRegistry;
  const distinctions = distinctionsForObject(registry, object);
  if (!distinctions.length) {
    return `
      <section class="typed-distinction-section">
        <p class="fabric-kicker">DISTINCTIONS</p>
        <p class="fabric-missing">NO ADMITTED SOURCE-BOUND DISTINCTIONS</p>
      </section>
    `;
  }
  return `
    <section class="typed-distinction-section">
      <p class="fabric-kicker">DISTINCTIONS</p>
      ${distinctions.map((distinction) => {
        const reconstruction = reconstructionHandleFor(registry, distinction.distinction_id);
        return `
          <article class="typed-distinction is-${escapeHtml(distinction.standing.toLowerCase())}">
            <h3>${escapeHtml(distinction.value.left)} != ${escapeHtml(distinction.value.right)}</h3>
            <dl>
              ${field('RELATION_TYPE', value(distinction.relation_type))}
              ${field('STANDING', value(distinction.standing))}
              ${field('CURRENTNESS', value(distinction.currentness))}
              ${field('SOURCE_HANDLES', `<pre>${escapeHtml(JSON.stringify(distinction.resolved_source_handles, null, 2))}</pre>`)}
              ${field('CLAIM_CEILING', value(distinction.claim_ceiling))}
              ${field('DEPENDENCIES', `<pre>${escapeHtml(JSON.stringify(distinction.dependencies, null, 2))}</pre>`)}
              ${field('UNRESOLVED', `<pre>${escapeHtml(JSON.stringify(distinction.unresolved, null, 2))}</pre>`)}
              ${field('CHALLENGE / RECONSTRUCTION HANDLE', reconstruction
                ? `<pre>${escapeHtml(JSON.stringify(reconstruction, null, 2))}</pre>`
                : '<span class="fabric-missing">UNAVAILABLE</span>')}
            </dl>
          </article>
        `;
      }).join('')}
    </section>
  `;
}

function renderInspector(model, geometricField, episode, operatorState, temporalView) {
  const object = selectedRepositoryObject(model);
  if (!object) return '<aside class="fabric-inspector">NO OBJECT SELECTED</aside>';
  if (operatorState?.inspectorCollapsed) {
    return `<aside class="fabric-inspector is-collapsed"><button type="button" data-toggle-inspector>OPEN INSPECTOR</button></aside>`;
  }
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
          <button type="button" data-toggle-inspector>COLLAPSE INSPECTOR</button>
        </div>
      </header>
      ${operatorState?.overlay === 'SCIENTIFIC_EPISODE' && episode
        ? renderScientificChallenge(episode, object)
        : ''}
      ${renderMissingTemporalSelection(temporalView)}
      ${renderTransitionChallenge(temporalView)}
      ${renderDistinctions(object, temporalView)}
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
        ${object.object_kind === 'seat' || object.object_kind === 'cursor'
          ? field('ACTOR SOURCE', `<pre>${escapeHtml(JSON.stringify(object.source_artifact, null, 2))}</pre>`)
          : ''}
        ${object.object_kind === 'seat'
          ? field('SEAT / OCCUPANT / AUTHORITY', `<pre>${escapeHtml(JSON.stringify({
            seat_id: object.seat_id,
            consumer_id: object.consumer_id,
            trigger_state: object.trigger_state,
            occupant_binding: object.occupant_binding,
            authority_effect: object.authority_effect,
            execution_effect: object.execution_effect,
          }, null, 2))}</pre>`)
          : ''}
        ${object.object_kind === 'cursor'
          ? field('CURSOR COORDINATE', `<pre>${escapeHtml(JSON.stringify({
            consumer_id: object.consumer_id,
            cursor_state: object.cursor_state,
            last_seen_event_id: object.last_seen_event_id,
            bootstrap_mode: object.bootstrap_mode,
          }, null, 2))}</pre>`)
          : ''}
        ${field('TYPED_PROJECTIONS', typed)}
        ${field('MECHANICAL_RELATIONS', renderRelations(model, object))}
        ${field('CANONICAL_ADDRESS', `<pre class="fabric-address">${escapeHtml(address)}</pre>`)}
      </dl>
    </aside>
  `;
}

function renderTemporalOperator(temporalView) {
  if (!temporalView?.lineage) {
    return `<section class="fabric-temporal-operator is-unavailable"><p class="fabric-kicker">TEMPORAL LINEAGE</p><strong>UNAVAILABLE</strong></section>`;
  }
  const {lineage, state, emissionLedger} = temporalView;
  const frame = lineage.frames[state.frameIndex];
  const incoming = emissionLedger?.transition;
  const wound = lineage.woundReplay;
  const woundStep = state.woundActive ? wound.steps[state.woundStep] : null;
  return `
    <section class="fabric-temporal-operator">
      <p class="fabric-kicker">TEMPORAL LINEAGE OPERATOR V0</p>
      <label class="temporal-frame-control">
        <span>FRAME ${state.frameIndex + 1} / ${lineage.frames.length}</span>
        <input type="range" min="0" max="${lineage.frames.length - 1}" step="1"
          value="${state.frameIndex}" data-temporal-frame>
      </label>
      <code>${escapeHtml(frame.commit_sha)}</code>
      <small>${escapeHtml(frame.subject)}</small>
      <dl>
        ${field('FRAME_ID', value(frame.frame_id))}
        ${field('TREE_IDENTITY', value(frame.tree_sha))}
        ${field('GIT_AUTHOR - METADATA ONLY', `<pre>${escapeHtml(JSON.stringify(frame.git_author, null, 2))}</pre>`)}
        ${field('SEAT_ACTOR', value('UNRESOLVED UNLESS EXPLICIT SOURCE BINDS TRANSITION'))}
        ${field('INCOMING_TRANSITION', value(incoming?.transition_id, 'ROOT FRAME'))}
        ${field('TRANSITION EVENTS', value(incoming?.event_count, '0'))}
      </dl>
      <button type="button" data-toggle-actor-layer>${state.actorLayer ? 'HIDE' : 'SHOW'} SEATS / CURSORS</button>
      <button type="button" data-activate-wound>${state.woundActive ? 'RESTART' : 'REPLAY'} PATH IDENTITY WOUND</button>
      ${state.woundActive ? `
        <div class="wound-replay-controls">
          <strong>${escapeHtml(wound.family)}</strong>
          ${wound.steps.map((step, index) => `
            <button type="button" data-wound-step="${index}" class="${index === state.woundStep ? 'is-current' : ''}">
              ${index + 1}. ${escapeHtml(step.mechanical_diff.classifications.join(' + '))}
            </button>
          `).join('')}
          <p>ACTOR: ${escapeHtml(woundStep.actor_lineage)} / SEMANTIC CAUSE: ${escapeHtml(woundStep.semantic_lineage)}</p>
        </div>
      ` : ''}
    </section>
  `;
}

function renderEpisodeOperator(episode, operatorState, episodeError) {
  if (!episode) {
    return `
      <section class="fabric-episode-operator is-unavailable">
        <p class="fabric-kicker">OPERATOR - SCIENTIFIC EPISODE</p>
        <strong>EPISODE UNAVAILABLE</strong>
        <p>${escapeHtml(episodeError || 'No exact source-bound episode was loaded.')}</p>
      </section>
    `;
  }
  const active = operatorState.overlay === 'SCIENTIFIC_EPISODE';
  const step = episode.sequence[operatorState.episodeStep];
  return `
    <section class="fabric-episode-operator ${active ? 'is-active' : ''}">
      <p class="fabric-kicker">OPERATOR BASIS</p>
      <dl class="operator-coordinate">
        <div><dt>BASE</dt><dd>STRUCTURAL</dd></div>
        <div><dt>OVERLAY</dt><dd>${active ? 'SCIENTIFIC EPISODE' : 'NONE'}</dd></div>
        <div><dt>EPISODE</dt><dd>CELL 002</dd></div>
      </dl>
      <button type="button" data-toggle-episode>${active ? 'DISABLE' : 'ENABLE'} SCIENTIFIC EPISODE</button>
      <details ${active ? 'open' : ''}>
        <summary>EPISODE ADDRESS / BASIS</summary>
        <code>${escapeHtml(episode.episodeId)}</code>
        <pre>${escapeHtml(JSON.stringify(episode.episodeAddress, null, 2))}</pre>
      </details>
      ${active ? `
        <div class="episode-sequence" aria-label="recorded Cell 002 sequence">
          ${episode.sequence.map((item, index) => `
            <button type="button" data-episode-step="${index}" class="${index === operatorState.episodeStep ? 'is-current' : ''}">
              <span>${index + 1}</span>${escapeHtml(item.label)}
            </button>
          `).join('')}
        </div>
        <p class="episode-current-step">RECORDED STEP ${operatorState.episodeStep + 1}: ${escapeHtml(step.label)}</p>
      ` : ''}
    </section>
  `;
}

export function renderWorkcycleOperator(workcycle, runtimeError = null) {
  if (!workcycle) {
    return `
      <section class="fabric-workcycle-operator is-unavailable">
        <p class="fabric-kicker">WORKCYCLE / METABOLISM</p>
        <strong>RUNTIME PROJECTION UNAVAILABLE</strong>
        <p>${escapeHtml(runtimeError || 'No workcycle runtime snapshot received.')}</p>
      </section>
    `;
  }

  const summary = workcycle.operator_summary || {};
  const consequence = workcycle.latest_consequence;
  const evaluation = workcycle.latest_consequence_evaluation;
  const budget = workcycle.wake_budget;
  const cells = workcycle.campaign_progress || {};
  const cellRows = Object.entries(cells).map(([cell, state]) => `
    <div class="workcycle-cell">
      <span>${escapeHtml(cell)}</span>
      <strong>${escapeHtml(state?.posture || 'UNKNOWN')}</strong>
    </div>
  `).join('');

  const workBudget = budget?.work_items;
  const seatBudget = budget?.seat_invocations;
  const repairBudget = budget?.repair_attempts;
  const observations = consequence?.observations || {};
  const horizonClosure = workcycle.temporal_horizon_closure || {};
  const horizon = horizonClosure.primary_horizon || {};
  const surfaces = horizonClosure.seven_surfaces || {};
  const loads = horizonClosure.six_load_dimensions || {};
  const qualification = workcycle.qualification_readiness || {};
  const boundedQualification = qualification.bounded_workcycle || {};
  const selfMovingQualification = qualification.self_moving_workcycle || {};
  const basisRecord = workcycle.basis_record || {};
  const pressureJustification = workcycle.pressure_justification || {};
  const surfaceRows = Object.entries(surfaces).map(([name, item]) => `
    <div class="workcycle-stat"><span>${escapeHtml(name)}</span><strong>${escapeHtml(item?.posture || 'UNRESOLVED')}</strong></div>
  `).join('');
  const loadRows = Object.entries(loads).map(([name, item]) => `
    <div class="workcycle-stat"><span>${escapeHtml(name)}</span><strong>${escapeHtml(item?.direction || 'UNRESOLVED')}</strong></div>
  `).join('');

  return `
    <section class="fabric-workcycle-operator" id="workcycle-detail">
      <p class="fabric-kicker">WORKCYCLE / METABOLISM</p>
      <dl class="operator-coordinate workcycle-coordinate">
        <div><dt>WORKFLOW</dt><dd>${escapeHtml(summary.workflow || 'UNKNOWN')}</dd></div>
        <div><dt>CAMPAIGN</dt><dd>${escapeHtml(summary.campaign || 'UNKNOWN')}</dd></div>
        <div><dt>SEAT WORK</dt><dd>${escapeHtml(summary.seat_work || 'UNKNOWN')}</dd></div>
      </dl>
      <dl class="workcycle-ledger">
        ${field('CAMPAIGN', value(workcycle.campaign_id))}
        ${field('ACTIVE HORIZON', value(workcycle.active_horizon))}
        ${field('NEXT PRESSURE', value(workcycle.next_pressure))}
        ${field('ACTIVE WORK ITEM', value(workcycle.active_work_item, 'NONE'))}
        ${field('LATEST COMPLETED', value(workcycle.latest_completed_work_item, 'NONE'))}
        ${field('NEXT ELIGIBLE', value(workcycle.next_eligible_work_item, 'UNRESOLVED'))}
        ${field('REED ACTION', value(summary.reed_action, 'NONE'))}
      </dl>
      <div class="workcycle-cells" aria-label="workcycle campaign cells">
        ${cellRows || '<span class="fabric-missing">NO CELL PROJECTION</span>'}
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">RELATIONAL HORIZON</p>
        <div class="workcycle-stat"><span>FAMILY</span><strong>${escapeHtml(horizon.family || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>SUBJECT</span><strong>${escapeHtml(horizon.subject || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>POSTURE</span><strong>${escapeHtml(horizonClosure.disposition || 'UNRESOLVED')}</strong></div>
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">SEVEN CONSERVATION SURFACES</p>
        ${surfaceRows || '<span class="fabric-missing">SURFACE POSTURE UNAVAILABLE</span>'}
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">SIX LOAD DIMENSIONS</p>
        ${loadRows || '<span class="fabric-missing">LOAD POSTURE UNAVAILABLE</span>'}
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">QUALIFICATION READINESS</p>
        <div class="workcycle-stat"><span>BOUNDED WORKCYCLE</span><strong>${escapeHtml(boundedQualification.qualification_readiness || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>SELF-MOVING WORKCYCLE</span><strong>${escapeHtml(selfMovingQualification.qualification_readiness || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>BOUNDED BLOCKERS</span><strong>${escapeHtml((boundedQualification.blockers || []).join(' | ') || 'NONE')}</strong></div>
        <div class="workcycle-stat"><span>SELF-MOVING BLOCKERS</span><strong>${escapeHtml((selfMovingQualification.blockers || []).join(' | ') || 'NONE')}</strong></div>
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">BASIS / PRESSURE JUSTIFICATION</p>
        <div class="workcycle-stat"><span>BASIS</span><strong>${escapeHtml(basisRecord.basis_posture || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>LOAD-BEARING RELATION</span><strong>${escapeHtml(pressureJustification.load_bearing_relation || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>PRESSURE POSTURE</span><strong>${escapeHtml(pressureJustification.pressure_posture || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>PROPOSED PRESSURE</span><strong>${escapeHtml(pressureJustification.proposed_pressure || 'NONE')}</strong></div>
        <div class="workcycle-stat"><span>EXPECTED OPERATING CHANGE</span><strong>${escapeHtml(pressureJustification.if_resolved?.expected_operating_change || 'UNRESOLVED')}</strong></div>
        <div class="workcycle-stat"><span>IF NOTHING CHANGES</span><strong>${escapeHtml(pressureJustification.if_nothing_changes || 'DO_NOT_RUN')}</strong></div>
        <div class="workcycle-stat"><span>NEXT WORK POSTURE</span><strong>${escapeHtml(pressureJustification.next_work_posture || 'HOLD_NO_JUSTIFIED_WORK')}</strong></div>
      </div>
      <div class="workcycle-consequence">
        <p class="fabric-kicker">LATEST CONSEQUENCE</p>
        <div class="workcycle-stat"><span>SOURCE BYTES</span><strong>${escapeHtml(observations.source_bytes ?? '—')}</strong></div>
        <div class="workcycle-stat"><span>CANDIDATE BYTES</span><strong>${escapeHtml(observations.candidate_bytes ?? '—')}</strong></div>
        <div class="workcycle-stat"><span>DELTA BYTES</span><strong>${escapeHtml(observations.delta_bytes ?? '—')}</strong></div>
        <div class="workcycle-stat"><span>REDUCTION</span><strong>${escapeHtml(observations.reduction_ratio ?? '—')}</strong></div>
        <div class="workcycle-stat"><span>EVALUATION</span><strong>${escapeHtml(evaluation?.disposition || 'UNRESOLVED')}</strong></div>
      </div>
      <div class="workcycle-budget">
        <p class="fabric-kicker">WAKE BUDGET</p>
        <div class="workcycle-stat"><span>WORK ITEMS</span><strong>${escapeHtml(workBudget ? `${workBudget.consumed}+${workBudget.reserved}/${workBudget.allowed_per_wake}` : '—')}</strong></div>
        <div class="workcycle-stat"><span>SEAT INVOCATIONS</span><strong>${escapeHtml(seatBudget ? `${seatBudget.consumed}+${seatBudget.reserved}/${seatBudget.allowed_per_wake}` : '—')}</strong></div>
        <div class="workcycle-stat"><span>REPAIRS</span><strong>${escapeHtml(repairBudget ? `${repairBudget.consumed}+${repairBudget.reserved}/${repairBudget.allowed}` : '—')}</strong></div>
        <div class="workcycle-stat"><span>AUTO CONTINUATION</span><strong>${escapeHtml(summary.auto_continuation_limit ?? 0)}</strong></div>
      </div>
      <div class="workcycle-controls" aria-label="workcycle controls not yet admitted">
        <button type="button" disabled>WAKE</button>
        <button type="button" disabled>PAUSE</button>
        <button type="button" disabled>STOP</button>
      </div>
      <p class="fabric-unavailable-note">CONTROL WRITE NOT YET ADMITTED · DISPLAYED CONTROL STATE ≠ EXECUTION AUTHORITY</p>
    </section>
  `;
}

export function renderWorkcycleRail(
  workcycle,
  runtimeError = null,
  controlAvailable = false,
) {
  if (!workcycle) {
    return `
      <aside class="workcycle-rail is-unavailable" aria-label="workcycle witness rail">
        <p class="fabric-kicker">WORKCYCLE</p>
        <strong>UNAVAILABLE</strong>
        <p>${escapeHtml(runtimeError || 'No runtime projection.')}</p>
      </aside>
    `;
  }

  const summary = workcycle.operator_summary || {};
  const observation = workcycle.latest_consequence?.observations || {};
  const evaluation = workcycle.latest_consequence_evaluation?.disposition || 'UNRESOLVED';
  const budget = workcycle.wake_budget;
  const workBudget = budget?.work_items;
  const eligibility = workcycle.eligibility || {};
  const currentUnresolved = workcycle.current_unresolved || [];
  const horizonClosure = workcycle.temporal_horizon_closure || {};
  const primaryHorizon = horizonClosure.primary_horizon || {};
  const qualification = workcycle.qualification_readiness || {};
  const boundedQualification = qualification.bounded_workcycle || {};
  const selfMovingQualification = qualification.self_moving_workcycle || {};
  const basisRecord = workcycle.basis_record || {};
  const pressureJustification = workcycle.pressure_justification || {};
  const seatEcology = workcycle.seat_ecology || {};
  const runtimeSeats = seatEcology.registered_runtime_seats || [];
  const durableSeats = seatEcology.durable_seats || [];
  const occupied = new Set(
    (seatEcology.occupied_runtime_seats || []).map((seat) => seat.seat_id),
  );
  const runtimeById = new Map(runtimeSeats.map((seat) => [seat.seat_id, seat]));
  const seatIds = [...new Set([
    ...durableSeats.map((seat) => seat.seat_id),
    ...runtimeSeats.map((seat) => seat.seat_id),
  ].filter(Boolean))];
  const seatRows = seatIds.length
    ? seatIds.slice(0, 8).map((seatId) => {
        const runtime = runtimeById.get(seatId);
        const durable = durableSeats.find((seat) => seat.seat_id === seatId);
        const posture = occupied.has(seatId)
          ? 'OCCUPIED'
          : runtime?.occupancy_state
            || durable?.occupant_binding
            || durable?.trigger_state
            || 'REGISTERED';
        return `
          <div class="workcycle-seat-row">
            <strong>${escapeHtml(seatId)}</strong>
            <span>${escapeHtml(posture)}</span>
          </div>
        `;
      }).join('')
    : '<p class="fabric-missing">NO DURABLE OR LIVE SEATS OBSERVED</p>';

  const workflowEnabled = summary.workflow === 'ON';
  const wakeRequested = Boolean(summary.wake_requested);
  const admitReady = workcycle.next_eligible_work_item
    && workcycle.eligibility?.eligible === true;

  return `
    <aside class="workcycle-rail" aria-label="workcycle witness rail">
      <p class="fabric-kicker">WORKCYCLE / METABOLISM</p>
      <div class="workcycle-rail-state">
        <strong>${escapeHtml(summary.workflow || 'UNKNOWN')}</strong>
        <span>${escapeHtml(summary.campaign || 'UNKNOWN')}</span>
      </div>
      <dl>
        <div><dt>NEXT</dt><dd>${escapeHtml(workcycle.next_pressure || 'UNRESOLVED')}</dd></div>
        <div><dt>ACTIVE</dt><dd>${escapeHtml(workcycle.active_work_item || 'NONE')}</dd></div>
        <div><dt>LATEST</dt><dd>${escapeHtml(workcycle.latest_completed_work_item || 'NONE')}</dd></div>
        <div><dt>EVAL</dt><dd>${escapeHtml(evaluation)}</dd></div>
        <div><dt>DELTA</dt><dd>${escapeHtml(observation.delta_bytes ?? '—')}</dd></div>
        <div><dt>WAKE BUDGET</dt><dd>${escapeHtml(workBudget ? `${workBudget.consumed}+${workBudget.reserved}/${workBudget.allowed_per_wake}` : '—')}</dd></div>
        <div><dt>ELIGIBILITY</dt><dd>${escapeHtml(eligibility.posture || 'UNRESOLVED')}</dd></div>
        <div><dt>REED</dt><dd>${escapeHtml(summary.reed_action || 'NONE')}</dd></div>
        <div><dt>RELATIONAL HORIZON</dt><dd>${escapeHtml(primaryHorizon.family || 'UNRESOLVED')}</dd></div>
        <div><dt>HORIZON POSTURE</dt><dd>${escapeHtml(horizonClosure.disposition || 'UNRESOLVED')}</dd></div>
        <div><dt>HISTORY / CURRENT / UPCOMING</dt><dd>${escapeHtml(
          [
            horizonClosure.history_posture || 'UNRESOLVED',
            horizonClosure.currentness_posture || 'UNRESOLVED',
            horizonClosure.upcoming_work_posture || 'UNRESOLVED',
          ].join(' / '),
        )}</dd></div>
        <div><dt>BOUNDED QUALIFICATION</dt><dd>${escapeHtml(
          boundedQualification.qualification_readiness || 'UNRESOLVED'
        )}</dd></div>
        <div><dt>SELF-MOVING QUALIFICATION</dt><dd>${escapeHtml(
          selfMovingQualification.qualification_readiness || 'UNRESOLVED'
        )}</dd></div>
        <div><dt>PRESSURE JUSTIFICATION</dt><dd>${escapeHtml(
          pressureJustification.pressure_posture || 'UNRESOLVED'
        )}</dd></div>
        <div><dt>JUSTIFIED PRESSURE</dt><dd>${escapeHtml(
          pressureJustification.proposed_pressure || 'NONE'
        )}</dd></div>
        <div><dt>NEXT WORK POSTURE</dt><dd>${escapeHtml(
          pressureJustification.next_work_posture || 'HOLD_NO_JUSTIFIED_WORK'
        )}</dd></div>
      </dl>
      <div class="workcycle-seat-ecology">
        <p class="fabric-kicker">SEATS / OCCUPANTS</p>
        ${seatRows}
      </div>
      <div class="workcycle-rail-controls" aria-label="operator-local workcycle controls">
        <button type="button" data-workcycle-control="ENABLE"
          ${controlAvailable && !workflowEnabled ? '' : 'disabled'}>ENABLE</button>
        <button type="button" data-workcycle-control="WAKE"
          ${controlAvailable && workflowEnabled && !wakeRequested ? '' : 'disabled'}>WAKE</button>
        <button type="button" data-workcycle-control="ADMIT_ONE"
          ${controlAvailable && admitReady ? '' : 'disabled'}>ADMIT ONE</button>
        <button type="button" data-workcycle-control="PAUSE"
          ${controlAvailable && workflowEnabled ? '' : 'disabled'}>PAUSE</button>
        <button type="button" data-workcycle-control="STOP"
          ${controlAvailable ? '' : 'disabled'}>STOP</button>
      </div>
      <p class="workcycle-control-status">
        ${controlAvailable
          ? 'LOCAL OPERATOR CONTROL CONNECTED'
          : 'LOCAL OPERATOR CONTROL UNAVAILABLE'}
      </p>
      <a class="workcycle-detail-link" href="#workcycle-detail">OPEN SCIENTIFIC DETAIL</a>
      <p class="workcycle-rail-debt">${escapeHtml(currentUnresolved.length ? `${currentUnresolved.length} CURRENT UNRESOLVED` : 'NO CURRENT UNRESOLVED DEBT')}</p>
      <p class="fabric-unavailable-note">
        OPERATOR CONTROL IS LOCAL + PREVIEWED + CONFIRMED · ADMISSION ≠ MODEL INVOCATION
      </p>
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

export function renderRepositoryFabric(
  model,
  geometricField,
  operatorState = {overlay: 'NONE', episodeStep: 0, inspectorCollapsed: false},
  episode = null,
  episodeError = null,
  temporalView = null,
  workcycle = null,
  workcycleError = null,
  workcycleControlAvailable = false,
) {
  const source = model.source;
  const counts = repositoryFieldRelationCounts(geometricField);
  const matches = model.query ? repositoryQueryMatches(model).length : model.objects.length;
  const dependencyUnavailable = counts.dependency === 0;
  return `
    <main class="geometric-fabric ${operatorState.inspectorCollapsed ? 'inspector-collapsed' : ''}" data-atlas-primary-surface>
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
        ${renderWorkcycleRail(workcycle, workcycleError, workcycleControlAvailable)}
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
            ${temporalView?.state?.actorLayer ? '<span class="seat">SEAT</span><span class="cursor">CURSOR</span>' : ''}
            ${temporalView?.emissionLedger?.events?.length ? '<span class="transition-emission">TRANSITION EMISSION</span>' : ''}
            <span>ALL SEMANTIC STANDING VISIBLE</span>
            ${operatorState.overlay === 'SCIENTIFIC_EPISODE' ? `
              <span class="scientific-changed">CHANGED</span>
              <span class="scientific-held">HELD FIXED</span>
              <span class="scientific-witnessed">WITNESSED</span>
              <span class="scientific-unresolved">UNRESOLVED</span>
              <span class="scientific-out">OUT OF SCOPE - STILL VISIBLE</span>
            ` : ''}
          </div>
        </section>
        <aside class="fabric-dock" data-independent-inspector-dock>
          <div class="fabric-operators">
          ${renderTemporalOperator(temporalView)}
          ${renderEpisodeOperator(episode, operatorState, episodeError)}
          ${renderWorkcycleOperator(workcycle, workcycleError)}
          <section class="fabric-structural-operator">
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
              <div><dt>EXPLICIT ACTOR RELATIONS</dt><dd>${counts.actor || 'NONE IN FRAME'}</dd></div>
            </dl>
          </section>
          </div>
          ${renderInspector(model, geometricField, episode, operatorState, temporalView)}
        </aside>
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
  return {
    repository: '#f0f5f3', directory: '#b8a1ff', file: '#5ad7df', file_version: '#78d99a',
    seat: '#ff7bd5', cursor: '#ffbe5c',
  }[kind] || '#e5eef2';
}

function nodeRadius(kind) {
  return {repository: 7, directory: 4.5, file: 2.5, file_version: 1.8, seat: 10, cursor: 5.5}[kind] || 2;
}

function classificationColor(category) {
  return {
    CHANGED: '#ff9966',
    HELD_FIXED: '#67b7ff',
    WITNESSED: '#78d99a',
    UNRESOLVED: '#d79cff',
    UNCLASSIFIED: '#9aa8af',
  }[category] || '#596770';
}

export function drawGeometricRepositoryField(
  canvas,
  model,
  geometricField,
  episode = null,
  operatorState = null,
  temporalView = null,
) {
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
    const actorEdge = ['seat', 'cursor'].includes(model.objectById[edge.source_id]?.object_kind)
      || ['seat', 'cursor'].includes(model.objectById[edge.target_id]?.object_kind);
    if (actorEdge && !temporalView?.state?.actorLayer) continue;
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

  const overlayActive = operatorState?.overlay === 'SCIENTIFIC_EPISODE' && episode;
  const activeStep = overlayActive ? episode.sequence[operatorState.episodeStep] : null;
  const activeStepObjects = new Set(activeStep?.objectIds || []);
  const matches = new Set(model.query ? repositoryQueryMatches(model).map((object) => object.object_id) : []);
  const painterOrder = [...geometricField.nodes]
    .filter((node) => projectedById[node.objectId].visible)
    .filter((node) => !['seat', 'cursor'].includes(node.objectKind) || temporalView?.state?.actorLayer)
    .sort((left, right) => projectedById[right.objectId].depth - projectedById[left.objectId].depth);
  const selectedProjected = projectedById[model.selectedObjectId];
  let localDetailLabels = 0;
  let renderedObjects = 0;
  let overlayClassifiedObjects = 0;
  let outOfScopeObjects = 0;
  for (const node of painterOrder) {
    const projected = projectedById[node.objectId];
    const selected = node.objectId === model.selectedObjectId;
    const matched = matches.has(node.objectId);
    const radius = nodeRadius(node.objectKind) + (selected ? 2.5 : 0);
    context.beginPath(); context.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
    context.fillStyle = nodeColor(node.objectKind);
    const explicitlyClassified = overlayActive
      ? (episode.classificationByObjectId[node.objectId] || [])
      : [];
    const outOfScope = overlayActive && !episode.admittedObjectIds.has(node.objectId);
    const baseAlpha = Math.max(0.38, Math.min(1, 1150 / projected.depth));
    context.globalAlpha = outOfScope ? Math.max(0.22, baseAlpha * 0.48) : baseAlpha;
    context.fill(); context.globalAlpha = 1;
    if (selected || matched) {
      context.beginPath(); context.arc(projected.x, projected.y, radius + 5, 0, Math.PI * 2);
      context.strokeStyle = selected ? '#ffffff' : '#ffbe5c';
      context.lineWidth = selected ? 2 : 1.2; context.stroke();
    }
    if (overlayActive) {
      if (outOfScope) outOfScopeObjects += 1;
      if (explicitlyClassified.length) {
        overlayClassifiedObjects += 1;
        explicitlyClassified.slice(0, 4).forEach((classification, index) => {
          context.beginPath();
          context.arc(projected.x, projected.y, radius + 4 + index * 3, 0, Math.PI * 2);
          context.strokeStyle = classificationColor(classification.category);
          context.lineWidth = classification.category === 'CHANGED' ? 2.4 : 1.4;
          context.setLineDash?.(classification.category === 'UNRESOLVED' ? [3, 3] : []);
          context.stroke();
          context.setLineDash?.([]);
        });
      }
      if (activeStepObjects.has(node.objectId)) {
        context.beginPath();
        context.arc(projected.x, projected.y, radius + 12, 0, Math.PI * 2);
        context.strokeStyle = '#ffffff';
        context.lineWidth = 2.5;
        context.stroke();
      }
    }
    const topDirectory = node.objectKind === 'directory' && node.depth === 1;
    const nearSelected = selectedProjected?.visible
      && Math.hypot(projected.x - selectedProjected.x, projected.y - selectedProjected.y) < 190;
    const localDetail = geometricField.camera.distance < 520
      && nearSelected
      && node.objectKind !== 'file_version'
      && localDetailLabels < 36;
    const showLabel = selected || matched || explicitlyClassified.length
      || node.objectKind === 'repository' || topDirectory
      || localDetail;
    if (showLabel) {
      if (localDetail && !selected && !matched && !explicitlyClassified.length) {
        localDetailLabels += 1;
      }
      context.fillStyle = selected ? '#ffffff' : nodeColor(node.objectKind);
      context.font = selected ? '600 12px ui-monospace, monospace' : '10px ui-monospace, monospace';
      context.fillText(node.sourceObject.path || node.sourceObject.repository_identity, projected.x + radius + 5, projected.y - 3);
    }
    renderedObjects += 1;
  }
  const emissionHits = [];
  const regime = emissionScaleRegime(geometricField.camera.distance);
  const emissionGroups = temporalView?.emissionLedger
    ? aggregateTransitionEmissions(temporalView.emissionLedger, regime)
    : [];
  for (const group of emissionGroups) {
    const points = group.object_ids
      .map((objectId) => projectedById[objectId])
      .filter((point) => point?.visible);
    if (!points.length) continue;
    const x = points.reduce((sum, point) => sum + point.x, 0) / points.length;
    const y = points.reduce((sum, point) => sum + point.y, 0) / points.length;
    const radius = Math.min(30, 7 + Math.sqrt(group.event_ids.length) * 3.4);
    context.beginPath(); context.arc(x, y, radius, 0, Math.PI * 2);
    context.strokeStyle = group.classifications.includes('DISAPPEARED') ? '#ff667d'
      : group.classifications.includes('APPEARED') ? '#78d99a'
        : group.classifications.includes('IDENTITY_UNRESOLVED') ? '#d79cff' : '#ffbe5c';
    context.lineWidth = regime === 'LOCAL' ? 1.8 : 2.6;
    context.setLineDash?.(group.classifications.includes('IDENTITY_UNRESOLVED') ? [4, 4] : []);
    context.stroke(); context.setLineDash?.([]);
    emissionHits.push({x, y, radius: radius + 6, event_ids: group.event_ids, aggregate_id: group.aggregate_id});
  }
  return {
    width,
    height,
    projectedById,
    renderedObjects,
    renderedRelations,
    overlayClassifiedObjects,
    outOfScopeObjects,
    emissionRegime: regime,
    emissionGroups,
    emissionHits,
  };
}

export function pickTransitionEmission(frame, x, y) {
  let best = null;
  let distanceBest = Infinity;
  for (const emission of frame?.emissionHits || []) {
    const distance = Math.hypot(emission.x - x, emission.y - y);
    if (distance <= emission.radius && distance < distanceBest) {
      best = emission.event_ids[0] || null;
      distanceBest = distance;
    }
  }
  return best;
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
