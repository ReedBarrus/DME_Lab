import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  READ_ONLY_INTERACTIONS,
  buildObserverModel,
  loadProjection,
  navigationPresentation,
  selectOccurrence,
  selectedOccurrence,
} from '../../src/cockpit/observer/model.mjs';
import {
  renderDiagnostics,
  renderHeader,
  renderInspector,
  renderMap,
  renderNavigation,
  unavailableMarkup,
} from '../../src/cockpit/observer/render.mjs';

const fixtureRoot = new URL('./fixtures/observer/', import.meta.url);

async function fixture(name) {
  return JSON.parse(await readFile(new URL(name, fixtureRoot), 'utf8'));
}

function healthyModel() {
  return {
    repository_state: {
      projection_classification: 'derived_read_only',
      projection_status: 'complete',
      repository_identity: {
        status: 'known_value',
        host: 'github.com',
        owner: 'synthetic',
        repository: 'observer_fixture',
      },
      branch: { value: 'fixture', status: 'known_value' },
      source_ref: 'fixture-healthy',
      source_commit: 'synthetic-healthy',
      adapter_version: 'synthetic_fixture',
      projection_time: '2026-09-09T12:00:00Z',
      freshness: {
        status: 'current',
        observed_tail: 'synthetic-healthy',
      },
      current_navigation: {
        active_pressure: {
          value: null,
          status: 'agreement',
          semantic_status: 'explicit_none',
        },
        newly_reachable_open_pressures: {
          values: ['PR-018'],
          status: 'agreement',
        },
        shelved_pressures: { values: [], status: 'known_value' },
        next_experimental_pressure: {
          value: null,
          status: 'explicit_none',
        },
      },
    },
    pressure_nodes: [
      {
        id: 'PR-018',
        title: 'Synthetic open pressure',
        standing: { value: 'OPEN', status: 'known_value' },
        pressure: { value: 'Can OPEN remain inactive?', status: 'known_value' },
        resolution_history: [],
        evidence_ref_ids: [],
        provenance: { source_path: 'synthetic/map.md', source_line: 10 },
      },
      {
        id: 'PR-019',
        title: 'Synthetic bounded pressure with history',
        standing: { value: 'BOUNDED_RESOLUTION', status: 'known_value' },
        pressure: { value: 'Can history remain separate?', status: 'known_value' },
        missing_discriminator: { value: null, status: 'explicit_absent' },
        resolution_so_far: { value: 'Current bounded result.', status: 'known_value' },
        residue: { value: 'Earlier wound remains visible.', status: 'known_value' },
        blocked_by: { value: null, status: 'explicit_absent' },
        unlocks: { value: null, status: 'explicit_absent' },
        resolution_history: [
          {
            id: 'R0',
            standing: { value: 'BASIS_INSUFFICIENT', status: 'known_value' },
            summary: 'The first basis did not discriminate.',
            provenance: { source_path: 'synthetic/map.md', source_line: 30 },
          },
          {
            id: 'R1',
            standing: { value: 'BOUNDED_RESOLUTION', status: 'known_value' },
            summary: 'The second basis discriminated.',
            provenance: { source_path: 'synthetic/map.md', source_line: 31 },
          },
        ],
        evidence_ref_ids: [],
        provenance: { source_path: 'synthetic/map.md', source_line: 20 },
      },
    ],
    pressure_relations: [],
    constraints: [{ id: 'SYNTHETIC-CONSTRAINT-NOT-RENDERED' }],
    evidence_refs: [],
    projection_documents: [{ title: 'SYNTHETIC-PROJECTION-NOT-RENDERED' }],
    projection_diagnostics: [],
  };
}

test('normalized JSON loads through the supplied URL without repository access', async () => {
  const raw = healthyModel();
  let observedUrl;
  let observedOptions;
  const loaded = await loadProjection(async (url, options) => {
    observedUrl = url;
    observedOptions = options;
    return { ok: true, json: async () => raw };
  }, '/provided/normalized.json');

  assert.equal(observedUrl, '/provided/normalized.json');
  assert.deepEqual(observedOptions, { cache: 'no-store' });
  assert.equal(loaded.rawModel, raw);
  assert.equal(loaded.occurrences.length, 2);
});

