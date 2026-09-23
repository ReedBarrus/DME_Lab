import {
  DYNAMIC_BASIS_V0,
  STRUCTURAL_BASIS_V0,
  buildGeometricRepositoryField,
  dollyFieldCamera,
  focusFieldObject,
  orbitFieldCamera,
  panFieldCamera,
  resetWholeFieldCamera,
  setGeometricBasisWeights,
} from './repository_fabric_geometry.mjs';
import {
  REPOSITORY_FABRIC_PATH,
  buildRepositoryFabricModel,
  exactRepositoryQueryMatch,
  repositoryQueryMatches,
  selectRepositoryObject,
  setRepositoryQuery,
} from './repository_fabric_model.mjs';
import {
  drawGeometricRepositoryField,
  pickGeometricRepositoryObject,
  renderRepositoryFabric,
  renderRepositoryFabricUnavailable,
} from './repository_fabric_render.mjs';

const root = document.querySelector('#repository-fabric-root');
let model = null;
let geometricField = null;
let frame = null;
let resizeObserver = null;

function updateCameraCoordinate() {
  const output = root.querySelector('[data-camera-coordinate]');
  if (!output || !geometricField) return;
  const {camera} = geometricField;
  output.textContent = `YAW ${camera.yaw.toFixed(2)} / PITCH ${camera.pitch.toFixed(2)} / DOLLY ${camera.distance.toFixed(1)}`;
}

function draw() {
  const canvas = root.querySelector('[data-geometric-field]');
  if (!canvas || !model || !geometricField) return;
  frame = drawGeometricRepositoryField(canvas, model, geometricField);
  updateCameraCoordinate();
}

function pointerCoordinate(canvas, event) {
  const bounds = canvas.getBoundingClientRect();
  return {x: event.clientX - bounds.left, y: event.clientY - bounds.top};
}

function bindCanvas() {
  const canvas = root.querySelector('[data-geometric-field]');
  if (!canvas) return;
  const pointer = {active: false, moved: false, x: 0, y: 0, mode: 'orbit'};

  canvas.addEventListener('pointerdown', (event) => {
    pointer.active = true;
    pointer.moved = false;
    pointer.x = event.clientX;
    pointer.y = event.clientY;
    pointer.mode = event.shiftKey || event.button !== 0 ? 'pan' : 'orbit';
    canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!pointer.active) return;
    const deltaX = event.clientX - pointer.x;
    const deltaY = event.clientY - pointer.y;
    pointer.x = event.clientX;
    pointer.y = event.clientY;
    if (Math.abs(deltaX) + Math.abs(deltaY) > 1) pointer.moved = true;
    if (pointer.mode === 'pan') panFieldCamera(geometricField, deltaX, deltaY);
    else orbitFieldCamera(geometricField, deltaX * 0.006, deltaY * 0.006);
    draw();
  });
  canvas.addEventListener('pointerup', (event) => {
    if (!pointer.active) return;
    pointer.active = false;
    if (!pointer.moved && frame) {
      const point = pointerCoordinate(canvas, event);
      const objectId = pickGeometricRepositoryObject(frame, geometricField, point.x, point.y);
      if (objectId) {
        model = selectRepositoryObject(model, objectId);
        render();
      }
    }
  });
  canvas.addEventListener('pointercancel', () => { pointer.active = false; });
  canvas.addEventListener('contextmenu', (event) => event.preventDefault());
  canvas.addEventListener('wheel', (event) => {
    event.preventDefault();
    dollyFieldCamera(geometricField, event.deltaY * 0.0012);
    draw();
  }, {passive: false});
  canvas.addEventListener('keydown', (event) => {
    const orbit = 0.07;
    const pan = 18;
    if (event.key === 'ArrowLeft') event.shiftKey
      ? panFieldCamera(geometricField, -pan, 0)
      : orbitFieldCamera(geometricField, -orbit, 0);
    else if (event.key === 'ArrowRight') event.shiftKey
      ? panFieldCamera(geometricField, pan, 0)
      : orbitFieldCamera(geometricField, orbit, 0);
    else if (event.key === 'ArrowUp') event.shiftKey
      ? panFieldCamera(geometricField, 0, -pan)
      : orbitFieldCamera(geometricField, 0, -orbit);
    else if (event.key === 'ArrowDown') event.shiftKey
      ? panFieldCamera(geometricField, 0, pan)
      : orbitFieldCamera(geometricField, 0, orbit);
    else if (event.key === '+' || event.key === '=') dollyFieldCamera(geometricField, -0.12);
    else if (event.key === '-') dollyFieldCamera(geometricField, 0.12);
    else if (event.key.toLowerCase() === 'r') resetWholeFieldCamera(geometricField);
    else if (event.key.toLowerCase() === 'f') focusFieldObject(geometricField, model.selectedObjectId);
    else return;
    event.preventDefault();
    draw();
  });

  resizeObserver?.disconnect();
  resizeObserver = new ResizeObserver(draw);
  resizeObserver.observe(canvas);
}

