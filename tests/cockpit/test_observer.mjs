import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  READ_ONLY_INTERACTIONS,
  STANDING_FORMS,
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
        residue: { value: 'Earlier unresolved result remains visible.', status: 'known_value' },
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
  assert.match(renderMap(view), /duplicate identity/);
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
  assert.ok(markup.indexOf('CURRENT') < markup.indexOf('RESOLUTION HISTORY'));
  assert.match(markup, /R0/);
  assert.match(markup, /BASIS_INSUFFICIENT/);
  assert.match(markup, /R1/);
});

test('diagnostics remain globally visible and unsupported structure remains raw residue', async () => {
  const view = buildObserverModel(await fixture('partial_unsupported.json'));
  const diagnostics = renderDiagnostics(view);

  assert.equal(view.diagnostics.available, true);
  assert.equal(view.diagnostics.items.length, 1);
  assert.match(diagnostics, /PROJECTION DIAGNOSTICS PRESENT/);
  assert.match(diagnostics, /unsupported_structure/);
  assert.match(diagnostics, /R0 synthetic residue/);
  assert.equal(view.occurrences[0].node.resolution_history.length, 0);
  assert.equal(view.occurrences[0].hasProjectionDiagnostic, true);
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

test('unknown standing retains its exact value and projection diagnostic', async () => {
  const view = buildObserverModel(await fixture('unknown_standing.json'));
  const occurrence = view.occurrences[0];

  assert.equal(occurrence.currentStanding, 'UNSEEN_STANDING');
  assert.equal(occurrence.standingClass, 'unknown-standing');
  assert.equal(occurrence.hasUnknownStanding, true);
  assert.equal(occurrence.hasProjectionDiagnostic, true);
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

test('BASIS_INSUFFICIENT is a scientific standing, not a projection diagnostic', () => {
  const raw = healthyModel();
  raw.pressure_nodes[0].standing = {
    value: 'BASIS_INSUFFICIENT',
    status: 'known_value',
  };
  raw.pressure_nodes[0].missing_discriminator = {
    value: 'A public association from the detached result to reachable history.',
    status: 'known_value',
  };
  const view = buildObserverModel(raw);
  const occurrence = view.occurrences[0];
  const map = renderMap(view);

  assert.equal(occurrence.standingClass, 'basis-insufficient');
  assert.equal(occurrence.hasProjectionDiagnostic, false);
  assert.match(map, /BASIS_INSUFFICIENT &ne; projection diagnostic/);
  assert.doesNotMatch(map, /has-diagnostic/);
  assert.match(renderDiagnostics(view), /0 reported/);
});

test('projection diagnostics remain separate from scientific insufficiency', async () => {
  const view = buildObserverModel(await fixture('partial_unsupported.json'));
  const occurrence = view.occurrences[0];
  const map = renderMap(view);

  assert.equal(occurrence.hasProjectionDiagnostic, true);
  assert.match(map, /projection diagnostic 1/);
  assert.match(map, /has-diagnostic/);
  assert.match(renderDiagnostics(view), /unsupported_structure/);
});

test('candidate survived remains exact, basis-relative, and inactive', () => {
  const raw = healthyModel();
  raw.pressure_nodes[0].standing = {
    value: 'CANDIDATE_SURVIVED',
    status: 'known_value',
  };
  raw.pressure_nodes[0].missing_discriminator = {
    value: 'Exact scale matching and an antecedently declared invariant.',
    status: 'known_value',
  };
  raw.pressure_nodes[0].resolution_so_far = {
    value: 'The candidate survived the current bounded pressure only.',
    status: 'known_value',
  };
  const view = buildObserverModel(raw);
  const occurrence = view.occurrences[0];
  const markup = renderInspector(view) + renderMap(view);

  assert.equal(occurrence.currentStanding, 'CANDIDATE_SURVIVED');
  assert.equal(occurrence.isActive, false);
  assert.match(markup, /basis not explicitly projected/);
  assert.doesNotMatch(markup, />active<\/span>/);
  assert.doesNotMatch(markup, /fully resolved|prediction succeeded|verified candidate/i);
});

test('missing discriminator and residue remain separate inspector regions', () => {
  const raw = healthyModel();
  raw.pressure_nodes[0].missing_discriminator = {
    value: 'Synthetic missing discriminator.',
    status: 'known_value',
  };
  raw.pressure_nodes[0].residue = {
    value: 'Synthetic preserved residue.',
    status: 'known_value',
  };
  const markup = renderInspector(buildObserverModel(raw));

  assert.ok(markup.indexOf('MISSING DISCRIMINATOR') < markup.indexOf('Synthetic missing discriminator.'));
  assert.ok(markup.indexOf('RESIDUE') < markup.indexOf('Synthetic preserved residue.'));
  assert.notEqual(markup.indexOf('Synthetic missing discriminator.'), markup.indexOf('Synthetic preserved residue.'));
});

test('standing grammar contains no fully resolved category or scalar rank', () => {
  assert.deepEqual(Object.keys(STANDING_FORMS), [
    'OPEN',
    'PARTIAL_RESOLUTION',
    'BOUNDED_RESOLUTION',
    'BASIS_INSUFFICIENT',
    'BLOCKER_REMOVED',
    'CANDIDATE_SURVIVED',
    'EQUIVALENT_UNDER_CURRENT_PRESSURE',
    'SHELVED',
  ]);
  assert.doesNotMatch(JSON.stringify(STANDING_FORMS), /fully|percent|rank/i);
});

test('relation degree does not change standing or node geometry', () => {
  const withoutRelations = buildObserverModel(healthyModel());
  const raw = healthyModel();
  raw.pressure_relations = [
    {
      source_pressure_id: 'PR-018',
      relation_kind: 'unlocks',
      target_kind: 'pressure',
      target_pressure_id: 'PR-019',
      provenance: { source_path: 'synthetic/map.md', source_line: 10 },
    },
  ];
  const withRelations = buildObserverModel(raw);

  assert.equal(withRelations.occurrences[0].currentStanding, withoutRelations.occurrences[0].currentStanding);
  assert.equal(withRelations.occurrences[0].standingClass, withoutRelations.occurrences[0].standingClass);
  assert.match(renderMap(withRelations), /edge-unlocks/);
  assert.match(renderMap(withRelations), /legend-edge unlocks/);
  assert.doesNotMatch(renderMap(withRelations), /degree-|importance-|rank-/);
});

test('inspector exposes only explicit normalized relation topology', () => {
  const raw = healthyModel();
  raw.pressure_relations = [
    {
      source_pressure_id: 'PR-018',
      relation_kind: 'blocked_by',
      target_kind: 'pressure',
      target_pressure_id: 'PR-019',
      provenance: { source_path: 'synthetic/map.md', source_line: 10 },
    },
  ];
  const markup = renderInspector(buildObserverModel(raw));

  assert.match(markup, /RELATIONS/);
  assert.match(markup, /blocked_by/);
  assert.match(markup, /explicit normalized relation/);
  assert.match(markup, /data-follow-occurrence-key/);
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
