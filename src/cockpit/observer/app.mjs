import {
  buildObserverModel,
  loadProjection,
  selectOccurrence,
} from './model.mjs';
import {
  renderDiagnostics,
  renderHeader,
  renderInspector,
  renderMap,
  renderNavigation,
  unavailableMarkup,
} from './render.mjs';

const roots = {
  header: document.querySelector('#repository-root'),
  navigation: document.querySelector('#navigation-root'),
  map: document.querySelector('#map-root'),
  inspector: document.querySelector('#inspector-root'),
  diagnostics: document.querySelector('#diagnostics-root'),
  failure: document.querySelector('#failure-root'),
};

let viewModel = null;

function projectionUrl() {
  const requested = new URL(window.location.href).searchParams.get('model');
  return requested || '../../../generated/cockpit_projection.json';
}

function render() {
  if (!viewModel) {
    return;
  }
  roots.header.innerHTML = renderHeader(viewModel);
  roots.navigation.innerHTML = renderNavigation(viewModel);
  roots.map.innerHTML = renderMap(viewModel);
  roots.inspector.innerHTML = renderInspector(viewModel);
  roots.diagnostics.innerHTML = renderDiagnostics(viewModel);
  roots.failure.replaceChildren();

  document.querySelectorAll('[data-occurrence-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectOccurrence(viewModel, button.dataset.occurrenceKey);
      render();
    });
  });

  const copyButton = document.querySelector('#copy-pressure-id');
  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const value = copyButton.dataset.copyValue || '';
      try {
        await navigator.clipboard.writeText(value);
        copyButton.textContent = 'Copied';
      } catch {
        copyButton.textContent = 'Copy unavailable';
      }
    });
  }
}

function renderFailure(error) {
  viewModel = null;
  roots.header.replaceChildren();
  roots.navigation.replaceChildren();
  roots.map.replaceChildren();
  roots.inspector.replaceChildren();
  roots.diagnostics.replaceChildren();
  roots.failure.innerHTML = unavailableMarkup(error instanceof Error ? error.message : String(error));
  document.body.dataset.projectionState = 'unavailable';
}

async function start() {
  document.body.dataset.projectionState = 'loading';
  try {
    viewModel = await loadProjection(window.fetch.bind(window), projectionUrl());
    document.body.dataset.projectionState =
      viewModel.repositoryState?.projection_status || 'missing';
    render();
  } catch (error) {
    renderFailure(error);
  }
}

start();
