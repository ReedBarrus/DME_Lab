import { startRuntimeProjection } from './runtime_live.mjs';
import { startControlAdapter } from './control_live.mjs';
import { createPerceptualInstrument } from './perceptual_instrument.mjs';
import {
  buildObserverModel,
  followEvidence,
  followPressureRelation,
  loadProjection,
  openLineage,
  selectConstraint,
  selectEvidence,
  selectOccurrence,
  selectProjectionDocument,
  selectView,
} from './model.mjs';
import {
  renderActiveView,
  renderDiagnostics,
  renderHeader,
  renderNavigation,
  renderViewNavigation,
  unavailableMarkup,
} from './render.mjs';

const roots = {
  header: document.querySelector('#repository-root'),
  navigation: document.querySelector('#navigation-root'),
  viewNavigation: document.querySelector('#view-navigation-root'),
  view: document.querySelector('#view-root'),
  diagnostics: document.querySelector('#diagnostics-root'),
  failure: document.querySelector('#failure-root'),
};

let viewModel = null;
const instrument = createPerceptualInstrument(document.querySelector('#instrument-root'));

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
  roots.viewNavigation.innerHTML = renderViewNavigation(viewModel);
  roots.view.innerHTML = renderActiveView(viewModel);
  roots.diagnostics.innerHTML = renderDiagnostics(viewModel);
  roots.failure.replaceChildren();

  document.querySelectorAll('[data-view]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectView(viewModel, button.dataset.view);
      render();
    });
  });

  document.querySelectorAll('[data-occurrence-key]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const key = button.dataset.occurrenceKey;
      viewModel = selectOccurrence(viewModel, key);
      render();
      instrument?.selectAddress(
        'pressure_occurrence',
        key,
        event.ctrlKey || event.metaKey || event.shiftKey,
      );
    });
  });

  document.querySelectorAll('[data-open-lineage-key]').forEach((button) => {
    button.addEventListener('click', () => {
      const key = button.dataset.openLineageKey;
      viewModel = openLineage(viewModel, key);
      render();
      instrument?.selectAddress('pressure_occurrence', key);
    });
  });

  document.querySelectorAll('[data-follow-relation-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = followPressureRelation(
        viewModel,
        button.dataset.followRelationKey,
        button.dataset.fromOccurrenceKey,
      );
      render();
      if (viewModel.selectedOccurrenceKey) {
        instrument?.selectAddress(
          'pressure_occurrence',
          viewModel.selectedOccurrenceKey,
        );
      }
    });
  });

  document.querySelectorAll('[data-constraint-key]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const key = button.dataset.constraintKey;
      viewModel = selectConstraint(viewModel, key);
      render();
      instrument?.selectAddress(
        'constraint',
        key,
        event.ctrlKey || event.metaKey || event.shiftKey,
      );
    });
  });

  document.querySelectorAll('[data-evidence-key]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const key = button.dataset.evidenceKey;
      viewModel = selectEvidence(viewModel, key);
      render();
      instrument?.selectAddress(
        'evidence',
        key,
        event.ctrlKey || event.metaKey || event.shiftKey,
      );
    });
  });

  document.querySelectorAll('[data-follow-evidence-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = followEvidence(
        viewModel,
        button.dataset.evidenceOwnerKind,
        button.dataset.evidenceOwnerKey,
        button.dataset.followEvidenceKey,
      );
      render();
      if (viewModel.selectedEvidenceKey) {
        instrument?.selectAddress('evidence', viewModel.selectedEvidenceKey);
      }
    });
  });

  document.querySelectorAll('[data-projection-document-key]').forEach((button) => {
    button.addEventListener('click', (event) => {
      const key = button.dataset.projectionDocumentKey;
      viewModel = selectProjectionDocument(viewModel, key);
      render();
      instrument?.selectAddress(
        'projection_document',
        key,
        event.ctrlKey || event.metaKey || event.shiftKey,
      );
    });
  });

  document.querySelectorAll('[data-filter-target]').forEach((input) => {
    input.addEventListener('input', () => {
      const query = input.value.trim().toLowerCase();
      const target = input.dataset.filterTarget;
      if (target !== 'constraint-card' && target !== 'source-card') {
        return;
      }
      document.querySelectorAll('.' + target).forEach((item) => {
        item.hidden = query.length > 0 && !item.dataset.filterText.includes(query);
      });
    });
  });

  document.querySelectorAll('[data-copy-value]').forEach((copyButton) => {
    copyButton.addEventListener('click', async () => {
      const value = copyButton.dataset.copyValue || '';
      try {
        await navigator.clipboard.writeText(value);
        copyButton.textContent = 'Copied';
      } catch {
        copyButton.textContent = 'Copy unavailable';
      }
    });
  });
}

function renderFailure(error) {
  viewModel = null;
  roots.header.replaceChildren();
  roots.navigation.replaceChildren();
  roots.viewNavigation.replaceChildren();
  roots.view.replaceChildren();
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
    instrument?.setObserverModel(viewModel);
  } catch (error) {
    renderFailure(error);
  }
}

start();

startRuntimeProjection(
  document.querySelector('#runtime-root'),
  (snapshot) => instrument?.setRuntimeSnapshot(snapshot),
);
startControlAdapter(document.querySelector('#control-root'));