function render() {
  root.innerHTML = renderRepositoryFabric(model, geometricField);
  bindCanvas();
  draw();
}

root.addEventListener('click', async (event) => {
  if (event.target.closest('[data-focus-selected]')) {
    focusFieldObject(geometricField, model.selectedObjectId);
    draw();
    return;
  }
  if (event.target.closest('[data-reset-field]')) {
    resetWholeFieldCamera(geometricField);
    draw();
    return;
  }
  if (event.target.closest('[data-reset-basis]')) {
    setGeometricBasisWeights(geometricField, {
      structural: STRUCTURAL_BASIS_V0,
      dynamic: DYNAMIC_BASIS_V0,
    });
    render();
    return;
  }
  const copyButton = event.target.closest('[data-copy-repository-address]');
  if (!copyButton) return;
  const object = model.objectById[copyButton.dataset.copyRepositoryAddress];
  if (!object) return;
  try {
    await navigator.clipboard.writeText(JSON.stringify(object.address));
    copyButton.textContent = 'ADDRESS COPIED';
  } catch {
    copyButton.textContent = 'COPY UNAVAILABLE';
  }
});

root.addEventListener('input', (event) => {
  if (event.target.matches('[data-repository-query]')) {
    model = setRepositoryQuery(model, event.target.value);
    const count = root.querySelector('[data-query-count]');
    if (count) count.textContent = `${repositoryQueryMatches(model).length} MATCHES - FIELD UNFILTERED`;
    draw();
    return;
  }
  const channel = event.target.dataset.basisChannel;
  if (!channel || event.target.disabled) return;
  const structural = ['containment', 'dependency', 'version'].includes(channel)
    ? {[channel]: Number(event.target.value)}
    : {};
  const dynamic = ['authority', 'consequence'].includes(channel)
    ? {[channel]: Number(event.target.value)}
    : {};
  setGeometricBasisWeights(geometricField, {structural, dynamic});
  const output = root.querySelector(`[data-basis-value="${channel}"]`);
  if (output) output.textContent = Number(event.target.value).toFixed(2);
  draw();
});

root.addEventListener('change', (event) => {
  if (event.target.dataset.basisChannel && !event.target.disabled) render();
});

root.addEventListener('keydown', (event) => {
  if (!event.target.matches('[data-repository-query]') || event.key !== 'Enter') return;
  model = setRepositoryQuery(model, event.target.value);
  const object = exactRepositoryQueryMatch(model);
  if (!object) return;
  model = selectRepositoryObject(model, object.object_id);
  focusFieldObject(geometricField, object.object_id);
  render();
});

async function load() {
  try {
    const response = await fetch(REPOSITORY_FABRIC_PATH, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'same-origin',
    });
    if (!response.ok) throw new Error(`source fetch failed with HTTP ${response.status}`);
    model = buildRepositoryFabricModel(await response.json());
    geometricField = buildGeometricRepositoryField(model);
    render();
  } catch (error) {
    root.innerHTML = renderRepositoryFabricUnavailable(
      error instanceof Error ? error.message : String(error),
    );
  }
}

load();
