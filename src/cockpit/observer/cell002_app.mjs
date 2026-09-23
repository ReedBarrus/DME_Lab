import {
  CELL002_TRACE_PATH,
  buildCell002Specimen,
  selectInspectable,
  selectTraversal,
} from './cell002_model.mjs';
import { renderCell002Specimen, renderUnavailable } from './cell002_render.mjs';

const root = document.querySelector('#cell002-root');
let model = null;

function render() {
  root.innerHTML = renderCell002Specimen(model);
}

root.addEventListener('click', (event) => {
  const inspectTarget = event.target.closest('[data-inspect-id]');
  if (inspectTarget) {
    model = selectInspectable(model, inspectTarget.dataset.inspectId);
    render();
    document.querySelector('#inspector-title')?.focus({ preventScroll: true });
    return;
  }

  const traversalTarget = event.target.closest('[data-traversal]');
  if (traversalTarget) {
    model = selectTraversal(model, traversalTarget.dataset.traversal);
    render();
  }
});

async function loadSpecimen() {
  try {
    const response = await fetch(CELL002_TRACE_PATH, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'same-origin',
    });
    if (!response.ok) {
      throw new Error(`source fetch failed with HTTP ${response.status}`);
    }
    model = buildCell002Specimen(await response.json());
    render();
  } catch (error) {
    root.innerHTML = renderUnavailable(error instanceof Error ? error.message : String(error));
  }
}

loadSpecimen();
