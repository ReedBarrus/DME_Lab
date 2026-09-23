import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { startControlAdapter } from '../../src/cockpit/observer/control_live.mjs';
import { startRuntimeProjection } from '../../src/cockpit/observer/runtime_live.mjs';
import {
  CELL002_SPECIMEN_URL,
  CONSEQUENCE_SURFACE_NAMES,
  consequenceRuntimeStatus,
  createCell002SpecimenEmbed,
} from '../../src/cockpit/observer/perceptual_instrument.mjs';

const ROOT = new URL('../../', import.meta.url);

function fakeDocument() {
  return {
    createElement(tag) {
      return {
        tagName: tag.toUpperCase(),
        textContent: '',
        className: '',
        children: [],
        dataset: {},
        append(...items) { this.children.push(...items); },
        replaceChildren(...items) { this.children = [...items]; },
      };
    },
  };
}

function fakeRoot() {
  return {
    className: '',
    children: [],
    dataset: {},
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = [...items]; },
  };
}

test('composed app retains main Action Surface and perceptual runtime/addressing', async () => {
  const app = await readFile(new URL('src/cockpit/observer/app.mjs', ROOT), 'utf8');
  assert.match(app, /selectAction/);
  assert.match(app, /\[data-action-key\]/);
  assert.match(app, /createPerceptualInstrument/);
  assert.match(app, /instrument\?\.selectAddress/);
  assert.match(app, /startRuntimeProjection/);
  assert.match(app, /startControlAdapter/);
});

test('observer DOM exposes instrument, runtime, and separately bounded control roots', async () => {
  const html = await readFile(new URL('src/cockpit/observer/index.html', ROOT), 'utf8');
  for (const id of ['instrument-root', 'runtime-root', 'control-root']) {
    assert.match(html, new RegExp('id="' + id + '"'));
  }
  assert.notEqual(html.indexOf('id="runtime-root"'), html.indexOf('id="control-root"'));
});

test('composed CSS retains both Action Surface and perceptual/runtime families', async () => {
  const css = await readFile(new URL('src/cockpit/observer/styles.css', ROOT), 'utf8');
  assert.match(css, /Action Surface v0/);
  assert.match(css, /\.action-card/);
  assert.match(css, /\.instrument-map/);
  assert.match(css, /\.runtime-panel/);
  assert.match(css, /\.control-panel/);
});

test('composed Consequence surface exposes the recorded Cell 002 specimen in-shell', async () => {
  const html = await readFile(new URL('src/cockpit/observer/index.html', ROOT), 'utf8');
  const app = await readFile(new URL('src/cockpit/observer/app.mjs', ROOT), 'utf8');
  const instrument = await readFile(
    new URL('src/cockpit/observer/perceptual_instrument.mjs', ROOT),
    'utf8',
  );

  assert.match(html, /id="instrument-root"/);
  assert.match(app, /createPerceptualInstrument/);
  assert.deepEqual(CONSEQUENCE_SURFACE_NAMES, ['LIVE', 'CELL002_SPECIMEN']);
  assert.equal(CELL002_SPECIMEN_URL, './cell002.html');
  assert.match(instrument, /CELL 002 SPECIMEN/);
  assert.match(instrument, /RECORDED SPECIMEN != LIVE RUNTIME/);
  assert.match(instrument, /dataset\.consequenceSurface/);
});

test('Cell 002 embed preserves the existing interactive page without trace reinterpretation', async () => {
  const priorDocument = globalThis.document;
  globalThis.document = fakeDocument();
  try {
    const panel = createCell002SpecimenEmbed();
    assert.equal(panel.className, 'instrument-specimen-panel');
    assert.equal(panel.dataset.specimenStanding, 'RECORDED_SOURCE_BOUND_EVIDENCE');
    const frame = panel.children.find((item) => item.tagName === 'IFRAME');
    assert.ok(frame);
    assert.equal(frame.src, './cell002.html');
    assert.match(frame.title, /recorded authority replay specimen/i);
  } finally {
    globalThis.document = priorDocument;
  }

  const instrument = await readFile(
    new URL('src/cockpit/observer/perceptual_instrument.mjs', ROOT),
    'utf8',
  );
  assert.doesNotMatch(
    instrument,
    /authority_membrane_security_cell_002_installed_qualification_result\.json|buildCell002Specimen/,
  );
});

test('live runtime standing stays explicit and separate from the recorded specimen', async () => {
  assert.equal(consequenceRuntimeStatus(null), 'LIVE RUNTIME: NOT CONNECTED');
  assert.equal(consequenceRuntimeStatus({state_sha256: 'a'.repeat(64)}), 'LIVE RUNTIME: CONNECTED');

  const css = await readFile(new URL('src/cockpit/observer/styles.css', ROOT), 'utf8');
  assert.match(css, /body\.instrument-active #runtime-root\s*\{\s*display:\s*none;/s);
  assert.match(css, /\.instrument-consequence-navigation/);
});

test('composed specimen seam adds no control transport or synthetic runtime snapshot', async () => {
  const cellApp = await readFile(
    new URL('src/cockpit/observer/cell002_app.mjs', ROOT),
    'utf8',
  );
  assert.match(cellApp, /method: 'GET'/);
  assert.match(cellApp, /cache: 'no-store'/);
  assert.doesNotMatch(cellApp, /EventSource|WebSocket|startControlAdapter|control-prefill/);
  assert.doesNotMatch(cellApp, /method:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
});

test('unconfigured control remains explicitly unavailable and creates no client', () => {
  const priorWindow = globalThis.window;
  const priorDocument = globalThis.document;
  globalThis.window = {location: {href: 'http://localhost/cockpit/'}};
  globalThis.document = fakeDocument();
  try {
    const root = fakeRoot();
    const result = startControlAdapter(root);
    assert.equal(result, null);
    assert.equal(root.className, 'control-panel control-unavailable');
    assert.match(root.children.map((item) => item.textContent).join(' '), /no Cockpit writes/i);
  } finally {
    globalThis.window = priorWindow;
    globalThis.document = priorDocument;
  }
});

test('unconfigured runtime remains explicitly unavailable and creates no EventSource', () => {
  const priorWindow = globalThis.window;
  const priorDocument = globalThis.document;
  const priorEventSource = globalThis.EventSource;
  globalThis.window = {location: {href: 'http://localhost/cockpit/'}};
  globalThis.document = fakeDocument();
  let constructed = 0;
  globalThis.EventSource = class {
    constructor() { constructed += 1; }
  };
  try {
    const root = fakeRoot();
    const result = startRuntimeProjection(root);
    assert.equal(result, null);
    assert.equal(constructed, 0);
    assert.equal(root.className, 'runtime-panel runtime-unavailable');
    assert.match(root.children.map((item) => item.textContent).join(' '), /not configured/i);
  } finally {
    globalThis.window = priorWindow;
    globalThis.document = priorDocument;
    globalThis.EventSource = priorEventSource;
  }
});
