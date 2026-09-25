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
  pickTransitionEmission,
  renderRepositoryFabric,
  renderRepositoryFabricUnavailable,
} from './repository_fabric_render.mjs';
import {
  CELL002_EPISODE_TRACE_PATH,
  buildCell002EpisodeOverlay,
  createAtlasOperatorState,
  setEpisodeStep,
  toggleAtlasInspector,
  toggleScientificEpisode,
} from './cell002_episode_overlay.mjs';
import {
  REPOSITORY_TEMPORAL_LINEAGE_PATH,
  activateWoundReplay,
  bindCurrentTemporalContext,
  buildTemporalLineageModel,
  buildTransitionEmissionLedger,
  createTemporalOperatorState,
  moveTemporalFrame,
  recordTemporalSelection,
  reconstructTemporalFrame,
  selectTransitionEmission,
  setWoundStep,
  toggleActorLayer,
} from './repository_temporal_lineage.mjs';
import {
  TYPED_DISTINCTION_REGISTRY_PATH,
  buildTypedDistinctionRegistryModel,
} from './typed_distinction_registry.mjs';

const root = document.querySelector('#repository-fabric-root');
let model = null;
let geometricField = null;
let frame = null;
let resizeObserver = null;
let episode = null;
let episodeError = null;
let operatorState = createAtlasOperatorState(null);
let temporalLineage = null;
let temporalState = null;
let emissionLedger = null;
let episodeTrace = null;
let typedDistinctionRegistry = null;
let workcycleRuntime = null;
let workcycleRuntimeError = null;
let workcycleSource = null;
let workcycleControlBase = null;
let workcycleRuntimeEndpoint = null;

const LOAD_TIMEOUT_MS = 15000;

function renderLoadStage(stage, detail = '') {
  root.innerHTML = `
    <main class="fabric-unavailable fabric-loading-stage" data-load-stage="${stage}">
      <p class="fabric-kicker">ATLAS BOOT · ${stage}</p>
      <h1>${detail || stage}</h1>
    </main>
  `;
}

