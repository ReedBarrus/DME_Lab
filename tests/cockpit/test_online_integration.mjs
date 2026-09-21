import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import { startControlAdapter } from '../../src/cockpit/observer/control_live.mjs';
import { startRuntimeProjection } from '../../src/cockpit/observer/runtime_live.mjs';

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
