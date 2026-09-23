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
  );
  bindCanvas();
  draw();
}

root.addEventListener('click', async (event) => {
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

async function load() {
  try {
    const [response, temporalResponse, distinctionResponse] = await Promise.all([
      fetch(REPOSITORY_FABRIC_PATH, {
        method: 'GET', cache: 'no-store', credentials: 'same-origin',
      }),
      fetch(REPOSITORY_TEMPORAL_LINEAGE_PATH, {
        method: 'GET', cache: 'no-store', credentials: 'same-origin',
      }),
      fetch(TYPED_DISTINCTION_REGISTRY_PATH, {
        method: 'GET', cache: 'no-store', credentials: 'same-origin',
      }),
    ]);
    if (!response.ok) throw new Error(`source fetch failed with HTTP ${response.status}`);
    if (temporalResponse.ok) {
      temporalLineage = buildTemporalLineageModel(await temporalResponse.json());
      model = reconstructTemporalFrame(temporalLineage, temporalLineage.frames.length - 1);
      temporalState = createTemporalOperatorState(temporalLineage, model);
      emissionLedger = buildTransitionEmissionLedger(model);
      if (distinctionResponse.ok) {
        typedDistinctionRegistry = buildTypedDistinctionRegistryModel(
          await distinctionResponse.json(),
          temporalLineage,
        );
      }
    } else {
      model = buildRepositoryFabricModel(await response.json());
    }
    geometricField = buildGeometricRepositoryField(model);
    try {
      const episodeResponse = await fetch(CELL002_EPISODE_TRACE_PATH, {
        method: 'GET',
        cache: 'no-store',
        credentials: 'same-origin',
      });
      if (!episodeResponse.ok) {
        throw new Error(`episode source fetch failed with HTTP ${episodeResponse.status}`);
      }
      episodeTrace = await episodeResponse.json();
      rebuildEpisodeForFrame();
      const requestedView = new URL(window.location.href).searchParams;
      if (temporalState && temporalLineage) {
        if (requestedView.has('wound')) {
          const next = setWoundStep(temporalState, temporalLineage, requestedView.get('wound'));
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
      if (requestedView.get('overlay') === 'cell002') {
        operatorState = toggleScientificEpisode(operatorState, episode);
      }
      const requestedFocus = requestedView.get('focus');
      if (requestedFocus) {
        model = setRepositoryQuery(model, requestedFocus);
        const object = exactRepositoryQueryMatch(model);
        if (object) {
          model = selectRepositoryObject(model, object.object_id);
          if (temporalState) temporalState = recordTemporalSelection(temporalState, object);
          focusFieldObject(geometricField, object.object_id);
        }
      }
    } catch (error) {
      episodeError = error instanceof Error ? error.message : String(error);
      operatorState = createAtlasOperatorState(null);
    }
    render();
  } catch (error) {
    root.innerHTML = renderRepositoryFabricUnavailable(
      error instanceof Error ? error.message : String(error),
    );
  }
}

load();