async function fetchJsonResponse(url, label) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), LOAD_TIMEOUT_MS);
  try {
    const response = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'same-origin',
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`${label} fetch failed with HTTP ${response.status}`);
    return response;
  } catch (error) {
    if (error?.name === 'AbortError') {
      throw new Error(`${label} fetch exceeded ${LOAD_TIMEOUT_MS}ms`);
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function temporalView() {
  if (!temporalLineage || !temporalState) return null;
  return {
    lineage: temporalLineage,
    state: temporalState,
    emissionLedger,
    typedDistinctionRegistry,
  };
}

function updateCameraCoordinate() {
  const output = root.querySelector('[data-camera-coordinate]');
  if (!output || !geometricField) return;
  const {camera} = geometricField;
  output.textContent = `YAW ${camera.yaw.toFixed(2)} / PITCH ${camera.pitch.toFixed(2)} / DOLLY ${camera.distance.toFixed(1)}`;
}

function draw() {
  const canvas = root.querySelector('[data-geometric-field]');
  if (!canvas || !model || !geometricField) return;
  frame = drawGeometricRepositoryField(
    canvas,
    model,
    geometricField,
    episode,
    operatorState,
    temporalView(),
  );
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
      const emissionId = pickTransitionEmission(frame, point.x, point.y);
      if (emissionId && temporalState) {
        temporalState = selectTransitionEmission(temporalState, emissionId);
        render();
        return;
      }
      const objectId = pickGeometricRepositoryObject(frame, geometricField, point.x, point.y);
      if (objectId) {
        model = selectRepositoryObject(model, objectId);
        if (temporalState) temporalState = recordTemporalSelection(temporalState, model.objectById[objectId]);
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
  root.innerHTML = renderRepositoryFabric(
    model,
    geometricField,
    operatorState,
    episode,
    episodeError,
    temporalView(),
    workcycleRuntime,
    workcycleRuntimeError,
    Boolean(workcycleControlBase),
  );
  bindCanvas();
  draw();
}

function applyRuntimeSnapshot(snapshot) {
  const projectedWorkcycle = snapshot?.state?.workcycle || null;
  workcycleRuntime = projectedWorkcycle
    ? {
        ...projectedWorkcycle,
        temporal_horizon_closure: snapshot?.state?.temporal_horizon_closure || null,
        qualification_readiness: snapshot?.state?.workcycle_qualification || null,
        basis_record: snapshot?.state?.workcycle_basis || null,
        pressure_justification: snapshot?.state?.pressure_justification || null,
      }
    : null;
  workcycleRuntimeError = workcycleRuntime
    ? null
    : 'Runtime snapshot does not contain state.workcycle.';
  if (model && geometricField) render();
}

function runtimeSnapshotUrl() {
  if (!workcycleRuntimeEndpoint) return null;
  try {
    const url = new URL(workcycleRuntimeEndpoint, window.location.href);
    if (url.pathname.endsWith('/runtime/events')) {
      url.pathname = url.pathname.slice(0, -'/runtime/events'.length) + '/runtime/snapshot.json';
      url.search = '';
      url.hash = '';
      return url.toString();
    }
  } catch {
    return null;
  }
  return null;
}

async function refreshWorkcycleRuntimeNow() {
  const snapshotUrl = runtimeSnapshotUrl();
  if (!snapshotUrl) return false;
  const response = await fetch(snapshotUrl, {
    method: 'GET',
    cache: 'no-store',
  });
  if (!response.ok) throw new Error(`runtime refresh failed with HTTP ${response.status}`);
  applyRuntimeSnapshot(await response.json());
  return true;
}

function generatedWorkcycleGestureId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return 'workcycle-' + Date.now() + '-' + Math.floor(Math.random() * 1e9);
}

function controlUrl(suffix) {
  return String(workcycleControlBase || '').replace(/\/$/, '') + suffix;
}

async function postControl(suffix, payload) {
  if (!workcycleControlBase) throw new Error('local workcycle control unavailable');
  const response = await fetch(controlUrl(suffix), {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });
  const value = await response.json();
  if (!response.ok) throw new Error(value?.error || 'workcycle control rejected');
  return value;
}

async function commitWorkcycleGesture(verb) {
  const previewed = await postControl('/workcycle/control/preview', {
    verb,
    gesture_id: generatedWorkcycleGestureId(),
    reason: 'Cockpit operator gesture',
  });
  const next = previewed?.preview?.next_state || {};
  const confirmed = globalThis.confirm(
    [
      'CONFIRM WORKCYCLE CONTROL',
      '',
      'VERB: ' + verb,
      'LIFECYCLE: ' + (next.lifecycle_state || 'UNKNOWN'),
      'WORKFLOW: ' + (next.workflow_enabled ? 'ON' : 'OFF'),
      'SEAT WORK: ' + (next.seat_work_enabled ? 'ENABLED' : 'DISABLED'),
      'WAKE: ' + (next.wake_requested ? 'REQUESTED' : 'CLEAR'),
      'ADMISSION: ' + (next.current_admission?.work_item_id || 'NONE'),
      '',
      'Commit this exact local operator state transition?',
    ].join('\n'),
  );
  if (!confirmed) return null;
  const committed = await postControl('/workcycle/control/commit', {
    preview: previewed.preview,
    preview_sha256: previewed.preview_sha256,
    confirmed_by: 'REED',
  });
  await refreshWorkcycleRuntimeNow();
  return committed;
}

root.addEventListener('click', async (event) => {
  const workcycleControl = event.target.closest('[data-workcycle-control]');
  if (workcycleControl) {
    const verb = workcycleControl.dataset.workcycleControl;
    workcycleControl.disabled = true;
    const original = workcycleControl.textContent;
    workcycleControl.textContent = verb + '…';
    try {
      const result = await commitWorkcycleGesture(verb);
      workcycleControl.textContent = result ? 'COMMITTED' : original;
    } catch (error) {
      workcycleControl.textContent = 'REJECTED';
      globalThis.alert('WORKCYCLE CONTROL REJECTED\n' + error);
    }
    return;
  }
  if (event.target.closest('[data-toggle-actor-layer]') && temporalState) {
    temporalState = toggleActorLayer(temporalState);
    render();
    return;
  }
  if (event.target.closest('[data-activate-wound]') && temporalState && temporalLineage) {
    const next = activateWoundReplay(temporalState, temporalLineage);
    moveToTemporalFrame(next.frameIndex, next);
    return;
  }
  const woundStep = event.target.closest('[data-wound-step]');
  if (woundStep && temporalState && temporalLineage) {
    const next = setWoundStep(temporalState, temporalLineage, woundStep.dataset.woundStep);
    moveToTemporalFrame(next.frameIndex, next);
    const eventId = temporalLineage.woundReplay.steps[next.woundStep]?.event_id;
    temporalState = selectTransitionEmission(temporalState, eventId);
    render();
    return;
  }
  if (event.target.closest('[data-toggle-episode]')) {
    operatorState = toggleScientificEpisode(operatorState, episode);
    render();
    return;
  }
  const episodeStep = event.target.closest('[data-episode-step]');
  if (episodeStep) {
    operatorState = setEpisodeStep(operatorState, episode, episodeStep.dataset.episodeStep);
    render();
    return;
  }
  if (event.target.closest('[data-toggle-inspector]')) {
    operatorState = toggleAtlasInspector(operatorState);
    render();
    return;
  }
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
  if (event.target.matches('[data-temporal-frame]') && temporalState && temporalLineage) {
    moveToTemporalFrame(event.target.value);
    return;
  }
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
  if (temporalState) temporalState = recordTemporalSelection(temporalState, object);
  focusFieldObject(geometricField, object.object_id);
  render();
});

function startWorkcycleRuntimeProjection() {
  const params = new URL(window.location.href).searchParams;
  let endpoint = params.get('runtime');
  workcycleControlBase = params.get('control');
  if (!endpoint) {
    try {
      endpoint = new URL(window.parent.location.href).searchParams.get('runtime');
      workcycleControlBase = workcycleControlBase
        || new URL(window.parent.location.href).searchParams.get('control');
    } catch {
      // Same-origin parent fallback unavailable; retain explicit missing posture.
    }
  }
  if (!endpoint) {
    workcycleRuntimeEndpoint = null;
    workcycleRuntime = null;
    workcycleRuntimeError = 'Runtime sidecar not configured for Atlas workcycle projection.';
    if (model && geometricField) render();
    return null;
  }

  workcycleRuntimeEndpoint = endpoint;
  workcycleRuntimeError = 'Connecting to workcycle runtime projection...';
  workcycleSource?.close?.();
  workcycleSource = new EventSource(endpoint);

  workcycleSource.addEventListener('runtime_projection', (event) => {
    try {
      applyRuntimeSnapshot(JSON.parse(event.data));
    } catch (error) {
      workcycleRuntime = null;
      workcycleRuntimeError = `Workcycle runtime parse failure: ${error}`;
      if (model && geometricField) render();
    }
  });

  workcycleSource.onerror = () => {
    if (!workcycleRuntime) {
      workcycleRuntimeError = 'Live runtime sidecar unavailable for Atlas workcycle projection.';
      if (model && geometricField) render();
    }
  };
  return workcycleSource;
}

function rebuildEpisodeForFrame() {
  const inspectorCollapsed = operatorState.inspectorCollapsed;
  if (!episodeTrace || (temporalLineage
      && model.source.source_commit !== temporalLineage.source.source_commit)) {
    episode = null;
    episodeError = 'Cell 002 episode basis is not present at the selected historical frame.';
    operatorState = {...createAtlasOperatorState(null), inspectorCollapsed};
    return;
  }
  try {
    episode = buildCell002EpisodeOverlay(model, episodeTrace);
    episodeError = null;
    operatorState = {...createAtlasOperatorState(episode), inspectorCollapsed};
  } catch (error) {
    episode = null;
    episodeError = error instanceof Error ? error.message : String(error);
    operatorState = {...createAtlasOperatorState(null), inspectorCollapsed};
  }
}

function moveToTemporalFrame(frameIndex, stateOverride = null) {
  if (!temporalLineage || !temporalState) return;
  const camera = structuredClone(geometricField.camera);
  const weights = structuredClone(geometricField.weights);
  const moved = moveTemporalFrame(stateOverride || temporalState, temporalLineage, frameIndex, model);
  model = moved.model;
  temporalState = moved.state;
  geometricField = buildGeometricRepositoryField(model);
  geometricField.camera = camera;
  setGeometricBasisWeights(geometricField, weights);
  emissionLedger = buildTransitionEmissionLedger(model);
  rebuildEpisodeForFrame();
  render();
}

async function loadOptionalEpisodeOverlay(requestedView) {
  try {
    const episodeResponse = await fetchJsonResponse(
      CELL002_EPISODE_TRACE_PATH,
      'Cell 002 episode trace',
    );
    episodeTrace = await episodeResponse.json();
    rebuildEpisodeForFrame();
    if (requestedView.get('overlay') === 'cell002') {
      operatorState = toggleScientificEpisode(operatorState, episode);
    }
  } catch (error) {
    episodeError = `Optional scientific episode unavailable: ${error instanceof Error ? error.message : String(error)}`;
    operatorState = createAtlasOperatorState(null);
  }
  if (model && geometricField) render();
}

function applyRequestedView(requestedView) {
  if (temporalState && temporalLineage) {
    if (requestedView.has('wound')) {
      const next = setWoundStep(
        temporalState,
        temporalLineage,
        requestedView.get('wound'),
      );
      moveToTemporalFrame(next.frameIndex, next);
      temporalState = selectTransitionEmission(
        temporalState,
        temporalLineage.woundReplay.steps[temporalState.woundStep]?.event_id,
      );
    } else if (requestedView.has('frame')) {
      moveToTemporalFrame(requestedView.get('frame'));
    }
    if (requestedView.get('actors') === 'on' && !temporalState.actorLayer) {
      temporalState = toggleActorLayer(temporalState);
    }
  }

  const requestedFocus = requestedView.get('focus');
  if (requestedFocus) {
    model = setRepositoryQuery(model, requestedFocus);
    const object = exactRepositoryQueryMatch(model);
    if (object) {
      model = selectRepositoryObject(model, object.object_id);
      if (temporalState) {
        temporalState = recordTemporalSelection(temporalState, object);
      }
      focusFieldObject(geometricField, object.object_id);
    }
  }
}

async function attachHistoricalContext(requestedView) {
  const [temporalResponse, distinctionResponse] = await Promise.all([
    fetchJsonResponse(REPOSITORY_TEMPORAL_LINEAGE_PATH, 'temporal lineage')
      .catch((error) => ({ok: false, error})),
    fetchJsonResponse(TYPED_DISTINCTION_REGISTRY_PATH, 'typed distinction registry')
      .catch((error) => ({ok: false, error})),
  ]);

  if (temporalResponse.ok) {
    try {
      temporalLineage = buildTemporalLineageModel(await temporalResponse.json());
      bindCurrentTemporalContext(temporalLineage, model);
      temporalState = createTemporalOperatorState(temporalLineage, model);
      emissionLedger = buildTransitionEmissionLedger(model);
    } catch (error) {
      temporalLineage = null;
      temporalState = null;
      emissionLedger = null;
      episodeError = `Temporal context unavailable: ${error instanceof Error ? error.message : String(error)}`;
    }
  } else {
    episodeError = `Temporal lineage unavailable: ${temporalResponse.error || 'unknown error'}`;
  }

  if (temporalLineage && distinctionResponse.ok) {
    try {
      typedDistinctionRegistry = buildTypedDistinctionRegistryModel(
        await distinctionResponse.json(),
        temporalLineage,
      );
    } catch (error) {
      typedDistinctionRegistry = null;
      episodeError = [
        episodeError,
        `Typed distinction overlay unavailable: ${error instanceof Error ? error.message : String(error)}`,
      ].filter(Boolean).join(' | ');
    }
  }

  applyRequestedView(requestedView);
  if (model && geometricField) render();
  void loadOptionalEpisodeOverlay(requestedView);
}

async function load() {
  try {
    const bootStarted = performance.now();
    renderLoadStage('FETCHING CURRENT FABRIC', 'Loading the current addressed world...');

    const response = await fetchJsonResponse(
      REPOSITORY_FABRIC_PATH,
      'repository fabric',
    );

    renderLoadStage(
      'BUILDING CURRENT MODEL',
      'Constructing current source-bound repository model...',
    );
    model = buildRepositoryFabricModel(await response.json());

    renderLoadStage(
      'BUILDING GEOMETRY',
      `Laying out ${model.objects.length} addressed objects...`,
    );
    geometricField = buildGeometricRepositoryField(model);

    const requestedView = new URL(window.location.href).searchParams;
    applyRequestedView(requestedView);

    renderLoadStage(
      'RENDERING CURRENT WORLD',
      `Painting current Atlas after ${Math.round(performance.now() - bootStarted)}ms...`,
    );
    render();
    startWorkcycleRuntimeProjection();

    void attachHistoricalContext(requestedView);
  } catch (error) {
    root.innerHTML = renderRepositoryFabricUnavailable(
      error instanceof Error ? error.message : String(error),
    );
  }
}

load();