test('every pressure node entry becomes an independently addressable occurrence', async () => {
  const view = buildObserverModel(await fixture('duplicate_ambiguous.json'));
  const duplicates = view.occurrences.filter((occurrence) => occurrence.node.id === 'PR-901');

  assert.equal(duplicates.length, 2);
  assert.notEqual(duplicates[0].key, duplicates[1].key);
  assert.equal(new Set(view.occurrences.map((occurrence) => occurrence.key)).size, 3);
  assert.ok(duplicates.every((occurrence) => occurrence.isDuplicate));
  assert.match(renderMap(view), /duplicate ID/);
});

test('only normalized pressure relations create semantic edge objects', async () => {
  const duplicate = buildObserverModel(await fixture('duplicate_ambiguous.json'));
  const healthy = buildObserverModel(healthyModel());

  assert.equal(duplicate.semanticEdges.length, 1);
  assert.equal(duplicate.semanticEdges[0].relation.relation_kind, 'blocked_by');
  assert.equal(duplicate.semanticEdges[0].drawable, false);
  assert.equal(duplicate.semanticEdges[0].ambiguous, true);
  assert.equal(healthy.semanticEdges.length, 0);
});

test('explicit none is distinct from missing', async () => {
  const healthy = navigationPresentation(healthyModel().repository_state);
  const failed = navigationPresentation((await fixture('failed_projection.json')).repository_state);

  assert.deepEqual(healthy.active, {
    kind: 'explicit-none',
    text: 'none selected',
    raw: null,
    status: 'explicit_none',
  });
  assert.equal(failed.active.kind, 'missing');
  assert.match(renderNavigation(buildObserverModel(healthyModel())), /none selected/);
  const failedMarkup = renderNavigation(
    buildObserverModel(await fixture('failed_projection.json')),
  );
  assert.match(failedMarkup, /OPEN \/ REACHABLE<\/span><span class="missing">missing/);
  assert.match(failedMarkup, /SHELVED<\/span><span class="missing">missing/);
});

test('OPEN does not become ACTIVE and selection does not mutate activity', () => {
  const view = buildObserverModel(healthyModel());
  const open = view.occurrences.find((occurrence) => occurrence.node.id === 'PR-018');
  const beforeNavigation = structuredClone(view.rawModel.repository_state.current_navigation);

  assert.equal(open.currentStanding, 'OPEN');
  assert.equal(open.isActive, false);
  const selected = selectOccurrence(view, open.key);
  assert.equal(selectedOccurrence(selected).key, open.key);
  assert.equal(selectedOccurrence(selected).isActive, false);
  assert.deepEqual(selected.rawModel.repository_state.current_navigation, beforeNavigation);
});

test('current and historical standings remain separately accessible', () => {
  const initial = buildObserverModel(healthyModel());
  const pressure = initial.occurrences.find((occurrence) => occurrence.node.id === 'PR-019');
  const view = selectOccurrence(initial, pressure.key);
  const markup = renderInspector(view);

  assert.equal(pressure.currentStanding, 'BOUNDED_RESOLUTION');
  assert.deepEqual(
    pressure.node.resolution_history.map((entry) => entry.standing.value),
    ['BASIS_INSUFFICIENT', 'BOUNDED_RESOLUTION'],
  );
  assert.ok(markup.indexOf('CURRENT STANDING') < markup.indexOf('RESOLUTION HISTORY'));
  assert.match(markup, /R0/);
  assert.match(markup, /BASIS_INSUFFICIENT/);
  assert.match(markup, /R1/);
});

test('diagnostics remain globally visible and unsupported structure remains raw residue', async () => {
  const view = buildObserverModel(await fixture('partial_unsupported.json'));
  const diagnostics = renderDiagnostics(view);

  assert.equal(view.diagnostics.available, true);
  assert.equal(view.diagnostics.items.length, 1);
  assert.match(diagnostics, /PROJECTION WOUNDED/);
  assert.match(diagnostics, /unsupported_structure/);
  assert.match(diagnostics, /R0 synthetic residue/);
  assert.equal(view.occurrences[0].node.resolution_history.length, 0);
  assert.equal(view.occurrences[0].isWounded, true);
});

test('missing diagnostics is not rendered as zero diagnostics', () => {
  const raw = healthyModel();
  delete raw.projection_diagnostics;
  const markup = renderDiagnostics(buildObserverModel(raw));

  assert.match(markup, /Diagnostics unavailable/);
  assert.doesNotMatch(markup, /0 reported/);
});

test('freshness current, stale, and unknown remain visually distinct', async () => {
  const current = buildObserverModel(healthyModel());
  const stale = buildObserverModel(await fixture('stale_freshness.json'));
  const unknownRaw = await fixture('stale_freshness.json');
  unknownRaw.repository_state.freshness.status = 'unknown';
  const unknown = buildObserverModel(unknownRaw);

  assert.match(renderHeader(current), /freshness-current/);
  assert.match(renderHeader(stale), /freshness-stale/);
  assert.match(renderHeader(unknown), /freshness-unknown/);
});

test('source conflict is shown without selecting an active pressure', async () => {
  const view = buildObserverModel(await fixture('source_conflict.json'));
  const navigation = navigationPresentation(view.repositoryState);

  assert.equal(navigation.active.kind, 'conflict');
  assert.ok(view.occurrences.every((occurrence) => !occurrence.isActive));
  assert.match(renderNavigation(view), /conflict/);
  assert.match(renderDiagnostics(view), /source_conflict/);
});

test('unknown standing retains its exact value and remains wounded', async () => {
  const view = buildObserverModel(await fixture('unknown_standing.json'));
  const occurrence = view.occurrences[0];

  assert.equal(occurrence.currentStanding, 'UNSEEN_STANDING');
  assert.equal(occurrence.standingClass, 'neutral');
  assert.equal(occurrence.isWounded, true);
  assert.match(renderMap(view), /UNSEEN_STANDING/);
  assert.match(renderDiagnostics(view), /unknown_standing/);
});

test('broken evidence remains visible as a broken navigation reference', async () => {
  const view = buildObserverModel(await fixture('broken_evidence.json'));
  const markup = renderInspector(view);

  assert.match(markup, /missing synthetic evidence/);
  assert.match(markup, /reference status: broken/);
  assert.doesNotMatch(markup, />verified</i);
  assert.doesNotMatch(markup, />proved</i);
  assert.doesNotMatch(markup, />confirmed</i);
});

test('failed and unavailable projections remain explicit', async () => {
  const failed = buildObserverModel(await fixture('failed_projection.json'));
  assert.match(renderHeader(failed), /status-failed/);
  assert.match(renderDiagnostics(failed), /missing_required_source/);

  await assert.rejects(
    loadProjection(async () => ({ ok: false, status: 404 }), '/missing.json'),
    /projection JSON unavailable: HTTP 404/,
  );
  assert.match(unavailableMarkup('synthetic load failure'), /PROJECTION UNAVAILABLE/);
  assert.match(unavailableMarkup('synthetic load failure'), /no cached clean model/i);
});

test('the implemented interaction vocabulary has no mutation action', async () => {
  assert.deepEqual(
    READ_ONLY_INTERACTIONS,
    ['select', 'inspect', 'follow_relation', 'open_evidence_reference', 'copy_reference'],
  );
  const index = await readFile(
    new URL('../../src/cockpit/observer/index.html', import.meta.url),
    'utf8',
  );
  const app = await readFile(
    new URL('../../src/cockpit/observer/app.mjs', import.meta.url),
    'utf8',
  );
  assert.doesNotMatch(index, /<form|contenteditable/i);
  assert.doesNotMatch(app, /\bPOST\b|\bPUT\b|\bPATCH\b|\bDELETE\b/);
});

test('first observer rendering excludes deferred normalized surfaces', () => {
  const view = buildObserverModel(healthyModel());
  const markup = [
    renderHeader(view),
    renderNavigation(view),
    renderMap(view),
    renderInspector(view),
    renderDiagnostics(view),
  ].join('');

  assert.doesNotMatch(markup, /SYNTHETIC-CONSTRAINT-NOT-RENDERED/);
  assert.doesNotMatch(markup, /SYNTHETIC-PROJECTION-NOT-RENDERED/);
});
